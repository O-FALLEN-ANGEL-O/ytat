"""
Flask Web Application for YouTube Shorts Automation Control
Provides mobile-friendly web interface for remote control
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from threading import Thread
import schedule
import time

# Import our automation modules
from main import YouTubeShortsAutomation
from config import Config
from youtube_uploader import YouTubeUploader

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global automation instance
automation = None
automation_thread = None
is_running = False

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

def init_db():
    """Initialize SQLite database for user management"""
    conn = sqlite3.connect('automation.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create automation logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS automation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            status TEXT NOT NULL,
            message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create default admin user if none exists
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        admin_password = generate_password_hash('admin123')
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                      ('admin', admin_password))
    
    conn.commit()
    conn.close()

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('automation.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, password_hash FROM users WHERE id = ?', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        return User(user_data[0], user_data[1], user_data[2])
    return None

def log_action(action, status, message=""):
    """Log automation actions to database"""
    try:
        conn = sqlite3.connect('automation.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO automation_logs (action, status, message) VALUES (?, ?, ?)',
                      (action, status, message))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to log action: {e}")

def get_automation_stats():
    """Get automation statistics"""
    try:
        conn = sqlite3.connect('automation.db')
        cursor = conn.cursor()
        
        # Get total uploads
        cursor.execute('SELECT COUNT(*) FROM automation_logs WHERE action = "upload" AND status = "success"')
        total_uploads = cursor.fetchone()[0]
        
        # Get recent activity
        cursor.execute('SELECT action, status, message, timestamp FROM automation_logs ORDER BY timestamp DESC LIMIT 10')
        recent_activity = cursor.fetchall()
        
        # Get upload log
        upload_log = []
        if os.path.exists('uploads_log.json'):
            with open('uploads_log.json', 'r') as f:
                upload_log = json.load(f)
        
        conn.close()
        
        return {
            'total_uploads': total_uploads,
            'recent_activity': recent_activity,
            'upload_log': upload_log[-10:],  # Last 10 uploads
            'is_running': is_running
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return {'total_uploads': 0, 'recent_activity': [], 'upload_log': [], 'is_running': is_running}

def automation_worker():
    """Background thread for automation"""
    global automation, is_running
    
    try:
        automation = YouTubeShortsAutomation()
        log_action("automation_start", "success", "Automation started successfully")
        
        while is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except Exception as e:
        logger.error(f"Automation worker error: {e}")
        log_action("automation_error", "error", str(e))
        is_running = False

@app.route('/')
@login_required
def dashboard():
    """Main dashboard"""
    try:
        config = Config()
        stats = get_automation_stats()
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             config=config.settings,
                             upload_time=config.get_upload_schedule())
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('dashboard.html', stats={}, config={}, upload_time="10:00")

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('automation.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data and check_password_hash(user_data[2], password):
            user = User(user_data[0], user_data[1], user_data[2])
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/start', methods=['POST'])
@login_required
def start_automation():
    """Start automation via API"""
    global automation_thread, is_running
    
    try:
        if not is_running:
            is_running = True
            automation_thread = Thread(target=automation_worker, daemon=True)
            automation_thread.start()
            log_action("automation_start", "success", f"Started by {current_user.username}")
            return jsonify({'status': 'success', 'message': 'Automation started'})
        else:
            return jsonify({'status': 'error', 'message': 'Automation already running'})
    except Exception as e:
        log_action("automation_start", "error", str(e))
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/stop', methods=['POST'])
@login_required
def stop_automation():
    """Stop automation via API"""
    global is_running
    
    try:
        is_running = False
        log_action("automation_stop", "success", f"Stopped by {current_user.username}")
        return jsonify({'status': 'success', 'message': 'Automation stopped'})
    except Exception as e:
        log_action("automation_stop", "error", str(e))
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/status')
@login_required
def get_status():
    """Get automation status"""
    stats = get_automation_stats()
    return jsonify(stats)

@app.route('/api/test', methods=['POST'])
@login_required
def test_automation():
    """Run a test automation"""
    try:
        if automation:
            result = automation.daily_automation()
            status = 'success' if result else 'error'
            message = 'Test completed successfully' if result else 'Test failed'
            log_action("test_run", status, f"Test by {current_user.username}: {message}")
            return jsonify({'status': status, 'message': message})
        else:
            return jsonify({'status': 'error', 'message': 'Automation not initialized'})
    except Exception as e:
        log_action("test_run", "error", str(e))
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/config', methods=['GET', 'POST'])
@login_required
def manage_config():
    """Get or update configuration"""
    config = Config()
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Update specific settings
            if 'upload_time' in data:
                config.set('automation.daily_upload_time', data['upload_time'])
            if 'privacy' in data:
                config.set('automation.upload_privacy', data['privacy'])
            
            log_action("config_update", "success", f"Config updated by {current_user.username}")
            return jsonify({'status': 'success', 'message': 'Configuration updated'})
        except Exception as e:
            log_action("config_update", "error", str(e))
            return jsonify({'status': 'error', 'message': str(e)})
    
    return jsonify(config.settings)

@app.route('/config')
@login_required
def config_page():
    """Configuration page"""
    config = Config()
    return render_template('config.html', config=config.settings)

@app.route('/logs')
@login_required
def logs_page():
    """Logs page"""
    stats = get_automation_stats()
    return render_template('logs.html', 
                         recent_activity=stats['recent_activity'],
                         upload_log=stats['upload_log'])

# Mobile API endpoints for app control
@app.route('/api/mobile/quick-action/<action>', methods=['POST'])
@login_required
def mobile_quick_action(action):
    """Quick actions for mobile app"""
    try:
        if action == 'start':
            return start_automation()
        elif action == 'stop':
            return stop_automation()
        elif action == 'test':
            return test_automation()
        elif action == 'status':
            return get_status()
        else:
            return jsonify({'status': 'error', 'message': 'Invalid action'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    init_db()
    
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run in debug mode locally, production mode in cloud
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
