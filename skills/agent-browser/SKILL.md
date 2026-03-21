---
name: agent-browser
description: Web browser automation and control for agents to interact with web pages.
metadata:
  {
    "openclaw": {
      "requires": { "bins": ["playwright"] }
    }
  }
---

# Agent Browser Skill

Enable AI agents to automatically interact with web browsers and web applications.

## Features
- Automated web page navigation
- Form filling and submission
- Click and interaction automation
- Screenshot and visual analysis
- Web scraping and data extraction
- Multi-tab and multi-window management
- Headless browser operation

## Usage
- `/agent-browser navigate <url>` - Navigate to webpage
- `/agent-browser click <selector>` - Click element
- `/agent-browser type <selector> <text>` - Type text
- `/agent-browser screenshot` - Take screenshot
- `/agent-browser scrape <selector>` - Extract data
- `/agent-browser wait <condition>` - Wait for conditions
- `/agent-browser tabs` - Manage browser tabs

## Requirements
- Requires Playwright for browser automation
- No API keys needed - uses local browser instances
- Supports Chrome, Firefox, and WebKit
- Can run headless or with visible browser