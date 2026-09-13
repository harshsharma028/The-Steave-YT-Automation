# The Steave - Complete YouTube Automation System

## Quick Start Guide (30 Minutes to First Video)

Welcome! This guide gets you from zero to running a fully automated YouTube channel in 30 minutes.

---

## 📋 Prerequisites

You'll need:
- Python 3.8+
- Git
- A YouTube channel (create at youtube.com)
- API keys (free):
  - **Gemini API** (for AI scripts/metadata): https://makersuite.google.com/app/apikey
  - **VidIQ API** (for research): https://www.vidiq.com/ (free tier available)

---

## ⚡ Quick Setup (5 Minutes)

### 1. Clone & Install
```bash
git clone https://github.com/harshsharma028/The-Steave-YT-Automation.git
cd The-Steave-YT-Automation
pip install -r requirements.txt
```

### 2. Get API Keys
- **Gemini API**: Visit https://makersuite.google.com/app/apikey → Create API Key
- **VidIQ API**: Sign up at https://www.vidiq.com → Copy API Key

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your API keys:
# CHAT_API_KEY=your_gemini_key
# IMAGE_API_KEY=your_gemini_key
# VIDIQ_API_KEY=your_vidiq_key
```

### 4. Verify Setup
```bash
python test_end_to_end.py
```

✅ If you see "ALL SYSTEMS GO!" you're ready!

---

## 🚀 Run the Full Pipeline (25 Minutes)

### Option A: One Command (Recommended)

```python
from feedback_loop import FeedbackLoop

# This does everything: research → script → metadata → thumbnail → publish
loop = FeedbackLoop()
result = loop.run_complete_feedback_loop()
```

### Option B: Step-by-Step

```python
from topic_research import TopicResearcher
from script_generator import ScriptGenerator
from metadata_generator import MetadataGenerator
from youtube_uploader_v2 import YouTubeUploaderV2
import os
from dotenv import load_dotenv

load_dotenv()

# Step 1: Find trending topic
print("1. Researching trending topics...")
researcher = TopicResearcher(os.getenv('VIDIQ_API_KEY'))
topic = researcher.select_best_topic()
print(f"✓ Topic: {topic['title']}")

# Step 2: Generate script
print("\n2. Generating script...")
gen = ScriptGenerator(os.getenv('CHAT_API_KEY'))
scripts = gen.generate_variations(topic['title'], num_variations=3)
scored = gen.score_variations(scripts)
best_script = scored[0]
print(f"✓ Script: {best_script['hook_type']} ({best_script['quality_score']}/10)")

# Step 3: Create metadata
print("\n3. Creating metadata...")
metadata_gen = MetadataGenerator(os.getenv('CHAT_API_KEY'))
metadata = metadata_gen.generate_complete_metadata(best_script, topic['title'])
print(f"✓ Title: {metadata['titles']['best_title']['title']}")
print(f"✓ Tags: {len(metadata['tags']['youtube_tags'])} tags generated")

# Step 4: Upload to YouTube (requires setup from Phase 1)
# print("\n4. Uploading to YouTube...")
# uploader = YouTubeUploaderV2()
# result = uploader.upload_video(
#     video_file='your_video.mp4',
#     metadata_dict={
#         'title': metadata['titles']['best_title']['title'],
#         'description': metadata['description']['text'],
#         'tags': metadata['tags']['youtube_tags'],
#         'category': 'Education'
#     },
#     visibility='private'  # Start private, make public later
# )
# print(f"✓ Uploaded! Video ID: {result['video_id']}")

print("\n✅ Pipeline complete!")
```

---

## 📚 What Each Phase Does

| Phase | Purpose | Time | Example |
|-------|---------|------|---------|
| **1** | YouTube setup + API keys | 10m | OAuth authentication |
| **2** | Generate scripts | 2m | AI writes script with hook |
| **3** | Create metadata | 2m | SEO titles, descriptions, tags |
| **4** | Design thumbnails | 2m | AI generates images + text |
| **5** | Publish to YouTube | 5m | Upload + schedule + manage |
| **6** | Learn & improve | 1m | Analyze data, optimize next |

---

## 💻 Copy-Paste Examples

### Example 1: Research Only
```python
from topic_research import TopicResearcher

researcher = TopicResearcher('your_vidiq_key')
topics = researcher.research_and_rank_topics(limit=10)

for i, topic in enumerate(topics, 1):
    print(f"{i}. {topic['title']} ({topic['opportunity_score']}/100)")
```

### Example 2: Generate Scripts for Custom Topic
```python
from script_generator import ScriptGenerator

gen = ScriptGenerator('your_gemini_key')

# Generate 3 different versions
scripts = gen.generate_variations('AI Tools 2025', num_variations=3)
scored = gen.score_variations(scripts)

# Best script
print(scored[0]['script_text'])
```

### Example 3: Create Complete Metadata Package
```python
from metadata_generator import MetadataGenerator

gen = MetadataGenerator('your_gemini_key')

metadata = gen.generate_complete_metadata(
    {'script_text': 'Your script...', 'hook_type': 'curiosity'},
    topic='AI Tools 2025'
)

