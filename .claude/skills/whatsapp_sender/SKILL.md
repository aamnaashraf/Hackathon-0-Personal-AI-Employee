---
name: whatsapp_sender
description: Sends WhatsApp messages via MCP server. Use when needing to send replies to WhatsApp contacts.
---

## Overview
This skill sends WhatsApp messages using the WhatsApp MCP server.

## When to Use
- Sending responses to WhatsApp inquiries
- Following up with contacts
- Sending promotional messages (with approval)
- Confirming appointments or meetings

## Parameters
- `contact_name`: Full name or phone number of the contact
- `message_text`: The message to send

## Processing Guidelines
1. **Verify Contact**: Ensure contact exists in address book
2. **Message Quality**: Keep messages professional and concise
3. **Approval Check**: Get approval for business communications
4. **Rate Limiting**: Don't send too many messages rapidly

## Example Usage
```
whatsapp_sender.send_message("Aamna Ashraf Rajput", "Thank you for your inquiry. We'll send you more information shortly.")
```

## Restrictions
- Follow Company Handbook communication guidelines
- Get approval for external communications over $500
- Respect privacy and spam regulations
- Don't send marketing messages without consent