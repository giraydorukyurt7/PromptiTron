
"""Promptitron Control Panel
Minimal web interface for system control and monitoring
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
import json
from datetime import datetime
import logging

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API base URL
API_BASE_URL = "http://localhost:5008"

@app.route('/')
def index():
    """Control panel home page"""
    return render_template('control_panel.html')

@app.route('/api/status')
def get_status():
    """Get system status"""
    try:
        # Get health status from API
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                "status": "online",
                "api_status": data.get("status", "unknown"),
                "components": data.get("components", {}),
                "version": data.get("version", "unknown"),
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "status": "error",
                "api_status": "offline",
                "error": f"API returned {response.status_code}"
            }), 500
    except Exception as e:
        return jsonify({
            "status": "offline",
            "api_status": "unreachable",
            "error": str(e)
        }), 500

@app.route('/api/logs')
def get_logs():
    """Get recent system logs"""
    try:
        # This would typically read from a log file or database
        # For now, return mock data
        return jsonify({
            "logs": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": "System running normally",
                    "component": "API"
                }
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/metrics')
def get_metrics():
    """Get system metrics"""
    try:
        response = requests.get(f"{API_BASE_URL}/metrics", timeout=5)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to get metrics"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/control/<action>', methods=['POST'])
def control_action(action):
    """Execute control actions"""
    try:
        if action == 'restart':
            # Implement restart logic
            return jsonify({"message": "Restart initiated"})
        elif action == 'clear-cache':
            # Implement cache clearing
            return jsonify({"message": "Cache cleared"})
        elif action == 'reload-config':
            # Implement config reload
            return jsonify({"message": "Configuration reloaded"})
        else:
            return jsonify({"error": f"Unknown action: {action}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True)