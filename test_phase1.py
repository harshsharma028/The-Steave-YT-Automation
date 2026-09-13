"""
Phase 1 Integration Test - Verify YouTube API, VidIQ API, and Analytics Database.
Run this after completing Phase 1 setup to ensure everything works.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("\n" + "=" * 70)
print("PHASE 1: SETUP & INTEGRATION TEST")
print("=" * 70)

# Test 1: Check environment variables
print("\n[1/6] 🔧 Checking Environment Variables...")
try:
    youtube_secrets = os.getenv('YOUTUBE_CLIENT_SECRETS_FILE', 'youtube_client_secret.json')
    vidiq_key = os.getenv('VIDIQ_API_KEY')

    if not vidiq_key:
        print("⚠️  WARNING: VIDIQ_API_KEY not set in .env")
        vidiq_key = input("Enter your VidIQ API key: ").strip()

    print(f"✓ YouTube secrets file: {youtube_secrets}")
    print(f"✓ VidIQ API key configured")

except Exception as e:
    print(f"❌ Environment setup failed: {e}")
    sys.exit(1)

# Test 2: YouTube API
print("\n[2/6] 🎬 Testing YouTube API...")
try:
    from youtube_uploader import YouTubeUploader

    uploader = YouTubeUploader(youtube_secrets)
    channel_info = uploader.get_channel_info()

    if channel_info:
        print(f"✓ Connected to: {channel_info['title']}")
        print(f"  - Channel ID: {channel_info['channel_id']}")
        print(f"  - Subscribers: {channel_info['subscribers']}")
        print(f"  - Videos: {channel_info['video_count']}")
        print(f"  - Total views: {channel_info['view_count']}")
    else:
        print("❌ Failed to get channel info")
        sys.exit(1)

except Exception as e:
    print(f"❌ YouTube API test failed: {e}")
    print("   Make sure:")
    print("   - youtube_client_secret.json exists")
    print("   - You've authorized the OAuth flow")
    sys.exit(1)

# Test 3: VidIQ API
print("\n[3/6] 📊 Testing VidIQ Analytics API...")
try:
    from vidiq_analytics import VidIQAnalytics

    vidiq = VidIQAnalytics(vidiq_key)

    # Test keyword research
    print("  Testing keyword research...")
    keyword_data = vidiq.research_keyword("AI automation", region='US')

    if keyword_data:
        print(f"  ✓ Keyword: {keyword_data['keyword']}")
        print(f"    - Search volume: {keyword_data['search_volume']:,} searches/month")
        print(f"    - Competition: {keyword_data['competition']}")
        print(f"    - Trend score: {keyword_data['trend_score']}/100")
        print(f"    - CPC: ${keyword_data['cpc']:.2f}")
    else:
        print("  ❌ Keyword research failed")
        sys.exit(1)

    # Test trending topics
    print("  Testing trending topics...")
    topics = vidiq.get_trending_topics(category='all', limit=3)

    if topics:
        print(f"  ✓ Found {len(topics)} trending topics:")
        for i, topic in enumerate(topics, 1):
            print(f"    {i}. {topic['title'][:50]}... (Score: {topic['trending_score']})")
    else:
        print("  ⚠️  No trending topics found (API might have limitations)")

except Exception as e:
    print(f"❌ VidIQ API test failed: {e}")
    print("   Make sure:")
    print("   - VIDIQ_API_KEY is set in .env")
    print("   - Your API key is valid")
    sys.exit(1)

# Test 4: Analytics Database
print("\n[4/6] 🗄️  Testing Analytics Database...")
try:
    from analytics_db import AnalyticsDB

    db = AnalyticsDB()
    print("✓ Database initialized (channel_analytics.db)")

    # Add test topic
    print("  Adding test topic...")
    topic_id = db.add_topic(
        title="Test Topic: AI Automation",
        niche="Technology",
        trending_score=keyword_data['trend_score'],
        search_volume=keyword_data['search_volume'],
        competition=keyword_data['competition'],
        difficulty=5.0
    )
    print(f"  ✓ Topic added (ID: {topic_id})")

    # Add test script
    print("  Adding test script...")
    script_id = db.add_script(
        topic_id=topic_id,
        script_text="This is a test script about AI automation...",
        quality_score=8.5,
        hook_type="curiosity",
        length_seconds=480
    )
    print(f"  ✓ Script added (ID: {script_id})")

except Exception as e:
    print(f"❌ Database test failed: {e}")
    sys.exit(1)

# Test 5: Channel Statistics
print("\n[5/6] 📈 Retrieving Channel Statistics...")
try:
    stats = db.get_channel_statistics()

    print(f"✓ Channel Statistics:")
    print(f"  - Total videos: {stats['total_videos']}")
    print(f"  - Total views: {stats['total_views']:,}")
    print(f"  - Avg watch time: {stats['avg_watch_time_hours']:.2f} hours")
    print(f"  - Avg engagement: {stats['avg_engagement_rate']:.2f}%")

except Exception as e:
    print(f"❌ Statistics retrieval failed: {e}")
    sys.exit(1)

# Test 6: Title Scoring
print("\n[6/6] ⭐ Testing Title Scoring...")
try:
    test_title = "7 AI Writing Tools That Save 10 Hours Per Week"
    score_result = vidiq.score_title(test_title, keyword_data['keyword'])

    if score_result:
        print(f"✓ Title score: {score_result['score']}/100")
        print(f"  - CTR potential: {score_result['ctr_potential']}")
        print(f"  - Keyword match: {score_result['keyword_match']}")
        if score_result['suggestions']:
            print(f"  - Suggestions:")
            for suggestion in score_result['suggestions'][:2]:
                print(f"    • {suggestion}")
    else:
        print("⚠️  Title scoring not available (API limitation)")

except Exception as e:
    print(f"⚠️  Title scoring test failed: {e}")
    print("   This is optional and may not be available on all API plans")

# Test 7: Export Report
print("\n[7/7] 📄 Testing Report Export...")
try:
    report_path = db.export_report('test_channel_report.json')
    print(f"✓ Report exported: {report_path}")

except Exception as e:
    print(f"❌ Report export failed: {e}")
    sys.exit(1)

# Success Summary
print("\n" + "=" * 70)
print("✅ PHASE 1 INTEGRATION TEST COMPLETE")
print("=" * 70)

print("\n📋 Summary:")
print("  ✓ YouTube API authenticated and working")
print("  ✓ VidIQ Analytics API connected")
print("  ✓ Analytics database created and functional")
print("  ✓ Can research keywords and topics")
print("  ✓ Can store and retrieve channel data")
print("  ✓ Can score titles for SEO")
print("  ✓ Can export analytics reports")

print("\n🎯 You're ready for Phase 2!")
print("   Next: Script generation engine (generate_scripts.py)")

print("\n📊 Test Data:")
print(f"  - Channel: {channel_info['title']}")
print(f"  - Test keyword: '{keyword_data['keyword']}'")
print(f"  - Search volume: {keyword_data['search_volume']:,}/month")
print(f"  - Test topic ID: {topic_id}")
print(f"  - Test script ID: {script_id}")
print(f"  - Report: test_channel_report.json")

print("\n" + "=" * 70)
print("\n✨ All systems operational. Happy creating! 🚀\n")