print(f"Title: {metadata['titles']['best_title']['title']}")
print(f"Description: {metadata['description']['text'][:100]}...")
print(f"Tags: {', '.join(metadata['tags']['youtube_tags'][:5])}...")
print(f"Instagram: {' '.join(metadata['hashtags']['instagram'][:5])}...")
```

### Example 4: Schedule Content Calendar
```python
from youtube_scheduler import YouTubeScheduler

scheduler = YouTubeScheduler()

# Create 5-video schedule
schedule = scheduler.schedule_content_calendar(
    num_videos=5,
    niche='technology',
    spacing_days=3
)

scheduler.print_schedule(schedule)
```

### Example 5: Run Feedback Loop (Learn from Data)
```python
from feedback_loop import FeedbackLoop

loop = FeedbackLoop()

# Analyze your videos + Extract learnings + Apply improvements
result = loop.run_complete_feedback_loop()

print(f"Videos analyzed: {result['videos_analyzed']}")
print(f"Optimization score: {result['optimization_score']}/100")
print(f"Recommendations:")
for rec in result['analysis'].get('recommendations', [])[:3]:
    print(f"  - {rec['title']}")
```

---

## 🎯 Common Workflows

### Workflow 1: Daily Content Generation
```bash
# Every day, generate one optimized video
python -c "
from feedback_loop import FeedbackLoop
loop = FeedbackLoop()
result = loop.run_complete_feedback_loop()
print(f'Score: {result[\"optimization_score\"]}/100')
"
```

### Workflow 2: Weekly Batch (5 Videos)
```python
from topic_research import TopicResearcher
from script_generator import ScriptGenerator
import os

os.chdir('D:\Projects\The Steave')

researcher = TopicResearcher(os.getenv('VIDIQ_API_KEY'))
gen = ScriptGenerator(os.getenv('CHAT_API_KEY'))

for i in range(5):
    topic = researcher.select_best_topic()
    scripts = gen.generate_variations(topic['title'], num_variations=3)
    scored = gen.score_variations(scripts)
    print(f"Video {i+1}: {scored[0]['hook_type']} ({scored[0]['quality_score']}/10)")
```

### Workflow 3: A/B Test Thumbnails
```python
from thumbnail_generator import ThumbnailGenerator

gen = ThumbnailGenerator()

# Create 5 variations with different styles
variations = gen.generate_variations(
    title="7 AI Tools That Save 10 Hours",
    topic="AI Tools",
    num_variations=5
)

scored = gen.score_variations(variations)

print(f"Best variation: {scored[0]['style']} ({scored[0]['quality_score']}/10)")
```

---

## 🔐 YouTube OAuth Setup (One-Time)

If you need to upload to YouTube:

1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable "YouTube Data API v3"
4. Create OAuth 2.0 credentials (Desktop app)
5. Download JSON → Save as `youtube_client_secret.json`
6. Run: `python test_phase5.py` → Follow authorization flow
7. Token saved to `youtube_token.pickle`

---

## 📊 Check System Status

```bash
# Verify all modules load
python test_end_to_end.py

# Test individual phases
python test_phase1.py    # Setup
python test_phase2.py    # Scripts
python test_phase3.py    # Metadata
python test_phase4.py    # Thumbnails
python test_phase5.py    # YouTube upload
python test_phase6.py    # Analytics
```

---

## 🐛 Troubleshooting

### "ImportError: No module named 'google'"
```bash
pip install google-genai google-auth-oauthlib google-api-python-client
```

### "VIDIQ_API_KEY not found"
Check .env file has: `VIDIQ_API_KEY=your_actual_key`

### "YouTube auth fails"
1. Delete `youtube_token.pickle`
2. Re-run `test_phase5.py`
3. Complete OAuth flow in browser

### "Script generation times out"
Gemini API has rate limits. Wait 1 minute, try again.

### "Unicode encoding errors"
Windows terminal issue (harmless). Use:
```python
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

---

## 📈 Expected Results

With the system running:

```
Week 1: Generate 5 videos
Week 2: Analyze performance
Week 3: Apply learnings, improve next batch
Week 4: System is optimized, uploads 2-3x more effective

6 Month Results:
- 100+ videos generated
- Continuously improving quality
- Self-learning system optimizing itself
- <$500 total API costs
- Fully automated channel
```

---

## 🎓 Next Steps

1. **Get API Keys** (5 min) → Gemini + VidIQ
2. **Setup Environment** (5 min) → Clone + install + .env
3. **Run Test** (5 min) → `python test_end_to_end.py`
4. **Generate First Video** (10 min) → Use examples above
5. **Schedule Automation** (optional) → Use APScheduler
6. **Monitor Performance** → Run feedback loop weekly

---

## 🚀 You're Ready!

The system is fully functional. Start with:

```python
from feedback_loop import FeedbackLoop
loop = FeedbackLoop()
result = loop.run_complete_feedback_loop()
print("✅ First video generated!")
```

For help with any phase, see the individual setup guides:
- `PHASE_1_SETUP.md` - YouTube API setup
- `PHASE_2_SETUP.md` - Script generation
- `PHASE_3_SETUP.md` - Metadata creation
- `PHASE_4_SETUP.md` - Thumbnails
- `PHASE_5_SETUP.md` - YouTube publishing
- `PHASE_6_SETUP.md` - Analytics

---

**Happy automating!** 🎬🚀

Questions? Check the full documentation or run the test suites.
