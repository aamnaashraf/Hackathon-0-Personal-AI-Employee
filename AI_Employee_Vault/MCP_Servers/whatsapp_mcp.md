---
type: mcp_server
server_id: MCP_002
status: active
protocol: whatsapp_web
---

# WhatsApp MCP Server Definition

This defines a Managed Control Plane server for WhatsApp communication in the AI Employee system.

## Server Details
- Type: WhatsApp Web Interface
- Protocol: Playwright-based browser automation
- Status: Active
- Endpoint: whatsapp_watcher.py integration

## Capabilities
- Send WhatsApp messages to contacts
- Receive WhatsApp message notifications
- Manage WhatsApp session persistence
- Handle message delivery confirmations

## Configuration
```json
{
  "session_path": "./whatsapp_session",
  "send_timeout": 30000,
  "retry_attempts": 3,
  "rate_limit": 10,
  "notifications": true
}
```

## API Endpoints
- `send_message(contact_name, message_text)` - Send message to specific contact
- `get_status()` - Check WhatsApp connection status
- `get_unread_count()` - Get number of unread messages