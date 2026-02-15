@echo off
REM WhatsApp Message Processing Workflow Helper

echo ========================================
echo WhatsApp Message Processing Workflow
echo ========================================
echo.

echo Step 1: Check for new WhatsApp messages
echo Files in Watchers/WhatsApp folder:
dir "E:\hackathon 0\Hackathon-0-FTE-s-\AI_Employee_Vault\Watchers\WhatsApp" /b

echo.
echo Step 2: To move a message to Pending Approval:
echo Example: move "E:\hackathon 0\Hackathon-0-FTE-s-\AI_Employee_Vault\Watchers\WhatsApp\whatsapp_*.md" "E:\hackathon 0\Hackathon-0-FTE-s-\AI_Employee_Vault\Pending_Approval\"
echo.

echo Step 3: To send a reply to a contact:
echo Example: python whatsapp_mcp.py "Contact Name" "Your message"
echo.

echo Current time: %date% %time%
echo ========================================