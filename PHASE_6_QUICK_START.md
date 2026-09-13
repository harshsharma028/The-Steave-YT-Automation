# Phase 6: Quick Start (Copy-Paste Ready)

## ✅ Prerequisites

Make sure Phase 5 is complete:
```bash
python test_phase5.py  # Should pass
```

You need:
- ✓ YouTube videos published (at least 3-5 for meaningful analysis)
- ✓ Some performance data (wait a few days after upload)
- ✓ Database from previous phases

---

## 🚀 One Command Test

```bash
python test_phase6.py
```

---

## 📝 Copy-Paste: Run Feedback Loop

```python
from feedback_loop import FeedbackLoop

# Initialize
loop = FeedbackLoop()

# Run complete cycle: Analyze → Learn → Apply
result = loop.run_complete_feedback_loop()

# Print report
loop.print_feedback_report(result)

# Export
loop.export_feedback_report(result, 'feedback_report.json')

print(f"✅ Optimization score: {result['optimization_score']}/100")
```

---

## 📝 Copy-Paste: Analyze Videos

```python
from youtube_analytics import YouTubeAnalytics

analytics = YouTubeAnalytics()

# Get latest 10 videos
videos = analytics.get_latest_videos(limit=10)

# Analyze trends
analysis = analytics.analyze_performance_trend(videos)
print(f"Average views: {analysis['avg_views_per_video']:,.0f}")
print(f"Average engagement: {analysis['avg_engagement_rate']}%")

# Find patterns
patterns = analytics.identify_successful_patterns(videos)
print(f"Top videos: {len(patterns['top_videos'])}")
print(f"Bottom videos: {len(patterns['bottom_videos'])}")
```

---

## 📝 Copy-Paste: Get Recommendations

```python
from youtube_analytics import YouTubeAnalytics
from content_optimizer import ContentOptimizer

analytics = YouTubeAnalytics()
optimizer = ContentOptimizer()

# Get video data
videos = analytics.get_latest_videos(limit=20)
analysis = analytics.analyze_performance_trend(videos)

# Get recommendations
recommendations = optimizer.get_content_recommendations(videos, analysis)

# Print
optimizer.print_recommendations(recommendations)

# Also predict best hooks
hooks = optimizer.predict_successful_hooks(videos)
print(f"\nBest hooks:")
for hook, score in hooks[:3]:
    print(f"  - {hook}: {score:,.0f} views")
```

---

## 📝 Copy-Paste: Store Learnings

```python
from feedback_loop import FeedbackLoop

loop = FeedbackLoop()

# Analyze
result = loop.analyze_and_learn()

# Store learnings in database
learning_ids = loop.store_learnings(result)
print(f"✅ Stored {len(learning_ids)} learnings")

# Retrieve and apply
strategy = loop.apply_learnings_to_future_content()
print(f"Applied {strategy['total_learnings']} learnings to future content")
```

---

## 📝 Copy-Paste: Complete Feedback Loop

```python
from feedback_loop import FeedbackLoop

loop = FeedbackLoop()

# 1. Analyze videos
print("📊 Analyzing...")
result = loop.analyze_and_learn()

# 2. Store learnings
print("💾 Storing learnings...")
learning_ids = loop.store_learnings(result)

# 3. Apply to future content
print("🎯 Applying to future content...")
strategy = loop.apply_learnings_to_future_content()

# 4. Print report
loop.print_feedback_report(result)

# 5. Export
loop.export_feedback_report(result)

print(f"""
✅ FEEDBACK LOOP COMPLETE
   Videos analyzed: {result['videos_analyzed']}
   Learnings stored: {len(learning_ids)}
   Optimization score: {result['optimization_score']}/100
   Next video recommendations ready!
""")
```

---

## 🎯 Typical Workflow

```
1. Upload 5+ videos (Phase 5)
2. Wait 1-3 days for performance data
3. python test_phase6.py           # Verify setup
4. loop = FeedbackLoop()
5. result = loop.run_complete_feedback_loop()
6. Use recommendations for next video
7. Repeat weekly/bi-weekly
```

---

## 📊 Key Metrics to Watch

| Metric | Good | Excellent |
|--------|------|-----------|
| Avg Views/Video | 100+ | 1,000+ |
| Engagement Rate | 2%+ | 5%+ |
| Optimization Score | 60+ | 80+ |
| Like Rate | 1%+ | 3%+ |
| Comment Rate | 0.5%+ | 2%+ |

---

## 💡 Using Feedback for Next Video

After running feedback loop:

```python
# Get recommendations
recommendations = result['recommendations']

# For next script:
# - Use predicted hooks (highest scoring)
# - Create similar topics to top performers
# - Add more CTAs (if low engagement)

# For next thumbnail:
# - Analyze top vs bottom performer titles
# - Use color schemes from successful videos

# For metadata:
# - Include power words from top videos
# - Use recommended hooks in title
```

---

## 🔄 Automation Options

### Option 1: Manual (Every Week)
```python
# Run weekly
loop = FeedbackLoop()
result = loop.run_complete_feedback_loop()
```

### Option 2: Scheduled (Automatic)
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def run_feedback():
    loop = FeedbackLoop()
    result = loop.run_complete_feedback_loop()
    print("Feedback loop completed!")

# Run every 24 hours
scheduler.add_job(run_feedback, 'interval', hours=24)
scheduler.start()
```

---

## ❓ FAQ

**Q: When should I run the feedback loop?**  
A: After every 5-10 videos, or weekly if uploading regularly

**Q: How many videos needed?**  
A: At least 3-5 for meaningful patterns. 10+ for reliable analysis

**Q: What if optimization score is low?**  
A: Review recommendations and apply to next videos

**Q: Can I use learnings immediately?**  
A: Yes! Use recommendations for your next script/thumbnail

---

**Time: 1 minute to test, 2-5 min to run feedback loop**

Ready? → `python test_phase6.py` ✨
