# 🎬 YouTube Shorts Automation System

An intelligent automation system that creates and uploads funny YouTube Shorts daily. The system fetches jokes from various APIs, creates engaging videos with text overlays and animations, and automatically uploads them to YouTube with optimized titles, descriptions, and tags.

## ✨ Features

- **🤖 Fully Automated**: Runs daily without manual intervention
- **😂 Smart Content**: Fetches funny jokes from multiple APIs with local fallbacks
- **🎨 Dynamic Videos**: Creates engaging videos with animated backgrounds and text
- **📱 YouTube Shorts Optimized**: Perfect 9:16 aspect ratio and under 60 seconds
- **🏷️ SEO Optimized**: Automatic title, description, and tag generation
- **📊 Analytics**: Tracks uploads and performance
- **⚙️ Configurable**: Extensive customization options
- **🔄 Reliable**: Robust error handling and retry mechanisms

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd youtube_shorts_automation

# Run the setup script
python setup.py
```

### 2. YouTube API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable **YouTube Data API v3**
4. Create **OAuth 2.0 credentials**
5. Download `client_secrets.json` and place it in the project directory
6. Configure OAuth consent screen

### 3. Configure Settings

Edit `config.json` to customize:
- Upload schedule
- Video settings
- Title templates
- Tags and descriptions

### 4. Test the System

```bash
# Test run (creates one video without uploading)
python main.py --test
```

### 5. Start Automation

```bash
# Start daily automation
python main.py
```

## 📁 Project Structure

```
youtube_shorts_automation/
├── main.py                 # Main automation script
├── script_generator.py     # Joke fetching and script generation
├── video_creator.py        # Video creation and editing
├── youtube_uploader.py     # YouTube API integration
├── config.py              # Configuration management
├── setup.py               # Installation and setup
├── requirements.txt       # Python dependencies
├── README.md              # Documentation
├── config.json            # Configuration file (created on first run)
├── client_secrets.json    # YouTube API credentials (you provide)
├── scripts/               # Generated scripts
├── videos/                # Created videos
├── temp/                  # Temporary files
└── logs/                  # Log files
```

## ⚙️ Configuration Options

### Upload Schedule
```json
{
  "automation": {
    "daily_upload_time": "10:00",
    "upload_privacy": "public",
    "enable_scheduling": true
  }
}
```

### Video Settings
```json
{
  "video_creation": {
    "resolution": {
      "width": 1080,
      "height": 1920
    },
    "fps": 30,
    "background_type": "animated",
    "text_style": {
      "font": "Arial-Bold",
      "font_size": 80,
      "color": "white"
    }
  }
}
```

### YouTube Settings
```json
{
  "youtube": {
    "default_category": "23",
    "default_tags": ["funny", "comedy", "shorts", "viral"],
    "title_templates": [
      "😂 This Will Make You LAUGH!",
      "🤣 Funniest Short You'll See Today!"
    ]
  }
}
```

## 🎯 How It Works

### 1. Script Generation
- Fetches jokes from multiple APIs:
  - Official Joke API
  - JokeAPI.dev
  - icanhazdadjoke
- Falls back to local jokes if APIs fail
- Formats content for video display

### 2. Video Creation
- Creates 9:16 aspect ratio videos (YouTube Shorts format)
- Adds animated or gradient backgrounds
- Displays text with smooth transitions
- Includes emoji animations
- Optimizes duration (15-60 seconds)

### 3. YouTube Upload
- Automatically uploads videos
- Sets optimized titles and descriptions
- Adds relevant tags for discoverability
- Configures as YouTube Shorts
- Tracks upload status and analytics

### 4. Scheduling
- Runs daily at configured time
- Handles errors gracefully
- Logs all activities
- Continues on failures

## 🛠️ Advanced Usage

### Custom Joke Sources
Add your own joke APIs in `config.json`:
```json
{
  "script_generation": {
    "joke_apis": [
      "https://your-custom-api.com/jokes",
      "https://another-api.com/random"
    ]
  }
}
```

### Video Customization
Modify `video_creator.py` to add:
- Custom backgrounds
- Sound effects
- Voice narration
- Advanced animations

### Multiple Channels
Run separate instances for different channels:
```bash
# Channel 1
python main.py --config config_channel1.json

# Channel 2
python main.py --config config_channel2.json
```

## 🔧 Dependencies

### Required Python Packages
- **moviepy**: Video editing and creation
- **Pillow**: Image processing
- **google-api-python-client**: YouTube API
- **requests**: HTTP requests for joke APIs
- **schedule**: Task scheduling
- **numpy**: Numerical operations

### System Requirements
- Python 3.8+
- FFmpeg (for video processing)
- Internet connection
- YouTube channel with API access

## 📊 Monitoring and Analytics

### Log Files
- `automation.log`: Main application logs
- `uploads_log.json`: Upload history and metadata

### Monitoring Upload Status
```python
from youtube_uploader import YouTubeUploader

uploader = YouTubeUploader()
recent_uploads = uploader.list_recent_uploads(10)
```

### Performance Metrics
- Upload success rate
- Video processing time
- API response times
- Error frequency

## 🚨 Troubleshooting

### Common Issues

**1. YouTube API Authentication Failed**
```
Solution: 
- Verify client_secrets.json is correct
- Check OAuth consent screen configuration
- Ensure YouTube Data API v3 is enabled
```

**2. Video Creation Errors**
```
Solution:
- Install FFmpeg
- Check video codec support
- Verify sufficient disk space
```

**3. Joke API Failures**
```
Solution:
- Check internet connection
- Verify API endpoints are working
- System automatically falls back to local jokes
```

**4. Upload Failures**
```
Solution:
- Check YouTube API quotas
- Verify video file integrity
- Review upload privacy settings
```

### Debug Mode
Run with verbose logging:
```bash
python main.py --debug
```

## 🔒 Security Considerations

### API Keys and Credentials
- Store credentials securely
- Use environment variables for sensitive data
- Regularly rotate API keys
- Limit OAuth scope to minimum required

### Content Guidelines
- Ensure jokes comply with YouTube policies
- Avoid copyrighted content
- Respect community guidelines
- Monitor for inappropriate content

## 📈 Optimization Tips

### Content Strategy
- Analyze performing videos
- Adjust title templates based on engagement
- Optimize upload timing for your audience
- Experiment with different joke categories

### Technical Optimization
- Use SSD storage for faster video processing
- Adjust video quality settings for faster uploads
- Implement content caching
- Monitor system resources

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov

# Run tests
pytest tests/

# Code formatting
black *.py
```

### Adding Features
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## ⚠️ Disclaimer

- Use responsibly and comply with YouTube's Terms of Service
- Respect API rate limits and quotas
- Ensure content is appropriate and original
- Monitor uploads for quality and compliance

## 🆘 Support

### Documentation
- Check this README for common issues
- Review configuration examples
- Read inline code comments

### Community
- Create issues for bugs or feature requests
- Share successful configurations
- Help others in discussions

### Professional Support
For commercial use or advanced customization, consider professional development services.

---

**Happy automating! 🎬✨**

*Create engaging YouTube Shorts effortlessly and grow your channel with consistent, funny content.*
