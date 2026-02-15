"""
WhatsApp Sender Skill Implementation
Sends WhatsApp messages via the MCP server
"""
import json
import subprocess
import sys
from pathlib import Path

def send_whatsapp_message(contact_name, message_text):
    """
    Send a WhatsApp message to a specific contact

    Args:
        contact_name (str): Name or phone number of the contact
        message_text (str): Message to send

    Returns:
        dict: Result of the operation
    """
    try:
        # Import the WhatsApp MCP module
        from whatsapp_mcp import create_whatsapp_mcp_instance

        # Create MCP instance
        mcp = create_whatsapp_mcp_instance()

        # Send the message
        result = mcp.send_message(contact_name, message_text)

        return result

    except ImportError:
        # Fallback: try to call the script directly
        try:
            script_path = Path(__file__).parent.parent.parent / "whatsapp_mcp.py"
            cmd = [sys.executable, str(script_path), contact_name, message_text]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return {"success": True, "output": result.stdout}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

def main():
    """Main function to handle command line calls"""
    if len(sys.argv) < 3:
        print("Usage: python whatsapp_sender.py <contact_name> <message_text>")
        sys.exit(1)

    contact_name = sys.argv[1]
    message_text = sys.argv[2]

    result = send_whatsapp_message(contact_name, message_text)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()