# Phase 3: Metadata Generation - Setup & Usage

## 🎯 What Phase 3 Does

**Goal**: Auto-generate SEO-optimized YouTube metadata from scripts.

**Input**: Video script (from Phase 2) + topic  
**Output**: Complete metadata package (titles, description, tags, hashtags)  
**Time**: ~2-3 minutes per video

---

## 📋 Phase 3 Workflow

```
1. Input: Script from Phase 2
2. Title Generation: Create 5-10 variations, rank by SEO
3. Description: Generate keyword-optimized description with timestamps
4. Tags: Create 30 YouTube tags (max allowed)
5. Hashtags: Generate for Instagram, TikTok, Twitter
6. Output: Metadata package ready for YouTube upload
```

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Verify Phase 2 is Complete
Make sure you have:
- `script_generator.py` ✓
- Scripts in database ✓
- `.env` file with `CHAT_API_KEY` ✓

### Step 2: Test Phase 3
```bash
python test_phase3.py
```

This will:
- Generate 5 title variations
- Create optimized description
- Generate YouTube tags
- Create Instagram hashtags
- Create TikTok hashtags

### Step 3: You're Done! ✨
All Phase 3 modules are ready to use.

---

## 📁 Files Created for Phase 3

| File | Purpose |
|------|---------|
| `title_generator.py` | Generate SEO-optimized titles (5-10 variations) |
| `description_generator.py` | Create keyword-rich descriptions |
| `tag_generator.py` | Generate YouTube tags + social hashtags |
| `metadata_generator.py` | Orchestrate complete metadata generation |
| `test_phase3.py` | Integration test (run this!) |
| `PHASE_3_SETUP.md` | Detailed setup guide (this file) |
| `PHASE_3_QUICK_START.md` | Quick reference guide |
| `requirements_phase3.txt` | Python dependencies |

---

## 🧠 Understanding the Modules

### TitleGenerator (`title_generator.py`)

**Purpose**: Create multiple YouTube titles ranked by SEO/CTR potential

**Key Methods**:
- `generate_titles()` - Create 5-10 title variations
- `score_titles()` - Rate each for SEO quality (0-10)
- `get_best_title()` - Get the #1 ranked title
- `generate_youtube_ready_metadata()` - Clean for YouTube upload

**Scoring Factors**:
- Keyword inclusion (does it have main keyword?)
- Power words (how, why, best, top, revealed, etc.)
- Length (ideal: 50-60 characters)
- Format variety (question vs. statement)
- Clickability (would you click it?)

**Example**:
```python
from title_generator import TitleGenerator

gen = TitleGenerator('your_api_key')
titles = gen.generate_titles(script, topic, num_titles=5)
scored = gen.score_titles(titles, topic)

print(scored[0]['title'])  # Best title
```

---

### DescriptionGenerator (`description_generator.py`)

**Purpose**: Write comprehensive, keyword-optimized YouTube descriptions

**Key Methods**:
- `generate_description()` - Create main description
- `add_timestamps()` - Add chapter timestamps
- `add_links_section()` - Add resources/links
- `finalize_description()` - Prepare for upload
- `score_description()` - Rate quality (0-10)

**Scoring Factors**:
- Keyword placement (in first 2 sentences?)
- Length (500-5000 chars optimal)
- Structure (has sections and formatting)
- CTAs (calls-to-action for engagement)
- Readability (line breaks, bullet points)

**Description Sections**:
1. Hook (attention-grabbing intro)
2. Key Topics (bullet points of main points)
3. Timestamps (chapter markers)
4. Links (resources section)
5. Engagement CTA (subscribe, like, comment)

**Example**:
```python
from description_generator import DescriptionGenerator

gen = DescriptionGenerator('your_api_key')
desc = gen.generate_description(script, topic, title)
desc = gen.add_timestamps(desc, script)
desc = gen.finalize_description(desc)

print(desc['final_text'])  # Ready to paste
```

---

### TagGenerator (`tag_generator.py`)

