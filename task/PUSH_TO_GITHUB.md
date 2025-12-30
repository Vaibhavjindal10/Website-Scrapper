# Push to GitHub - Step by Step Guide

Your GitHub: **https://github.com/Vaibhavjindal10**

## Quick Method: GitHub Desktop (Easiest - No Command Line)

1. **Download GitHub Desktop**: https://desktop.github.com/
2. **Install and sign in** with your GitHub account (Vaibhavjindal10)
3. **Add Repository**:
   - Click "File" → "Add Local Repository"
   - Browse to: `C:\Users\vaibh\OneDrive\Desktop\task`
   - Click "Add Repository"
4. **Commit**:
   - You'll see all your files
   - Write commit message: "Initial commit: Lyftr AI Website Scraper"
   - Click "Commit to main"
5. **Publish**:
   - Click "Publish repository" button at the top
   - Repository name: `lyftr-ai-scraper` (or any name you like)
   - Make it Public or Private
   - Click "Publish Repository"

Done! Your code will be at: `https://github.com/Vaibhavjindal10/lyftr-ai-scraper`

---

## Alternative: Install Git and Use Command Line

### Step 1: Install Git
Download from: https://git-scm.com/download/win
- During installation, use default settings
- After installation, **restart your terminal/PowerShell**

### Step 2: Run These Commands

Open PowerShell in this folder and run:

```powershell
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Lyftr AI Website Scraper"

# Add your GitHub as remote (replace REPO_NAME with your desired name)
git remote add origin https://github.com/Vaibhavjindal10/REPO_NAME.git

# Set main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

**Important**: Before running the last commands, you need to:
1. Go to https://github.com/new
2. Create a new repository (name it `lyftr-ai-scraper` or any name)
3. **Don't** initialize with README, .gitignore, or license
4. Copy the repository URL and use it in the `git remote add origin` command

---

## Repository Name Suggestions

- `lyftr-ai-scraper`
- `universal-website-scraper`
- `website-scraper-mvp`
- `lyftr-fullstack-assignment`

Choose any name you like!

