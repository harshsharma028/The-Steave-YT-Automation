# Phase 5: Quick Start (Copy-Paste Ready)

## ✅ Prerequisites

Make sure Phase 4 is complete:
```bash
python test_phase4.py  # Should pass
```

You need:
- ✓ `youtube_uploader_v2.py`
- ✓ `youtube_scheduler.py`
- ✓ `youtube_video_manager.py`
- ✓ `.env` with `YOUTUBE_CLIENT_SECRETS_FILE`
- ✓ YouTube OAuth credentials (from Phase 1)
- ✓ Video file (MP4)
- ✓ Metadata package (from Phase 3)
- ✓ Thumbnail image (from Phase 4)

---

## 🚀 One Command Test

```bash
python test_phase5.py
```

---

## 📝 Copy-Paste: Upload Video

```python
import os
from dotenv import load_dotenv
from youtube_uploader_v2 import YouTubeUploaderV2

load_dotenv()

# Initialize uploader
uploader = YouTubeUploaderV2()

# Prepare metadata
metadata = {
    'title': '7 AI Tools That Save 10 Hours Per Week',
    'description': 'Discover the best AI writing tools...',
    'tags': ['AI', 'productivity', 'tools', 'tutorial'],
    'category': 'Technology'
}

# Upload
result = uploader.upload_video(
    video_file='final_video.mp4',
    metadata_dict=metadata,
    thumbnail_file='thumbnail.jpg',
    visibility='private'  # Start private, then make public
)

print(f"✅ Video uploaded!")
print(f"   ID: {result['video_id']}")
print(f"   Title: {result['title']}")
print(f"   Visibility: {result['visibility']}")
```

---

## 📝 Copy-Paste: Schedule Video Publishing

```python
from datetime import datetime, timedelta
from youtube_uploader_v2 import YouTubeUploaderV2

uploader = YouTubeUploaderV2()

# Schedule for 3 days from now at optimal time
publish_date = (datetime.utcnow() + timedelta(days=3))
publish_date = publish_date.replace(hour=14, minute=0, second=0)  # 2 PM UTC
publish_timestamp = publish_date.isoformat() + 'Z'

# Upload with scheduling
result = uploader.upload_video(
    video_file='final_video.mp4',
    metadata_dict=metadata,
    thumbnail_file='thumbnail.jpg',
    publish_at=publish_timestamp,  # Will be published at this time
    visibility='private'  # Required for scheduling
)

print(f"✅ Video scheduled for: {publish_timestamp}")
```

---

## 📝 Copy-Paste: Create Content Calendar

```python
from youtube_scheduler import YouTubeScheduler

scheduler = YouTubeScheduler()

# Create schedule for 5 videos
schedule = scheduler.schedule_content_calendar(
    num_videos=5,
    niche='tech',
    spacing_days=3  # Publish every 3 days
)

# Print
scheduler.print_schedule(schedule)

# Export
scheduler.export_schedule(schedule, 'content_calendar.json')

print("✅ Content calendar created!")
```

---

## 📝 Copy-Paste: Change Video Visibility

```python
from youtube_video_manager import YouTubeVideoManager

manager = YouTubeVideoManager()

# Make video public
manager.change_video_visibility('VIDEO_ID', 'public')

# Or private
manager.change_video_visibility('VIDEO_ID', 'private')

# Or unlisted
manager.change_video_visibility('VIDEO_ID', 'unlisted')
```

---

## 📝 Copy-Paste: Complete Upload Workflow

