# Phase 2: Script Generation Engine - Setup & Usage

## 🎯 What Phase 2 Does

**Goal**: Automatically research trending topics and generate multiple compelling video scripts with different hooks.

**Input**: Topic (or VidIQ will find one)  
**Output**: 3-6 script variations with quality scores  
**Time**: ~2-5 minutes per topic (depends on API response times)

---

## 📋 Phase 2 Workflow

```
1. Research: Find trending topics via VidIQ
2. Generate: Create 3-6 script variations (different hooks)
3. Score: Rate each script for quality (0-10)
4. Validate: Check for engagement, structure, CTAs
5. Store: Save to analytics database
6. Select: Pick best script to feed into Phase 3
```

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Verify Phase 1 is Complete
Make sure you have:
- `youtube_uploader.py` ✓
- `vidiq_analytics.py` ✓
- `analytics_db.py` ✓
- `.env` file with `CHAT_API_KEY` and `VIDIQ_API_KEY` ✓

### Step 2: Test Phase 2
```bash
python test_phase2.py
```

This will:
- Find trending topics via VidIQ
- Generate 3 script variations
- Validate them
- Store in database

### Step 3: You're Done! ✨
All Phase 2 modules are ready to use.

---

## 📁 Files Created for Phase 2

| File | Purpose |
|------|---------|
| `topic_research.py` | Find and rank trending topics by opportunity |
| `script_generator.py` | Generate scripts using Gemini/Claude with different hooks |
| `script_validator.py` | Check scripts for quality, structure, engagement |
| `test_phase2.py` | Integration test (run this!) |
| `PHASE_2_SETUP.md` | This file |

---

## 🧠 Understanding the Modules

### TopicResearcher (`topic_research.py`)

**Purpose**: Find what people are searching for and want to watch.

**Key Methods**:
- `research_and_rank_topics(limit=10)` - Get trending topics ranked by opportunity
- `select_best_topic(min_opportunity_score=60)` - Auto-pick the best topic
- `get_topic_insights(topic_title)` - Detailed analysis (keywords, title suggestions)
- `print_topic_report(topics)` - Formatted output

**Example**:
```python
from topic_research import TopicResearcher

researcher = TopicResearcher('your_vidiq_key', niche='Technology')

# Get trending topics
topics = researcher.research_and_rank_topics(limit=10)

# Auto-select best one
best_topic = researcher.select_best_topic()
print(f"Topic: {best_topic['title']}")
```

**Scoring**: Combines trending score + search volume + growth rate + difficulty

---

### ScriptGenerator (`script_generator.py`)

**Purpose**: Write engaging video scripts from scratch.

**Key Methods**:
- `generate_script(topic, hook_type, video_length_seconds)` - Single script
- `generate_variations(topic, num_variations=3)` - Multiple scripts with different hooks
- `score_script(script_dict)` - Rate script quality (0-10)
- `score_variations(variations)` - Score all and sort by quality

**Hook Types**:
1. **Curiosity** - Intriguing question ("What if I told you...?")
2. **Storytelling** - Personal story or anecdote
3. **Statistic** - Surprising fact/number
4. **Problem** - Identify pain point
5. **Promise** - Clear benefit statement
6. **Bold** - Controversial claim

**Example**:
```python
from script_generator import ScriptGenerator

gen = ScriptGenerator('your_gemini_key')

# Generate 3 variations
scripts = gen.generate_variations('AI tools for writing', num_variations=3)

# Score them
scored = gen.score_variations(scripts)
best = scored[0]  # Highest score first

print(f"Best script ({best['hook_type']}): {best['quality_score']}/10")
print(f"Length: {best['word_count']} words (~{int(best['word_count']/2.5)} seconds)")
```

**Scoring Factors**:
- Hook strength (grabs attention in first 20 words)
- Structure (clear sections, transitions)
- Calls-to-action (subscribe, like, comment, etc.)
- Word count appropriateness
- Readability (sentence variety, 10-25 words/sentence ideal)

---

### ScriptValidator (`script_validator.py`)

**Purpose**: Quality-check scripts before using them.

**Key Methods**:
- `validate_script(script_dict)` - Comprehensive validation
- `suggest_improvements(script_dict, validation)` - Get specific fixes
- `validate_batch(script_dicts)` - Validate multiple scripts
- `get_valid_scripts(validated_scripts)` - Filter valid ones only

**Validation Checks**:
- ✓ Length appropriate for target video time
- ✓ Has attention-grabbing hook
- ✓ Contains calls-to-action (CTAs)
- ✓ Good sentence variety
- ✓ Emotional engagement words
- ✓ No excessive "filler" words
- ✓ Includes questions for audience

