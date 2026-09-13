"""
VidIQ Analytics Integration - Research trends, score content, track performance.
Handles keyword research, trending video analysis, and performance monitoring.
"""

import requests
import json
from datetime import datetime, timedelta
from utils import setup_logger

logger = setup_logger("VidIQAnalytics")

# VidIQ API endpoints
VIDIQ_API_BASE = "https://api.vidiq.com/api/v2"


class VidIQAnalytics:
    """Integrate with VidIQ for YouTube analytics and research."""

    def __init__(self, api_key):
        """
        Initialize VidIQ integration.

        Args:
            api_key: VidIQ API key from https://www.vidiq.com/api
        """
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        self._test_connection()

    def _test_connection(self):
        """Verify API key and connection."""
        try:
            response = requests.get(f'{VIDIQ_API_BASE}/auth/verify', headers=self.headers)
            if response.status_code == 200:
                logger.info("✓ VidIQ connection verified")
            else:
                logger.error(f"❌ VidIQ auth failed: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ VidIQ connection error: {e}")

    def research_keyword(self, keyword, region='US'):
        """
        Research keyword metrics (search volume, competition, etc).

        Args:
            keyword: Keyword to research
            region: Region code (e.g., 'US', 'GB', 'JP')

        Returns:
            Dict with search_volume, competition, trend_score, etc.
        """
        try:
            params = {
                'keyword': keyword,
                'region': region
            }
            response = requests.get(
                f'{VIDIQ_API_BASE}/keyword/research',
                headers=self.headers,
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                logger.info(f"📊 Keyword research: {keyword}")
                return {
                    'keyword': keyword,
                    'search_volume': data.get('search_volume', 0),
                    'competition': data.get('competition', 'unknown'),  # Low/Medium/High
                    'trend_score': data.get('trend_score', 0),  # 0-100
                    'cpc': data.get('cpc', 0),  # Cost per click (advertiser interest)
                    'suggested_video_length': data.get('avg_video_length', 0)
                }
            else:
                logger.error(f"❌ Keyword research failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"❌ Keyword research error: {e}")
            return None

    def get_trending_topics(self, category='all', region='US', limit=10):
        """
        Get trending topics from YouTube.

        Args:
            category: Video category ('all', 'gaming', 'music', 'news', etc)
            region: Region code
            limit: Max topics to return

        Returns:
            List of trending topics with metrics
        """
        try:
            params = {
                'category': category,
                'region': region,
                'limit': limit
            }
            response = requests.get(
                f'{VIDIQ_API_BASE}/trends/topics',
                headers=self.headers,
                params=params
            )

            if response.status_code == 200:
                topics = response.json().get('topics', [])
                logger.info(f"🔥 Found {len(topics)} trending topics in {category}")
                return [
                    {
                        'title': t.get('title'),
                        'trending_score': t.get('trending_score'),
                        'estimated_views': t.get('estimated_views'),
                        'growth_rate': t.get('growth_rate'),
                        'difficulty': t.get('difficulty')  # How competitive
                    }
                    for t in topics
                ]
            else:
                logger.error(f"❌ Failed to fetch trends: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"❌ Trending topics error: {e}")
            return []

    def analyze_competitor_channel(self, channel_id):
        """
        Analyze competitor channel metrics.

        Args:
            channel_id: YouTube channel ID

        Returns:
            Dict with subscriber count, avg views, top videos, etc.
        """
        try:
            params = {'channel_id': channel_id}
            response = requests.get(
                f'{VIDIQ_API_BASE}/channel/analysis',
                headers=self.headers,
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                logger.info(f"📈 Analyzed competitor channel {channel_id}")
                return {
                    'channel_name': data.get('channel_name'),
                    'subscriber_count': data.get('subscriber_count'),
                    'total_views': data.get('total_views'),
                    'avg_views_per_video': data.get('avg_views_per_video'),
                    'upload_frequency': data.get('upload_frequency'),  # Videos per week
                    'top_performing_topics': data.get('top_topics'),
                    'engagement_rate': data.get('engagement_rate')
                }
            else:
                logger.error(f"❌ Channel analysis failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"❌ Competitor analysis error: {e}")
            return None

    def score_title(self, title, keyword, region='US'):
        """
        Score a video title for SEO and CTR potential.

        Args:
            title: Video title to score
            keyword: Target keyword
            region: Region code

        Returns:
            Score 0-100, plus improvement suggestions
        """
        try:
            payload = {
                'title': title,
                'keyword': keyword,
                'region': region
            }
            response = requests.post(
                f'{VIDIQ_API_BASE}/seo/score-title',
                headers=self.headers,
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                score = data.get('score', 0)
                logger.info(f"⭐ Title score: {score}/100")
                return {
                    'score': score,
                    'ctr_potential': data.get('ctr_potential'),
                    'keyword_match': data.get('keyword_match'),
                    'suggestions': data.get('suggestions', [])
                }
            else:
                logger.error(f"❌ Title scoring failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"❌ Title scoring error: {e}")
            return None

    def get_video_analytics(self, video_id):
        """
        Fetch detailed analytics for a published video.

        Args:
            video_id: YouTube video ID

        Returns:
            Dict with views, watch time, engagement, audience data
        """
        try:
            params = {'video_id': video_id}
            response = requests.get(
                f'{VIDIQ_API_BASE}/video/analytics',
                headers=self.headers,
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                logger.info(f"📊 Video analytics for {video_id}")
                return {
                    'video_id': video_id,
                    'views': data.get('views', 0),
                    'watch_time_hours': data.get('watch_time_hours', 0),
                    'average_view_duration': data.get('avg_view_duration', 0),  # Seconds
                    'click_through_rate': data.get('ctr', 0),  # %
                    'likes': data.get('likes', 0),
                    'comments': data.get('comments', 0),
                    'shares': data.get('shares', 0),
                    'audience_retention': data.get('retention_curve'),  # [0-100]
                    'traffic_sources': data.get('traffic_sources')  # Browse, search, etc
                }
            else:
                logger.error(f"❌ Analytics fetch failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"❌ Analytics error: {e}")
            return None

    def get_best_upload_time(self, channel_id):
        """
        Get optimal upload time based on channel's audience.

        Args:
            channel_id: YouTube channel ID

        Returns:
            Dict with day_of_week, hour (24h), expected_performance_boost
        """
        try:
            params = {'channel_id': channel_id}
            response = requests.get(
                f'{VIDIQ_API_BASE}/channel/best-upload-time',
                headers=self.headers,
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                logger.info(f"⏰ Best upload time: {data['day']} at {data['hour']}:00")
                return {
                    'day_of_week': data.get('day'),  # Monday, Tuesday, etc
                    'hour_utc': data.get('hour'),  # 0-23 in UTC
                    'expected_performance_boost': data.get('boost_percentage')  # %
                }
            else:
                logger.error(f"❌ Failed to get upload time: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"❌ Upload time error: {e}")
            return None

    def generate_seo_tags(self, title, keyword, limit=15):
        """
        Generate SEO-optimized tags for video.

        Args:
            title: Video title
            keyword: Main keyword
            limit: Max tags to generate

        Returns:
            List of suggested tags
        """
        try:
            payload = {
                'title': title,
                'keyword': keyword,
                'limit': limit
            }
            response = requests.post(
                f'{VIDIQ_API_BASE}/seo/generate-tags',
                headers=self.headers,
                json=payload
            )

            if response.status_code == 200:
                tags = response.json().get('tags', [])
                logger.info(f"🏷️  Generated {len(tags)} SEO tags")
                return tags
            else:
                logger.error(f"❌ Tag generation failed: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"❌ Tag generation error: {e}")
            return []
