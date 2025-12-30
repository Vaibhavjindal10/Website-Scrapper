# Design Notes

## Static vs JS Fallback

**Strategy**: The scraper implements a static-first approach with intelligent fallback to JavaScript rendering.

1. **Static Scraping First**: Always attempts to fetch and parse static HTML using `requests` and `selectolax` for speed.

2. **Heuristic for JS Fallback**: If static scraping yields less than 500 characters of text content across all sections, the scraper automatically falls back to Playwright for JavaScript rendering.

3. **Fallback Conditions**:
   - Static fetch fails (network error, timeout)
   - Very little content extracted (< 500 chars total)
   - Missing main content indicators

4. **Error Handling**: If JS rendering fails, the scraper returns whatever static content was successfully extracted, along with error information in the `errors` array.

## Wait Strategy for JS

- [x] Network idle
- [x] Fixed sleep
- [ ] Wait for selectors

**Details**: The scraper uses a combination of `wait_until="networkidle"` for initial page load, followed by a fixed 2-second sleep to allow JavaScript to fully render. This ensures that most dynamic content is loaded before extraction begins. For interactions (clicks, scrolls), additional 1-2 second waits are used to allow content to load after each action.

## Click & Scroll Strategy

**Click flows implemented**:
- Tab clicking: Attempts to find and click `[role="tab"]` elements or elements with `.tab` class
- Load more buttons: Searches for buttons/links containing "Load more" or "Show more" text, or elements with `load-more`/`show-more` classes

**Scroll / pagination approach**:
- **Infinite Scroll**: Performs 3 scroll operations, scrolling to the bottom of the page and waiting 2 seconds between each scroll to allow lazy-loaded content to appear
- **Pagination Links**: If scrolling doesn't reveal new content, attempts to find and click "Next" pagination links
- **Hybrid Approach**: Combines both strategies - scrolls first, then tries pagination if needed

**Stop conditions**:
- Maximum of 3 pages visited (to prevent infinite loops)
- Maximum of 3 scroll operations
- Timeout of 30 seconds for page navigation
- Timeout of 5 seconds for individual interactions

## Section Grouping & Labels

**How you group DOM into sections**:
1. **Primary Strategy**: Uses HTML5 semantic landmarks (`<header>`, `<nav>`, `<main>`, `<section>`, `<footer>`, `<article>`) to identify natural content boundaries
2. **Fallback Strategy**: If no landmarks are found, uses heading elements (`<h1>` through `<h6>`) to create section boundaries
3. **Final Fallback**: If neither landmarks nor headings are found, creates a single section from the `<body>` element

**How you derive section `type` and `label`**:
- **Type Detection**:
  - Based on HTML tag name (`header` → `nav`, `nav` → `nav`, `footer` → `footer`)
  - Checks for semantic class names containing "hero", "faq", "pricing"
  - Defaults to `section` for generic sections, `unknown` if unclear
- **Label Generation**:
  - Primary: Uses the first heading (`<h1>`, `<h2>`, `<h3>`) found in the section
  - Fallback: Takes the first 5-7 words of the section's text content
  - Default: "Section" if no suitable label can be derived

## Noise Filtering & Truncation

**What you filter out**:
- Script and style tags (always excluded)
- Cookie banners: Elements with class/id containing "cookie"
- Modals and popups: Elements with class/id containing "modal", "popup", "overlay"
- Banners: Elements with class/id containing "banner"
- Uses case-insensitive matching on class and id attributes

**How you truncate `rawHtml` and set `truncated`**:
- **Truncation Limit**: 5000 characters per section
- **Method**: If `rawHtml` exceeds 5000 characters, it's truncated to the first 5000 characters with "..." appended
- **Truncated Flag**: Set to `true` when truncation occurs, `false` otherwise
- **Rationale**: Keeps response sizes manageable while preserving enough HTML for debugging and analysis

## Additional Design Decisions

1. **Link Normalization**: All relative URLs are converted to absolute URLs using `urljoin` to ensure consistency

2. **Content Limits**: 
   - Links: Maximum 50 per section
   - Images: Maximum 20 per section
   - Lists: Maximum 10 per section
   - Tables: Maximum 5 per section
   - Text: Maximum 5000 characters per section

3. **Error Collection**: Errors are collected throughout the scraping process and included in the response, allowing partial results even when some operations fail

4. **Meta Extraction**: Prioritizes Open Graph tags for title/description, falls back to standard meta tags, and uses `<html lang>` attribute for language detection

5. **Timeout Strategy**: Uses reasonable timeouts (10s for HTTP requests, 30s for page navigation) to prevent hanging on slow or unresponsive sites

