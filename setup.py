#!/usr/bin/env python3
"""
Setup and Installation Script for YouTube Shorts Automation
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python requirements...")
    
    success, stdout, stderr = run_command(f"{sys.executable} -m pip install -r requirements.txt")
    
    if success:
        print("✅ Requirements installed successfully!")
        return True
    else:
        print(f"❌ Failed to install requirements: {stderr}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        'scripts', 'videos', 'audio', 'images', 
        'temp', 'logs', 'assets'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  Created: {directory}/")
    
    print("✅ Directories created successfully!")

def create_youtube_credentials_template():
    """Create YouTube API credentials template"""
    print("🔑 Setting up YouTube API credentials template...")
    
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
        print("  Created: client_secrets_template.json")
        print("  ⚠️  You need to fill in your YouTube API credentials!")
    else:
        print("  client_secrets.json already exists")
    
    print("✅ YouTube API template created!")

def create_environment_file():
    """Create .env file for environment variables"""
    print("🌍 Creating environment file...")
    
    env_content = """# YouTube Shorts Automation Environment Variables

# YouTube API Settings
YOUTUBE_API_KEY=your_api_key_here
YOUTUBE_CLIENT_ID=your_client_id_here
YOUTUBE_CLIENT_SECRET=your_client_secret_here

# Automation Settings
DAILY_UPLOAD_TIME=10:00
UPLOAD_PRIVACY=public

# Optional: Custom joke APIs
CUSTOM_JOKE_API_URL=
JOKE_API_KEY=

# Logging
LOG_LEVEL=INFO
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("  Created: .env")
    else:
        print("  .env already exists")
    
    print("✅ Environment file ready!")

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing package imports...")
    
    required_packages = [
        ('schedule', 'schedule'),
        ('moviepy.editor', 'moviepy'),
        ('PIL', 'Pillow'),
        ('numpy', 'numpy'),
        ('google.auth', 'google-auth'),
        ('googleapiclient', 'google-api-python-client'),
        ('requests', 'requests')
    ]
    
    failed_imports = []
    
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            failed_imports.append(name)
    
    if failed_imports:
        print(f"❌ Some packages failed to import: {', '.join(failed_imports)}")
        return False
    else:
        print("✅ All packages imported successfully!")
        return True

def display_setup_instructions():
    """Display post-setup instructions"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print()
    print("📋 NEXT STEPS:")
    print()
    print("1. 🔑 Set up YouTube API credentials:")
    print("   - Go to https://console.cloud.google.com/")
    print("   - Create a new project or select an existing one")
    print("   - Enable YouTube Data API v3")
    print("   - Create OAuth 2.0 credentials")
    print("   - Download client_secrets.json and place it in this directory")
    print()
    print("2. 🎬 Test the system:")
    print("   python main.py --test")
    print()
    print("3. 🚀 Start daily automation:")
    print("   python main.py")
    print()
    print("4. ⚙️ Customize settings:")
    print("   Edit config.json to customize video settings, upload schedule, etc.")
    print()
    print("📖 For detailed instructions, see README.md")
    print()
    print("⚠️  IMPORTANT:")
    print("   - Make sure to replace placeholders in client_secrets_template.json")
    print("   - Configure your YouTube channel for API access")
    print("   - Test with a private video first")
    print("="*60)

def main():
    """Main setup function"""
    print("🚀 YouTube Shorts Automation Setup")
    print("="*40)
    print()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed during package installation!")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create credentials template
    create_youtube_credentials_template()
    
    # Create environment file
    create_environment_file()
    
    # Test imports
    if not test_imports():
        print("⚠️  Some packages may not be working correctly!")
    
    # Initialize config
    print("⚙️ Initializing configuration...")
    try:
        from config import Config
        config = Config()
        config.create_directories()
        print("✅ Configuration initialized!")
    except Exception as e:
        print(f"⚠️  Configuration initialization failed: {e}")
    
    # Display instructions
    display_setup_instructions()

if __name__ == "__main__":
    main()
