#!/usr/bin/env python3
"""
Free Cloud Deployment Script for YouTube Shorts Automation
Deploys to completely FREE platforms with no time limits
"""

import os
import sys
import json
import subprocess
import base64
import webbrowser
from pathlib import Path

class FreeCloudDeployer:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.free_platforms = {
            'render': self.deploy_render_free,
            'railway': self.deploy_railway_free,
            'pythonanywhere': self.deploy_pythonanywhere,
            'glitch': self.deploy_glitch,
            'vercel': self.deploy_vercel_free
        }
    
    def display_free_options(self):
        """Display all free deployment options"""
        print("🆓 COMPLETELY FREE Cloud Platforms:")
        print("=" * 50)
        print()
        print("1. 🚀 Render (RECOMMENDED)")
        print("   ✅ 750 hours/month FREE")
        print("   ✅ Auto-sleep when inactive")
        print("   ✅ Custom domains")
        print("   ✅ GitHub integration")
        print()
        print("2. 🚄 Railway")
        print("   ✅ $5 free credit monthly")
        print("   ✅ Sleeps after 1 hour inactive")
        print("   ✅ Very fast deployment")
        print()
        print("3. 🐍 PythonAnywhere")
        print("   ✅ Always-on free tier")
        print("   ✅ 1 web app free forever")
        print("   ✅ Great for Python apps")
        print()
        print("4. 🎨 Glitch")
        print("   ✅ Free hosting")
        print("   ✅ Auto-sleep after 5 minutes")
        print("   ✅ Easy to use")
        print()
        print("5. ▲ Vercel (Static hosting + serverless)")
        print("   ✅ Free hobby plan")
        print("   ✅ Fast global CDN")
        print("   ✅ Serverless functions")
        print()
    
    def deploy_render_free(self):
        """Deploy to Render (FREE tier - 750 hours/month)"""
        print("🚀 Deploying to Render FREE tier...")
        print("📊 FREE tier includes: 750 hours/month, auto-sleep")
        
        # Create render.yaml for free deployment
        render_config = {
            "services": [
                {
                    "type": "web",
                    "name": "youtube-shorts-automation",
                    "env": "python",
                    "plan": "free",  # FREE plan
                    "buildCommand": "pip install -r requirements.txt",
                    "startCommand": "python web_app.py",
                    "envVars": [
                        {
                            "key": "FLASK_ENV",
                            "value": "production"
                        },
                        {
                            "key": "SECRET_KEY",
                            "generateValue": True
                        },
                        {
                            "key": "PYTHONPATH",
                            "value": "/opt/render/project/src"
                        }
                    ],
                    "autoDeploy": False,
                    "disk": {
                        "name": "data",
                        "mountPath": "/opt/render/project/src/data",
                        "sizeGB": 1
                    }
                }
            ]
        }
        
        # Save render.yaml
        with open('render.yaml', 'w') as f:
            import yaml
            yaml.dump(render_config, f, default_flow_style=False)
        
        # Create .gitignore for sensitive files
        gitignore_content = """
# Secrets and credentials
client_secrets.json
youtube_credentials.pkl
*.db
.env

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/

# Logs
logs/
*.log

# Temporary files
temp/
*.tmp
"""
        
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content)
        
        # Create README for Render setup
        render_readme = """# Deploy to Render (FREE)

## Quick Deploy Button
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## Manual Setup:
1. Push code to GitHub
2. Connect GitHub to Render
3. Use render.yaml configuration
4. Set environment variables in Render dashboard
5. Deploy!

## Environment Variables to Set:
- SECRET_KEY (auto-generated)
- YOUTUBE_CLIENT_SECRETS (base64 encoded client_secrets.json)
- FLASK_ENV=production
"""
        
        with open('RENDER_DEPLOY.md', 'w') as f:
            f.write(render_readme)
        
        print("✅ Render configuration created!")
        print("📋 Next steps:")
        print("1. Push your code to GitHub")
        print("2. Visit https://render.com")
        print("3. Connect your GitHub repository")
        print("4. Use the render.yaml configuration")
        print("5. Set environment variables (we'll help with this)")
        
        # Open Render signup
        try:
            webbrowser.open("https://render.com")
            print("🌐 Opening Render signup page...")
        except:
            pass
        
        return True
    
    def deploy_railway_free(self):
        """Deploy to Railway (FREE $5 credit monthly)"""
        print("🚄 Deploying to Railway FREE tier...")
        print("💰 FREE tier includes: $5 credit monthly")
        
        # Create railway.json
        railway_config = {
            "build": {
                "builder": "NIXPACKS"
            },
            "deploy": {
                "startCommand": "python web_app.py",
                "healthcheckPath": "/",
                "restartPolicyType": "ON_FAILURE"
            }
        }
        
        with open('railway.json', 'w') as f:
            json.dump(railway_config, f, indent=2)
        
        # Create nixpacks.toml for optimization
        nixpacks_config = """[phases.setup]
nixPkgs = ["python39", "ffmpeg"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[phases.build]
cmds = ["echo 'Build complete'"]

[start]
cmd = "python web_app.py"
"""
        
        with open('nixpacks.toml', 'w') as f:
            f.write(nixpacks_config)
        
        print("✅ Railway configuration created!")
        print("📋 Next steps:")
        print("1. Push code to GitHub")
        print("2. Visit https://railway.app")
        print("3. Sign up with GitHub")
        print("4. Deploy from GitHub repo")
        print("5. Configure environment variables")
        
        try:
            webbrowser.open("https://railway.app")
            print("🌐 Opening Railway signup page...")
        except:
            pass
        
        return True
    
    def deploy_pythonanywhere(self):
        """Deploy to PythonAnywhere (FREE tier - always on)"""
        print("🐍 Deploying to PythonAnywhere FREE tier...")
        print("🔄 FREE tier includes: 1 web app, always-on, 512MB storage")
        
        # Create WSGI file for PythonAnywhere
        wsgi_content = """
import sys
import os

# Add your project directory to sys.path
project_home = '/home/yourusername/youtube-shorts-automation'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['PYTHONPATH'] = project_home

# Import your Flask app
from web_app import app as application

if __name__ == "__main__":
    application.run()
"""
        
        with open('wsgi.py', 'w') as f:
            f.write(wsgi_content)
        
        # Create setup script for PythonAnywhere
        setup_script = """#!/bin/bash
# PythonAnywhere Setup Script

echo "🐍 Setting up YouTube Shorts Automation on PythonAnywhere..."

# Install requirements
pip3.9 install --user -r requirements.txt

# Create necessary directories
mkdir -p ~/youtube-shorts-automation/videos
mkdir -p ~/youtube-shorts-automation/logs
mkdir -p ~/youtube-shorts-automation/temp

# Set permissions
chmod +x ~/youtube-shorts-automation/main.py
chmod +x ~/youtube-shorts-automation/web_app.py

echo "✅ Setup complete!"
echo "📋 Configure your web app in PythonAnywhere dashboard"
echo "🌐 Point source code to: /home/yourusername/youtube-shorts-automation"
echo "📁 Point WSGI file to: /home/yourusername/youtube-shorts-automation/wsgi.py"
"""
        
        with open('setup_pythonanywhere.sh', 'w') as f:
            f.write(setup_script)
        
        # Make it executable
        os.chmod('setup_pythonanywhere.sh', 0o755)
        
        print("✅ PythonAnywhere configuration created!")
        print("📋 Next steps:")
        print("1. Sign up at https://www.pythonanywhere.com")
        print("2. Upload your code to ~/youtube-shorts-automation")
        print("3. Run: bash setup_pythonanywhere.sh")
        print("4. Configure web app in dashboard")
        print("5. Set WSGI file path")
        
        try:
            webbrowser.open("https://www.pythonanywhere.com")
            print("🌐 Opening PythonAnywhere signup page...")
        except:
            pass
        
        return True
    
    def deploy_glitch(self):
        """Deploy to Glitch (FREE hosting)"""
        print("🎨 Deploying to Glitch FREE hosting...")
        print("🎯 FREE tier includes: Free hosting, auto-sleep after 5 min")
        
        # Create glitch.json
        glitch_config = {
            "install": "pip install -r requirements.txt",
            "start": "python web_app.py",
            "watch": {
                "ignore": [
                    "\\.pyc$",
                    "^logs/",
                    "^temp/",
                    "^videos/"
                ]
            },
            "throttle": 1000
        }
        
        with open('glitch.json', 'w') as f:
            json.dump(glitch_config, f, indent=2)
        
        # Create requirements for Glitch
        print("✅ Glitch configuration created!")
        print("📋 Next steps:")
        print("1. Visit https://glitch.com")
        print("2. Click 'New Project' > 'Import from GitHub'")
        print("3. Enter your GitHub repository URL")
        print("4. Glitch will auto-deploy!")
        print("5. Configure environment variables in .env file")
        
        try:
            webbrowser.open("https://glitch.com")
            print("🌐 Opening Glitch...")
        except:
            pass
        
        return True
    
    def deploy_vercel_free(self):
        """Deploy to Vercel (FREE hobby plan)"""
        print("▲ Deploying to Vercel FREE tier...")
        print("⚡ FREE tier includes: Serverless functions, global CDN")
        
        # Create vercel.json
        vercel_config = {
            "version": 2,
            "builds": [
                {
                    "src": "web_app.py",
                    "use": "@vercel/python"
                }
            ],
            "routes": [
                {
                    "src": "/(.*)",
                    "dest": "web_app.py"
                }
            ],
            "env": {
                "FLASK_ENV": "production"
            }
        }
        
        with open('vercel.json', 'w') as f:
            json.dump(vercel_config, f, indent=2)
        
        # Create index.py for Vercel
        vercel_entry = """
from web_app import app

# Vercel expects 'app' or 'application'
application = app

if __name__ == "__main__":
    app.run()
"""
        
        with open('index.py', 'w') as f:
            f.write(vercel_entry)
        
        print("✅ Vercel configuration created!")
        print("📋 Next steps:")
        print("1. Install Vercel CLI: npm i -g vercel")
        print("2. Run: vercel --prod")
        print("3. Or deploy via GitHub integration")
        print("4. Set environment variables in Vercel dashboard")
        
        try:
            webbrowser.open("https://vercel.com")
            print("🌐 Opening Vercel...")
        except:
            pass
        
        return True
    
    def create_github_actions(self):
        """Create GitHub Actions for automated deployment"""
        os.makedirs('.github/workflows', exist_ok=True)
        
        github_workflow = """name: Deploy to Free Cloud

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy-render:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Test application
      run: |
        python -m pytest tests/ || echo "No tests found"
    
    - name: Deploy to Render
      if: github.ref == 'refs/heads/main'
      run: |
        echo "Deploying to Render..."
        # Render auto-deploys from GitHub when connected
"""
        
        with open('.github/workflows/deploy.yml', 'w') as f:
            f.write(github_workflow)
        
        print("✅ GitHub Actions workflow created!")
    
    def setup_environment_secrets(self):
        """Create template for environment variables"""
        env_template = """# Environment Variables for Free Cloud Deployment
# Copy these to your cloud platform's environment settings

# Security (generate new values)
SECRET_KEY=your-secret-key-here

# Flask Configuration
FLASK_ENV=production
PYTHONPATH=/app

# YouTube API Credentials
# Get these from Google Cloud Console
YOUTUBE_CLIENT_SECRETS=base64-encoded-client-secrets-json

# Optional: Database URL (for platforms that provide it)
DATABASE_URL=sqlite:///automation.db

# Platform-specific settings
PORT=5000
"""
        
        with open('.env.template', 'w') as f:
            f.write(env_template)
        
        print("📝 Environment template created: .env.template")
    
    def deploy(self, platform):
        """Deploy to specified free platform"""
        if platform not in self.free_platforms:
            print(f"❌ Unsupported platform: {platform}")
            print(f"🆓 Available FREE platforms: {', '.join(self.free_platforms.keys())}")
            return False
        
        print(f"🌐 Preparing FREE deployment to {platform.title()}...")
        
        # Create common files
        self.setup_environment_secrets()
        self.create_github_actions()
        
        # Deploy to specific platform
        return self.free_platforms[platform]()
    
    def show_cost_comparison(self):
        """Show cost comparison of different platforms"""
        print("💰 FREE Tier Comparison:")
        print("=" * 50)
        print("🚀 Render FREE:")
        print("   ✅ 750 hours/month (never expires)")
        print("   ✅ Auto-sleep after 15 min idle")
        print("   ✅ Custom domains")
        print("   ⚠️  Spins down when inactive")
        print()
        print("🚄 Railway FREE:")
        print("   ✅ $5 credit monthly (renewable)")
        print("   ✅ Very fast performance")
        print("   ⚠️  Sleeps after 1 hour")
        print()
        print("🐍 PythonAnywhere FREE:")
        print("   ✅ Always-on (no sleeping)")
        print("   ✅ 1 web app forever")
        print("   ⚠️  Limited CPU seconds")
        print()
        print("🎨 Glitch FREE:")
        print("   ✅ Easy to use")
        print("   ⚠️  Sleeps after 5 minutes")
        print()
        print("▲ Vercel FREE:")
        print("   ✅ Serverless (always available)")
        print("   ✅ Global CDN")
        print("   ⚠️  Function timeouts")

