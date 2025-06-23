#!/usr/bin/env python3
"""
YouTube Shorts Automation System
Automatically creates and uploads funny YouTube Shorts daily
"""

import os
import sys
import json
import logging
import schedule
import time
from datetime import datetime
from pathlib import Path

# Import our custom modules
from script_generator import ScriptGenerator
# Use lightweight video creator for cloud deployment
try:
    from video_creator import VideoCreator
except ImportError:
    from video_creator_lite import VideoCreatorLite as VideoCreator
from youtube_uploader import YouTubeUploader
from config import Config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class YouTubeShortsAutomation:
    def __init__(self):
        self.config = Config()
        self.script_gen = ScriptGenerator()
        self.video_creator = VideoCreator()
        self.uploader = YouTubeUploader()
        
        # Create necessary directories
        self.create_directories()
    
    def create_directories(self):
        """Create necessary directories for the automation"""
        directories = [
            'scripts',
            'videos',
            'audio',
            'images',
            'temp',
            'logs'
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def generate_content(self):
        """Generate script, video, and metadata for a YouTube Short"""
        try:
            logger.info("Starting content generation...")
            
            # Step 1: Generate funny script
            logger.info("Generating funny script...")
            script_data = self.script_gen.generate_funny_script()
            
            if not script_data:
                logger.error("Failed to generate script")
                return None
            
            # Step 2: Create video from script
            logger.info("Creating video from script...")
            video_path = self.video_creator.create_video(script_data)
            
            if not video_path:
                logger.error("Failed to create video")
                return None
            
            # Step 3: Generate title and tags
            logger.info("Generating title and tags...")
            title = self.generate_title(script_data)
            tags = self.generate_tags(script_data)
            description = self.generate_description(script_data)
            
            content_data = {
                'video_path': video_path,
                'title': title,
                'description': description,
                'tags': tags,
                'script': script_data,
                'created_at': datetime.now().isoformat()
            }
            
            # Save content metadata
            metadata_path = f"videos/{datetime.now().strftime('%Y%m%d_%H%M%S')}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(content_data, f, indent=2)
            
            logger.info(f"Content generated successfully: {video_path}")
            return content_data
            
        except Exception as e:
            logger.error(f"Error in content generation: {str(e)}")
            return None
    
    def upload_video(self, content_data):
        """Upload video to YouTube"""
        try:
            logger.info("Uploading video to YouTube...")
            
            upload_result = self.uploader.upload_video(
                video_path=content_data['video_path'],
                title=content_data['title'],
                description=content_data['description'],
                tags=content_data['tags']
            )
            
            if upload_result:
                logger.info(f"Video uploaded successfully: {upload_result}")
                return upload_result
            else:
                logger.error("Failed to upload video")
                return None
                
        except Exception as e:
            logger.error(f"Error uploading video: {str(e)}")
            return None
    
    def generate_title(self, script_data):
        """Generate an engaging title for the video"""
        base_titles = [
            "😂 This Will Make You LAUGH!",
            "🤣 Funniest Short You'll See Today!",
            "😂 You Won't Believe This!",
            "🤣 This Is TOO FUNNY!",
            "😂 Watch This & Try Not to Laugh!",
            "🤣 Hilarious Short Alert!",
            "😂 This Cracked Me Up!",
            "🤣 You NEED to See This!"
        ]
        
        import random
        return random.choice(base_titles)
    
    def generate_tags(self, script_data):
        """Generate relevant tags for the video"""
        base_tags = [
            "funny", "comedy", "humor", "shorts", "viral", "laugh", 
            "hilarious", "entertainment", "fun", "joke", "meme",
            "youtubeshorts", "short", "trending", "fyp", "foryou"
        ]
        
        # Add script-specific tags if available
        if 'topic' in script_data:
            base_tags.extend(script_data['topic'].lower().split())
        
        return base_tags[:15]  # YouTube allows max 15 tags
    
    def generate_description(self, script_data):
        """Generate video description"""
        description = f"""🤣 Hope this made you laugh! 

{script_data.get('script', 'Funny content ahead!')}

🔔 Subscribe for daily funny shorts!
👍 Like if this made you smile!
💬 Comment your favorite part!

#Shorts #Funny #Comedy #Viral #Entertainment
"""
        return description
    
    def daily_automation(self):
        """Main daily automation function"""
        try:
            logger.info("=== Starting Daily YouTube Shorts Automation ===")
            
            # Generate content
            content_data = self.generate_content()
            if not content_data:
                logger.error("Content generation failed - aborting automation")
                return False
            
            # Upload to YouTube
            upload_result = self.upload_video(content_data)
            if not upload_result:
                logger.error("Video upload failed")
                return False
            
            logger.info("=== Daily automation completed successfully! ===")
            return True
            
        except Exception as e:
            logger.error(f"Error in daily automation: {str(e)}")
            return False
    
    def start_scheduler(self):
        """Start the daily scheduler"""
        # Schedule daily upload at 10:00 AM
        schedule.every().day.at("10:00").do(self.daily_automation)
        
        logger.info("Scheduler started - Daily uploads at 10:00 AM")
        logger.info("Press Ctrl+C to stop the automation")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Automation stopped by user")

def main():
    """Main function"""
    automation = YouTubeShortsAutomation()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # Test mode - run once
        logger.info("Running in test mode...")
        automation.daily_automation()
    else:
        # Normal mode - start scheduler
        automation.start_scheduler()

if __name__ == "__main__":
    main()
