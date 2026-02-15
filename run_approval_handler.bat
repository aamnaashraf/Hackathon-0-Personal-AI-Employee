@echo off
echo ========================================
echo Approval Handler - Auto Social Posting
echo ========================================
echo.
echo Monitoring Approved folder for:
echo   - Instagram posts (INSTA_POST_*.md)
echo   - Facebook posts (FB_POST_*.md)
echo   - LinkedIn posts (LINKEDIN_POST_*.md)
echo   - WhatsApp replies (WHATSAPP_REPLY_*.md)
echo   - Email replies (REPLY_APPROVED_*.md)
echo.
echo Press Ctrl+C to stop monitoring
echo.
echo ========================================
echo.

python approval_handler.py

pause
