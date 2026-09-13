# Phase 2: Script Generation Engine - Architecture & Design

## 🎯 Overview

Phase 2 transforms **trending topics** into **production-ready video scripts** with quality scoring and validation.

```
Input Topics (from VidIQ)
         ↓
   [Topic Research]
   - Rank by opportunity
   - Get keywords
   - Analyze competition
         ↓
    Best Topics
         ↓
  [Script Generation]
  - Generate 3-6 variations
  - Different hooks (curiosity, story, stats, etc.)
  - Gemini/Claude powered
         ↓
   Raw Scripts
         ↓
   [Quality Scoring]
   - Score each script (0-10)
   - Rate hook strength
   - Check structure
   - Sort by quality
         ↓
   Ranked Scripts
         ↓
  [Validation & QA]
  - Check word count
  - Verify CTAs present
  - Assess engagement level
  - Get improvement suggestions
         ↓
   Production-Ready Scripts
         ↓
   [Database Storage]
   - Save to analytics_db
   - Link to topics
   - Track quality metrics
         ↓
   Ready for Phase 3
```

---

## 🧩 Module Architecture

### Layer 1: Topic Research (`topic_research.py`)

**Responsibility**: Find what people want to watch

**Key Classes**:
- `TopicResearcher` - Main research coordinator

**Key Methods**:
```
research_and_rank_topics()        → Find trending, score by opportunity
select_best_topic()               → Auto-pick best topic
get_keywords_for_topic()          → Research related keywords
get_topic_insights()              → Full topic analysis
score_topic_opportunity()         → Calculate opportunity score
```

**Scoring Algorithm**:
```
Opportunity Score = 
    (Trending Score × 0.2) +           # Is it hot?
    (Search Volume × 0.3) +            # Do people care?
    ((100 - Difficulty) × 0.2) +       # Easy to rank?
    (Growth Rate × 0.3)                # Is it growing?
    
Max = 100
```

**Integration**:
- Calls `VidIQAnalytics` for real data
- Returns ranked list of topics with scores
- Seeds `ScriptGenerator` with topics to write about

---

### Layer 2: Script Generation (`script_generator.py`)

**Responsibility**: Write engaging video scripts using AI

**Key Classes**:
- `ScriptGenerator` - Main generation engine

**Key Methods**:
```
generate_script()                 → Create single script with hook
generate_variations()             → Create 3-6 variations
score_script()                    → Rate script quality (0-10)
score_variations()                → Score all & sort
export_scripts()                  → Save to JSON
```

**Hook Types** (6 variants):
1. **Curiosity** - "What if I told you...?" 
2. **Storytelling** - Personal anecdote
3. **Statistic** - Surprising fact
4. **Problem** - Pain point identification
5. **Promise** - Clear benefit statement
6. **Bold** - Controversial claim

**Scoring Algorithm**:
```
Quality Score (0-10) =
    Hook Strength (0-2 pts)       - Does first sentence grab attention?
    Structure (0-2 pts)           - Clear sections & transitions?
    CTAs (0-2 pts)                - Calls-to-action present?
    Word Count (0-2 pts)          - Match target length?
    Readability (0-2 pts)         - Good sentence variety?
```

**Generation Process**:
1. Build context-specific prompt
2. Call Gemini/Claude with `temperature=0.7` (creative but coherent)
3. Extract raw text from response
4. Calculate automatic quality score
5. Return script dict

**Integration**:
- Takes topics from `TopicResearcher`
- Produces scripts for `ScriptValidator`
- Feeds best scripts to `AnalyticsDB`

---

### Layer 3: Script Validation (`script_validator.py`)

**Responsibility**: Quality assurance before publishing

**Key Classes**:
- `ScriptValidator` - QA coordinator

**Key Methods**:
```
validate_script()                 → Comprehensive validation
suggest_improvements()            → Get specific fixes
validate_batch()                  → QA multiple scripts
get_valid_scripts()               → Filter only valid ones
```

**Validation Checks** (10 total):

| Check | What | Pass Criteria |
|-------|------|---------------|
| Length | Word count vs target | Within ±20% of target |
| Hook | Attention-grabbing | Curiosity/emotion in first 50 chars |
| CTAs | Calls-to-action | 2+ CTAs (subscribe, like, comment, etc.) |
| Structure | Sentences present | 3+ sentences minimum |
| Engagement | Emotional words | "amazing", "incredible", etc. present |
| Weak Words | Filler removal | < 5% weak words (just, really, very) |
| Readability | Sentence length | 10-25 words/sentence ideal |
| Questions | Audience engagement | 1+ question marks |
| Repetition | Word variety | No word repeated 5+ times |
| Format | Cleanliness | No double spaces, trimmed |

**Improvement Suggestions**:
- **HIGH**: Missing hook, no CTA
- **MEDIUM**: Low engagement, too many weak words
- **LOW**: Sentence length, word variety

**Integration**:
- Validates output from `ScriptGenerator`
- Flags issues before database storage
- Feeds validation results to `AnalyticsDB` for scoring

---

### Layer 4: Database Integration (`analytics_db.py`)

