---
name: polymarket-odds
description: Get real-time odds and market data from Polymarket prediction markets.
metadata:
  {
    "openclaw": {
      "requires": { "bins": ["curl"] }
    }
  }
---

# Polymarket Odds Skill

Fetch real-time odds, market data, and predictions from Polymarket.

## Features
- Get current market odds
- Track price movements
- Monitor specific prediction markets
- Analyze market sentiment
- Export data for analysis

## Usage
- `/polymarket-odds market <market-id>` - Get specific market data
- `/polymarket-odds trending` - Get trending markets
- `/polymarket-odds search <query>` - Search markets by topic
- `/polymarket-odds categories` - List market categories

## Requirements
- Uses public Polymarket API endpoints
- No authentication required for basic data
- Requires curl for HTTP requests