**Example**:
```python
from script_validator import ScriptValidator

validator = ScriptValidator()

# Validate
result = validator.validate_script(script_dict)

if result['is_valid']:
    print("✅ Script passes validation")
else:
    print("❌ Script has issues:")
    for issue in result['issues']:
        print(f"  • {issue}")

# Get suggestions
suggestions = validator.suggest_improvements(script_dict, result)
for s in suggestions:
    print(f"[{s['priority']}] {s['title']}")
    print(f"  Example: {s['example']}")
```

---

## 💡 Complete Example: Topic → Scripts → Database

```python
import os
from dotenv import load_dotenv
from topic_research import TopicResearcher
from script_generator import ScriptGenerator
from script_validator import ScriptValidator
from analytics_db import AnalyticsDB

load_dotenv()

# 1. Research
researcher = TopicResearcher(os.getenv('VIDIQ_API_KEY'))
best_topic = researcher.select_best_topic()
print(f"🎯 Topic: {best_topic['title']}")

# 2. Generate
generator = ScriptGenerator(os.getenv('CHAT_API_KEY'))
scripts = generator.generate_variations(
    best_topic['title'],
    num_variations=3
)

# 3. Score & Pick Best
scored = generator.score_variations(scripts)
best_script = scored[0]

# 4. Validate
validator = ScriptValidator()
validation = validator.validate_script(best_script)

if validation['is_valid']:
    print(f"✅ Best script validated ({best_script['quality_score']}/10)")
else:
    print(f"⚠️  Issues found: {validation['issues']}")
    suggestions = validator.suggest_improvements(best_script, validation)
    # Fix issues if needed

# 5. Store in Database
db = AnalyticsDB()
topic_id = db.add_topic(
    title=best_topic['title'],
    niche='Technology',
    trending_score=best_topic.get('trending_score', 0),
    search_volume=best_topic.get('estimated_views', 0),
    competition='medium',
    difficulty=5.0
)

script_id = db.add_script(
    topic_id=topic_id,
    script_text=best_script['script_text'],
    quality_score=best_script['quality_score'],
    hook_type=best_script['hook_type'],
    length_seconds=300
)

print(f"✓ Saved to database (topic={topic_id}, script={script_id})")

# 6. Script Ready for Phase 3!
print(f"\nScript ready for Phase 3: Video generation")
```

---

## ⚙️ Configuration

### Environment Variables Needed

```env
# From Phase 1 (already have these)
CHAT_API_KEY=your_gemini_api_key
VIDIQ_API_KEY=your_vidiq_api_key
YOUTUBE_CLIENT_SECRETS_FILE=youtube_client_secret.json

# Existing variables
TEXT_MODEL=gemini-2.5-flash
IMAGE_MODEL=gemini-3.1-flash-image
```

### Adjust Script Generation

In `script_generator.py`:
- **Language**: Prompts are English. Fork to support other languages.
- **Length**: Default 300 seconds (~750 words). Adjust `word_count_estimate` logic.
- **Style**: Casual/conversational tone. Modify prompt for academic/formal style.
- **Tone**: Modify hook descriptions in `HOOKS` dict.

---

## 🔍 Common Workflows

### Workflow 1: Auto-Generate Single Best Script
```python
researcher = TopicResearcher(vidiq_key)
best_topic = researcher.select_best_topic()

generator = ScriptGenerator(gemini_key)
script = generator.generate_script(best_topic['title'])

print(script['script_text'])
```

### Workflow 2: Generate & Rate Multiple Versions
```python
generator = ScriptGenerator(gemini_key)

# Create 3 versions
scripts = generator.generate_variations('AI 2025', num_variations=3)

# Score & print report
scored = generator.score_variations(scripts)
generator.print_script_report(scored)
```

### Workflow 3: Quality Gate Before Publishing
```python
validator = ScriptValidator()

for script in scripts:
    result = validator.validate_script(script)
    
    if not result['is_valid']:
        print(f"❌ {script['hook_type']}: Issues found")
        for issue in result['issues']:
            print(f"  • {issue}")
    else:
        print(f"✅ {script['hook_type']}: Ready to use")
        db.add_script(topic_id, script['script_text'], ...)
```

### Workflow 4: Find Topic → Generate → Store
```python
# Complete flow (copy-paste ready!)
from topic_research import TopicResearcher
from script_generator import ScriptGenerator
from analytics_db import AnalyticsDB
import os
from dotenv import load_dotenv

load_dotenv()

# Research
researcher = TopicResearcher(os.getenv('VIDIQ_API_KEY'))
topic = researcher.select_best_topic()

# Generate
generator = ScriptGenerator(os.getenv('CHAT_API_KEY'))
scripts = generator.generate_variations(topic['title'], num_variations=3)
scored = generator.score_variations(scripts)

# Store
db = AnalyticsDB()
topic_id = db.add_topic(topic['title'], 'Technology', 75, 50000, 'medium', 5.0)
script_id = db.add_script(topic_id, scored[0]['script_text'], 
                          scored[0]['quality_score'], scored[0]['hook_type'], 300)

print(f"✅ Done! Topic {topic_id}, Script {script_id}")
```

