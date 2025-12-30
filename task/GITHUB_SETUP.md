# GitHub Setup Instructions

## Option 1: Using GitHub Desktop (Easiest)

1. Download and install GitHub Desktop: https://desktop.github.com/
2. Open GitHub Desktop
3. Click "File" → "Add Local Repository"
4. Select this folder: `C:\Users\vaibh\OneDrive\Desktop\task`
5. Click "Publish repository" button
6. Choose a name for your repository
7. Click "Publish Repository"

## Option 2: Using Git Command Line

### Step 1: Install Git
Download Git from: https://git-scm.com/download/win
After installation, restart your terminal.

### Step 2: Initialize Repository
```bash
cd C:\Users\vaibh\OneDrive\Desktop\task
git init
git add .
git commit -m "Initial commit: Lyftr AI Website Scraper"
```

### Step 3: Create Repository on GitHub
1. Go to https://github.com/new
2. Create a new repository (don't initialize with README)
3. Copy the repository URL

### Step 4: Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## Option 3: Using GitHub CLI

If you have GitHub CLI installed:
```bash
gh repo create lyftr-ai-scraper --public --source=. --remote=origin --push
```

