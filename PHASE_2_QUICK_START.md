# Phase 2: Quick Start (Copy-Paste Ready)

## ✅ Prerequisites

Make sure Phase 1 is complete:
```bash
python test_phase1.py  # Should pass all tests
```

You need:
- ✓ `youtube_uploader.py`
- ✓ `vidiq_analytics.py`
- ✓ `analytics_db.py`
- ✓ `.env` with `CHAT_API_KEY` and `VIDIQ_API_KEY`

---

## 🚀 One Command Test

```bash
python test_phase2.py
```

Done! All Phase 2 modules are working.

---

## 📝 Copy-Paste: Auto-Generate Best Script

```python
import os
from dotenv import load_dotenv
from topic_research import TopicResearcher
from script_generator import ScriptGenerator
from script_validator import ScriptValidator
from analytics_db import AnalyticsDB

load_dotenv()

print("🔍 Finding trending topic...")
researcher = TopicResearcher(os.getenv('VIDIQ_API_KEY'))
topic = researcher.select_best_topic()
print(f"✓ Topic: {topic['title']}")

print("\n✍️  Generating 3 script variations...")
generator = ScriptGenerator(os.getenv('CHAT_API_KEY'))
scripts = generator.generate_variations(topic['title'], num_variations=3)

print("\n📊 Scoring scripts...")
scored = generator.score_variations(scripts)
best = scored[0]
print(f"✓ Best script: {best['hook_type'].upper()} ({best['quality_score']}/10)")

print("\n✅ Validating...")
validator = ScriptValidator()
validation = validator.validate_script(best)
print(f"✓ Status: {validation['status']}")

print("\n💾 Saving to database...")
db = AnalyticsDB()
topic_id = db.add_topic(topic['title'], 'Technology', 75, 50000, 'medium', 5.0)
script_id = db.add_script(topic_id, best['script_text'], best['quality_score'], 
                          best['hook_type'], 300)

print(f"\n🎉 Done!")
print(f"   Topic ID: {topic_id}")
print(f"   Script ID: {script_id}")
print(f"   Script: {best['script_text'][:100]}...")
```

---

## 📝 Copy-Paste: Generate Scripts for Custom Topic

```python
import os
from dotenv import load_dotenv
from script_generator import ScriptGenerator

load_dotenv()

topic = "How to Learn Machine Learning in 30 Days"
print(f"✍️  Generating scripts for: {topic}")

generator = ScriptGenerator(os.getenv('CHAT_API_KEY'))

# Generate 3 variations with different hooks
scripts = generator.generate_variations(topic, num_variations=3)

# Score them
scored = generator.score_variations(scripts)

# Print report
generator.print_script_report(scored, topic)

# Save best script
generator.export_scripts(scored, 'ml_scripts.json')
print("✓ Saved to ml_scripts.json")
```

---

## 📝 Copy-Paste: Validate & Improve Script

```python
import os
from dotenv import load_dotenv
from script_generator import ScriptGenerator
from script_validator import ScriptValidator

load_dotenv()

# Your script text
my_script = "Hey everyone, did you know that AI is changing the world? Let me show you five amazing tools..."

script_dict = {
    'script_text': my_script,
    'target_length_seconds': 300,
    'hook_type': 'curiosity'
}

# Validate
validator = ScriptValidator()
result = validator.validate_script(script_dict)

print(f"Validation: {result['status']}")

if not result['is_valid']:
    print("\n⚠️  Issues to fix:")
    for issue in result['issues']:
        print(f"  • {issue}")

if result['warnings']:
    print("\n💡 Suggestions:")
    for warning in result['warnings'][:3]:
        print(f"  • {warning}")

# Get detailed improvements
suggestions = validator.suggest_improvements(script_dict, result)
validator.print_suggestions(suggestions)
```

---

## 📝 Copy-Paste: Research Topics Only

```python
import os
from dotenv import load_dotenv
from topic_research import TopicResearcher

load_dotenv()

researcher = TopicResearcher(os.getenv('VIDIQ_API_KEY'), niche='Technology')

# Get top 10 trending topics
print("📊 Top Trending Topics in Technology:\n")
topics = researcher.research_and_rank_topics(limit=10)

for i, topic in enumerate(topics, 1):
    print(f"{i}. {topic['title']}")
    print(f"   Score: {topic['opportunity_score']}/100")
    print(f"   Trending: {topic.get('trending_score', 0)}/100")
    print(f"   Growth: +{topic.get('growth_rate', 0):.1%}\n")

# Or use built-in report
researcher.print_topic_report(topics)
```

---

## 📝 Copy-Paste: Analyze Specific Topic

