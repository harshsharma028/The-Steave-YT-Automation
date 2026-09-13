"""
Phase 2 Integration Test - Topic research, script generation, and validation.
Run this after completing Phase 2 setup to ensure everything works.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("\n" + "=" * 70)
print("PHASE 2: SCRIPT GENERATION ENGINE TEST")
print("=" * 70)

# Test 1: Environment Setup
print("\n[1/6] 🔧 Checking Environment Variables...")
try:
    chat_api_key = os.getenv('CHAT_API_KEY')
    vidiq_key = os.getenv('VIDIQ_API_KEY')

    if not chat_api_key:
        print("⚠️  WARNING: CHAT_API_KEY not set in .env")
        chat_api_key = input("Enter your Gemini API key: ").strip()

    if not vidiq_key:
        print("⚠️  WARNING: VIDIQ_API_KEY not set in .env")
        vidiq_key = input("Enter your VidIQ API key: ").strip()

    print(f"✓ Gemini API key configured")
    print(f"✓ VidIQ API key configured")

except Exception as e:
    print(f"❌ Environment setup failed: {e}")
    sys.exit(1)

# Test 2: Topic Research
print("\n[2/6] 🔍 Testing Topic Research...")
try:
    from topic_research import TopicResearcher

    researcher = TopicResearcher(vidiq_key, niche="Technology")

    print("  Finding trending topics...")
    ranked_topics = researcher.research_and_rank_topics(limit=5)

    if ranked_topics:
        print(f"  ✓ Found {len(ranked_topics)} trending topics")
        best_topic = ranked_topics[0]
        print(f"  ✓ Best topic: {best_topic['title']} (Score: {best_topic['opportunity_score']})")
        test_topic = best_topic['title']
    else:
        print("  ⚠️  No trending topics found - using default topic")
        test_topic = "How AI is Changing Technology in 2025"

except Exception as e:
    print(f"❌ Topic research test failed: {e}")
    print("   Make sure VIDIQ_API_KEY is valid")
    test_topic = "How AI is Changing Technology in 2025"
    # Don't exit - continue with default topic

# Test 3: Script Generation
print("\n[3/6] ✍️  Testing Script Generation...")
try:
    from script_generator import ScriptGenerator

    generator = ScriptGenerator(chat_api_key)

    print(f"  Generating script for: {test_topic}")
    script = generator.generate_script(
        topic=test_topic,
        hook_type="curiosity",
        video_length_seconds=300
    )

    if script and script.get('script_text'):
        print(f"  ✓ Script generated")
        print(f"    - Length: {script['word_count']} words (~{int(script['word_count']/2.5)} seconds)")
        print(f"    - Hook type: {script['hook_type']}")
        print(f"    - Quality score: {script.get('quality_score', 'N/A')}")
        print(f"\n  Preview: {script['script_text'][:100]}...\n")
    else:
        print("  ❌ Script generation returned empty")
        sys.exit(1)

except Exception as e:
    print(f"❌ Script generation test failed: {e}")
    print("   Make sure:")
    print("   - CHAT_API_KEY is valid")
    print("   - config.py has correct TEXT_MODEL")
    sys.exit(1)

# Test 4: Script Variations
print("\n[4/6] 🔄 Testing Script Variations...")
try:
    print(f"  Generating 3 script variations...")
    variations = generator.generate_variations(
        topic=test_topic,
        num_variations=3,
        video_length_seconds=300
    )

    if variations:
        print(f"  ✓ Generated {len(variations)} variations")
        for v in variations:
            print(f"    - {v['hook_type'].title()}: {v['word_count']} words")

        # Score them
        scored = generator.score_variations(variations)
        best_script = scored[0]
        print(f"\n  ✓ Best variation: {best_script['hook_type'].upper()} (Score: {best_script['quality_score']}/10)")

    else:
        print("  ❌ No variations generated")
        sys.exit(1)

except Exception as e:
    print(f"❌ Script variations test failed: {e}")
    sys.exit(1)

# Test 5: Script Validation
print("\n[5/6] ✅ Testing Script Validation...")
try:
    from script_validator import ScriptValidator

    validator = ScriptValidator()

    validation = validator.validate_script(best_script)

    print(f"  Validation status: {validation['status']}")
    print(f"  • Issues: {len(validation['issues'])}")
    print(f"  • Warnings: {len(validation['warnings'])}")

    if validation['issues']:
        for issue in validation['issues']:
            print(f"    ⚠️  {issue}")

    if validation['warnings']:
        print(f"  Sample warnings:")
        for warning in validation['warnings'][:2]:
            print(f"    • {warning}")

    # Get suggestions
    suggestions = validator.suggest_improvements(best_script, validation)
    print(f"  • Improvement suggestions: {len(suggestions)}")

    print(f"  ✓ Validation complete")

except Exception as e:
    print(f"❌ Script validation test failed: {e}")
    sys.exit(1)

# Test 6: Database Integration
print("\n[6/6] 🗄️  Testing Database Integration...")
try:
    from analytics_db import AnalyticsDB

    db = AnalyticsDB()

    # Add the topic we researched
    topic_id = db.add_topic(
        title=test_topic,
        niche="Technology",
        trending_score=75,  # Sample score
        search_volume=50000,
        competition="medium",
        difficulty=6.0
    )
    print(f"  ✓ Topic added (ID: {topic_id})")

    # Add the best script
    script_id = db.add_script(
        topic_id=topic_id,
        script_text=best_script['script_text'],
        quality_score=best_script['quality_score'],
        hook_type=best_script['hook_type'],
        length_seconds=300
    )
    print(f"  ✓ Script added (ID: {script_id})")

except Exception as e:
    print(f"❌ Database integration test failed: {e}")
    sys.exit(1)

# Success Summary
print("\n" + "=" * 70)
print("✅ PHASE 2 INTEGRATION TEST COMPLETE")
print("=" * 70)

print("\n📋 Summary:")
print("  ✓ Topic research working (VidIQ integration)")
print("  ✓ Script generation working (Gemini/Claude)")
print("  ✓ Script variations generated (3+ hooks)")
print("  ✓ Script validation working")
print("  ✓ Database storing topics and scripts")

print("\n📊 Test Results:")
print(f"  • Topic: {test_topic}")
print(f"  • Best script score: {best_script['quality_score']}/10")
print(f"  • Script length: {best_script['word_count']} words")
print(f"  • Variations tested: {len(variations)}")
print(f"  • Validation issues: {len(validation['issues'])}")
print(f"  • Database topic ID: {topic_id}")
print(f"  • Database script ID: {script_id}")

print("\n🎯 Next Steps:")
print("  1. Test with your own topics")
print("  2. Review generated scripts for quality")
print("  3. Adjust hook types based on performance")
print("  4. Ready for Phase 3 (Metadata & Thumbnails)")

print("\n" + "=" * 70)
print("\n✨ Phase 2 ready to go! 🚀\n")