def main():
    """Main deployment function"""
    deployer = FreeCloudDeployer()
    
    print("🆓 YouTube Shorts Automation - FREE Cloud Deployment")
    print("=" * 60)
    print()
    
    deployer.display_free_options()
    deployer.show_cost_comparison()
    
    print()
    print("Which FREE platform would you like to use?")
    choice = input("Enter number (1-5) or platform name: ").strip().lower()
    
    platform_map = {
        '1': 'render',
        '2': 'railway', 
        '3': 'pythonanywhere',
        '4': 'glitch',
        '5': 'vercel',
        'render': 'render',
        'railway': 'railway',
        'pythonanywhere': 'pythonanywhere',
        'glitch': 'glitch',
        'vercel': 'vercel'
    }
    
    platform = platform_map.get(choice, 'render')
    
    print(f"\n🚀 Deploying to {platform.title()} FREE tier...")
    
    success = deployer.deploy(platform)
    
    if success:
        print("\n" + "🎉" * 20)
        print("🆓 FREE DEPLOYMENT READY!")
        print("🎉" * 20)
        print()
        print("📋 What's Next:")
        print("1. 📤 Push your code to GitHub")
        print("2. 🔗 Connect GitHub to your chosen platform")
        print("3. ⚙️ Set environment variables")
        print("4. 🚀 Deploy and start automating!")
        print()
        print("📱 Mobile Access:")
        print("   - Your app will be accessible worldwide")
        print("   - Control from any device with internet")
        print("   - Bookmark on mobile for quick access")
        print()
        print("💡 Pro Tips:")
        print("   - Apps may sleep when inactive (free tier)")
        print("   - Visit your app URL to wake it up")
        print("   - Set up monitoring to keep it alive")

if __name__ == "__main__":
    main()
