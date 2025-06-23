#!/usr/bin/env python3
"""
Cloud Deployment Script for YouTube Shorts Automation
Supports Heroku, Railway, Render, and other cloud platforms
"""

import os
import sys
import json
import subprocess
import base64
from pathlib import Path

class CloudDeployer:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.platforms = {
            'heroku': self.deploy_heroku,
            'railway': self.deploy_railway,
            'render': self.deploy_render,
            'docker': self.deploy_docker
        }
    
    def check_requirements(self):
        """Check if all required files exist"""
        required_files = [
            'requirements.txt',
            'Procfile',
            'runtime.txt',
            'web_app.py',
            'main.py'
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.project_dir / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Missing required files: {', '.join(missing_files)}")
            return False
        
        print("✅ All required files present")
        return True
    
    def prepare_environment_variables(self):
        """Prepare environment variables for cloud deployment"""
        env_vars = {
            'SECRET_KEY': self.generate_secret_key(),
            'FLASK_ENV': 'production',
            'PYTHONPATH': '/app'
        }
        
        # Check if client_secrets.json exists and encode it
        if (self.project_dir / 'client_secrets.json').exists():
            with open(self.project_dir / 'client_secrets.json', 'r') as f:
                client_secrets = json.load(f)
            env_vars['YOUTUBE_CLIENT_SECRETS'] = base64.b64encode(
                json.dumps(client_secrets).encode()
            ).decode()
        
        return env_vars
    
    def generate_secret_key(self):
        """Generate a secure secret key"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def deploy_heroku(self):
        """Deploy to Heroku"""
        print("🚀 Deploying to Heroku...")
        
        # Check if Heroku CLI is installed
        try:
            subprocess.run(['heroku', '--version'], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Heroku CLI not installed. Please install it first:")
            print("   https://devcenter.heroku.com/articles/heroku-cli")
            return False
        
        app_name = input("Enter Heroku app name (or press Enter for auto-generation): ").strip()
        
        commands = [
            ['heroku', 'create'] + ([app_name] if app_name else []),
            ['heroku', 'addons:create', 'heroku-postgresql:mini'],
            ['git', 'add', '.'],
            ['git', 'commit', '-m', 'Deploy YouTube Shorts Automation'],
            ['git', 'push', 'heroku', 'main']
        ]
        
        # Set environment variables
        env_vars = self.prepare_environment_variables()
        for key, value in env_vars.items():
            commands.append(['heroku', 'config:set', f'{key}={value}'])
        
        for cmd in commands:
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                print(f"✅ {' '.join(cmd)}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed: {' '.join(cmd)}")
                print(f"   Error: {e.stderr}")
                return False
        
        print("🎉 Successfully deployed to Heroku!")
        print("📱 Your automation is now running in the cloud!")
        return True
    
    def deploy_railway(self):
        """Deploy to Railway"""
        print("🚀 Deploying to Railway...")
        
        # Create railway.json configuration
        railway_config = {
            "build": {
                "builder": "NIXPACKS"
            },
            "deploy": {
                "startCommand": "python web_app.py",
                "healthcheckPath": "/"
            }
        }
        
        with open(self.project_dir / 'railway.json', 'w') as f:
            json.dump(railway_config, f, indent=2)
        
        print("📝 Railway configuration created")
        print("🌐 Please visit https://railway.app and:")
        print("   1. Connect your GitHub repository")
        print("   2. Set environment variables:")
        
        env_vars = self.prepare_environment_variables()
        for key, value in env_vars.items():
            print(f"      {key}={value}")
        
        print("   3. Deploy from the Railway dashboard")
        return True
    
    def deploy_render(self):
        """Deploy to Render"""
        print("🚀 Preparing for Render deployment...")
        
        # Create render.yaml
        render_config = {
            "services": [
                {
                    "type": "web",
                    "name": "youtube-shorts-automation",
                    "env": "python",
                    "buildCommand": "pip install -r requirements.txt",
                    "startCommand": "python web_app.py",
                    "envVars": [
                        {"key": "FLASK_ENV", "value": "production"},
                        {"key": "PYTHONPATH", "value": "/opt/render/project/src"}
                    ]
                }
            ]
        }
        
        with open(self.project_dir / 'render.yaml', 'w') as f:
            import yaml
            yaml.dump(render_config, f, default_flow_style=False)
        
        print("📝 Render configuration created")
        print("🌐 Please visit https://render.com and:")
        print("   1. Connect your GitHub repository")
        print("   2. Use the render.yaml configuration")
        print("   3. Set additional environment variables as needed")
        return True
    
    def deploy_docker(self):
        """Create Docker deployment instructions"""
        print("🐳 Docker deployment setup...")
        
        # Create docker run script
        docker_script = """#!/bin/bash
# Build the Docker image
docker build -t youtube-shorts-automation .

# Run the container
docker run -d \\
  --name youtube-automation \\
  -p 5000:5000 \\
  -v $(pwd)/videos:/app/videos \\
  -v $(pwd)/logs:/app/logs \\
  -v $(pwd)/automation.db:/app/automation.db \\
  -e SECRET_KEY=$(openssl rand -hex 32) \\
  -e FLASK_ENV=production \\
  youtube-shorts-automation

echo "🎉 YouTube Shorts Automation is running!"
echo "📱 Access the control panel at: http://localhost:5000"
echo "🔧 To stop: docker stop youtube-automation"
"""
        
        with open(self.project_dir / 'run_docker.sh', 'w') as f:
            f.write(docker_script)
        
        # Make it executable
        os.chmod(self.project_dir / 'run_docker.sh', 0o755)
        
        print("📝 Docker run script created: run_docker.sh")
        print("🐳 To deploy with Docker:")
        print("   1. Make sure Docker is installed")
        print("   2. Run: ./run_docker.sh")
        print("   3. Access at http://localhost:5000")
        return True
    
    def create_mobile_app_config(self):
        """Create configuration for mobile app integration"""
        mobile_config = {
            "app_name": "YouTube Shorts Control",
            "base_url": "https://your-app-url.herokuapp.com",
            "api_endpoints": {
                "login": "/login",
                "status": "/api/status",
                "start": "/api/start",
                "stop": "/api/stop",
                "test": "/api/test",
                "config": "/api/config"
            },
            "quick_actions": [
                {"name": "Start Automation", "endpoint": "/api/mobile/quick-action/start", "color": "green"},
                {"name": "Stop Automation", "endpoint": "/api/mobile/quick-action/stop", "color": "red"},
                {"name": "Test Run", "endpoint": "/api/mobile/quick-action/test", "color": "blue"},
                {"name": "Check Status", "endpoint": "/api/mobile/quick-action/status", "color": "gray"}
            ]
        }
        
        with open(self.project_dir / 'mobile_app_config.json', 'w') as f:
            json.dump(mobile_config, f, indent=2)
        
        print("📱 Mobile app configuration created: mobile_app_config.json")
    
    def deploy(self, platform):
        """Deploy to specified platform"""
        if not self.check_requirements():
            return False
        
        if platform not in self.platforms:
            print(f"❌ Unsupported platform: {platform}")
            print(f"Supported platforms: {', '.join(self.platforms.keys())}")
            return False
        
        print(f"🌐 Preparing deployment to {platform.title()}...")
        
        # Create mobile app config
        self.create_mobile_app_config()
        
        # Deploy to platform
        return self.platforms[platform]()

def main():
    """Main deployment function"""
    deployer = CloudDeployer()
    
    print("🎬 YouTube Shorts Automation - Cloud Deployment")
    print("=" * 50)
    print()
    
    if len(sys.argv) > 1:
        platform = sys.argv[1].lower()
    else:
        print("Available deployment platforms:")
        print("1. heroku    - Deploy to Heroku (recommended)")
        print("2. railway   - Deploy to Railway")
        print("3. render    - Deploy to Render")
        print("4. docker    - Create Docker deployment")
        print()
        
        choice = input("Select platform (1-4): ").strip()
        platform_map = {'1': 'heroku', '2': 'railway', '3': 'render', '4': 'docker'}
        platform = platform_map.get(choice, 'heroku')
    
    success = deployer.deploy(platform)
    
    if success:
        print()
        print("🎉 Deployment completed successfully!")
        print()
        print("📋 Next Steps:")
        print("1. 📱 Access your web dashboard from any device")
        print("2. 🔑 Set up YouTube API credentials in the web interface")
        print("3. ⚙️ Configure automation settings")
        print("4. 🚀 Start your automation!")
        print()
        print("📱 Mobile Control:")
        print("   - Bookmark the web dashboard on your phone")
        print("   - Use quick action buttons for easy control")
        print("   - Monitor status and logs remotely")
    else:
        print("❌ Deployment failed. Please check the errors above.")

if __name__ == "__main__":
    main()
