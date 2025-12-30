# PowerShell script to set up and push to GitHub
# Run this after installing Git

Write-Host "=== Setting up Git Repository ===" -ForegroundColor Green

# Check if git is installed
try {
    $gitVersion = git --version
    Write-Host "Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Git is not installed!" -ForegroundColor Red
    Write-Host "Please install Git from: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "After installation, restart PowerShell and run this script again." -ForegroundColor Yellow
    exit 1
}

# Initialize repository
Write-Host "`nInitializing git repository..." -ForegroundColor Cyan
git init

# Add all files
Write-Host "Adding files..." -ForegroundColor Cyan
git add .

# Create commit
Write-Host "Creating initial commit..." -ForegroundColor Cyan
git commit -m "Initial commit: Lyftr AI Website Scraper"

Write-Host "`n=== Repository initialized successfully! ===" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Go to https://github.com/new" -ForegroundColor White
Write-Host "2. Create a new repository (e.g., 'lyftr-ai-scraper')" -ForegroundColor White
Write-Host "3. DO NOT initialize with README, .gitignore, or license" -ForegroundColor White
Write-Host "4. Copy the repository URL" -ForegroundColor White
Write-Host "5. Run these commands:" -ForegroundColor White
Write-Host "   git remote add origin https://github.com/Vaibhavjindal10/YOUR_REPO_NAME.git" -ForegroundColor Cyan
Write-Host "   git branch -M main" -ForegroundColor Cyan
Write-Host "   git push -u origin main" -ForegroundColor Cyan

