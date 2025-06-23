"""
Video Creator Module
Creates YouTube Shorts videos from scripts using moviepy and other libraries
"""

import os
import logging
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

try:
    from moviepy.editor import (
        VideoFileClip, TextClip, CompositeVideoClip, 
        AudioFileClip, ColorClip, ImageClip, concatenate_videoclips
    )
    from moviepy.video.tools.subtitles import SubtitlesClip
    from moviepy.video.fx import resize, fadein, fadeout
    from moviepy.audio.fx import volumex
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    import requests
    import io
except ImportError as e:
    print(f"Missing required libraries: {e}")
    print("Please install: pip install moviepy pillow requests numpy")

logger = logging.getLogger(__name__)

class VideoCreator:
    def __init__(self):
        self.output_dir = Path("videos")
        self.temp_dir = Path("temp")
        self.assets_dir = Path("assets")
        
        # Create directories
        for directory in [self.output_dir, self.temp_dir, self.assets_dir]:
            directory.mkdir(exist_ok=True)
        
        # Video settings for YouTube Shorts
        self.video_settings = {
            "size": (1080, 1920),  # 9:16 aspect ratio
            "fps": 30,
            "duration": 60,  # Max duration for Shorts
            "background_color": (0, 0, 0)  # Black background
        }
        
        # Text settings
        self.text_settings = {
            "font": "Arial-Bold",
            "fontsize": 80,
            "color": "white",
            "stroke_color": "black",
            "stroke_width": 3,
            "method": "caption"
        }
        
        # Background colors for variety
        self.background_colors = [
            (25, 25, 112),    # MidnightBlue
            (72, 61, 139),    # DarkSlateBlue
            (106, 90, 205),   # SlateBlue
            (30, 144, 255),   # DodgerBlue
            (0, 100, 0),      # DarkGreen
            (85, 107, 47),    # DarkOliveGreen
            (139, 69, 19),    # SaddleBrown
            (160, 82, 45),    # Sienna
        ]
    
    def create_background_video(self, duration: float, color: Tuple[int, int, int] = None) -> VideoFileClip:
        """Create a solid color background video"""
        if color is None:
            color = random.choice(self.background_colors)
        
        # Create a color clip
        background = ColorClip(
            size=self.video_settings["size"],
            color=color,
            duration=duration
        )
        
        return background
    
    def create_animated_background(self, duration: float) -> VideoFileClip:
        """Create an animated gradient background"""
        try:
            # Create a simple animated background with moving gradient
            def make_frame(t):
                # Create a gradient that changes over time
                w, h = self.video_settings["size"]
                gradient = np.zeros((h, w, 3), dtype=np.uint8)
                
                # Animated gradient
                for i in range(h):
                    r = int(50 + 50 * np.sin(2 * np.pi * t / 4 + i / h))
                    g = int(50 + 50 * np.cos(2 * np.pi * t / 6 + i / h))
                    b = int(100 + 50 * np.sin(2 * np.pi * t / 8 + i / h))
                    gradient[i, :] = [r, g, b]
                
                return gradient
            
            background = VideoFileClip(make_frame, duration=duration)
            return background
        except Exception as e:
            logger.warning(f"Failed to create animated background: {e}")
            return self.create_background_video(duration)
    
    def create_text_clip(self, text: str, start_time: float, end_time: float, 
                        position: str = "center", fontsize: int = None) -> TextClip:
        """Create a text clip with styling"""
        if fontsize is None:
            fontsize = self.text_settings["fontsize"]
        
        # Adjust font size for long text
        if len(text) > 50:
            fontsize = max(40, fontsize - 10)
        elif len(text) > 100:
            fontsize = max(30, fontsize - 20)
        
        try:
            text_clip = TextClip(
                text,
                fontsize=fontsize,
                color=self.text_settings["color"],
                font=self.text_settings["font"],
                stroke_color=self.text_settings["stroke_color"],
                stroke_width=self.text_settings["stroke_width"],
                method=self.text_settings["method"]
            ).set_position(position).set_start(start_time).set_end(end_time)
            
            # Add fade in/out effects
            text_clip = text_clip.crossfadein(0.3).crossfadeout(0.3)
            
            return text_clip
        except Exception as e:
            logger.error(f"Failed to create text clip: {e}")
            # Fallback to simple text
            return TextClip(
                text,
                fontsize=fontsize,
                color="white"
            ).set_position(position).set_start(start_time).set_end(end_time)
    
    def create_emoji_clip(self, emoji: str, start_time: float, duration: float = 1.0) -> TextClip:
        """Create an emoji clip"""
        try:
            emoji_clip = TextClip(
                emoji,
                fontsize=150,
                color="white"
            ).set_position("center").set_start(start_time).set_duration(duration)
            
            # Add bounce effect
            emoji_clip = emoji_clip.resize(lambda t: 1 + 0.1 * np.sin(2 * np.pi * t))
            
            return emoji_clip
        except Exception as e:
            logger.error(f"Failed to create emoji clip: {e}")
            return None
    
    def add_background_music(self, video: VideoFileClip, music_type: str = "upbeat") -> VideoFileClip:
        """Add background music to the video"""
        try:
            # For now, we'll skip background music as it requires audio files
            # In a full implementation, you'd have a library of royalty-free music
            logger.info("Background music feature not implemented yet")
            return video
        except Exception as e:
            logger.error(f"Failed to add background music: {e}")
            return video
    
    def create_video_from_script(self, script_data: Dict) -> Optional[str]:
        """Create a video from script data"""
        try:
            duration = min(script_data.get("duration", 10), 60)  # Max 60 seconds for Shorts
            
            # Create background
            if random.choice([True, False]):
                background = self.create_animated_background(duration)
            else:
                background = self.create_background_video(duration)
            
            # Create text overlays
            clips = [background]
            
            if script_data["type"] == "dad_joke" and "setup" in script_data:
                # Two-part joke: setup and punchline
                setup_clip = self.create_text_clip(
                    script_data["setup"],
                    start_time=0,
                    end_time=duration * 0.6,
                    position="center"
                )
                clips.append(setup_clip)
                
                punchline_clip = self.create_text_clip(
                    script_data["punchline"],
                    start_time=duration * 0.4,
                    end_time=duration,
                    position="center",
                    fontsize=self.text_settings["fontsize"] + 10
                )
                clips.append(punchline_clip)
                
                # Add laughing emoji at the end
                emoji_clip = self.create_emoji_clip("😂", duration * 0.8, 1.0)
                if emoji_clip:
                    clips.append(emoji_clip)
            
            else:
                # Single text joke
                text_clip = self.create_text_clip(
                    script_data["script"],
                    start_time=0,
                    end_time=duration,
                    position="center"
                )
                clips.append(text_clip)
                
                # Add laughing emoji
                emoji_clip = self.create_emoji_clip("🤣", duration * 0.7, 1.0)
                if emoji_clip:
                    clips.append(emoji_clip)
            
            # Compose final video
            final_video = CompositeVideoClip(clips, size=self.video_settings["size"])
            final_video = final_video.set_duration(duration)
            
            # Add background music if specified
            if script_data.get("background_audio"):
                final_video = self.add_background_music(final_video)
            
            return final_video
            
        except Exception as e:
            logger.error(f"Error creating video from script: {e}")
            return None
    
    def create_video(self, script_data: Dict) -> Optional[str]:
        """Main method to create a video from script data"""
        try:
            logger.info("Creating video from script...")
            
            # Create video clip
            video_clip = self.create_video_from_script(script_data)
            if not video_clip:
                logger.error("Failed to create video clip")
                return None
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"short_{timestamp}.mp4"
            output_path = self.output_dir / output_filename
            
            # Export video
            logger.info(f"Exporting video to {output_path}")
            video_clip.write_videofile(
                str(output_path),
                fps=self.video_settings["fps"],
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=str(self.temp_dir / 'temp_audio.m4a'),
                remove_temp=True,
                verbose=False,
                logger=None  # Suppress moviepy logs
            )
            
            # Clean up
            video_clip.close()
            
            logger.info(f"Video created successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error creating video: {e}")
            return None
    
    def create_thumbnail(self, script_data: Dict, video_path: str) -> Optional[str]:
        """Create a thumbnail for the video"""
        try:
            # Create thumbnail image
            thumbnail_size = (1280, 720)  # YouTube thumbnail size
            
            # Create image
            img = Image.new('RGB', thumbnail_size, color=random.choice(self.background_colors))
            draw = ImageDraw.Draw(img)
            
            # Add text
            try:
                # Try to use a bold font
                font = ImageFont.truetype("arial.ttf", 60)
            except:
                font = ImageFont.load_default()
            
            # Get text
            text = script_data.get("setup", script_data.get("script", "Funny Short!"))[:50]
            
            # Calculate text position
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (thumbnail_size[0] - text_width) // 2
            y = (thumbnail_size[1] - text_height) // 2
            
            # Draw text with outline
            for adj in range(3):
                draw.text((x-adj, y), text, font=font, fill='black')
                draw.text((x+adj, y), text, font=font, fill='black')
                draw.text((x, y-adj), text, font=font, fill='black')
                draw.text((x, y+adj), text, font=font, fill='black')
            
            draw.text((x, y), text, font=font, fill='white')
            
            # Add emoji
            emoji_font_size = 100
            try:
                emoji_font = ImageFont.truetype("seguiemj.ttf", emoji_font_size)
                draw.text((50, 50), "😂", font=emoji_font, fill='white')
            except:
                pass
            
            # Save thumbnail
            thumbnail_path = video_path.replace('.mp4', '_thumbnail.jpg')
            img.save(thumbnail_path)
            
            logger.info(f"Thumbnail created: {thumbnail_path}")
            return thumbnail_path
            
        except Exception as e:
            logger.error(f"Error creating thumbnail: {e}")
            return None

# Test the video creator
if __name__ == "__main__":
    # Set up logging for testing
    logging.basicConfig(level=logging.INFO)
    
    # Test script data
    test_script = {
        "script": "Why don't scientists trust atoms? Because they make up everything!",
        "setup": "Why don't scientists trust atoms?",
        "punchline": "Because they make up everything!",
        "type": "dad_joke",
        "duration": 8
    }
    
    creator = VideoCreator()
    video_path = creator.create_video(test_script)
    
    if video_path:
        print(f"Test video created: {video_path}")
        thumbnail_path = creator.create_thumbnail(test_script, video_path)
        if thumbnail_path:
            print(f"Thumbnail created: {thumbnail_path}")
    else:
        print("Failed to create test video")
