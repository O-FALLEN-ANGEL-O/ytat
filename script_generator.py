"""
Script Generator Module
Generates funny scripts for YouTube Shorts using various sources
"""

import os
import json
import random
import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ScriptGenerator:
    def __init__(self):
        self.joke_apis = [
            "https://official-joke-api.appspot.com/random_joke",
            "https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,religious,political,racist,sexist,explicit&type=single",
            "https://icanhazdadjoke.com/"
        ]
        
        # Pre-defined funny script templates
        self.script_templates = [
            {
                "type": "dad_joke",
                "template": "Why {setup}? Because {punchline}!",
                "duration": 5
            },
            {
                "type": "one_liner",
                "template": "{joke}",
                "duration": 3
            },
            {
                "type": "story_joke",
                "template": "{setup} {punchline}",
                "duration": 8
            }
        ]
        
        # Backup local jokes in case APIs fail
        self.backup_jokes = [
            {
                "setup": "Why don't scientists trust atoms?",
                "punchline": "Because they make up everything!",
                "type": "dad_joke"
            },
            {
                "setup": "What do you call a fake noodle?",
                "punchline": "An impasta!",
                "type": "dad_joke"
            },
            {
                "setup": "Why did the scarecrow win an award?",
                "punchline": "Because he was outstanding in his field!",
                "type": "dad_joke"
            },
            {
                "setup": "What do you call a bear with no teeth?",
                "punchline": "A gummy bear!",
                "type": "dad_joke"
            },
            {
                "setup": "Why don't eggs tell jokes?",
                "punchline": "They'd crack each other up!",
                "type": "dad_joke"
            },
            {
                "joke": "I told my wife she was drawing her eyebrows too high. She looked surprised.",
                "type": "one_liner"
            },
            {
                "joke": "I invented a new word: Plagiarism!",
                "type": "one_liner"
            },
            {
                "joke": "Why do programmers prefer dark mode? Because light attracts bugs!",
                "type": "one_liner"
            }
        ]
    
    def fetch_joke_from_api(self, api_url: str) -> Optional[Dict]:
        """Fetch a joke from a specific API"""
        try:
            headers = {'Accept': 'application/json'}
            if 'icanhazdadjoke' in api_url:
                headers['User-Agent'] = 'YouTube Shorts Bot (https://github.com/yourbot)'
            
            response = requests.get(api_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse different API formats
            if 'official-joke-api' in api_url:
                return {
                    "setup": data.get('setup', ''),
                    "punchline": data.get('punchline', ''),
                    "type": "dad_joke"
                }
            elif 'jokeapi.dev' in api_url:
                if data.get('type') == 'single':
                    return {
                        "joke": data.get('joke', ''),
                        "type": "one_liner"
                    }
                else:
                    return {
                        "setup": data.get('setup', ''),
                        "punchline": data.get('delivery', ''),
                        "type": "dad_joke"
                    }
            elif 'icanhazdadjoke' in api_url:
                return {
                    "joke": data.get('joke', ''),
                    "type": "one_liner"
                }
                
        except Exception as e:
            logger.warning(f"Failed to fetch joke from {api_url}: {str(e)}")
            return None
    
    def get_joke_from_apis(self) -> Optional[Dict]:
        """Try to get a joke from various APIs"""
        random.shuffle(self.joke_apis)  # Randomize API order
        
        for api_url in self.joke_apis:
            joke_data = self.fetch_joke_from_api(api_url)
            if joke_data:
                logger.info(f"Successfully fetched joke from {api_url}")
                return joke_data
        
        logger.warning("All APIs failed, using backup jokes")
        return None
    
    def get_backup_joke(self) -> Dict:
        """Get a random backup joke"""
        return random.choice(self.backup_jokes)
    
    def format_script(self, joke_data: Dict) -> Dict:
        """Format joke data into a script"""
        script_data = {
            "timestamp": datetime.now().isoformat(),
            "source": "api" if "setup" in joke_data or "joke" in joke_data else "backup",
            "type": joke_data.get("type", "unknown")
        }
        
        if joke_data["type"] == "dad_joke" and "setup" in joke_data:
            script_data.update({
                "script": f"{joke_data['setup']} {joke_data['punchline']}",
                "setup": joke_data["setup"],
                "punchline": joke_data["punchline"],
                "duration": 6,
                "topic": "dad joke"
            })
        elif joke_data["type"] == "one_liner" and "joke" in joke_data:
            script_data.update({
                "script": joke_data["joke"],
                "duration": 4,
                "topic": "one liner"
            })
        else:
            # Fallback formatting
            script_text = joke_data.get("joke", f"{joke_data.get('setup', '')} {joke_data.get('punchline', '')}")
            script_data.update({
                "script": script_text,
                "duration": len(script_text.split()) // 2,  # Rough estimate
                "topic": "humor"
            })
        
        return script_data
    
    def enhance_script_for_video(self, script_data: Dict) -> Dict:
        """Enhance script with video-specific instructions"""
        enhanced_script = script_data.copy()
        
        # Add visual cues
        enhanced_script["visual_cues"] = []
        enhanced_script["text_overlays"] = []
        
        if script_data["type"] == "dad_joke":
            enhanced_script["visual_cues"] = [
                {"time": 0, "action": "show_setup_text"},
                {"time": 2, "action": "dramatic_pause"},
                {"time": 3, "action": "show_punchline_text"},
                {"time": 5, "action": "show_laughing_emoji"}
            ]
            enhanced_script["text_overlays"] = [
                {"text": script_data.get("setup", ""), "start": 0, "end": 2.5},
                {"text": script_data.get("punchline", ""), "start": 3, "end": 6}
            ]
        else:
            enhanced_script["visual_cues"] = [
                {"time": 0, "action": "show_joke_text"},
                {"time": enhanced_script["duration"], "action": "show_laughing_emoji"}
            ]
            enhanced_script["text_overlays"] = [
                {"text": script_data["script"], "start": 0, "end": enhanced_script["duration"]}
            ]
        
        # Add background music suggestions
        enhanced_script["background_audio"] = {
            "type": "upbeat_comedy",
            "volume": 0.3,
            "fade_in": 0.5,
            "fade_out": 0.5
        }
        
        # Add hashtag suggestions
        enhanced_script["suggested_hashtags"] = [
            "#shorts", "#funny", "#comedy", "#joke", "#humor", 
            "#viral", "#laughs", "#entertainment"
        ]
        
        return enhanced_script
    
    def generate_funny_script(self) -> Optional[Dict]:
        """Main method to generate a funny script"""
        try:
            logger.info("Generating funny script...")
            
            # Try to get joke from APIs first
            joke_data = self.get_joke_from_apis()
            
            # Fall back to backup jokes if APIs fail
            if not joke_data:
                joke_data = self.get_backup_joke()
            
            # Format the joke into a script
            script_data = self.format_script(joke_data)
            
            # Enhance for video production
            enhanced_script = self.enhance_script_for_video(script_data)
            
            # Save script to file
            script_filename = f"scripts/script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(script_filename, 'w', encoding='utf-8') as f:
                json.dump(enhanced_script, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Script generated and saved: {script_filename}")
            logger.info(f"Script content: {enhanced_script['script'][:100]}...")
            
            return enhanced_script
            
        except Exception as e:
            logger.error(f"Error generating script: {str(e)}")
            return None
    
    def validate_script(self, script_data: Dict) -> bool:
        """Validate that the script has all required fields"""
        required_fields = ["script", "duration", "type"]
        
        for field in required_fields:
            if field not in script_data:
                logger.error(f"Script missing required field: {field}")
                return False
        
        if len(script_data["script"]) < 10:
            logger.error("Script too short")
            return False
        
        if script_data["duration"] > 60:
            logger.warning("Script might be too long for YouTube Shorts")
        
        return True

# Test the script generator
if __name__ == "__main__":
    # Set up logging for testing
    logging.basicConfig(level=logging.INFO)
    
    generator = ScriptGenerator()
    script = generator.generate_funny_script()
    
    if script:
        print("Generated script:")
        print(json.dumps(script, indent=2))
    else:
        print("Failed to generate script")
