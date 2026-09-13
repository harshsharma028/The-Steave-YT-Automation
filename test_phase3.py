"""
Phase 3 Integration Test - Metadata generation (titles, descriptions, tags).
Run this after Phase 3 setup to verify everything works.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("\n" + "=" * 70)
print("PHASE 3: METADATA GENERATION TEST")
print("=" * 70)

# Test 1: Environment Setup
print("\n[1/5] 🔧 Checking Environment Variables...")
try:
    chat_api_key = os.getenv('CHAT_API_KEY')

    if not chat_api_key:
        print("⚠️  WARNING: CHAT_API_KEY not set in .env")
        chat_api_key = input("Enter your Gemini API key: ").strip()

    print(f"✓ Gemini API key configured")

except Exception as e:
    print(f"❌ Environment setup failed: {e}")
    sys.exit(1)

# Test 2: Fetch script from database
print("\n[2/5] 🗄️  Retrieving script from database...")
try:
    from analytics_db import AnalyticsDB

    db = AnalyticsDB()

    # Get latest script
    import sqlite3
    conn = sqlite3.connect('channel_analytics.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT scripts.id, scripts.script_text, scripts.topic_id, topics.title
        FROM scripts
        JOIN topics ON scripts.topic_id = topics.id
        ORDER BY scripts.created_date DESC
        LIMIT 1
    ''')
    result = cursor.fetchone()
    conn.close()

    if result:
        script_id, script_text, topic_id, topic_title = result
        print(f"✓ Found script (ID: {script_id})")
        print(f"  Topic: {topic_title}")
        print(f"  Length: {len(script_text.split())} words")
    else:
        print("⚠️  No scripts found in database")
        print("  Run: python test_phase2.py (generates test script)")
        topic_title = "AI Tools for 2025"
        script_text = "Welcome to this video about AI tools. Today we'll explore the top AI writing assistants that can save you hours. Let me show you five amazing tools that will change how you work..."

except Exception as e:
    print(f"⚠️  Database error (using test script): {e}")
    topic_title = "AI Tools for 2025"
    script_text = "Welcome to this video about AI tools. Today we'll explore the top AI writing assistants that can save you hours. Let me show you five amazing tools that will change how you work..."

# Test 3: Title Generation
print("\n[3/5] 📝 Testing Title Generation...")
try:
    from title_generator import TitleGenerator

    title_gen = TitleGenerator(chat_api_key)
    titles = title_gen.generate_titles(script_text, topic_title, num_titles=5)
    titles_scored = title_gen.score_titles(titles, topic_title)

    if titles_scored:
        print(f"✓ Generated {len(titles_scored)} titles")
        best_title = titles_scored[0]
        print(f"  Best: {best_title['title']} (Score: {best_title.get('seo_score', '?')}/10)")
    else:
        print("❌ No titles generated")
        sys.exit(1)

except Exception as e:
    print(f"❌ Title generation test failed: {e}")
    sys.exit(1)

# Test 4: Description Generation
print("\n[4/5] 📄 Testing Description Generation...")
try:
    from description_generator import DescriptionGenerator

    desc_gen = DescriptionGenerator(chat_api_key)
    description = desc_gen.generate_description(
        script_text, topic_title, best_title['title'],
        video_length_seconds=300
    )
    description = desc_gen.add_timestamps(description, script_text)
    description = desc_gen.finalize_description(description)
    desc_score = desc_gen.score_description(description, topic_title)

    if description and description.get('description_text'):
        print(f"✓ Description generated")
        print(f"  Characters: {description.get('character_count', 0)}")
        print(f"  Words: {description.get('word_count', 0)}")
        print(f"  Score: {desc_score}/10")
        print(f"  Preview: {description.get('description_text', '')[:100]}...")
    else:
        print("❌ Description generation failed")
        sys.exit(1)

except Exception as e:
    print(f"❌ Description generation test failed: {e}")
    sys.exit(1)

# Test 5: Tags & Hashtags Generation
print("\n[5/5] 🏷️  Testing Tags & Hashtags Generation...")
try:
    from tag_generator import TagGenerator

    tag_gen = TagGenerator(chat_api_key)

    # YouTube tags
    tags = tag_gen.generate_tags(script_text, topic_title, best_title['title'], max_tags=30)
    print(f"✓ Generated {len(tags)} YouTube tags")
    print(f"  {', '.join(tags[:5])}...")

    # Instagram hashtags
    instagram_tags = tag_gen.generate_hashtags(
        script_text, topic_title, best_title['title'],
        max_hashtags=20, for_platform='instagram'
    )
    print(f"✓ Generated {len(instagram_tags)} Instagram hashtags")

    # TikTok hashtags
    tiktok_tags = tag_gen.generate_hashtags(
        script_text, topic_title, best_title['title'],
        max_hashtags=15, for_platform='tiktok'
    )
    print(f"✓ Generated {len(tiktok_tags)} TikTok hashtags")

except Exception as e:
    print(f"❌ Tags generation test failed: {e}")
    sys.exit(1)

# Success Summary
print("\n" + "=" * 70)
print("✅ PHASE 3 INTEGRATION TEST COMPLETE")
print("=" * 70)

print("\n📋 Summary:")
print("  ✓ Title generation working (5+ variations)")
print("  ✓ Title scoring working (SEO optimization)")
print("  ✓ Description generation working")
print("  ✓ Description timestamps working")
print("  ✓ Tags generation working (YouTube max 30)")
print("  ✓ Instagram hashtags working")
print("  ✓ TikTok hashtags working")

print("\n📊 Test Results:")
print(f"  • Topic: {topic_title}")
print(f"  • Script length: {len(script_text.split())} words")
print(f"  • Best title: {best_title['title']}")
print(f"  • Title score: {best_title.get('seo_score', '?')}/10")
print(f"  • Description length: {description.get('character_count', 0)} chars")
print(f"  • Description score: {desc_score}/10")
print(f"  • YouTube tags: {len(tags)}")
print(f"  • Instagram hashtags: {len(instagram_tags)}")
print(f"  • TikTok hashtags: {len(tiktok_tags)}")

print("\n🎯 Next Steps:")
print("  1. Test complete metadata generation (MetadataGenerator)")
print("  2. Export metadata to JSON")
print("  3. Export for YouTube upload (separate files)")
print("  4. Ready for Phase 4 (Thumbnail Generation)")

print("\n" + "=" * 70)
print("\n✨ Phase 3 ready to go! 🚀\n")
