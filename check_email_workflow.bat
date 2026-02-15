@echo off
echo ========================================
echo Email Workflow - Complete System Check
echo ========================================
echo.

echo [1] Checking Email Sender Watcher Status...
tasklist | findstr python | findstr -v findstr
echo.

echo [2] Checking Today's Email Logs...
type "AI_Employee_Vault\Logs\2026-02-14_email_sender.log" 2>nul || echo No emails sent today yet
echo.

echo [3] Checking Done Folder (Sent Emails)...
dir /B /O-D "AI_Employee_Vault\Done\REPLY_*.md" 2>nul | findstr /C:"REPLY" || echo No email replies in Done folder
echo.

echo [4] Checking Approved Folder (Ready to Send)...
dir /B "AI_Employee_Vault\Approved\REPLY_*.md" 2>nul | findstr /C:"REPLY" || echo No email replies waiting in Approved
echo.

echo [5] Checking Pending_Approval Folder (Drafts)...
dir /B "AI_Employee_Vault\Pending_Approval\REPLY_*.md" 2>nul | findstr /C:"REPLY" || echo No email drafts in Pending_Approval
echo.

echo ========================================
echo Workflow Status Summary
echo ========================================
echo.
echo To START email sender watcher:
echo   python done_folder_email_sender.py
echo.
echo To CHECK your Gmail inbox:
echo   Open: https://mail.google.com
echo   Login: aamnaashraf501@gmail.com
echo.
echo To TEST workflow:
echo   1. Create draft in Pending_Approval
echo   2. Move to Approved (review)
echo   3. Move to Done (auto-send)
echo.
pause
