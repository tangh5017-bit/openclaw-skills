---
name: youtube-watcher
description: Monitor YouTube channels and videos for new content, updates, and trends.
metadata:
  {
    "openclaw": {
      "requires": { "bins": ["yt-dlp"] }
    }
  }
---

# YouTube Watcher Skill

Monitor YouTube channels, playlists, and videos for new content and updates.

## Features
- Track channel uploads
- Monitor video statistics changes  
- Get notifications for new content
- Extract video metadata and transcripts
- Analyze trending patterns

## Usage
- `/youtube-watcher channel <channel-url>` - Monitor a specific channel
- `/youtube-watcher video <video-url>` - Track video stats
- `/youtube-watcher trending` - Get current trending videos
- `/youtube-watcher search <query>` - Search YouTube content

## Requirements
- Requires yt-dlp for video downloading and metadata extraction
- No API key needed - uses public YouTube data