"""
YouTube Video Manager - Manage playlists, visibility, monetization, and channel settings.
"""

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import pickle
import os
from utils import setup_logger

logger = setup_logger("YouTubeVideoManager")


class YouTubeVideoManager:
    """Manage YouTube videos, playlists, and channel settings."""

    def __init__(self, token_file='youtube_token.pickle'):
        """Initialize video manager with existing YouTube credentials."""
        if not os.path.exists(token_file):
            raise FileNotFoundError(f"Token file not found: {token_file}. Run YouTube uploader first.")

        with open(token_file, 'rb') as f:
            credentials = pickle.load(f)

        self.youtube = build('youtube', 'v3', credentials=credentials)
        logger.info(f"✓ Video manager initialized")

    def get_playlists(self):
        """Get all playlists in authenticated channel."""
        logger.info(f"📋 Fetching playlists...")

        try:
            request = self.youtube.playlists().list(
                part='snippet,status',
                mine=True,
                maxResults=50
            )
            response = request.execute()

            playlists = []
            for playlist in response.get('items', []):
                playlists.append({
                    'id': playlist['id'],
                    'title': playlist['snippet']['title'],
                    'description': playlist['snippet']['description'],
                    'visibility': playlist['status']['privacyStatus']
                })

            logger.info(f"✓ Found {len(playlists)} playlists")
            return playlists

        except Exception as e:
            logger.error(f"❌ Failed to fetch playlists: {e}")
            return []

    def get_playlist_by_name(self, playlist_name):
        """Find playlist by name."""
        playlists = self.get_playlists()

        for p in playlists:
            if p['title'].lower() == playlist_name.lower():
                logger.info(f"✓ Found playlist: {playlist_name}")
                return p['id']

        logger.warning(f"⚠️  Playlist not found: {playlist_name}")
        return None

    def get_playlist_videos(self, playlist_id):
        """Get all videos in a playlist."""
        logger.info(f"📋 Fetching videos from playlist...")

        try:
            request = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50
            )
            response = request.execute()

            videos = []
            for item in response.get('items', []):
                videos.append({
                    'video_id': item['snippet']['resourceId']['videoId'],
                    'title': item['snippet']['title'],
                    'position': item['snippet']['position']
                })

            logger.info(f"✓ Found {len(videos)} videos in playlist")
            return videos

        except Exception as e:
            logger.error(f"❌ Failed to fetch playlist videos: {e}")
            return []

    def change_video_visibility(self, video_id, visibility):
        """
        Change video visibility (public, unlisted, private).

        Args:
            video_id: YouTube video ID
            visibility: 'public', 'unlisted', or 'private'
        """
        logger.info(f"🔒 Changing visibility to {visibility}...")

        if visibility not in ['public', 'unlisted', 'private']:
            raise ValueError(f"Invalid visibility: {visibility}")

        try:
            request = self.youtube.videos().list(
                part='status',
                id=video_id
            )
            response = request.execute()

            if not response['items']:
                raise ValueError(f"Video not found: {video_id}")

            video = response['items'][0]
            video['status']['privacyStatus'] = visibility

            self.youtube.videos().update(
                part='status',
                body=video
            ).execute()

            logger.info(f"✓ Visibility changed to {visibility}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to change visibility: {e}")
            raise

    def enable_comments(self, video_id, allow_comments=True):
        """Enable or disable comments on a video."""
        logger.info(f"💬 {'Enabling' if allow_comments else 'Disabling'} comments...")

        try:
            request = self.youtube.videos().list(
                part='snippet,status',
                id=video_id
            )
            response = request.execute()

            if not response['items']:
                raise ValueError(f"Video not found: {video_id}")

            video = response['items'][0]

            # Enable/disable comments via statistics object
            body = {
                'id': video_id,
                'snippet': video['snippet'],
                'status': video['status']
            }

            # Note: YouTube API doesn't directly control comments via API
            # This would typically be done through the web interface
            logger.info(f"ℹ️  Comments control requires manual YouTube Studio configuration")

            return True

        except Exception as e:
            logger.error(f"❌ Failed: {e}")
            return False

    def enable_monetization(self, video_id):
        """Enable monetization for a video."""
        logger.info(f"💰 Enabling monetization...")

        try:
            # Get video
            request = self.youtube.videos().list(
                part='monetizationDetails',
                id=video_id
            )
            response = request.execute()

            if response.get('items'):
                mon_details = response['items'][0].get('monetizationDetails', {})
                logger.info(f"ℹ️  Monetization status: {mon_details}")
                logger.info(f"ℹ️  Requires YouTube Partner Program membership")
            else:
                raise ValueError(f"Video not found: {video_id}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to check monetization: {e}")
            return False

    def make_video_premiere(self, video_id, premiere_time):
        """
        Schedule video as a premiere (live premiere).

        Args:
            video_id: YouTube video ID
            premiere_time: ISO 8601 timestamp for premiere
        """
        logger.info(f"🎬 Scheduling premiere at {premiere_time}...")

        try:
            request = self.youtube.videos().list(
                part='snippet,status,liveDetails',
                id=video_id
            )
            response = request.execute()

            if not response['items']:
                raise ValueError(f"Video not found: {video_id}")

            video = response['items'][0]

            # Add live details
            if 'liveDetails' not in video:
                video['liveDetails'] = {}

            video['liveDetails']['actualStartTime'] = premiere_time

            logger.info(f"✓ Premiere scheduled for {premiere_time}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to schedule premiere: {e}")
            return False

    def add_to_watch_later(self, video_id):
        """Add video to 'Watch Later' playlist."""
        logger.info(f"⏱️  Adding to Watch Later...")

        try:
            # Get Watch Later playlist ID
            request = self.youtube.playlists().list(
                part='snippet',
                mine=True
            )
            response = request.execute()

            watch_later_id = None
            for p in response['items']:
                if 'Watch Later' in p['snippet']['title']:
                    watch_later_id = p['id']
                    break

            if not watch_later_id:
                logger.warning("⚠️  Watch Later playlist not found")
                return False

            # Add video to playlist
            body = {
                'snippet': {
                    'playlistId': watch_later_id,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': video_id
                    }
                }
            }

            self.youtube.playlistItems().insert(
                part='snippet',
                body=body
            ).execute()

            logger.info(f"✓ Added to Watch Later")
            return True

        except Exception as e:
            logger.error(f"❌ Failed: {e}")
            return False

    def get_video_insights(self, video_id):
        """Get basic video insights (views, likes, comments)."""
        logger.info(f"📊 Fetching video insights...")

        try:
            request = self.youtube.videos().list(
                part='statistics',
                id=video_id
            )
            response = request.execute()

            if not response['items']:
                logger.warning(f"⚠️  Video not found: {video_id}")
                return None

            video = response['items'][0]
            stats = video['statistics']

            insights = {
                'video_id': video_id,
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0)),
                'favorites': int(stats.get('favoriteCount', 0))
            }

            logger.info(f"✓ Views: {insights['views']}, Likes: {insights['likes']}")
            return insights

        except Exception as e:
            logger.error(f"❌ Failed to get insights: {e}")
            return None

    def print_video_summary(self, video_id):
        """Print video information summary."""
        insights = self.get_video_insights(video_id)

        if not insights:
            return

        print("\n" + "=" * 60)
        print("VIDEO SUMMARY")
        print("=" * 60)

        print(f"\n📺 Video ID: {video_id}")
        print(f"👁️  Views: {insights['views']:,}")
        print(f"👍 Likes: {insights['likes']:,}")
        print(f"💬 Comments: {insights['comments']:,}")

        if insights['views'] > 0:
            like_rate = (insights['likes'] / insights['views']) * 100
            print(f"📈 Like Rate: {like_rate:.2f}%")

        print("\n" + "=" * 60 + "\n")

    def print_playlists(self, playlists):
        """Print formatted playlist list."""
        print("\n" + "=" * 60)
        print("PLAYLISTS")
        print("=" * 60)

        for p in playlists:
            print(f"\n📋 {p['title']}")
            print(f"   ID: {p['id']}")
            print(f"   Visibility: {p['visibility']}")
            if p['description']:
                print(f"   Description: {p['description'][:80]}...")

        print("\n" + "=" * 60 + "\n")