```python
import os
from dotenv import load_dotenv
from youtube_uploader_v2 import YouTubeUploaderV2
from youtube_scheduler import YouTubeScheduler
from youtube_video_manager import YouTubeVideoManager

load_dotenv()

# 1. Initialize
uploader = YouTubeUploaderV2()
scheduler = YouTubeScheduler()
manager = YouTubeVideoManager()

# 2. Prepare metadata (from Phase 3)
metadata = {
    'title': 'Your Video Title',
    'description': 'Full description from Phase 3...',
    'tags': ['tag1', 'tag2', 'tag3'],
    'category': 'Technology'
}

# 3. Get optimal publish time
publish_time = scheduler.get_optimal_publish_time('tech')

# 4. Upload video
print("📤 Uploading...")
result = uploader.upload_video(
    video_file='final_video.mp4',
    metadata_dict=metadata,
    thumbnail_file='thumbnail.jpg',
    publish_at=publish_time,
    visibility='private'
)

video_id = result['video_id']
print(f"✅ Uploaded! Video ID: {video_id}")

# 5. Get video info
insights = manager.get_video_insights(video_id)
print(f"   Views: {insights['views']}")

# 6. Create content calendar for next videos
schedule = scheduler.schedule_content_calendar(4, 'tech')
scheduler.print_schedule(schedule)

print("\n✅ COMPLETE WORKFLOW DONE!")
```

---

## 🧪 Test Individual Modules

### Test Uploader
```bash
python -c "
from youtube_uploader_v2 import YouTubeUploaderV2
u = YouTubeUploaderV2()
c = u.get_channel_info()
print(f'✓ Channel: {c[\"title\"]}')
"
```

### Test Scheduler
```bash
python -c "
from youtube_scheduler import YouTubeScheduler
s = YouTubeScheduler()
t = s.get_optimal_publish_time('general')
print(f'✓ Publish at: {t}')
"
```

### Test Manager
```bash
python -c "
from youtube_video_manager import YouTubeVideoManager
m = YouTubeVideoManager()
p = m.get_playlists()
print(f'✓ Playlists: {len(p)}')
"
```

---

## 📊 Video Categories

```python
'Entertainment': 24
'Education': 27
'Science & Tech': 28
'People & Blogs': 15
'Howto & Style': 26
'News & Politics': 25
'Gaming': 20
'Music': 10
```

---

## 🎯 Upload Flow

```
1. Prepare files:
   - video.mp4
   - metadata dict (title, description, tags)
   - thumbnail.jpg

2. Create uploader:
   uploader = YouTubeUploaderV2()

3. Upload:
   result = uploader.upload_video(
       'video.mp4',
       metadata,
       'thumbnail.jpg',
       visibility='private'
   )

4. Get video ID:
   video_id = result['video_id']

5. Make public (when ready):
   manager = YouTubeVideoManager()
   manager.change_video_visibility(video_id, 'public')
```

---

## ⏱️ Scheduling Example

```python
from datetime import datetime, timedelta

# Schedule for Friday 8 PM UTC
now = datetime.utcnow()
friday = now + timedelta(days=(4 - now.weekday()) % 7)
publish_time = friday.replace(hour=20, minute=0, second=0, microsecond=0)
iso_time = publish_time.isoformat() + 'Z'

result = uploader.upload_video(
    'video.mp4',
    metadata,
    publish_at=iso_time  # Will publish at this time
)
```

---

## 🎯 Typical Workflow

```
1. python test_phase5.py            # Verify setup
2. Prepare video.mp4 + metadata
3. uploader.upload_video()          # Upload private first
4. manager.get_video_insights()     # Check status
5. manager.change_video_visibility()# Make public when ready
6. scheduler.schedule_content_calendar()  # Plan next videos
```

---

## ❓ FAQ

**Q: What's the best upload time?**  
A: Use `scheduler.get_optimal_publish_time(niche)` - varies by content type

**Q: Can I schedule videos in advance?**  
A: Yes! Use `publish_at` parameter with ISO 8601 timestamp

**Q: How do I make video public after uploading?**  
A: `manager.change_video_visibility(video_id, 'public')`

**Q: Can I upload to a playlist?**  
A: Yes! Pass `playlist_id` to `upload_video()`

**Q: What video formats work?**  
A: MP4 is recommended. Also supports MOV, AVI, WMV, FLV, 3GP, WebM, etc.

---

**Time: 1 minute to test, 2-5 min per upload**

Ready? → `python test_phase5.py` ✨
