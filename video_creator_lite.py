"""
Lightweight Video Creator for Cloud Deployment
Creates simple text-based images instead of videos for cloud hosting
"""

import os
import logging
import random
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
import json

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available - using text-only mode")

logger = logging.getLogger(__name__)

class VideoCreatorLite:
    def __init__(self):
        self.output_dir = Path("videos")
        self.output_dir.mkdir(exist_ok=True)
        
        # Video settings for YouTube Shorts
        self.image_settings = {
            "size": (1080, 1920),  # 9:16 aspect ratio
            "background_colors": [
                (25, 25, 112),    # MidnightBlue
                (72, 61, 139),    # DarkSlateBlue
                (106, 90, 205),   # SlateBlue
                (30, 144, 255),   # DodgerBlue
                (0, 100, 0),      # DarkGreen
                (85, 107, 47),    # DarkOliveGreen
                (139, 69, 19),    # SaddleBrown
                (160, 82, 45),    # Sienna
            ]
        }
    
    def create_text_image(self, script_data: Dict) -> Optional[str]:
        """Create a text-based image instead of video for cloud deployment"""
        try:
            if not PIL_AVAILABLE:
                return self.create_text_file(script_data)
            
            # Create image
            width, height = self.image_settings["size"]
            background_color = random.choice(self.image_settings["background_colors"])
            
            # Create image with background
            img = Image.new('RGB', (width, height), color=background_color)
            draw = ImageDraw.Draw(img)
            
            # Try to load font
            try:
                font_size = 80
                font = ImageFont.truetype("arial.ttf", font_size)
                emoji_font = ImageFont.truetype("seguiemj.ttf", 150)
            except:
                try:
                    font = ImageFont.load_default()
                    emoji_font = font
                except:
                    # Fallback text creation
                    return self.create_text_file(script_data)
            
            # Get text content
            if script_data["type"] == "dad_joke" and "setup" in script_data:
                text_lines = [
                    script_data["setup"],
                    "",
                    script_data["punchline"],
                    "",
                    "😂"
                ]
            else:
                text_lines = [
                    script_data["script"],
                    "",
                    "🤣"
                ]
            
            # Calculate text positioning
            y_offset = height // 4
            line_height = 100
            
            for i, line in enumerate(text_lines):
                if not line:
                    continue
                
                # Use emoji font for emojis
                current_font = emoji_font if line in ["😂", "🤣", "😄", "😆"] else font
                
                # Calculate text size and position
                bbox = draw.textbbox((0, 0), line, font=current_font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (width - text_width) // 2
                y = y_offset + (i * line_height)
                
                # Draw text with outline
                outline_range = 3
                for adj_x in range(-outline_range, outline_range + 1):
                    for adj_y in range(-outline_range, outline_range + 1):
                        if adj_x != 0 or adj_y != 0:
                            draw.text((x + adj_x, y + adj_y), line, font=current_font, fill='black')
                
                # Draw main text
                draw.text((x, y), line, font=current_font, fill='white')
            
            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"short_{timestamp}.jpg"
            output_path = self.output_dir / output_filename
            
            img.save(output_path, "JPEG", quality=95)
            
            logger.info(f"Image created successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error creating image: {e}")
            return self.create_text_file(script_data)
    
    def create_text_file(self, script_data: Dict) -> Optional[str]:
        """Fallback: Create a text file with the joke content"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"short_{timestamp}.txt"
            output_path = self.output_dir / output_filename
            
            content = f"""YouTube Short Content
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Type: {script_data.get('type', 'unknown')}

Content:
{script_data.get('script', 'No content available')}

Duration: {script_data.get('duration', 'Unknown')} seconds
Topic: {script_data.get('topic', 'humor')}

Visual Cues:
{json.dumps(script_data.get('visual_cues', []), indent=2)}

Text Overlays:
{json.dumps(script_data.get('text_overlays', []), indent=2)}
"""
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Text content created: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error creating text file: {e}")
            return None
    
    def create_video(self, script_data: Dict) -> Optional[str]:
        """Main method - creates content based on available libraries"""
        try:
            logger.info("Creating content from script (cloud-optimized)...")
            
            # In cloud environment, create image or text content
            content_path = self.create_text_image(script_data)
            
            if not content_path:
                logger.error("Failed to create content")
                return None
            
            logger.info(f"Content created successfully: {content_path}")
            return content_path
            
        except Exception as e:
            logger.error(f"Error creating content: {e}")
            return None
    
    def create_thumbnail(self, script_data: Dict, content_path: str) -> Optional[str]:
        """Create a thumbnail - same as main content in lite version"""
        if content_path and content_path.endswith('.jpg'):
            return content_path
        
        # If content is text file, try to create a simple thumbnail
        try:
            if PIL_AVAILABLE:
                return self.create_text_image(script_data)
            else:
                logger.info("Thumbnail creation skipped - PIL not available")
                return None
        except Exception as e:
            logger.error(f"Error creating thumbnail: {e}")
            return None

# Test the lite video creator
if __name__ == "__main__":
    # Set up logging for testing
    logging.basicConfig(level=logging.INFO)
    
    # Test script data
    test_script = {
        "script": "Why don't scientists trust atoms? Because they make up everything!",
        "setup": "Why don't scientists trust atoms?",
        "punchline": "Because they make up everything!",
        "type": "dad_joke",
        "duration": 8,
        "topic": "science humor"
    }
    
    creator = VideoCreatorLite()
    content_path = creator.create_video(test_script)
    
    if content_path:
        print(f"Test content created: {content_path}")
    else:
        print("Failed to create test content")
