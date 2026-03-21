---
name: tavily
description: Search the web using Tavily API with advanced AI-powered search capabilities
metadata:
  {
    "openclaw":
      {
        "requires": { "env": ["TAVILY_API_KEY"] },
        "primaryEnv": "TAVILY_API_KEY"
      }
  }
---

# Tavily Search Skill

Use Tavily API to perform advanced web searches with AI-powered results.

## Usage

The Tavily skill provides powerful search capabilities:

- **Search**: Get comprehensive search results with relevance scoring
- **Answer**: Get direct answers to questions with supporting evidence
- **Context**: Get search context for AI model augmentation

## Configuration

You need a Tavily API key. Set it in your OpenClaw config:

```json
{
  "skills": {
    "entries": {
      "tavily": {
        "enabled": true,
        "apiKey": "your-tavily-api-key"
      }
    }
  }
}
```

## Examples

- `/tavily search latest AI developments`
- `/tavily answer what is the weather in Beijing today`
- `/tavily context machine learning best practices`

## Notes

- Tavily provides more relevant and focused results than traditional search engines
- Results include source URLs and content snippets
- The API supports various search parameters for fine-tuning results