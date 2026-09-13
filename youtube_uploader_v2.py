"""
YouTube Uploader v2 - Complete video upload pipeline with metadata integration.
Handles video files, metadata, thumbnails, and publishing options.
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from utils import setup_logger

logger = setup_logger("YouTubeUploader")


class YouTubeUploaderV2:
    """Upload videos to YouTube with complete metadata and thumbnail support."""

    # OAuth 2.0 scopes
    SCOPES = [
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube',
        'https://www.googleapis.com/auth/youtube.readonly'
    ]

    # Video categories
    CATEGORIES = {
        'Entertainment': 24,
        'Education': 27,
        'Science & Tech': 28,
        'People & Blogs': 15,
        'Howto & Style': 26,
        'News & Politics': 25,
        'Gaming': 20,
        'Music': 10,
        'Short Movies': 18,
        'Trailers': 44,
        'Movies': 1,
        'Shorts': 42
    }

    def __init__(self, secrets_file='youtube_client_secret.json', token_file='youtube_token.pickle'):
        """
        Initialize YouTube uploader with OAuth 2.0 authentication.

        Args:
            secrets_file: Path to OAuth 2.0 client secrets JSON
            token_file: Path to store/load credentials pickle
        """
        self.secrets_file = secrets_file
        self.token_file = token_file
        self.youtube = self._authenticate()
        logger.info(f"🎬 YouTube uploader initialized")

    def _authenticate(self):
        """Authenticate with YouTube API using OAuth 2.0."""
        credentials = None

        # Load existing credentials if available
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as f:
                credentials = pickle.load(f)

        # Refresh credentials if expired
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        elif not credentials or not credentials.valid:
            # Start OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(
                self.secrets_file, self.SCOPES)
            credentials = flow.run_local_server(port=0)

        # Save credentials for next time
        with open(self.token_file, 'wb') as f:
            pickle.dump(credentials, f)

        logger.info(f"✓ YouTube API authenticated")
        return build('youtube', 'v3', credentials=credentials)

    def upload_video(self, video_file, metadata_dict, thumbnail_file=None,
                    playlist_id=None, publish_at=None, visibility='private'):
        """
        Upload video with complete metadata package.

        Args:
            video_file: Path to MP4 video file
            metadata_dict: Dict with title, description, tags, category
            thumbnail_file: Path to thumbnail image (PNG/JPG)
            playlist_id: Optional playlist ID to add video to
            publish_at: ISO 8601 timestamp for scheduled publishing
            visibility: 'private', 'unlisted', or 'public'

        Returns:
            Dict with video_id and upload status
        """
        logger.info(f"📤 Uploading video: {metadata_dict.get('title', 'Unknown')}")

        if not os.path.exists(video_file):
            raise FileNotFoundError(f"Video file not found: {video_file}")

        try:
            # Prepare request body
            body = self._build_video_body(metadata_dict, visibility, publish_at)

            # Prepare media upload
            media_upload = MediaFileUpload(
                video_file,
                mimetype='video/mp4',
                resumable=True,
                chunksize=1024 * 1024  # 1MB chunks
            )

            # Execute upload
            logger.info(f"  Uploading file: {video_file}")
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media_upload
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    percent = int(status.progress() * 100)
                    logger.info(f"  Progress: {percent}%")

            video_id = response['id']
            logger.info(f"✓ Video uploaded successfully (ID: {video_id})")

            # Upload thumbnail if provided
            if thumbnail_file and os.path.exists(thumbnail_file):
                try:
                    self._set_custom_thumbnail(video_id, thumbnail_file)
                except Exception as e:
                    logger.warning(f"⚠️  Failed to set thumbnail: {e}")

            # Add to playlist if provided
            if playlist_id:
                try:
                    self._add_to_playlist(video_id, playlist_id)
                except Exception as e:
                    logger.warning(f"⚠️  Failed to add to playlist: {e}")

            result = {
                'video_id': video_id,
                'status': 'success',
                'title': metadata_dict.get('title'),
                'visibility': visibility,
                'scheduled': bool(publish_at)
            }

            return result

        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
            raise

    def _build_video_body(self, metadata_dict, visibility, publish_at):
        """Build request body for video insert."""
        title = metadata_dict.get('title', 'Untitled Video')[:100]
        description = metadata_dict.get('description', '')[:5000]
        tags = metadata_dict.get('tags', [])[:30]  # YouTube max 30 tags
        category = metadata_dict.get('category', 'Entertainment')
        category_id = self.CATEGORIES.get(category, 24)  # Default: Entertainment

        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': str(category_id),
                'defaultLanguage': 'en',
                'defaultAudioLanguage': 'en'
            },
            'status': {
                'privacyStatus': visibility,
                'selfDeclaredMadeForKids': False
            }
        }

        # Add scheduled publish time if provided
        if publish_at:
            body['status']['publishAt'] = publish_at
            body['status']['privacyStatus'] = 'private'  # Must be private for scheduling

        return body

    def _set_custom_thumbnail(self, video_id, thumbnail_file):
        """Set custom thumbnail for uploaded video."""
        logger.info(f"  Setting custom thumbnail...")

        media_upload = MediaFileUpload(
            thumbnail_file,
            mimetype='image/jpeg'
        )

        self.youtube.thumbnails().set(
            videoId=video_id,
            media_body=media_upload
        ).execute()

        logger.info(f"✓ Thumbnail set")

    def _add_to_playlist(self, video_id, playlist_id):
        """Add video to playlist."""
        logger.info(f"  Adding to playlist...")

        body = {
            'snippet': {
                'playlistId': playlist_id,
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

        logger.info(f"✓ Added to playlist")

    def get_channel_info(self):
        """Get authenticated channel information."""
        logger.info(f"📊 Fetching channel info...")

        try:
            request = self.youtube.channels().list(
                part='snippet,statistics',
                mine=True
            )
            response = request.execute()

            if response['items']:
                channel = response['items'][0]
                channel_info = {
                    'title': channel['snippet']['title'],
                    'channel_id': channel['id'],
                    'description': channel['snippet']['description'],
                    'subscribers': channel['statistics'].get('subscriberCount', 'private'),
                    'video_count': channel['statistics'].get('videoCount', 0),
                    'view_count': channel['statistics'].get('viewCount', 0)
                }
                logger.info(f"✓ Channel: {channel_info['title']}")
                return channel_info

        except Exception as e:
            logger.error(f"❌ Failed to get channel info: {e}")
            return None

    def create_playlist(self, title, description='', privacy_status='private'):
        """Create a new playlist."""
        logger.info(f"📋 Creating playlist: {title}")

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

            request = self.youtube.playlists().insert(
                part='snippet,status',
                body=body
            )
            response = request.execute()

            playlist_id = response['id']
            logger.info(f"✓ Playlist created (ID: {playlist_id})")
            return playlist_id

        except Exception as e:
            logger.error(f"❌ Failed to create playlist: {e}")
            raise

    def get_video_status(self, video_id):
        """Get status of uploaded video."""
        logger.info(f"🔍 Checking video status: {video_id}")

        try:
            request = self.youtube.videos().list(
                part='status,statistics',
                id=video_id
            )
            response = request.execute()

            if response['items']:
                video = response['items'][0]
                status_info = {
                    'video_id': video_id,
                    'privacy_status': video['status']['privacyStatus'],
                    'publish_at': video['status'].get('publishAt'),
                    'views': video['statistics'].get('viewCount', 0),
                    'likes': video['statistics'].get('likeCount', 0),
                    'comments': video['statistics'].get('commentCount', 0)
                }
                logger.info(f"✓ Status retrieved")
                return status_info

        except Exception as e:
            logger.error(f"❌ Failed to get status: {e}")
            return None

    def update_video_metadata(self, video_id, title=None, description=None,
                            tags=None, category=None):
        """Update metadata of existing video."""
        logger.info(f"✏️  Updating video metadata: {video_id}")

        try:
            # Get current metadata
            request = self.youtube.videos().list(
                part='snippet,status',
                id=video_id
            )
            response = request.execute()

            if not response['items']:
                raise ValueError(f"Video not found: {video_id}")

            video = response['items'][0]
            snippet = video['snippet']

            # Update fields if provided
            if title:
                snippet['title'] = title[:100]
            if description:
                snippet['description'] = description[:5000]
            if tags:
                snippet['tags'] = tags[:30]
            if category:
                snippet['categoryId'] = str(self.CATEGORIES.get(category, 24))

            # Update video
            body = {
                'id': video_id,
                'snippet': snippet,
                'status': video['status']
            }

            self.youtube.videos().update(
                part='snippet,status',
                body=body
            ).execute()

            logger.info(f"✓ Metadata updated")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update metadata: {e}")
            raise

    def delete_video(self, video_id):
        """Delete a video from YouTube."""
        logger.info(f"🗑️  Deleting video: {video_id}")

        try:
            self.youtube.videos().delete(id=video_id).execute()
            logger.info(f"✓ Video deleted")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to delete video: {e}")
            raise

    def print_upload_summary(self, upload_result):
        """Print formatted upload summary."""
        print("\n" + "=" * 70)
        print("UPLOAD SUMMARY")
        print("=" * 70)

        print(f"\n✅ Status: {upload_result.get('status', 'unknown').upper()}")
        print(f"📺 Video ID: {upload_result.get('video_id')}")
        print(f"📝 Title: {upload_result.get('title')}")
        print(f"🔒 Visibility: {upload_result.get('visibility')}")

        if upload_result.get('scheduled'):
            print(f"📅 Scheduled: Yes")

        print("\n" + "=" * 70 + "\n")
