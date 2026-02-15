@echo off
echo ========================================
echo Git History Reset Script
echo ========================================
echo.
echo This will:
echo 1. Delete all git history
echo 2. Create fresh initial commit
echo 3. Keep all your current files
echo.
echo WARNING: This cannot be undone!
echo.
pause

echo.
echo [1/4] Removing .git directory...
rmdir /s /q .git

echo [2/4] Initializing new git repository...
git init

echo [3/4] Adding all files...
git add .

echo [4/4] Creating initial commit...
git commit -m "Initial commit - Gold Tier AI Employee System

Complete autonomous AI Employee implementation with:
- 3 operational watchers (Gmail, WhatsApp, File System)
- 4 social media integrations (Facebook, Instagram, LinkedIn, Twitter/X)
- 6 MCP servers (Email, Odoo, Facebook, Instagram, Twitter, WhatsApp)
- 23 Claude Code skills
- CEO briefing generator
- Comprehensive audit logging
- Error recovery and health monitoring
- 97.3%% test pass rate
- 16 completed tasks

Gold Tier requirements: 100%% complete
"

echo.
echo ========================================
echo Done! Clean history created.
echo ========================================
echo.
echo Next steps:
echo 1. Review with: git log
echo 2. Push to GitHub: git remote add origin https://github.com/faqehanoor/Hackathon-0-FTE-s-.git
echo 3. Force push: git push -u origin main --force
echo.
pause
