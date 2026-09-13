# Phase 1: Quick Start Guide (5 Steps)

## 🚀 Do This Now

### Step 1: Install Dependencies (2 min)
```bash
pip install -r requirements_phase1.txt
```

### Step 2: Get YouTube API Credentials (15 min)
1. Go to https://console.cloud.google.com/
2. Create project: "YouTube-Channel-Automation"
3. Enable YouTube Data API v3
4. Create OAuth 2.0 Desktop credentials
5. Download JSON → save as `youtube_client_secret.json`

### Step 3: Get VidIQ API Key (5 min)
1. Go to https://www.vidiq.com/ (free tier available)
2. Sign up / log in
3. Settings → API → Copy key
4. Paste into `.env` file

### Step 4: Set Up Environment (2 min)
```bash
cp .env.example .env
# Edit .env and add your keys
```

### Step 5: Run Test (1 min)
```bash
python test_phase1.py
```

**Total time: ~30 minutes** ✨

---

## 📁 Files Created for Phase 1

```
D:\Projects\The Steave\
├── youtube_uploader.py          # YouTube API client
├── vidiq_analytics.py           # VidIQ research & analytics
├── analytics_db.py              # SQLite database
├── PHASE_1_SETUP.md             # Detailed setup guide (you are here)
├── PHASE_1_QUICK_START.md       # This file
├── YOUTUBE_CHANNEL_PLAN.md      # Full 9-week plan
├── .env.example                 # Template for environment variables
├── requirements_phase1.txt      # Python dependencies
├── youtube_client_secret.json   # (Create after Google Cloud setup)
├── .env                         # (Create by copying .env.example)
└── channel_analytics.db         # (Auto-created on first run)
```

---

## 🧪 3-Minute Test

Once everything is set up, verify it works:

```python
# Save as quick_test.py
import os
from dotenv import load_dotenv
from youtube_uploader import YouTubeUploader
from vidiq_analytics import VidIQAnalytics

load_dotenv()

# Test 1: YouTube
uploader = YouTubeUploader('youtube_client_secret.json')
print("✓ YouTube:", uploader.get_channel_info()['title'])

# Test 2: VidIQ
vidiq = VidIQAnalytics(os.getenv('VIDIQ_API_KEY'))
data = vidiq.research_keyword("AI writing")
print(f"✓ VidIQ: {data['search_volume']} searches/month")

print("\n✅ Phase 1 working!")
```

Run it:
```bash
python quick_test.py
```

---

## 🎯 What Each Module Does

### `youtube_uploader.py`
**What**: Upload videos to YouTube  
**Key methods**:
- `upload_video()` - Upload video with title, description, tags, thumbnail
- `get_channel_info()` - Get your channel stats
- `create_playlist()` - Create playlist
- `schedule_video()` - Schedule video for future publish

### `vidiq_analytics.py`
**What**: Research topics & track performance  
**Key methods**:
- `research_keyword()` - Get search volume, competition, trends
- `get_trending_topics()` - What's hot right now
- `analyze_competitor_channel()` - Learn from successful channels
- `score_title()` - Is your title good for SEO?
- `get_video_analytics()` - Track views, engagement, audience retention
- `get_best_upload_time()` - When should you publish?

### `analytics_db.py`
**What**: Store and query all your data  
**Key methods**:
- `add_topic()` - Save researched topic
- `add_script()` - Save generated script
- `add_video()` - Record published video
- `update_analytics()` - Update daily metrics
- `add_learning()` - Record patterns you discover
- `get_channel_statistics()` - Overall metrics
- `export_report()` - JSON export of everything

---

## 💡 Quick Examples

### Research a Keyword
```python
from vidiq_analytics import VidIQAnalytics

vidiq = VidIQAnalytics('your_api_key')
data = vidiq.research_keyword("AI tools 2025")
print(f"Volume: {data['search_volume']}, Competition: {data['competition']}")
```

### Store a Topic
```python
from analytics_db import AnalyticsDB

db = AnalyticsDB()
topic_id = db.add_topic("AI Tools", "Tech", 8.5, 5000, "medium", 5.0)
```

### Upload a Video (not real, just structure)
```python
from youtube_uploader import YouTubeUploader

uploader = YouTubeUploader('youtube_client_secret.json')
video_id = uploader.upload_video(
    video_file='final_video.mp4',
    title='Best AI Writing Tools 2025',
    description='Top AI tools for writers...',
    tags=['AI', 'writing', 'tools'],
    thumbnail_file='thumbnail.jpg'
)
```

---

## ⚠️ Common Mistakes

❌ **Don't do these:**
- Commit `youtube_client_secret.json` to git
- Commit `youtube_token.pickle` to git
- Hardcode API keys in code
- Upload to YouTube before testing

✅ **Do this instead:**
- Add to `.gitignore`: `*.json`, `*.pickle`, `.env`
- Use `.env` file for secrets
- Use environment variables: `os.getenv('VIDIQ_API_KEY')`
- Test with private/unlisted videos first

---

## 🔗 Important Links

| Resource | URL |
|----------|-----|
| Google Cloud Console | https://console.cloud.google.com |
| YouTube Data API Docs | https://developers.google.com/youtube/v3 |
| VidIQ Dashboard | https://www.vidiq.com |
| YouTube Studio | https://studio.youtube.com |

---

## 📋 Pre-Phase 2 Checklist

- [ ] Dependencies installed
- [ ] YouTube API OAuth working (can call `get_channel_info()`)
- [ ] VidIQ API working (can call `research_keyword()`)
- [ ] Database created and tables exist
- [ ] Can research keywords and see results
- [ ] Environment variables in `.env` file (not hardcoded)
- [ ] `test_phase1.py` runs without errors

**Once all ✅**: Ready for Phase 2 (Script Generation)

---

## 🆘 Still Stuck?

Check **PHASE_1_SETUP.md** section: **Troubleshooting** for common errors

Most common:
1. **YouTube auth fails** → Delete `youtube_token.pickle` and retry
2. **VidIQ returns 401** → Check API key is correct in `.env`
3. **Database locked** → Close any SQLite browser windows

---

**Time to complete Phase 1: ~30 minutes**

When done → `python test_phase1.py` ✨
