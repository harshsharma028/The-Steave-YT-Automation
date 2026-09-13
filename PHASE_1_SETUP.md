# Phase 1: Setup & Integration Guide

## ✅ Checklist

- [ ] YouTube API OAuth setup
- [ ] VidIQ API key configuration
- [ ] Environment variables configured
- [ ] Dependencies installed
- [ ] Test YouTube uploader
- [ ] Test VidIQ analytics
- [ ] Database initialized
- [ ] End-to-end workflow tested

---

## 📦 Step 1: Install Dependencies

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client requests
```

**What's being installed**:
- `google-auth-oauthlib` - OAuth 2.0 authentication for YouTube
- `google-api-python-client` - YouTube API client
- `requests` - HTTP library for VidIQ API calls

---

## 🔐 Step 2: YouTube API Setup

### 2.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: Click the project dropdown → "New Project"
3. Name it: `YouTube-Channel-Automation`
4. Wait for project to be created

### 2.2 Enable YouTube Data API

1. In Google Cloud Console, go to **APIs & Services**
2. Click **+ Enable APIs and Services**
3. Search for: `YouTube Data API v3`
4. Click "Enable"

### 2.3 Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **OAuth Client ID**
3. Choose **Desktop application** (for local testing) or **Web application**
4. Download the JSON file
5. Save it as `youtube_client_secret.json` in the project root

**Contents should look like**:
```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "client_secret": "YOUR_CLIENT_SECRET",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}
```

### 2.4 First-Time Authorization

Run this Python snippet to authorize:

```python
from youtube_uploader import YouTubeUploader

uploader = YouTubeUploader('youtube_client_secret.json')
channel_info = uploader.get_channel_info()
print(channel_info)
```

This will:
1. Open your browser to Google login
2. Ask for permissions to upload videos
3. Save `youtube_token.pickle` (don't share this!)
4. Confirm connection is working

---

## 🎯 Step 3: VidIQ API Setup

### 3.1 Get VidIQ API Key

1. Go to [VidIQ Dashboard](https://www.vidiq.com/)
2. Sign up or log in (they have a free tier)
3. Go to **Settings** → **API**
4. Copy your API key

### 3.2 Configure Environment Variables

Create `.env` file in project root:

```bash
# YouTube
YOUTUBE_CLIENT_SECRETS_FILE=youtube_client_secret.json

# VidIQ
VIDIQ_API_KEY=your_vidiq_api_key_here

# Project Settings
CHANNEL_NICHE=Technology
CHANNEL_TARGET_AUDIENCE=Tech Professionals
OUTPUT_DIR=projects
```

### 3.3 Load Environment Variables

Add this to main.py or use `python-dotenv`:

```bash
pip install python-dotenv
```

Then in your code:
```python
from dotenv import load_dotenv
import os

load_dotenv()
vidiq_key = os.getenv('VIDIQ_API_KEY')
```

---

## 🗄️ Step 4: Initialize Analytics Database

The `analytics_db.py` module creates SQLite database automatically on first run:

```python
from analytics_db import AnalyticsDB

# Initialize database (creates channel_analytics.db)
db = AnalyticsDB()

# Add a topic
topic_id = db.add_topic(
    title="AI Writing Tools 2025",
    niche="Technology",
    trending_score=8.5,
    search_volume=12000,
    competition="medium",
    difficulty=5.5
)

# Get channel statistics
stats = db.get_channel_statistics()
print(stats)
# Output: {'total_videos': 0, 'total_views': 0, 'avg_watch_time_hours': 0.0, 'avg_engagement_rate': 0.0}
```

This creates tables for:
- `topics` - Researched topics
- `scripts` - Generated scripts
- `videos` - Published videos
- `analytics` - Performance metrics
- `learnings` - Discovered patterns

---

## 🧪 Step 5: Test YouTube Uploader

```python
from youtube_uploader import YouTubeUploader

uploader = YouTubeUploader('youtube_client_secret.json')

# Get your channel info
channel_info = uploader.get_channel_info()
print(f"Channel: {channel_info['title']}")
print(f"Subscribers: {channel_info['subscribers']}")
print(f"Videos: {channel_info['video_count']}")
```

**Expected output**:
```
Channel: Your Channel Name
Subscribers: 42
Videos: 5
```

---

## 🎬 Step 6: Test VidIQ Analytics

```python
from vidiq_analytics import VidIQAnalytics
import os

api_key = os.getenv('VIDIQ_API_KEY')
vidiq = VidIQAnalytics(api_key)

# Research a keyword
keyword_data = vidiq.research_keyword("AI writing tools")
print(f"Keyword: {keyword_data['keyword']}")
print(f"Search Volume: {keyword_data['search_volume']}")
print(f"Competition: {keyword_data['competition']}")
print(f"Trend Score: {keyword_data['trend_score']}/100")

# Get trending topics
topics = vidiq.get_trending_topics(category='technology', limit=5)
for topic in topics:
    print(f"📈 {topic['title']} - Trending Score: {topic['trending_score']}")
```

**Expected output**:
```
Keyword: AI writing tools
Search Volume: 12000
Competition: medium
Trend Score: 85/100

