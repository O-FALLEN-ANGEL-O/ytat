"""
YouTube Uploader Module
Handles automatic uploading of videos to YouTube using the YouTube Data API
"""

import os
import json
import logging
import pickle
from datetime import datetime
from typing import Dict, List, Optional

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
except ImportError as e:
    print(f"Missing required libraries: {e}")
    print("Please install: pip install google-auth google-auth-oauthlib google-api-python-client")

logger = logging.getLogger(__name__)

class YouTubeUploader:
    def __init__(self):
        # YouTube API scopes
        self.SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
        
        # API service name and version
        self.API_SERVICE_NAME = 'youtube'
        self.API_VERSION = 'v3'
        
        # Credentials file paths
        self.CLIENT_SECRETS_FILE = 'client_secrets.json'
        self.CREDENTIALS_FILE = 'youtube_credentials.pkl'
        
        # Initialize YouTube service
        self.youtube = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with YouTube API"""
        try:
            credentials = None
            
            # Load existing credentials
            if os.path.exists(self.CREDENTIALS_FILE):
                with open(self.CREDENTIALS_FILE, 'rb') as token:
                    credentials = pickle.load(token)
            
            # If there are no valid credentials, get new ones
            if not credentials or not credentials.valid:
                if credentials and credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())
                else:
                    if not os.path.exists(self.CLIENT_SECRETS_FILE):
                        logger.error(f"Client secrets file not found: {self.CLIENT_SECRETS_FILE}")
                        logger.info("Please download client_secrets.json from Google Cloud Console")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.CLIENT_SECRETS_FILE, self.SCOPES)
                    credentials = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(self.CREDENTIALS_FILE, 'wb') as token:
                    pickle.dump(credentials, token)
            
            # Build YouTube service
            self.youtube = build(
                self.API_SERVICE_NAME, 
                self.API_VERSION, 
                credentials=credentials
            )
            
            logger.info("Successfully authenticated with YouTube API")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def upload_video(self, video_path: str, title: str, description: str, 
                    tags: List[str], category_id: str = "23") -> Optional[str]:
        """Upload a video to YouTube"""
        try:
            if not self.youtube:
                logger.error("YouTube service not authenticated")
                return None
            
            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return None
            
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'categoryId': category_id,
                    'defaultLanguage': 'en',
                    'defaultAudioLanguage': 'en'
                },
                'status': {
                    'privacyStatus': 'public',  # Can be 'private', 'unlisted', or 'public'
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Create media upload object
            media = MediaFileUpload(
                video_path,
                chunksize=-1,  # Upload in single chunk
                resumable=True,
                mimetype='video/*'
            )
            
            # Execute upload request
            logger.info(f"Starting upload for: {title}")
            
            insert_request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            video_id = self._resumable_upload(insert_request)
            
            if video_id:
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                logger.info(f"Video uploaded successfully: {video_url}")
                
                # Save upload metadata
                self._save_upload_metadata(video_id, video_path, title, description, tags)
                
                return video_id
            else:
                logger.error("Video upload failed")
                return None
                
        except HttpError as e:
            logger.error(f"HTTP error during upload: {e}")
            return None
        except Exception as e:
            logger.error(f"Error uploading video: {e}")
            return None
    
    def _resumable_upload(self, insert_request):
        """Handle resumable upload with retry logic"""
        response = None
        error = None
        retry = 0
        
        while response is None:
            try:
                status, response = insert_request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        return response['id']
                    else:
                        logger.error(f"Upload failed with unexpected response: {response}")
                        return None
            except HttpError as e:
                if e.resp.status in [500, 502, 503, 504]:
                    # Retriable error
                    error = f"A retriable HTTP error {e.resp.status} occurred: {e.content}"
                    logger.warning(error)
                else:
                    # Non-retriable error
                    logger.error(f"A non-retriable HTTP error occurred: {e}")
                    return None
            except Exception as e:
                error = f"An error occurred: {e}"
                logger.error(error)
                return None
            
            if error is not None:
                retry += 1
                if retry > 3:
                    logger.error("Maximum retries exceeded")
                    return None
                
                logger.info(f"Retrying upload (attempt {retry})...")
                import time
                time.sleep(2 ** retry)  # Exponential backoff
    
    def _save_upload_metadata(self, video_id: str, video_path: str, title: str, 
                             description: str, tags: List[str]):
        """Save upload metadata for tracking"""
        try:
            metadata = {
                'video_id': video_id,
                'video_path': video_path,
                'title': title,
                'description': description,
                'tags': tags,
                'upload_time': datetime.now().isoformat(),
                'url': f"https://www.youtube.com/watch?v={video_id}"
            }
            
            # Save to uploads log
            uploads_log_path = 'uploads_log.json'
            
            if os.path.exists(uploads_log_path):
                with open(uploads_log_path, 'r') as f:
                    uploads = json.load(f)
            else:
                uploads = []
            
            uploads.append(metadata)
            
            with open(uploads_log_path, 'w') as f:
                json.dump(uploads, f, indent=2)
            
            logger.info(f"Upload metadata saved to {uploads_log_path}")
            
        except Exception as e:
            logger.error(f"Failed to save upload metadata: {e}")
    
    def set_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """Set a custom thumbnail for the video"""
        try:
            if not self.youtube:
                logger.error("YouTube service not authenticated")
                return False
            
            if not os.path.exists(thumbnail_path):
                logger.error(f"Thumbnail file not found: {thumbnail_path}")
                return False
            
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            
            logger.info(f"Thumbnail set successfully for video {video_id}")
            return True
            
        except HttpError as e:
            logger.error(f"HTTP error setting thumbnail: {e}")
            return False
        except Exception as e:
            logger.error(f"Error setting thumbnail: {e}")
            return False
    
    def update_video_metadata(self, video_id: str, title: str = None, 
                             description: str = None, tags: List[str] = None) -> bool:
        """Update video metadata after upload"""
        try:
            if not self.youtube:
                logger.error("YouTube service not authenticated")
                return False
            
            # Get current video metadata
            video_response = self.youtube.videos().list(
                part='snippet',
                id=video_id
            ).execute()
            
            if not video_response['items']:
                logger.error(f"Video {video_id} not found")
                return False
            
            current_snippet = video_response['items'][0]['snippet']
            
            # Update only provided fields
            if title:
                current_snippet['title'] = title
            if description:
                current_snippet['description'] = description
            if tags:
                current_snippet['tags'] = tags
            
            # Update video
            self.youtube.videos().update(
                part='snippet',
                body={
                    'id': video_id,
                    'snippet': current_snippet
                }
            ).execute()
            
            logger.info(f"Video metadata updated for {video_id}")
            return True
            
        except HttpError as e:
            logger.error(f"HTTP error updating video: {e}")
            return False
        except Exception as e:
            logger.error(f"Error updating video: {e}")
            return False
    
    def get_upload_status(self, video_id: str) -> Optional[Dict]:
        """Get the processing status of an uploaded video"""
        try:
            if not self.youtube:
                logger.error("YouTube service not authenticated")
                return None
            
            response = self.youtube.videos().list(
                part='status,processingDetails',
                id=video_id
            ).execute()
            
            if response['items']:
                return response['items'][0]
            else:
                logger.error(f"Video {video_id} not found")
                return None
                
        except HttpError as e:
            logger.error(f"HTTP error getting video status: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting video status: {e}")
            return None
    
    def list_recent_uploads(self, max_results: int = 10) -> List[Dict]:
        """List recent uploads from the channel"""
        try:
            if not self.youtube:
                logger.error("YouTube service not authenticated")
                return []
            
            # Get channel's uploads playlist
            channels_response = self.youtube.channels().list(
                part='contentDetails',
                mine=True
            ).execute()
            
            if not channels_response['items']:
                logger.error("No channel found")
                return []
            
            uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from uploads playlist
            playlist_response = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=max_results
            ).execute()
            
            return playlist_response['items']
            
        except HttpError as e:
            logger.error(f"HTTP error listing uploads: {e}")
            return []
        except Exception as e:
            logger.error(f"Error listing uploads: {e}")
            return []

def setup_youtube_api():
    """Helper function to set up YouTube API credentials"""
    print("YouTube API Setup Instructions:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a new project or select existing one")
    print("3. Enable YouTube Data API v3")
    print("4. Create OAuth 2.0 credentials")
    print("5. Download client_secrets.json and place it in this directory")
    print("6. Make sure your OAuth consent screen is configured")
    
    client_secrets_template = {
        "installed": {
            "client_id": "YOUR_CLIENT_ID.googleusercontent.com",
            "project_id": "your-project-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "YOUR_CLIENT_SECRET",
            "redirect_uris": ["http://localhost"]
        }
    }
    
    if not os.path.exists('client_secrets.json'):
        with open('client_secrets_template.json', 'w') as f:
            json.dump(client_secrets_template, f, indent=2)
        print("Created client_secrets_template.json - fill in your credentials and rename to client_secrets.json")

# Test the uploader
if __name__ == "__main__":
    # Set up logging for testing
    logging.basicConfig(level=logging.INFO)
    
    # Check if credentials exist
    if not os.path.exists('client_secrets.json'):
        setup_youtube_api()
    else:
        uploader = YouTubeUploader()
        if uploader.youtube:
            print("YouTube API authentication successful!")
            
            # List recent uploads as a test
            recent_uploads = uploader.list_recent_uploads(5)
            print(f"Found {len(recent_uploads)} recent uploads")
        else:
            print("YouTube API authentication failed!")