**Existing Schema** (Phase 1):
```
topics table:
  - id (primary key)
  - title (UNIQUE)
  - niche
  - trending_score
  - search_volume
  - competition
  - difficulty
  - research_date
  - status

scripts table:
  - id (primary key)
  - topic_id (foreign key → topics)
  - script_text
  - quality_score
  - hook_type
  - estimated_length_seconds
  - created_date
  - status
```

**Phase 2 Usage**:
```python
# Add researched topic
topic_id = db.add_topic(
    title="AI Writing Tools 2025",
    niche="Technology",
    trending_score=85,
    search_volume=75000,
    competition="medium",
    difficulty=5.0
)

# Store generated script
script_id = db.add_script(
    topic_id=topic_id,
    script_text="Generated script...",
    quality_score=8.5,
    hook_type="curiosity",
    length_seconds=300
)
```

**Integration**:
- `TopicResearcher` feeds topics → `add_topic()`
- `ScriptValidator` scores scripts → stored with quality_score
- Enables performance tracking: which topics/hooks perform best

---

## 🔄 Complete Workflow

### Workflow A: Auto-Best-Script (Recommended for MVP)
```
┌─────────────────────────────────────────────────────────────┐
│ 1. TopicResearcher.select_best_topic()                      │
│    ↓ Returns: best_topic dict                               │
├─────────────────────────────────────────────────────────────┤
│ 2. ScriptGenerator.generate_variations(best_topic, n=3)     │
│    ↓ Returns: 3 scripts with different hooks                │
├─────────────────────────────────────────────────────────────┤
│ 3. ScriptGenerator.score_variations(scripts)                │
│    ↓ Returns: sorted by quality (highest first)             │
├─────────────────────────────────────────────────────────────┤
│ 4. ScriptValidator.validate_script(best_script)             │
│    ↓ Returns: validation result (PASS/FAIL)                 │
├─────────────────────────────────────────────────────────────┤
│ 5. If PASS: AnalyticsDB.add_topic() + add_script()          │
│    ↓ Stores to database                                     │
├─────────────────────────────────────────────────────────────┤
│ 6. Best script ready for Phase 3                            │
└─────────────────────────────────────────────────────────────┘
```

**Time**: ~2-3 minutes  
**Result**: Production-ready script in database

---

### Workflow B: Manual Review (High Quality)
```
┌─────────────────────────────────────────────────────────────┐
│ 1. Generate 3 scripts with different hooks                  │
│    ↓ All variations generated in parallel                   │
├─────────────────────────────────────────────────────────────┤
│ 2. Score & rank all scripts                                 │
│    ↓ User sees top 3 ranked options                         │
├─────────────────────────────────────────────────────────────┤
│ 3. Validate each script                                     │
│    ↓ Show issues & improvement suggestions                  │
├─────────────────────────────────────────────────────────────┤
│ 4. User picks favorite (or best scored)                     │
│    ↓ Manual review of content quality                       │
├─────────────────────────────────────────────────────────────┤
│ 5. Optional: Edit script text                               │
│    ↓ User improves before publishing                        │
├─────────────────────────────────────────────────────────────┤
│ 6. Store final script in database                           │
│    ↓ Ready for Phase 3                                      │
└─────────────────────────────────────────────────────────────┘
```

**Time**: ~5-10 minutes (includes human review)  
**Result**: High-confidence, manually-approved script

---

## 🔌 API Integrations

### Gemini API (Text Generation)
```
ScriptGenerator
    ↓
genai.Client().models.generate_content()
    ├─ model: TEXT_MODEL (gemini-2.5-flash)
    ├─ prompt: Topic + hook type + length target
    ├─ temperature: 0.7 (creative but coherent)
    └─ Returns: Generated script text
```

**Cost**: ~$0.075 per 1M input tokens, negligible per script  
**Rate Limit**: Free tier ~15 requests/min  
**Fallback**: If API down, cache previous scripts

---

### VidIQ API (Topic Research)
```
TopicResearcher
    ↓
VidIQAnalytics
    ├─ get_trending_topics()
    ├─ research_keyword()
    ├─ analyze_competitor_channel()
    └─ score_title()
```

**Cost**: Depends on plan (free tier limited)  
**Rate Limit**: ~60 req/min on free tier  
**Fallback**: Use cached topics or manual input

---

### SQLite Database (Local Storage)
```
AnalyticsDB
    ├─ topics table (researched topics)
    └─ scripts table (generated scripts)
```

**No API call** - Everything local  
**Performance**: Instant queries  
**Scalability**: SQLite good for <1M rows

---

## 📊 Data Flow

```
VidIQ API
    ↓
TopicResearcher
    ├─ Fetches trending topics
    ├─ Scores by opportunity
    └─ Returns ranked list
         ↓
     Best Topic
         ↓
  ScriptGenerator
    ├─ Receives topic title
    ├─ Generates 3-6 variations
    ├─ Auto-scores each
    └─ Returns sorted by quality
         ↓
     Best Scripts
         ↓
  ScriptValidator
    ├─ Validates structure
    ├─ Checks engagement
    ├─ Provides suggestions
    └─ Returns issues & fixes
         ↓
     Validated Scripts
         ↓
    AnalyticsDB
    ├─ Stores topics
    ├─ Stores scripts
    └─ Tracks metrics
         ↓
  Database Ready
         ↓
   Phase 3 Input
```

