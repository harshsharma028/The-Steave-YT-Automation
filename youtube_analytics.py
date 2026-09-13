"""
YouTube Analytics - Fetch and analyze video performance data.
Tracks views, engagement, watch time, and audience behavior.
"""

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import pickle
import os
from datetime import datetime, timedelta
from utils import setup_logger

logger = setup_logger("YouTubeAnalytics")


class YouTubeAnalytics:
    """Fetch and analyze video performance from YouTube."""

    def __init__(self, token_file='youtube_token.pickle'):
        """Initialize analytics engine with YouTube credentials."""
        if not os.path.exists(token_file):
            raise FileNotFoundError(f"Token file not found: {token_file}")

        with open(token_file, 'rb') as f:
            credentials = pickle.load(f)

        self.youtube = build('youtube', 'v3', credentials=credentials)
        logger.info(f"📊 YouTube analytics engine initialized")

    def get_channel_statistics(self, days_back=30):
        """
        Get overall channel statistics.

        Args:
            days_back: Look back this many days

        Returns:
            Dict with channel-level metrics
        """
        logger.info(f"📊 Fetching channel statistics (last {days_back} days)...")

        try:
            request = self.youtube.channels().list(
                part='statistics',
                mine=True
            )
            response = request.execute()

            if response['items']:
                stats = response['items'][0]['statistics']
                metrics = {
                    'total_videos': int(stats.get('videoCount', 0)),
                    'total_views': int(stats.get('viewCount', 0)),
                    'total_subscribers': stats.get('subscriberCount', 'private'),
                    'timestamp': datetime.utcnow().isoformat()
                }
                logger.info(f"✓ Channel stats: {metrics['total_videos']} videos, {metrics['total_views']:,} views")
                return metrics

        except Exception as e:
            logger.error(f"❌ Failed to fetch channel statistics: {e}")
            return None

    def get_video_metrics(self, video_id):
        """
        Get detailed metrics for a single video.

        Args:
            video_id: YouTube video ID

        Returns:
            Dict with video metrics (views, likes, comments, etc.)
        """
        logger.info(f"📊 Fetching metrics for video: {video_id}")

        try:
            request = self.youtube.videos().list(
                part='statistics,snippet',
                id=video_id
            )
            response = request.execute()

            if not response['items']:
                logger.warning(f"⚠️  Video not found: {video_id}")
                return None

            video = response['items'][0]
            stats = video['statistics']

            metrics = {
                'video_id': video_id,
                'title': video['snippet']['title'],
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0)),
                'favorites': int(stats.get('favoriteCount', 0)),
                'timestamp': datetime.utcnow().isoformat()
            }

            # Calculate engagement rate
            if metrics['views'] > 0:
                metrics['engagement_rate'] = round(
                    ((metrics['likes'] + metrics['comments']) / metrics['views']) * 100, 2
                )
                metrics['like_rate'] = round((metrics['likes'] / metrics['views']) * 100, 2)
            else:
                metrics['engagement_rate'] = 0
                metrics['like_rate'] = 0

            logger.info(f"✓ Views: {metrics['views']:,}, Engagement: {metrics['engagement_rate']}%")
            return metrics

        except Exception as e:
            logger.error(f"❌ Failed to get metrics: {e}")
            return None

    def get_latest_videos(self, limit=10):
        """
        Get latest uploaded videos and their metrics.

        Args:
            limit: Number of videos to fetch

        Returns:
            List of videos with metrics
        """
        logger.info(f"📺 Fetching latest {limit} videos...")

        try:
            request = self.youtube.search().list(
                part='snippet',
                forMine=True,
                type='video',
                order='date',
                maxResults=limit
            )
            response = request.execute()

            videos = []
            for item in response.get('items', []):
                video_id = item['snippet']['videoId']
                metrics = self.get_video_metrics(video_id)
                if metrics:
                    videos.append(metrics)

            logger.info(f"✓ Fetched metrics for {len(videos)} videos")
            return videos

        except Exception as e:
            logger.error(f"❌ Failed to get latest videos: {e}")
            return []

    def get_top_videos(self, limit=10, metric='views'):
        """
        Get top performing videos by metric.

        Args:
            limit: Number of videos to return
            metric: 'views', 'engagement_rate', or 'like_rate'

        Returns:
            Sorted list of videos
        """
        logger.info(f"🏆 Finding top {limit} videos by {metric}...")

        videos = self.get_latest_videos(limit=50)

        # Sort by metric
        if metric == 'views':
            sorted_videos = sorted(videos, key=lambda x: x.get('views', 0), reverse=True)
        elif metric == 'engagement_rate':
            sorted_videos = sorted(videos, key=lambda x: x.get('engagement_rate', 0), reverse=True)
        elif metric == 'like_rate':
            sorted_videos = sorted(videos, key=lambda x: x.get('like_rate', 0), reverse=True)
        else:
            sorted_videos = sorted(videos, key=lambda x: x.get('views', 0), reverse=True)

        logger.info(f"✓ Top video: {sorted_videos[0]['title'][:50]} ({sorted_videos[0].get('views', 0)} views)")
        return sorted_videos[:limit]

    def analyze_performance_trend(self, videos):
        """
        Analyze performance trends across videos.

        Args:
            videos: List of video metrics dicts

        Returns:
            Trend analysis dict
        """
        if not videos:
            return None

        logger.info(f"📈 Analyzing performance trends...")

        views = [v.get('views', 0) for v in videos]
        engagement = [v.get('engagement_rate', 0) for v in videos]

        analysis = {
            'total_videos': len(videos),
            'total_views': sum(views),
            'avg_views_per_video': round(sum(views) / len(views), 0) if views else 0,
            'max_views': max(views) if views else 0,
            'min_views': min(views) if views else 0,
            'avg_engagement_rate': round(sum(engagement) / len(engagement), 2) if engagement else 0,
            'total_likes': sum(v.get('likes', 0) for v in videos),
            'total_comments': sum(v.get('comments', 0) for v in videos),
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info(f"✓ Avg views per video: {analysis['avg_views_per_video']:,.0f}")
        logger.info(f"✓ Avg engagement: {analysis['avg_engagement_rate']}%")
        return analysis

    def identify_successful_patterns(self, videos):
        """
        Identify patterns in successful videos.

        Args:
            videos: List of video metrics dicts

        Returns:
            Dict of identified patterns
        """
        logger.info(f"🔍 Identifying successful patterns...")

        if not videos or len(videos) < 3:
            logger.warning("⚠️  Not enough videos to analyze patterns")
            return None

        # Find top 3 videos
        top_videos = sorted(videos, key=lambda x: x.get('views', 0), reverse=True)[:3]
        bottom_videos = sorted(videos, key=lambda x: x.get('views', 0))[:3]

        patterns = {
            'top_videos': top_videos,
            'bottom_videos': bottom_videos,
            'top_avg_views': round(sum(v.get('views', 0) for v in top_videos) / 3, 0),
            'bottom_avg_views': round(sum(v.get('views', 0) for v in bottom_videos) / 3, 0),
            'insights': []
        }

        # Analyze engagement differences
        top_engagement = sum(v.get('engagement_rate', 0) for v in top_videos) / 3
        bottom_engagement = sum(v.get('engagement_rate', 0) for v in bottom_videos) / 3

        if top_engagement > bottom_engagement:
            patterns['insights'].append(
                f"Top videos have {top_engagement:.1f}% engagement vs {bottom_engagement:.1f}% for low performers"
            )

        logger.info(f"✓ Identified patterns in top vs bottom performers")
        return patterns

    def calculate_growth_metrics(self, videos, days=7):
        """
        Calculate growth metrics over time period.

        Args:
            videos: List of video metrics
            days: Period to analyze

        Returns:
            Growth metrics dict
        """
        logger.info(f"📈 Calculating growth metrics...")

        if not videos:
            return None

        total_views = sum(v.get('views', 0) for v in videos)
        avg_views_per_day = total_views / max(days, 1)

        growth = {
            'period_days': days,
            'total_views': total_views,
            'avg_views_per_day': round(avg_views_per_day, 0),
            'videos_analyzed': len(videos),
            'total_likes': sum(v.get('likes', 0) for v in videos),
            'total_comments': sum(v.get('comments', 0) for v in videos),
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info(f"✓ {growth['avg_views_per_day']:.0f} views/day average")
        return growth

    def print_analytics_report(self, videos, analysis=None):
        """Print formatted analytics report."""
        print("\n" + "=" * 70)
        print("VIDEO ANALYTICS REPORT")
        print("=" * 70)

        print(f"\n📊 Videos Analyzed: {len(videos)}")

        if analysis:
            print(f"\n📈 Overall Metrics:")
            print(f"   Total Views: {analysis.get('total_views', 0):,}")
            print(f"   Avg Views/Video: {analysis.get('avg_views_per_video', 0):,.0f}")
            print(f"   Avg Engagement: {analysis.get('avg_engagement_rate', 0)}%")
            print(f"   Total Likes: {analysis.get('total_likes', 0):,}")
            print(f"   Total Comments: {analysis.get('total_comments', 0):,}")

        print(f"\n🏆 Top Videos:")
        for i, video in enumerate(videos[:5], 1):
            print(f"   {i}. {video['title'][:50]}")
            print(f"      Views: {video.get('views', 0):,} | Engagement: {video.get('engagement_rate', 0)}%")

        print("\n" + "=" * 70 + "\n")

    def export_analytics(self, videos, analysis, output_file='analytics.json'):
        """Export analytics to JSON."""
        import json

        export_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'videos': videos,
            'analysis': analysis,
            'total_videos': len(videos)
        }

        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"✓ Analytics exported to {output_file}")
        return output_file
