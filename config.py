"""
Configuration Module
Contains all configuration settings for the YouTube Shorts automation system
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

class Config:
    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file
        self.settings = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        default_config = {
            # General settings
            "automation": {
                "daily_upload_time": "10:00",  # 24-hour format
                "max_video_duration": 60,  # seconds
                "upload_privacy": "public",  # public, unlisted, private
                "auto_set_thumbnail": True,
                "enable_scheduling": True
            },
            
            # Script generation settings
            "script_generation": {
                "joke_apis": [
                    "https://official-joke-api.appspot.com/random_joke",
                    "https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,religious,political,racist,sexist,explicit&type=single",
                    "https://icanhazdadjoke.com/"
                ],
                "fallback_to_local": True,
                "min_script_length": 10,
                "max_script_length": 200,
                "preferred_joke_types": ["dad_joke", "one_liner", "pun"]
            },
            
            # Video creation settings
            "video_creation": {
                "resolution": {
                    "width": 1080,
                    "height": 1920  # 9:16 aspect ratio for Shorts
                },
                "fps": 30,
                "background_type": "animated",  # solid, animated, gradient
                "text_style": {
                    "font": "Arial-Bold",
                    "font_size": 80,
                    "color": "white",
                    "stroke_color": "black",
                    "stroke_width": 3
                },
                "emoji_settings": {
                    "enabled": True,
                    "size": 150,
                    "animation": True
                },
                "background_colors": [
                    [25, 25, 112],    # MidnightBlue
                    [72, 61, 139],    # DarkSlateBlue
                    [106, 90, 205],   # SlateBlue
                    [30, 144, 255],   # DodgerBlue
                    [0, 100, 0],      # DarkGreen
                    [85, 107, 47],    # DarkOliveGreen
                    [139, 69, 19],    # SaddleBrown
                    [160, 82, 45]     # Sienna
                ]
            },
            
            # YouTube upload settings
            "youtube": {
                "default_category": "23",  # Comedy category
                "default_language": "en",
                "made_for_kids": False,
                "enable_comments": True,
                "enable_ratings": True,
                "default_tags": [
                    "funny", "comedy", "humor", "shorts", "viral", 
                    "laugh", "hilarious", "entertainment", "fun", 
                    "joke", "meme", "youtubeshorts", "short", 
                    "trending", "fyp", "foryou"
                ],
                "title_templates": [
                    "😂 This Will Make You LAUGH!",
                    "🤣 Funniest Short You'll See Today!",
                    "😂 You Won't Believe This!",
                    "🤣 This Is TOO FUNNY!",
                    "😂 Watch This & Try Not to Laugh!",
                    "🤣 Hilarious Short Alert!",
                    "😂 This Cracked Me Up!",
                    "🤣 You NEED to See This!"
                ],
                "description_template": """🤣 Hope this made you laugh! 

{script_content}

🔔 Subscribe for daily funny shorts!
👍 Like if this made you smile!
💬 Comment your favorite part!

#Shorts #Funny #Comedy #Viral #Entertainment"""
            },
            
            # Directories
            "directories": {
                "scripts": "scripts",
                "videos": "videos",
                "audio": "audio",
                "images": "images",
                "temp": "temp",
                "logs": "logs",
                "assets": "assets"
            },
            
            # Logging settings
            "logging": {
                "level": "INFO",
                "file": "automation.log",
                "max_file_size": "10MB",
                "backup_count": 5
            },
            
            # API settings
            "apis": {
                "timeout": 10,
                "retry_attempts": 3,
                "retry_delay": 2
            },
            
            # Advanced settings
            "advanced": {
                "cleanup_temp_files": True,
                "save_metadata": True,
                "create_thumbnails": True,
                "backup_videos": False,
                "analytics_tracking": True
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                # Merge with defaults (in case new settings are added)
                return self._merge_configs(default_config, loaded_config)
            except Exception as e:
                print(f"Error loading config file: {e}")
                print("Using default configuration")
                return default_config
        else:
            # Create default config file
            self.save_config(default_config)
            return default_config
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Recursively merge loaded config with defaults"""
        for key, value in loaded.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    default[key] = self._merge_configs(default[key], value)
                else:
                    default[key] = value
            else:
                default[key] = value
        return default
    
    def save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file"""
        if config is None:
            config = self.settings
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key_path: str, default=None):
        """Get a configuration value using dot notation (e.g., 'video_creation.fps')"""
        keys = key_path.split('.')
        value = self.settings
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value):
        """Set a configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.settings
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
        self.save_config()
    
    def create_directories(self):
        """Create all required directories"""
        directories = self.get('directories', {})
        
        for dir_name, dir_path in directories.items():
            Path(dir_path).mkdir(exist_ok=True)
            print(f"Created directory: {dir_path}")
    
    def get_upload_schedule(self) -> str:
        """Get the upload schedule time"""
        return self.get('automation.daily_upload_time', '10:00')
    
    def get_video_settings(self) -> Dict:
        """Get video creation settings"""
        return self.get('video_creation', {})
    
    def get_youtube_settings(self) -> Dict:
        """Get YouTube upload settings"""
        return self.get('youtube', {})
    
    def get_script_settings(self) -> Dict:
        """Get script generation settings"""
        return self.get('script_generation', {})
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled"""
        feature_map = {
            'scheduling': 'automation.enable_scheduling',
            'thumbnails': 'automation.auto_set_thumbnail',
            'emoji': 'video_creation.emoji_settings.enabled',
            'cleanup': 'advanced.cleanup_temp_files',
            'metadata': 'advanced.save_metadata',
            'analytics': 'advanced.analytics_tracking'
        }
        
        if feature in feature_map:
            return self.get(feature_map[feature], True)
        
        return False
    
    def validate_config(self) -> bool:
        """Validate configuration settings"""
        errors = []
        
        # Check required settings
        required_paths = [
            'automation.daily_upload_time',
            'video_creation.resolution.width',
            'video_creation.resolution.height',
            'youtube.default_category'
        ]
        
        for path in required_paths:
            if self.get(path) is None:
                errors.append(f"Missing required setting: {path}")
        
        # Validate upload time format
        upload_time = self.get('automation.daily_upload_time')
        if upload_time:
            try:
                hours, minutes = upload_time.split(':')
                if not (0 <= int(hours) <= 23 and 0 <= int(minutes) <= 59):
                    errors.append("Invalid upload time format. Use HH:MM (24-hour)")
            except:
                errors.append("Invalid upload time format. Use HH:MM")
        
        # Validate video resolution
        width = self.get('video_creation.resolution.width', 0)
        height = self.get('video_creation.resolution.height', 0)
        if width <= 0 or height <= 0:
            errors.append("Invalid video resolution")
        
        # Print errors
        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        print("Configuration validation passed")
        return True

# Test configuration
if __name__ == "__main__":
    config = Config()
    
    print("Configuration loaded successfully!")
    print(f"Upload time: {config.get_upload_schedule()}")
    print(f"Video resolution: {config.get('video_creation.resolution.width')}x{config.get('video_creation.resolution.height')}")
    print(f"Default tags: {config.get('youtube.default_tags')[:5]}...")
    
    # Validate configuration
    config.validate_config()
    
    # Create directories
    config.create_directories()