**Purpose**: Generate YouTube tags + social media hashtags

**Key Methods**:
- `generate_tags()` - Create YouTube tags (max 30)
- `generate_hashtags()` - Create platform-specific hashtags
- `score_tags()` - Rate relevance (0-10)
- `get_youtube_tags_string()` - Format for upload
- `get_social_media_hashtag_string()` - Format for social

**YouTube Tags**:
- 30 tags maximum (YouTube limit)
- Mix of: main keyword, long-tail keywords, related topics, trending terms
- Each tag max 30 characters

**Social Hashtags**:
- Instagram: 15-30 hashtags (visible in caption)
- TikTok: 10-15 hashtags (in description)
- Twitter: 1-3 hashtags (concise)

**Example**:
```python
from tag_generator import TagGenerator

gen = TagGenerator('your_api_key')

# YouTube tags
tags = gen.generate_tags(script, topic, title, max_tags=30)
print(' '.join(tags))  # Paste into YouTube

# Instagram hashtags
insta = gen.generate_hashtags(script, topic, title, for_platform='instagram')
print(' '.join(insta))

# TikTok hashtags
tiktok = gen.generate_hashtags(script, topic, title, for_platform='tiktok')
print(' '.join(tiktok))
```

---

### MetadataGenerator (`metadata_generator.py`)

**Purpose**: Orchestrate all metadata generation in one call

**Key Methods**:
- `generate_complete_metadata()` - Generate everything at once
- `score_metadata()` - Rate overall quality (0-10)
- `export_metadata()` - Save to JSON
- `export_for_upload()` - Create separate files for YouTube

**Output Dictionary**:
```python
{
    'titles': {best_title, all_variations, scores},
    'description': {text, character_count, score},
    'tags': {youtube_tags, tag_count},
    'hashtags': {instagram, tiktok},
    'ready_for_upload': True
}
```

**Example**:
```python
from metadata_generator import MetadataGenerator

gen = MetadataGenerator('your_api_key')
metadata = gen.generate_complete_metadata(script_dict, topic)

# Print formatted report
gen.print_metadata_report(metadata)

# Export to JSON
gen.export_metadata(metadata, 'metadata.json')

# Or export as separate files
gen.export_for_upload(metadata, 'youtube_upload/')
```

---

## 💡 Complete Example: Script → Complete Metadata

```python
import os
from dotenv import load_dotenv
from script_generator import ScriptGenerator
from metadata_generator import MetadataGenerator
from analytics_db import AnalyticsDB

load_dotenv()

# 1. Get script from database
db = AnalyticsDB()
import sqlite3
conn = sqlite3.connect('channel_analytics.db')
cursor = conn.cursor()
cursor.execute('''
    SELECT scripts.script_text, scripts.hook_type, 
           topics.title, topics.trending_score
    FROM scripts
    JOIN topics ON scripts.topic_id = topics.id
    ORDER BY scripts.created_date DESC LIMIT 1
''')
result = cursor.fetchone()
conn.close()

if result:
    script_text, hook_type, topic, score = result
else:
    print("No script found. Run Phase 2 first!")
    exit()

# 2. Generate complete metadata
print(f"🎬 Generating metadata for: {topic}")
metadata_gen = MetadataGenerator(os.getenv('CHAT_API_KEY'))

script_dict = {
    'script_text': script_text,
    'hook_type': hook_type,
    'quality_score': 8.5
}

metadata = metadata_gen.generate_complete_metadata(script_dict, topic)

# 3. Print formatted report
metadata_gen.print_metadata_report(metadata)

# 4. Score overall quality
overall_score = metadata_gen.score_metadata(metadata)
print(f"📊 Overall Metadata Quality: {overall_score}/10")

# 5. Export
print("\n💾 Exporting...")
metadata_gen.export_metadata(metadata, 'metadata.json')
metadata_gen.export_for_upload(metadata, 'youtube_upload')

# 6. Display what's ready
metadata_dict = metadata
print(f"""
✅ METADATA READY FOR YOUTUBE
Title:       {metadata_dict['titles']['best_title']}
Description: {metadata_dict['description']['text'][:100]}...
Tags:        {len(metadata_dict['tags']['youtube_tags'])} tags
Hashtags:    Instagram ({len(metadata_dict['hashtags']['instagram'])}) 
             TikTok ({len(metadata_dict['hashtags']['tiktok'])})

📁 Files created in youtube_upload/:
   - title.txt (copy to YouTube)
   - description.txt (copy to YouTube)
   - tags.txt (copy to YouTube)
   - hashtags.json (for social media)
""")
```