📈 ChatGPT Alternatives 2025 - Trending Score: 92
📈 Best AI for Writing - Trending Score: 88
...
```

---

## 🔄 Step 7: End-to-End Test Workflow

Here's a complete test of the Phase 1 integration:

```python
import os
from dotenv import load_dotenv
from youtube_uploader import YouTubeUploader
from vidiq_analytics import VidIQAnalytics
from analytics_db import AnalyticsDB

load_dotenv()

print("=" * 60)
print("PHASE 1: SETUP & INTEGRATION TEST")
print("=" * 60)

# 1. Initialize YouTube uploader
print("\n1️⃣  Testing YouTube API...")
uploader = YouTubeUploader('youtube_client_secret.json')
channel_info = uploader.get_channel_info()
print(f"   ✓ Connected to: {channel_info['title']}")

# 2. Initialize VidIQ analytics
print("\n2️⃣  Testing VidIQ API...")
vidiq = VidIQAnalytics(os.getenv('VIDIQ_API_KEY'))
keyword_data = vidiq.research_keyword("AI automation")
print(f"   ✓ Keyword research working")
print(f"   ✓ '{keyword_data['keyword']}': {keyword_data['search_volume']} searches/month")

# 3. Initialize analytics database
print("\n3️⃣  Testing Analytics Database...")
db = AnalyticsDB()
topic_id = db.add_topic(
    title="Test Topic: AI Automation",
    niche="Technology",
    trending_score=keyword_data['trend_score'],
    search_volume=keyword_data['search_volume'],
    competition=keyword_data['competition'],
    difficulty=5.0
)
print(f"   ✓ Topic stored: ID {topic_id}")

# 4. Get channel statistics
stats = db.get_channel_statistics()
print("\n4️⃣  Channel Statistics:")
print(f"   Videos: {stats['total_videos']}")
print(f"   Total Views: {stats['total_views']}")
print(f"   Avg Watch Time: {stats['avg_watch_time_hours']}h")
print(f"   Avg Engagement: {stats['avg_engagement_rate']:.2f}%")

# 5. Get trending topics
print("\n5️⃣  Trending Topics:")
topics = vidiq.get_trending_topics(category='all', limit=3)
for i, topic in enumerate(topics, 1):
    print(f"   {i}. {topic['title']} (Score: {topic['trending_score']})")

print("\n" + "=" * 60)
print("✅ PHASE 1 INTEGRATION TEST COMPLETE")
print("=" * 60)
```

Save this as `test_phase1.py` and run:

```bash
python test_phase1.py
```

---

## 📋 Troubleshooting

### YouTube Auth Issues

**Error**: `InvalidGrantError: 'invalid_grant'`
- **Solution**: Delete `youtube_token.pickle` and re-authenticate
- **Cause**: Token expired or invalid

**Error**: `QuotaExceeded`
- **Solution**: YouTube API has quotas. Check [Google Cloud Console](https://console.cloud.google.com/apis/dashboard) → Quota tab
- **Free tier**: 10,000 quota units/day (enough for ~50 uploads/day)

### VidIQ API Issues

**Error**: `401 Unauthorized`
- **Solution**: Check API key in `.env` is correct
- **Cause**: Invalid or expired API key

**Error**: `Rate limit exceeded`
- **Solution**: VidIQ has rate limits. Add delays between requests:
```python
import time
time.sleep(1)  # 1 second between requests
```

### Database Issues

**Error**: `database is locked`
- **Solution**: Close any other SQLite connections, or use `.retry`:
```python
conn = sqlite3.connect('channel_analytics.db', timeout=10)
```

---

## 🚀 What's Next (Phase 2)

Once Phase 1 is working:

1. **Script Generation Engine** - Auto-generate video scripts using Claude/Gemini
2. **Topic Research Module** - Automatically discover trending topics
3. **Content Calendar** - Schedule videos to upload
4. **Performance Monitoring** - Track views, engagement, retention

---

## 📚 File Reference

| File | Purpose |
|------|---------|
| `youtube_uploader.py` | YouTube API integration (upload, metadata, scheduling) |
| `vidiq_analytics.py` | VidIQ API integration (research, trending, analytics) |
| `analytics_db.py` | SQLite database for tracking everything |
| `youtube_client_secret.json` | OAuth 2.0 credentials (NEVER commit to git!) |
| `youtube_token.pickle` | OAuth token (NEVER commit to git!) |
| `.env` | Environment variables (NEVER commit to git!) |
| `channel_analytics.db` | SQLite database file |

---

## 🔒 Security Notes

**NEVER commit these files to git**:
```
youtube_client_secret.json
youtube_token.pickle
.env
channel_analytics.db (optional, but usually not shared)
```

Add to `.gitignore`:
```
youtube_client_secret.json
youtube_token.pickle
.env
*.pickle
*.db
```

---

## ✨ Success Indicators

You've completed Phase 1 when:

✅ YouTube API OAuth works (can get channel info)  
✅ VidIQ API works (can research keywords)  
✅ Analytics database works (can add/query topics)  
✅ End-to-end test completes with no errors  
✅ You can research a trending topic and see metrics  
✅ All credentials are in `.env` (not hardcoded)  

---

## 📞 Next Steps

1. **Run the test**: `python test_phase1.py`
2. **Fix any issues** using troubleshooting above
3. **Move to Phase 2**: Script generation engine
4. **Target completion**: End of this week

Good luck! 🚀
