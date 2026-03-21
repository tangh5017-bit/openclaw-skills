---
name: clawdirect
description: Direct communication and messaging through OpenClaw's native channels.
metadata:
  {
    "openclaw": {}
  }
---

# ClawDirect Skill

Enable direct, real-time communication through OpenClaw's built-in messaging capabilities.

## Features
- Send direct messages to users
- Broadcast to multiple recipients
- Rich media support (images, files, voice)
- Message formatting and styling
- Delivery confirmation and read receipts
- Cross-platform messaging (QQ, Telegram, WhatsApp, etc.)

## Usage
- `/clawdirect send <user> <message>` - Send direct message
- `/clawdirect broadcast <message>` - Broadcast to all channels
- `/clawdirect media <user> <file>` - Send media file
- `/clawdirect voice <user> <text>` - Send voice message
- `/clawdirect status` - Check delivery status

## Requirements
- Uses OpenClaw's built-in messaging infrastructure
- No external API keys needed
- Works with configured communication channels
- Real-time delivery through native protocols