---

## ⚙️ Configuration

### Environment Variables
```env
CHAT_API_KEY=your_gemini_api_key  # Required
```

### Adjust Generation Parameters

**In `title_generator.py`**:
- `temperature=0.8` - Adjust creativity (0=deterministic, 1=random)
- Number of titles: 3-10 recommended

**In `description_generator.py`**:
- Description length: 500-5000 characters ideal
- Can add custom sections

**In `tag_generator.py`**:
- YouTube max: 30 tags
- Instagram: 15-30 hashtags
- TikTok: 10-15 hashtags

---

## 📊 Metadata Quality Scoring

### Title Quality (0-10)
- **10**: Keyword + power word + perfect length + clickable
- **8-9**: Keyword + good format + reasonable length
- **6-7**: Has keyword, decent format
- **<6**: Missing keyword or poor format

### Description Quality (0-10)
- **10**: Keyword in first 2 sentences + 10+ structure elements
- **8-9**: Keyword included + good structure
- **6-7**: Okay structure, keyword somewhere
- **<6**: Missing keyword or poorly structured

### Overall Metadata (0-10)
- **10**: Best titles (8+/10) + description (8+/10) + 30 tags + hashtags
- **8-9**: Good titles + good description + complete tags
- **6-7**: Acceptable quality, may need minor edits
- **<6**: Needs significant improvement

---

## 🔌 API Integrations

| Component | API | Cost | Rate |
|-----------|-----|------|------|
| Title Generation | Gemini | ~$0.003 | Instant |
| Description | Gemini | ~$0.005 | Instant |
| Tags | Gemini | ~$0.003 | Instant |
| Database | SQLite | Free | Instant |

**Total cost per video**: <$0.02 (mostly free)

---

## 🎯 Common Workflows

### Workflow 1: Auto-Generate Everything (Fastest)
```python
metadata = MetadataGenerator(api_key).generate_complete_metadata(
    script_dict, 
    topic
)
```
**Time**: ~3 min  
**Quality**: Good (auto-optimized)

---

### Workflow 2: Generate + Manual Review
```python
# Generate
metadata = MetadataGenerator(api_key).generate_complete_metadata(script_dict, topic)

# Review
MetadataGenerator(api_key).print_metadata_report(metadata)

# Edit if needed (titles are just text)
metadata['titles']['best_title'] = "Your edited title"

# Export
MetadataGenerator(api_key).export_for_upload(metadata)
```
**Time**: ~10 min (with review)  
**Quality**: Excellent (human-reviewed)

---

### Workflow 3: Custom Title Only
```python
# Generate multiple titles, pick your favorite
titles = TitleGenerator(api_key).generate_titles(script, topic, num_titles=10)
scored = TitleGenerator(api_key).score_titles(titles, topic)

# Pick manually
your_title = scored[3]['title']  # Or any you prefer

# Then generate rest of metadata
description = DescriptionGenerator(api_key).generate_description(
    script, topic, your_title
)
tags = TagGenerator(api_key).generate_tags(script, topic, your_title)
```
**Time**: ~5 min  
**Quality**: Very Good (custom titles)

---

## 🧪 Testing Checklist

Before moving to Phase 4, verify:

- [ ] `python test_phase3.py` runs without errors
- [ ] Titles generated (5+ variations)
- [ ] Titles have meaningful scores (different numbers)
- [ ] Description generated (500+ characters)
- [ ] Tags generated (30 tags)
- [ ] Hashtags generated (Instagram + TikTok)
- [ ] Can export metadata to JSON
- [ ] Can export to YouTube upload folder
- [ ] Metadata files are readable text

