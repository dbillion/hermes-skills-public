# TikHub SDK Usage

## Initialization
```python
from tikhub import TikHubClient
# Initialize with your API key
client = TikHubClient(api_token="YOUR_TOKEN")
```

## Supported Platforms
The SDK provides access to 16+ platforms including:
- TikTok (User, Video, Trends)
- Instagram (Profiles, Media)
- Douyin
- LinkedIn (via Web endpoints)

## Execution Pattern
Always use `uv run` to execute scraping scripts:
```bash
uv run python my_scraper.py
```
Refer to `/home/deeone/mcp_servers/TikHub-API-Python-SDK/examples` for ready-to-use scripts.
