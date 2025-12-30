"""
Website Scraper - Core scraping logic
Handles static scraping, JS rendering, interactions, and section extraction
"""
import re
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    # Dummy types for type hints when Playwright is not available
    Page = None
    Browser = None
    BrowserContext = None


class WebsiteScraper:
    """Main scraper class"""
    
    def __init__(self, url: str):
        self.url = url
        self.base_url = url
        self.visited_urls = set()
        self.sections = []
        self.interactions = {
            "clicks": [],
            "scrolls": 0,
            "pages": []
        }
        self.errors = []
        self.meta = {
            "title": "",
            "description": "",
            "language": "en",
            "canonical": None
        }
    
    async def scrape(self) -> Dict[str, Any]:
        """Main scraping method"""
        scraped_at = datetime.now(timezone.utc).isoformat()
        
        # Try static scraping first
        static_html = self._static_fetch()
        
        sections = []
        if static_html:
            # Parse static HTML
            parser = BeautifulSoup(static_html, 'html.parser')
            self._extract_meta(parser)
            sections = self._extract_sections(parser, self.url)
            
            # Heuristic: if we got very little content, try JS rendering
            total_text = sum(len(s.get("content", {}).get("text", "")) for s in sections)
            if total_text < 500:  # Less than 500 chars, likely needs JS
                try:
                    js_result = await self._js_scrape()
                    if js_result and js_result["sections"]:
                        sections = js_result["sections"]
                        self.interactions = js_result["interactions"]
                        self.errors.extend(js_result.get("errors", []))
                except Exception as e:
                    self.errors.append({
                        "message": f"JS scraping failed: {str(e)}",
                        "phase": "render"
                    })
                    # Keep static sections if JS fails
        else:
            # Static fetch failed, try JS
            try:
                js_result = await self._js_scrape()
                if js_result:
                    sections = js_result["sections"]
                    self.interactions = js_result["interactions"]
                    self.errors.extend(js_result.get("errors", []))
            except Exception as e:
                self.errors.append({
                    "message": f"JS scraping failed: {str(e)}",
                    "phase": "render"
                })
                sections = []
        
        # Ensure we have at least one section
        if not sections:
            sections = [{
                "id": "empty-0",
                "type": "unknown",
                "label": "No content found",
                "sourceUrl": self.url,
                "content": {
                    "headings": [],
                    "text": "",
                    "links": [],
                    "images": [],
                    "lists": [],
                    "tables": []
                },
                "rawHtml": "",
                "truncated": False
            }]
        
        return {
            "url": self.url,
            "scrapedAt": scraped_at,
            "meta": self.meta,
            "sections": sections,
            "interactions": self.interactions,
            "errors": self.errors
        }
    
    def _static_fetch(self) -> Optional[str]:
        """Fetch static HTML"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.errors.append({
                "message": f"Static fetch failed: {str(e)}",
                "phase": "fetch"
            })
            return None
    
    def _extract_meta(self, parser: BeautifulSoup):
        """Extract meta information"""
        # Title
        title_elem = parser.select_one("title")
        if not title_elem:
            og_title = parser.select_one('meta[property="og:title"]')
            if og_title:
                self.meta["title"] = og_title.get("content", "")
        else:
            self.meta["title"] = title_elem.get_text(strip=True)
        
        # Description
        desc_elem = parser.select_one('meta[name="description"]')
        if not desc_elem:
            og_desc = parser.select_one('meta[property="og:description"]')
            if og_desc:
                self.meta["description"] = og_desc.get("content", "")
        else:
            self.meta["description"] = desc_elem.get("content", "")
        
        # Language
        html_elem = parser.select_one("html")
        if html_elem:
            lang = html_elem.get("lang", "en")
            self.meta["language"] = lang[:2] if lang else "en"
        
        # Canonical
        canonical_elem = parser.select_one('link[rel="canonical"]')
        if canonical_elem:
            self.meta["canonical"] = canonical_elem.get("href")
    
    def _extract_sections(self, parser: BeautifulSoup, source_url: str) -> List[Dict[str, Any]]:
        """Extract sections from HTML"""
        sections = []
        section_id_counter = 0
        
        # Filter out noise
        noise_selectors = [
            'script', 'style', 'noscript',
            '[class*="cookie"]', '[class*="banner"]', '[class*="modal"]',
            '[class*="popup"]', '[class*="overlay"]', '[id*="cookie"]',
            '[id*="banner"]', '[id*="modal"]', '[id*="popup"]'
        ]
        
        # Find landmark elements
        landmarks = parser.select("header, nav, main, section, footer, article")
        
        if not landmarks:
            # Fallback: use headings to create sections
            headings = parser.select("h1, h2, h3")
            for heading in headings:
                # Skip if in noise
                parent = heading.parent
                if parent and any(noise in str(parent).lower() for noise in ["cookie", "banner", "modal"]):
                    continue
                
                if parent:
                    section = self._extract_section_from_element(parent, source_url, section_id_counter)
                    if section:
                        sections.append(section)
                        section_id_counter += 1
        else:
            for landmark in landmarks:
                # Skip noise elements
                if any(noise in str(landmark).lower() for noise in ["cookie", "banner", "modal", "popup"]):
                    continue
                
                section = self._extract_section_from_element(landmark, source_url, section_id_counter)
                if section:
                    sections.append(section)
                    section_id_counter += 1
        
        # If still no sections, create one from body
        if not sections:
            body = parser.select_one("body")
            if body:
                section = self._extract_section_from_element(body, source_url, section_id_counter)
                if section:
                    sections.append(section)
        
        return sections
    
    def _extract_section_from_element(self, element, source_url: str, section_id: int) -> Optional[Dict[str, Any]]:
        """Extract section data from a DOM element"""
        if not element:
            return None
        
        # Determine type
        tag_name = element.name.lower() if element.name else "unknown"
        section_type = "unknown"
        if tag_name == "header":
            section_type = "nav"
        elif tag_name == "nav":
            section_type = "nav"
        elif tag_name == "footer":
            section_type = "footer"
        elif tag_name in ("section", "article", "main"):
            section_type = "section"
        
        # Check class attribute
        class_attr = element.get("class", [])
        class_str = " ".join(class_attr) if isinstance(class_attr, list) else str(class_attr)
        if "hero" in class_str.lower():
            section_type = "hero"
        elif "faq" in class_str.lower():
            section_type = "faq"
        elif "pricing" in class_str.lower():
            section_type = "pricing"
        
        # Extract headings
        headings = []
        for h in element.select("h1, h2, h3, h4, h5, h6"):
            text = h.get_text(strip=True)
            if text:
                headings.append(text)
        
        # Extract text
        text_parts = []
        for p in element.select("p"):
            text = p.get_text(strip=True)
            if text and len(text) > 10:  # Filter very short text
                text_parts.append(text)
        
        # Also get text from divs and spans if paragraphs are sparse
        if len(text_parts) < 2:
            for div in element.select("div, span"):
                text = div.get_text(strip=True)
                if text and len(text) > 20 and text not in text_parts:
                    text_parts.append(text)
        
        text_content = " ".join(text_parts[:10])  # Limit to first 10 paragraphs
        
        # Extract links
        links = []
        for a in element.select("a"):
            href = a.get("href")
            if href:
                absolute_url = urljoin(source_url, href)
                link_text = a.get_text(strip=True)
                if link_text:
                    links.append({
                        "text": link_text[:100],  # Truncate long link text
                        "href": absolute_url
                    })
        
        # Extract images
        images = []
        for img in element.select("img"):
            src = img.get("src") or img.get("data-src")
            if src:
                absolute_src = urljoin(source_url, src)
                alt = img.get("alt", "")
                images.append({
                    "src": absolute_src,
                    "alt": alt
                })
        
        # Extract lists
        lists = []
        for ul_ol in element.select("ul, ol"):
            items = []
            for li in ul_ol.select("li"):
                item_text = li.get_text(strip=True)
                if item_text:
                    items.append(item_text)
            if items:
                lists.append(items)
        
        # Extract tables (simplified)
        tables = []
        for table in element.select("table"):
            table_data = []
            for tr in table.select("tr"):
                row = []
                for td in tr.select("td, th"):
                    cell_text = td.get_text(strip=True)
                    row.append(cell_text)
                if row:
                    table_data.append(row)
            if table_data:
                tables.append(table_data)
        
        # Generate label
        label = "Section"
        if headings:
            label = headings[0][:50]
        elif text_content:
            words = text_content.split()[:7]
            label = " ".join(words)
        
        # Get raw HTML
        raw_html = str(element)
        truncated = False
        if len(raw_html) > 5000:
            raw_html = raw_html[:5000] + "..."
            truncated = True
        
        return {
            "id": f"{section_type}-{section_id}",
            "type": section_type,
            "label": label[:100],
            "sourceUrl": source_url,
            "content": {
                "headings": headings[:10],
                "text": text_content[:5000],  # Limit text length
                "links": links[:50],  # Limit links
                "images": images[:20],  # Limit images
                "lists": lists[:10],
                "tables": tables[:5]
            },
            "rawHtml": raw_html,
            "truncated": truncated
        }
    
    async def _js_scrape(self) -> Optional[Dict[str, Any]]:
        """Scrape using Playwright for JS-rendered content"""
        if not PLAYWRIGHT_AVAILABLE:
            self.errors.append({
                "message": "Playwright not available. Install with: pip install playwright && playwright install chromium",
                "phase": "render"
            })
            return None
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()
            
            try:
                # Navigate to URL
                await page.goto(self.url, wait_until="networkidle", timeout=30000)
                self.visited_urls.add(self.url)
                self.interactions["pages"].append(self.url)
                
                # Wait for content to load
                await page.wait_for_timeout(2000)  # Wait 2 seconds for JS to render
                
                # Try to click tabs or "Load more" buttons
                await self._handle_interactions(page)
                
                # Handle scroll/pagination
                await self._handle_scroll_and_pagination(page)
                
                # Get final HTML
                html = await page.content()
                
                # Extract sections
                parser = BeautifulSoup(html, 'lxml')
                self._extract_meta(parser)
                sections = self._extract_sections(parser, self.url)
                
                await browser.close()
                
                return {
                    "sections": sections,
                    "interactions": self.interactions,
                    "errors": []
                }
            
            except Exception as e:
                await browser.close()
                raise e
    
    async def _handle_interactions(self, page: Page):
        """Handle click interactions (tabs, load more buttons)"""
        try:
            # Try to find and click tabs
            tabs = await page.query_selector_all('[role="tab"], .tab, [class*="tab"]')
            if tabs and len(tabs) > 0:
                # Click first tab if not already active
                try:
                    await tabs[0].click(timeout=5000)
                    self.interactions["clicks"].append('[role="tab"] or .tab')
                    await page.wait_for_timeout(1000)
                except:
                    pass
            
            # Try to find "Load more" or "Show more" buttons
            load_more_selectors = [
                'button:has-text("Load more")',
                'button:has-text("Show more")',
                'a:has-text("Load more")',
                '[class*="load-more"]',
                '[class*="show-more"]'
            ]
            
            for selector in load_more_selectors:
                try:
                    button = await page.query_selector(selector)
                    if button:
                        await button.click(timeout=5000)
                        self.interactions["clicks"].append(selector)
                        await page.wait_for_timeout(2000)  # Wait for content to load
                        break
                except:
                    continue
        
        except Exception as e:
            self.errors.append({
                "message": f"Interaction handling failed: {str(e)}",
                "phase": "interaction"
            })
    
    async def _handle_scroll_and_pagination(self, page: Page):
        """Handle scrolling and pagination to depth ≥ 3"""
        try:
            # Strategy: Scroll down multiple times to trigger infinite scroll
            # or follow pagination links
            
            # First, try infinite scroll
            for i in range(3):
                # Scroll down
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                self.interactions["scrolls"] += 1
                await page.wait_for_timeout(2000)  # Wait for content to load
                
                # Check if new content loaded
                current_height = await page.evaluate("document.body.scrollHeight")
                await page.wait_for_timeout(1000)
                new_height = await page.evaluate("document.body.scrollHeight")
                
                # If no new content, try pagination
                if current_height == new_height and i == 0:
                    # Try pagination links
                    next_links = [
                        'a:has-text("Next")',
                        'a:has-text("next")',
                        '[class*="next"]',
                        '[class*="pagination"] a:last-child'
                    ]
                    
                    for selector in next_links:
                        try:
                            next_link = await page.query_selector(selector)
                            if next_link:
                                href = await next_link.get_attribute("href")
                                if href:
                                    next_url = urljoin(self.url, href)
                                    if next_url not in self.visited_urls and len(self.visited_urls) < 3:
                                        await next_link.click(timeout=5000)
                                        await page.wait_for_selector("body", timeout=10000)
                                        self.visited_urls.add(next_url)
                                        self.interactions["pages"].append(next_url)
                                        break
                        except:
                            continue
            
            # Ensure we have at least 3 pages or 3 scrolls
            if len(self.interactions["pages"]) < 3 and self.interactions["scrolls"] < 3:
                # Do more scrolling
                for _ in range(3 - self.interactions["scrolls"]):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    self.interactions["scrolls"] += 1
                    await page.wait_for_timeout(1500)
        
        except Exception as e:
            self.errors.append({
                "message": f"Scroll/pagination failed: {str(e)}",
                "phase": "scroll"
            })