---

## ⚠️ Common Issues & Fixes

### Issue: "CHAT_API_KEY not configured"
**Fix**:
```bash
# Check .env has:
CHAT_API_KEY=sk-proj-xxxxx...

# Or set it:
export CHAT_API_KEY=your_key
```

### Issue: "Failed to parse JSON response"
**Fix**:
- API response was malformed
- Try again (might be temporary)
- Check API quota not exceeded

### Issue: "Metadata generation incomplete"
**Fix**:
- One sub-generator failed
- Check logs for which one
- Try generating that part separately

### Issue: "Titles all have same SEO score"
**Fix**:
- Scoring algorithm might need tuning
- Check that titles are different
- Adjust power_words list

### Issue: "Description is too short"
**Fix**:
- Increase script length (Phase 2)
- Or use manual description
- Minimum is 150 characters for YouTube

---

## 📈 Optimization Tips

### 1. Parallel Generation (Faster)
```python
# Generate titles, description, tags in parallel using threads
from threading import Thread

results = {'titles': None, 'description': None, 'tags': None}

def gen_titles():
    results['titles'] = TitleGenerator(key).generate_titles(...)

def gen_desc():
    results['description'] = DescriptionGenerator(key).generate_description(...)

def gen_tags():
    results['tags'] = TagGenerator(key).generate_tags(...)

threads = [Thread(target=gen_titles), Thread(target=gen_desc), Thread(target=gen_tags)]
for t in threads:
    t.start()
for t in threads:
    t.join()

# Results ready
```
**Benefit**: 3 generators in parallel = 1/3 the time

---

### 2. Caching Metadata
```python
# Store generated metadata in JSON for future reference
import json

with open('metadata_cache.json', 'w') as f:
    json.dump(metadata, f)

# Reuse later without regenerating
with open('metadata_cache.json') as f:
    cached_metadata = json.load(f)
```

---

### 3. Batch Metadata Generation
```python
# Generate metadata for multiple scripts at once
scripts = db.get_scripts(limit=10)

all_metadata = []
for script_dict, topic in scripts:
    metadata = MetadataGenerator(key).generate_complete_metadata(script_dict, topic)
    all_metadata.append(metadata)

# Export all
for i, meta in enumerate(all_metadata):
    MetadataGenerator(key).export_metadata(meta, f'metadata_{i}.json')
```

---

## 🚀 Ready for Phase 4?

Phase 3 complete checklist:
- ✅ Can generate title variations
- ✅ Can generate descriptions
- ✅ Can generate tags & hashtags
- ✅ Can export complete metadata
- ✅ Database integration working
- ✅ Quality scoring implemented

**What's Next (Phase 4)**:
- Generate custom thumbnail images
- Use metadata to inform thumbnail design
- Create variation A/B tests
- Ready for YouTube upload

---

## 📝 Next Phase: Phase 4 - Thumbnail Generation

Phase 4 will take metadata and generate:
- **Thumbnail images** (based on topic + title)
- **Variations** (A/B test different styles)
- **Branding** (consistent visual style)
- **Text overlays** (topic + hook text)

**Input**: Metadata from Phase 3 (this phase)

**Output**: Professional thumbnail images ready for upload

---

## 🔗 Integration with Pipeline

```
Phase 2: Script Generation
    ↓ (produces scripts)
Phase 3: Metadata Generation (YOU ARE HERE)
    ↓ (produces titles, descriptions, tags)
Phase 4: Thumbnail Generation
    ↓ (produces cover images)
Phase 5: YouTube Upload
    ↓ (publishes with all metadata)
Analytics Loop
    ↓ (performance data)
Phase 3: Metadata (refined based on analytics)
```

---

**Time to complete Phase 3 setup: ~10 minutes (mostly testing)**

When ready: `python test_phase3.py` ✨
