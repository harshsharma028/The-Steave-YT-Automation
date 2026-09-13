"""
YouTube Video Uploader - Handles OAuth, uploads, and metadata management.
"""

import os
import pickle
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request
from utils import setup_logger

logger = setup_logger("YouTubeUploader")

# OAuth scopes required for YouTube API
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CREDENTIALS_FILE = 'youtube_credentials.json'
TOKEN_FILE = 'youtube_token.pickle'


class YouTubeUploader:
    """Handle YouTube authentication and video uploads."""

    def __init__(self, client_secrets_file='youtube_client_secret.json'):
        """
        Initialize YouTube uploader with OAuth credentials.

        Args:
            client_secrets_file: Path to OAuth 2.0 client secrets JSON
        """
        self.client_secrets_file = client_secrets_file
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with YouTube API using OAuth 2.0."""
        credentials = None

        # Load cached token if exists
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                credentials = pickle.load(token)
                logger.info("✓ Loaded cached YouTube credentials")

        # Refresh or create new credentials
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            logger.info("✓ Refreshed YouTube token")
        elif not credentials or not credentials.valid:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                self.client_secrets_file, SCOPES)
            credentials = flow.run_local_server(port=0)
            logger.info("✓ New YouTube OAuth flow completed")

        # Save token for future use
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(credentials, token)

        # Build YouTube service
        self.service = googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)
        logger.info("✓ YouTube API service initialized")

    def upload_video(self, video_file, title, description, tags=None, category_id='24',
                     privacy_status='private', thumbnail_file=None, playlist_id=None):
        """
        Upload video to YouTube.

        Args:
            video_file: Path to video file (MP4 recommended)
            title: Video title
            description: Video description
            tags: List of tags/keywords
            category_id: YouTube category ID (default: 24 = Entertainment)
            privacy_status: 'public', 'unlisted', or 'private'
            thumbnail_file: Path to thumbnail image (JPG/PNG)
            playlist_id: Add to playlist after upload

        Returns:
            Video ID if successful, None otherwise
        """
        if not os.path.exists(video_file):
            logger.error(f"❌ Video file not found: {video_file}")
            return None

        try:
            logger.info(f"📤 Uploading: {title}")

            # Prepare request body
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': category_id,
                    'defaultLanguage': 'en',
                    'defaultAudioLanguage': 'en'
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'madeForKids': False,
                    'selfDeclaredMadeForKids': False
                }
            }

            # Upload video
            request = self.service.videos().insert(
                part='snippet,status',
                body=body,
                media_body=googleapiclient.http.MediaFileUpload(video_file, chunksize=-1, resumable=True)
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.info(f"  Upload progress: {progress}%")

            video_id = response['id']
            logger.info(f"✓ Video uploaded successfully. ID: {video_id}")

            # Upload custom thumbnail if provided
            if thumbnail_file and os.path.exists(thumbnail_file):
                self._set_custom_thumbnail(video_id, thumbnail_file)

            # Add to playlist if specified
            if playlist_id:
                self._add_to_playlist(video_id, playlist_id)

            return video_id

        except googleapiclient.errors.HttpError as e:
            logger.error(f"❌ Upload failed: {e}")
            return None

    def _set_custom_thumbnail(self, video_id, thumbnail_file):
        """Set custom thumbnail for video."""
        try:
            request = self.service.thumbnails().set(
                videoId=video_id,
                media_body=googleapiclient.http.MediaFileUpload(thumbnail_file)
            )
            request.execute()
            logger.info(f"✓ Custom thumbnail set for {video_id}")
        except googleapiclient.errors.HttpError as e:
            logger.warning(f"⚠ Failed to set thumbnail: {e}")

    def _add_to_playlist(self, video_id, playlist_id):
        """Add video to playlist."""
        try:
            body = {
                'snippet': {
                    'playlistId': playlist_id,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': video_id
                    }
                }
            }
            request = self.service.playlistItems().insert(part='snippet', body=body)
            request.execute()
            logger.info(f"✓ Video added to playlist {playlist_id}")
        except googleapiclient.errors.HttpError as e:
            logger.warning(f"⚠ Failed to add to playlist: {e}")

    def get_channel_info(self):
        """Get authenticated user's channel info."""
        try:
            request = self.service.channels().list(part='snippet,statistics', mine=True)
            response = request.execute()

            if response['items']:
                channel = response['items'][0]
                info = {
                    'channel_id': channel['id'],
                    'title': channel['snippet']['title'],
                    'subscribers': channel['statistics'].get('subscriberCount', 'hidden'),
                    'video_count': channel['statistics'].get('videoCount', 0),
                    'view_count': channel['statistics'].get('viewCount', 0)
                }
                logger.info(f"✓ Channel: {info['title']}")
                return info
        except googleapiclient.errors.HttpError as e:
            logger.error(f"❌ Failed to fetch channel info: {e}")
        return None

    def create_playlist(self, title, description='', privacy_status='private'):
        """Create new playlist on channel."""
        try:
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'defaultLanguage': 'en'
                },
                'status': {
                    'privacyStatus': privacy_status
                }
            }
            request = self.service.playlists().insert(part='snippet,status', body=body)
            response = request.execute()
            playlist_id = response['id']
            logger.info(f"✓ Playlist created: {playlist_id}")
            return playlist_id
        except googleapiclient.errors.HttpError as e:
            logger.error(f"❌ Failed to create playlist: {e}")
            return None

    def schedule_video(self, video_id, publish_time):
        """
        Schedule video for future publication.

        Args:
            video_id: YouTube video ID
            publish_time: ISO 8601 format timestamp (e.g., "2025-09-20T18:00:00Z")
        """
        try:
            body = {
                'status': {
                    'privacyStatus': 'private',
                    'publishAt': publish_time
                }
            }
            request = self.service.videos().update(part='status', body={'id': video_id, **body})
            request.execute()
            logger.info(f"✓ Video {video_id} scheduled for {publish_time}")
        except googleapiclient.errors.HttpError as e:
            logger.error(f"❌ Failed to schedule video: {e}")