```python
import os
from dotenv import load_dotenv
from topic_research import TopicResearcher

load_dotenv()

researcher = TopicResearcher(os.getenv('VIDIQ_API_KEY'))

topic_title = "AI Writing Tools 2025"
insights = researcher.get_topic_insights(topic_title)

print(f"Topic: {insights['topic']}")
print(f"\nKeywords:")
for kw in insights['keywords']:
    print(f"  • {kw['keyword']}: {kw['search_volume']} searches/month")

print(f"\nBest Titles (by SEO score):")
for title in insights['title_suggestions']:
    print(f"  • {title['title']}")
    print(f"    Score: {title['seo_score']}/100")
```

---

## 📝 Copy-Paste: Store Script in Database

```python
from analytics_db import AnalyticsDB

db = AnalyticsDB()

# Add topic
topic_id = db.add_topic(
    title="Best AI Tools for 2025",
    niche="Technology",
    trending_score=85,
    search_volume=75000,
    competition="high",
    difficulty=6.5
)

# Add script
script_id = db.add_script(
    topic_id=topic_id,
    script_text="Your script text here...",
    quality_score=8.5,
    hook_type="curiosity",
    length_seconds=300
)

print(f"✓ Stored: topic={topic_id}, script={script_id}")
```

---

## 🧪 Test Individual Modules

### Test Topic Research
```bash
python -c "
from topic_research import TopicResearcher
import os
from dotenv import load_dotenv

load_dotenv()
r = TopicResearcher(os.getenv('VIDIQ_API_KEY'))
topics = r.research_and_rank_topics(limit=5)
print(f'✓ Found {len(topics)} topics')
print(f'  Best: {topics[0][\"title\"]}')
"
```

### Test Script Generation
```bash
python -c "
from script_generator import ScriptGenerator
import os
from dotenv import load_dotenv

load_dotenv()
g = ScriptGenerator(os.getenv('CHAT_API_KEY'))
s = g.generate_script('How to learn Python', hook_type='curiosity')
print(f'✓ Generated {s[\"word_count\"]} word script')
"
```

### Test Validation
```bash
python -c "
from script_validator import ScriptValidator

v = ScriptValidator()
result = v.validate_script({'script_text': 'Hello world. Check this out!', 'target_length_seconds': 60})
print(f'✓ Validation result: {result[\"status\"]}')
"
```

---

## 🔗 Module Cheat Sheet

| Need | Use | Command |
|------|-----|---------|
| Find trending topics | `TopicResearcher` | `research_and_rank_topics()` |
| Auto-pick best topic | `TopicResearcher` | `select_best_topic()` |
| Generate script | `ScriptGenerator` | `generate_script()` |
| Generate variations | `ScriptGenerator` | `generate_variations()` |
| Score scripts | `ScriptGenerator` | `score_variations()` |
| Validate script | `ScriptValidator` | `validate_script()` |
| Get improvements | `ScriptValidator` | `suggest_improvements()` |
| Store topic | `AnalyticsDB` | `add_topic()` |
| Store script | `AnalyticsDB` | `add_script()` |

---

## ⚡ One-Liner Examples

```python
# Get best trending topic
from topic_research import TopicResearcher
t = TopicResearcher('vidiq_key').select_best_topic()

# Generate script
from script_generator import ScriptGenerator  
s = ScriptGenerator('gemini_key').generate_script('AI tools')

# Score it
score = ScriptGenerator('gemini_key').score_script(s)

# Validate
from script_validator import ScriptValidator
v = ScriptValidator().validate_script(s)

# Save to DB
from analytics_db import AnalyticsDB
db = AnalyticsDB()
db.add_script(1, s['script_text'], s['quality_score'], 'curiosity', 300)
```

---

## 🎯 Typical Workflow

```
1. python test_phase2.py           # Verify everything works
2. Generate your own script:
   - Use one of the copy-paste examples above
   - Or run test_phase2.py which does the full flow
3. Review script quality
4. Manually tweak if needed
5. Store in database
6. Ready for Phase 3!
```

---

## ❓ Quick FAQ

**Q: Where's my API key?**  
A: In `.env` file. Check:
```bash
cat .env | grep -E "CHAT_API_KEY|VIDIQ_API_KEY"
```

**Q: How long does script generation take?**  
A: ~30-60 seconds per script depending on API load.

**Q: Can I generate more hook types?**  
A: Yes, up to 6 (all in `ScriptGenerator.HOOKS`). Add more in that dict.

**Q: Script is too short/long?**  
A: Adjust `video_length_seconds` parameter. Default is 300 (5 min).

**Q: How do I use generated scripts?**  
A: Feed into Phase 3 (Metadata generation) → Phase 5 (Video assembly).

---

**Time: 5 minutes to test, 2-5 min to generate scripts per topic**

Next: Phase 3 - Metadata & Thumbnails! 🎨

Ready? → `python test_phase2.py` ✨
