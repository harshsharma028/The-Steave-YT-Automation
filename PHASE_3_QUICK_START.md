# Phase 3: Quick Start (Copy-Paste Ready)

## ✅ Prerequisites

Make sure Phase 2 is complete:
```bash
python test_phase2.py  # Should pass all tests
```

You need:
- ✓ `script_generator.py` (Phase 2)
- ✓ `analytics_db.py` (Phase 1)
- ✓ `.env` with `CHAT_API_KEY`
- ✓ Scripts in database

---

## 🚀 One Command Test

```bash
python test_phase3.py
```

Done! All Phase 3 modules are working.

---

## 📝 Copy-Paste: Generate Complete Metadata

```python
import os
from dotenv import load_dotenv
from script_generator import ScriptGenerator
from metadata_generator import MetadataGenerator
from analytics_db import AnalyticsDB

load_dotenv()

# Get script from database (or generate new one)
db = AnalyticsDB()
import sqlite3
conn = sqlite3.connect('channel_analytics.db')
cursor = conn.cursor()
cursor.execute('''
    SELECT scripts.script_text, topics.title
    FROM scripts
    JOIN topics ON scripts.topic_id = topics.id
    ORDER BY scripts.created_date DESC LIMIT 1
''')
result = cursor.fetchone()
conn.close()

if result:
    script_text, topic = result
else:
    # Generate new script if none exists
    from topic_research import TopicResearcher
    from script_generator import ScriptGenerator
    researcher = TopicResearcher(os.getenv('VIDIQ_API_KEY'))
    topic_data = researcher.select_best_topic()
    topic = topic_data['title']
    
    gen = ScriptGenerator(os.getenv('CHAT_API_KEY'))
    script_data = gen.generate_script(topic)
    script_text = script_data['script_text']

# Generate metadata
print("🎬 Generating complete metadata...")
metadata_gen = MetadataGenerator(os.getenv('CHAT_API_KEY'))

script_dict = {'script_text': script_text, 'hook_type': 'curiosity'}
metadata = metadata_gen.generate_complete_metadata(script_dict, topic)

# Print report
metadata_gen.print_metadata_report(metadata)

# Export
metadata_gen.export_metadata(metadata, 'metadata.json')
print("✅ Metadata saved to metadata.json")
```

---

## 📝 Copy-Paste: Generate Titles Only

```python
import os
from dotenv import load_dotenv
from title_generator import TitleGenerator

load_dotenv()

topic = "How to Learn Python Fast"
script = "Your script text here..."

gen = TitleGenerator(os.getenv('CHAT_API_KEY'))

# Generate 5 titles
titles = gen.generate_titles(script, topic, num_titles=5)

# Score them
scored = gen.score_titles(titles, topic)

# Print report
gen.print_title_report(scored, topic)

# Get best
best = scored[0]
print(f"\n🏆 Best Title: {best['title']}")
print(f"   Score: {best['seo_score']}/10")
```

---

## 📝 Copy-Paste: Generate Description

```python
import os
from dotenv import load_dotenv
from description_generator import DescriptionGenerator

load_dotenv()

topic = "How to Learn Python Fast"
title = "7 Ways to Learn Python in 30 Days"
script = "Your script text here..."

gen = DescriptionGenerator(os.getenv('CHAT_API_KEY'))

# Generate description
desc = gen.generate_description(script, topic, title)

# Add timestamps
desc = gen.add_timestamps(desc, script)

# Finalize
desc = gen.finalize_description(desc)

# Print
print(desc['final_text'])

# Export
gen.export_description(desc, 'description.txt')
```

---

## 📝 Copy-Paste: Generate Tags

```python
import os
from dotenv import load_dotenv
from tag_generator import TagGenerator

load_dotenv()

topic = "How to Learn Python Fast"
title = "7 Ways to Learn Python in 30 Days"
script = "Your script text here..."

gen = TagGenerator(os.getenv('CHAT_API_KEY'))

# Generate YouTube tags (max 30)
tags = gen.generate_tags(script, topic, title, max_tags=30)
print(f"YouTube Tags: {', '.join(tags)}")

# Generate Instagram hashtags
insta = gen.generate_hashtags(script, topic, title, max_hashtags=20, for_platform='instagram')
print(f"Instagram: {' '.join(insta)}")

# Generate TikTok hashtags
tiktok = gen.generate_hashtags(script, topic, title, max_hashtags=15, for_platform='tiktok')
print(f"TikTok: {' '.join(tiktok)}")
```

---

## 📝 Copy-Paste: Export for YouTube Upload

```python
from metadata_generator import MetadataGenerator

metadata_gen = MetadataGenerator()

# After generating metadata...
metadata_gen.export_for_upload(metadata, output_dir='youtube_upload')

# Creates:
# - youtube_upload/title.txt
# - youtube_upload/description.txt
# - youtube_upload/tags.txt
# - youtube_upload/hashtags.json

print("✅ Ready to upload!")
```

---

## 🧪 Test Individual Modules