---

## 🧪 Testing Checklist

Before moving to Phase 3, verify:

- [ ] `python test_phase2.py` runs without errors
- [ ] Topic research returns trending topics
- [ ] Script generation produces 1000+ word scripts
- [ ] Different hook types produce different scripts
- [ ] Scoring ranks scripts meaningfully (scores differ)
- [ ] Validation catches issues
- [ ] Scripts store in database
- [ ] Can retrieve scripts from database

---

## ⚠️ Common Issues & Fixes

### Issue: "CHAT_API_KEY not configured"
**Fix**: 
```bash
# Check .env file has this line:
CHAT_API_KEY=sk-proj-xxxxx...

# Or set it:
python -c "import os; print(os.getenv('CHAT_API_KEY'))"
```

### Issue: "Script generation returns empty"
**Fix**: 
- Check Gemini API quota (free tier has limits)
- Verify `TEXT_MODEL=gemini-2.5-flash` is correct
- Try with shorter `video_length_seconds` first (e.g., 60 seconds)

### Issue: "VidIQ API returns 401 error"
**Fix**: 
- Regenerate VidIQ API key
- Verify key is pasted correctly (no spaces)
- Check API plan includes topic research endpoint

### Issue: "Database constraint error when adding script"
**Fix**: 
- Check topic_id exists in database first
- Verify you're using correct database path

### Issue: Validation says "no CTA found"
**Fix**: 
- Add "Subscribe" or "Like" to script text
- Or adjust CTA_WORDS list in `script_validator.py`

---

## 📈 Optimization Tips

1. **Parallel Generation**: Generate all 3 scripts at once with threading
2. **Caching**: Store researched topics locally to avoid repeated API calls
3. **Batch Validation**: Validate 10+ scripts in one call
4. **Selective Regeneration**: Only regenerate if score < 6.0
5. **Topic Filtering**: Add `trending_score > 70` to auto-select only hot topics

---

## 🔗 Integration with Pipeline

Phase 2 → Phase 3 (Metadata Generation):
```
Best script from Phase 2
         ↓
    (script_text)
         ↓
Phase 3: Generate titles, descriptions, tags
         ↓
Phase 4: Generate custom thumbnails
         ↓
Phase 5: Upload to YouTube
```

---

## 📊 Success Metrics

Track these to know if Phase 2 is working well:

| Metric | Target | How to Check |
|--------|--------|-------------|
| Avg script score | 7.0+ | `scored[0]['quality_score']` |
| Scripts passing validation | 80%+ | Count `is_valid == True` |
| Avg word count | 750-800 | Average `word_count` field |
| CTA presence | 100% | All scripts have 2+ CTAs |
| Generation time | <3 min/topic | Time `generate_variations()` |

---

## 🚀 Next: Phase 3 - Metadata & Thumbnails

Once Phase 2 is working:

```
✓ Phase 1: YouTube setup + Analytics
✓ Phase 2: Script generation (YOU ARE HERE)
→ Phase 3: Metadata generation (titles, descriptions, tags)
→ Phase 4: Custom thumbnails
→ Phase 5: YouTube upload
```

**When ready for Phase 3**, you'll have:
- Trending topics researched
- Multiple script variations generated
- Best script validated and scored
- Everything stored in analytics database

---

## ❓ FAQ

**Q: Can I use a different AI model instead of Gemini?**  
A: Yes - modify `script_generator.py` to use OpenAI (GPT-4) or Claude. Update `_build_script_prompt()` method.

**Q: How long are the generated scripts?**  
A: Default is ~750 words (300 seconds of video). Adjust `video_length_seconds` parameter.

**Q: Can I modify scripts after generation?**  
A: Yes! Generated script is plain text. Edit in Python:
```python
script['script_text'] = script['script_text'].replace('old text', 'new text')
```

**Q: What if script is too short?**  
A: Increase `video_length_seconds` or edit to add examples/stories.

**Q: Can I add my own scripts without generation?**  
A: Yes! Use database directly:
```python
db.add_script(topic_id, your_script_text, quality_score=7.5, hook_type='custom', ...)
```

---

## 📞 Support

If something breaks:
1. Check error message matches an issue in "Common Issues & Fixes"
2. Verify `.env` file has all keys
3. Run `test_phase2.py` to isolate which part fails
4. Check `pipeline.log` for detailed error traces

---

**Time to complete Phase 2 setup: ~10 minutes (mostly testing)**

When ready: `python test_phase2.py` ✨