---

## ⚙️ Configuration Points

### ScriptGenerator
```python
# In script_generator.py:
- temperature=0.7 → Adjust creativity (0=deterministic, 1=random)
- top_p=0.95 → Diversity in generation
- top_k=40 → Top-k sampling
- Hook types → Add/remove hook styles
```

### ScriptValidator
```python
# In script_validator.py:
- WEAK_WORDS list → Words to penalize
- ENGAGEMENT_WORDS list → Positive word signals
- CTA_WORDS list → Call-to-action vocabulary
- Sentence length range → 10-25 (adjustable)
```

### TopicResearcher
```python
# In topic_research.py:
- Niche → Change content category
- Scoring weights → Adjust opportunity formula
- Keyword extraction → Improve keyword research
```

---

## 🔍 Quality Metrics

### Script Quality Score
**Range**: 0-10  
**Factors**:
- Hook (how effective opening is)
- Structure (narrative flow)
- CTAs (engagement requests)
- Length (time match)
- Readability (sentence variety)

**Target**: 7.0+ for production use

---

### Topic Opportunity Score
**Range**: 0-100  
**Factors**:
- Trending score (current popularity)
- Search volume (audience size)
- Growth rate (trend trajectory)
- Difficulty (competition level)

**Target**: 60+ for good topics, 75+ for excellent

---

### Validation Status
**PASS**: Script meets all requirements  
**FAIL**: Script has blocking issues

**Issues** (must fix):
- No CTAs
- Wrong length (±30%)
- No hook

**Warnings** (recommended):
- Low engagement words
- High weak word density
- Missing questions

---

## 🚀 Optimization Strategies

### 1. Parallel Generation
```python
# Generate all 3 scripts in parallel threads
from threading import Thread

threads = []
results = []
for hook in hooks:
    t = Thread(target=lambda: 
        results.append(generator.generate_script(topic, hook))
    )
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

**Benefit**: 3x faster (3 scripts in ~1 min vs 3 min)

---

### 2. Caching Topics
```python
# Store researched topics locally
import json

with open('cached_topics.json', 'w') as f:
    json.dump(ranked_topics, f)

# Reuse without API call
with open('cached_topics.json') as f:
    cached = json.load(f)
```

**Benefit**: Skip VidIQ API costs for repeated topics

---

### 3. Batch Validation
```python
# Validate 10+ scripts at once
results = validator.validate_batch(scripts)
valid = validator.get_valid_scripts(results)
```

**Benefit**: More efficient than one-by-one

---

### 4. Selective Regeneration
```python
# Only regenerate if score < threshold
for script in scripts:
    if script['quality_score'] < 6.0:
        script = generator.generate_script(topic)
```

**Benefit**: Save API credits, faster processing

---

## 🔐 Error Handling

### API Failures
```python
try:
    script = generator.generate_script(topic)
except Exception as e:
    logger.error(f"Generation failed: {e}")
    # Fallback: Use cached script or prompt user
    script = cached_scripts.get(topic, {})
```

---

### Database Errors
```python
try:
    topic_id = db.add_topic(...)
except Exception as e:
    logger.error(f"DB error: {e}")
    # Fallback: Try again or use temporary storage
```

---

## 📈 Metrics to Track

| Metric | Purpose | Target |
|--------|---------|--------|
| Avg script quality | Content quality | 7.0+ |
| Scripts passing validation | QA effectiveness | 80%+ |
| Avg generation time | Speed efficiency | <3 min/topic |
| CTA coverage | Engagement | 100% |
| Topics researched | Research volume | Track over time |

---

## 🔄 Integration with Other Phases

```
Phase 1: Setup & Analytics
    ↓ (provides database access)
Phase 2: Script Generation (YOU ARE HERE)
    ↓ (produces scripts)
Phase 3: Metadata Generation
    ↓ (creates titles, descriptions)
Phase 4: Thumbnail Generation
    ↓ (creates cover images)
Phase 5: YouTube Upload
    ↓ (publishes video)
Feedback Loop:
    ↓ (analytics used to improve future scripts)
Phase 1: Setup & Analytics (cycle repeats)
```

---

## 🎓 Learning Outcomes

After Phase 2, you'll understand:
- Topic research and opportunity scoring
- AI-powered script generation with multiple styles
- Automated quality assessment
- Engagement metrics (CTAs, hooks, structure)
- Database integration with content generation

---

## 📚 Next Phase: Phase 3 - Metadata Generation

Phase 3 will take scripts and generate:
- **Titles** (multiple options ranked by SEO)
- **Descriptions** (detailed, keyword-optimized)
- **Tags** (15-30 relevant tags)
- **Hashtags** (for social media)
- **Thumbnail concepts** (text prompts for image generation)

**Dependency**: Script from Phase 2 (this phase)

---

**Phase 2 Status**: ✅ Complete and tested  
**Ready for**: Phase 3 development