### Test Title Generation
```bash
python -c "
from title_generator import TitleGenerator
import os
from dotenv import load_dotenv

load_dotenv()
t = TitleGenerator(os.getenv('CHAT_API_KEY'))
titles = t.generate_titles('Your script here', 'Topic', num_titles=3)
print(f'✓ Generated {len(titles)} titles')
for title in titles:
    print(f'  - {title[\"title\"]}')
"
```

### Test Description Generation
```bash
python -c "
from description_generator import DescriptionGenerator
import os
from dotenv import load_dotenv

load_dotenv()
d = DescriptionGenerator(os.getenv('CHAT_API_KEY'))
desc = d.generate_description('Your script', 'Topic', 'Your Title')
print(f'✓ Description generated')
print(f'  Length: {desc[\"character_count\"]} chars')
"
```

### Test Tags Generation
```bash
python -c "
from tag_generator import TagGenerator
import os
from dotenv import load_dotenv

load_dotenv()
t = TagGenerator(os.getenv('CHAT_API_KEY'))
tags = t.generate_tags('Your script', 'Topic', 'Your Title')
print(f'✓ Generated {len(tags)} tags')
print(f'  {tags[:5]}')
"
```

---

## 🔗 Module Cheat Sheet

| Need | Use | Command |
|------|-----|---------|
| Generate titles | `TitleGenerator` | `generate_titles()` |
| Score titles | `TitleGenerator` | `score_titles()` |
| Generate description | `DescriptionGenerator` | `generate_description()` |
| Add timestamps | `DescriptionGenerator` | `add_timestamps()` |
| Generate tags | `TagGenerator` | `generate_tags()` |
| Generate hashtags | `TagGenerator` | `generate_hashtags()` |
| Complete metadata | `MetadataGenerator` | `generate_complete_metadata()` |
| Export metadata | `MetadataGenerator` | `export_metadata()` |
| Export for upload | `MetadataGenerator` | `export_for_upload()` |

---

## ⚡ One-Liner Examples

```python
# Generate 5 titles
from title_generator import TitleGenerator
titles = TitleGenerator('api_key').generate_titles(script, topic, 5)

# Score them
scored = TitleGenerator('api_key').score_titles(titles, topic)

# Generate description
from description_generator import DescriptionGenerator
desc = DescriptionGenerator('api_key').generate_description(script, topic, title)

# Generate tags
from tag_generator import TagGenerator
tags = TagGenerator('api_key').generate_tags(script, topic, title)

# Everything at once
from metadata_generator import MetadataGenerator
metadata = MetadataGenerator('api_key').generate_complete_metadata(script_dict, topic)
```

---

## 🎯 Typical Workflow

```
1. python test_phase3.py           # Verify everything works
2. Get script from database        # or generate new one
3. MetadataGenerator.generate_complete_metadata()
4. Print report and review
5. Export for YouTube upload
6. Use in Phase 4 (Thumbnails)
```

---

## 💡 What Each Module Does

### TitleGenerator
**Generates**: 5-10 title variations ranked by SEO  
**Input**: Script, topic, keyword  
**Output**: Scored titles (0-10)

### DescriptionGenerator
**Generates**: SEO-optimized description with sections  
**Input**: Script, topic, title  
**Output**: Full description with timestamps

### TagGenerator
**Generates**: 30 YouTube tags + platform hashtags  
**Input**: Script, topic, title  
**Output**: Tags (YouTube) + hashtags (Instagram, TikTok)

### MetadataGenerator
**Orchestrates**: All three generators  
**Input**: Script dict, topic  
**Output**: Complete metadata package ready for YouTube

---

## 📊 Metadata Package Contents

```json
{
  "topic": "AI Tools 2025",
  "titles": {
    "best_title": "7 AI Tools That Save 10 Hours Per Week",
    "all_variations": [...],
    "total_variations": 5
  },
  "description": {
    "text": "Full optimized description...",
    "character_count": 1200,
    "word_count": 150,
    "score": 8.5
  },
  "tags": {
    "youtube_tags": ["AI", "tools", "productivity", ...],
    "tag_count": 30,
    "tags_string": "AI tools productivity..."
  },
  "hashtags": {
    "instagram": ["#AI", "#tools", ...],
    "tiktok": ["#AI", "#aitools", ...]
  }
}
```

---

## ❓ Quick FAQ

**Q: How many titles should I generate?**  
A: Start with 5-10. More = more options but slower.

**Q: Are descriptions auto-generated good?**  
A: Yes! 8.5/10 on average. Can edit if needed.

**Q: Do I have to use all 30 tags?**  
A: No, YouTube allows 1-30. Fewer is fine.

**Q: Can I edit generated metadata?**  
A: Absolutely! They're just text files.

**Q: What if I don't like a title?**  
A: Generate more variations or pick from the list.

---

## 🚀 Production Workflow

```
1. Generate script (Phase 2)
2. Generate metadata (Phase 3) ← YOU ARE HERE
3. Generate thumbnail (Phase 4)
4. Upload to YouTube (Phase 5)
5. Track analytics (Phase 6)
```

---

**Time: 1 minute to test, 2-3 min to generate metadata per video**

Ready? → `python test_phase3.py` ✨
