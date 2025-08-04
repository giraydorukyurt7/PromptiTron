
"""Simple Promptitron Web Interface - Standalone version for testing
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from flask import Flask, render_template, request, jsonify, session, send_file, flash
from flask_cors import CORS
from werkzeug.utils import secure_filename
import markdown2
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import logging

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "promptitron_secret_key_test_2024"
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API base URL
API_BASE_URL = "http://localhost:8000"

# Upload configurations
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'md', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Sample curriculum data for testing
SAMPLE_CURRICULUM = {
    "Matematik": {
        "topics": [
            {"name": "Fonksiyonlar", "description": "Fonksiyon kavrami ve ozellikleri"},
            {"name": "Turev", "description": "Turev kavrami ve uygulamalari"},
            {"name": "Integral", "description": "Integral kavrami ve uygulamalari"},
            {"name": "Geometri", "description": "Duzlem ve uzay geometrisi"}
        ]
    },
    "Fizik": {
        "topics": [
            {"name": "Hareket", "description": "Kinematik ve dinamik"},
            {"name": "Enerji", "description": "Enerji turleri ve korunumu"},
            {"name": "Elektrik", "description": "Elektrik ve manyetizma"},
            {"name": "Dalgalar", "description": "Dalga hareketi ve ozellikleri"}
        ]
    },
    "Kimya": {
        "topics": [
            {"name": "Atom Yapisi", "description": "Atom modelleri ve yapisi"},
            {"name": "Periyodik Sistem", "description": "Elementlerin ozellikleri"},
            {"name": "Kimyasal Baglar", "description": "Bag turleri ve ozellikleri"},
            {"name": "Reaksiyonlar", "description": "Kimyasal reaksiyonlar"}
        ]
    },
    "Biyoloji": {
        "topics": [
            {"name": "Hucre", "description": "Hucre yapisi ve islevleri"},
            {"name": "Genetik", "description": "Kalitim ve genetik"},
            {"name": "Evrim", "description": "Evrim teorisi ve kanitlari"},
            {"name": "Ekoloji", "description": "Ekosistem ve cevre"}
        ]
    }
}

class SimpleUIManager:
    """Simple UI manager for testing"""
    
    def __init__(self):
        self.session_id = None
        self.conversation_history = []
        
    def generate_session_id(self) -> str:
        """Generate a new session ID"""
        import uuid
        return str(uuid.uuid4())
    
    async def call_api(self, endpoint: str, method: str = "POST", data: dict = None) -> dict:
        """Simulate API calls"""
        try:
            # For testing, return mock responses
            if endpoint == "/chat":
                return {
                    "success": True,
                    "response": f"Bu bir test yanitidir. Mesajiniz: {data.get('message', 'Mesaj bulunamadi')}",
                    "system_used": "test_system"
                }
            elif endpoint == "/generate/questions":
                return {
                    "success": True,
                    "questions": [
                        {
                            "question_id": "test_1",
                            "question_text": f"{data.get('subject', 'Test')} - {data.get('topic', 'Test konusu')} hakkinda test sorusu",
                            "options": [
                                {"option_letter": "A", "option_text": "Secenek A"},
                                {"option_letter": "B", "option_text": "Secenek B"},
                                {"option_letter": "C", "option_text": "Secenek C"},
                                {"option_letter": "D", "option_text": "Secenek D"},
                                {"option_letter": "E", "option_text": "Secenek E"}
                            ],
                            "correct_answer": "A",
                            "explanation": "Bu test aciklamasidir."
                        }
                    ]
                }
            elif endpoint == "/generate/study-plan":
                return {
                    "success": True,
                    "study_plan": {
                        "plan_id": "test_plan",
                        "overall_strategy": "Sistematik calisma plani test versiyonu",
                        "weekly_plans": [
                            "Hafta 1: Matematik temel konular",
                            "Hafta 2: Fizik hareket konulari",
                            "Hafta 3: Kimya atom yapisi"
                        ]
                    }
                }
            elif endpoint == "/search":
                return {
                    "success": True,
                    "results": [
                        {
                            "title": "Test Sonucu",
                            "content": f"'{data.get('query', 'test')}' aramasi icin test sonucu",
                            "relevance_score": 0.95
                        }
                    ]
                }
            elif endpoint == "/analyze/content":
                return {
                    "success": True,
                    "analysis": f"Icerik analizi: {data.get('content', 'Test icerigi')[:100]}... Bu icerik test analizi sonucudur."
                }
            else:
                return {"error": f"Unknown endpoint: {endpoint}"}
                
        except Exception as e:
            logger.error(f"API simulation error: {str(e)}")
            return {"error": str(e)}

# Global UI manager
ui_manager = SimpleUIManager()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with two tabs"""
    if 'session_id' not in session:
        session['session_id'] = ui_manager.generate_session_id()
        ui_manager.session_id = session['session_id']
    
    return render_template('index.html', 
                         session_id=session['session_id'],
                         api_base_url=API_BASE_URL)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "backend_status": 200,
        "timestamp": datetime.now().isoformat(),
        "mode": "test"
    })

@app.route('/ai-assistant', methods=['POST'])
def ai_assistant():
    """AI Assistant endpoint - test version"""
    try:
        data = request.json
        user_input = data.get('message', '')
        
        if not user_input:
            return jsonify({"error": "Message is required"}), 400
        
        # Simulate AI processing
        result = {
            "success": True,
            "response": f"AI Asistan Test Yaniti: {user_input} mesajina yanit olarak, bu sistem test modunda calismaktadir. Gercek AI entegrasyonu icin backend servislerinin calismasi gerekiyor.",
            "system_used": "test_ai_assistant"
        }
        
        # Add to conversation history
        ui_manager.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "assistant": result.get('response'),
            "type": "ai_assistant"
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in AI assistant: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/manual/<operation>', methods=['POST'])
def manual_operation(operation):
    """Manual operation endpoints - test version"""
    try:
        data = request.json or {}
        
        # Simulate operation
        result = ui_manager.call_api(f"/{operation.replace('-', '/')}", "POST", data)
        
        # Add to conversation history
        ui_manager.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "input": data,
            "output": result,
            "type": "manual"
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in manual operation {operation}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """File upload endpoint - test version"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            return jsonify({
                "message": "File uploaded successfully (test mode)",
                "filename": filename,
                "result": {
                    "success": True,
                    "content_length": os.path.getsize(filepath),
                    "processed": True
                }
            })
        else:
            return jsonify({"error": "File type not allowed"}), 400
            
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/export/<format>')
def export_data(format):
    """Export conversation data in various formats"""
    try:
        if format not in ['pdf', 'json', 'markdown']:
            return jsonify({"error": "Unsupported format"}), 400
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'json':
            filename = f"conversation_history_{timestamp}.json"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(ui_manager.conversation_history, f, ensure_ascii=False, indent=2)
                
        elif format == 'markdown':
            filename = f"conversation_history_{timestamp}.md"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            content = "# Promptitron Konusma Gecmisi (Test)\n\n"
            for item in ui_manager.conversation_history:
                content += f"## {item['timestamp']}\n\n"
                if item['type'] == 'ai_assistant':
                    content += f"**Kullanici:** {item['user']}\n\n"
                    content += f"**Asistan:** {item['assistant']}\n\n"
                else:
                    content += f"**Islem:** {item['operation']}\n\n"
                content += "---\n\n"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                
        elif format == 'pdf':
            filename = f"conversation_history_{timestamp}.pdf"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            story.append(Paragraph("Promptitron Konusma Gecmisi (Test)", styles['Title']))
            story.append(Spacer(1, 20))
            
            for item in ui_manager.conversation_history:
                if item['type'] == 'ai_assistant':
                    story.append(Paragraph(f"Kullanici: {item['user']}", styles['Normal']))
                    story.append(Paragraph(f"Asistan: {item['assistant']}", styles['Normal']))
                    story.append(Spacer(1, 12))
            
            doc.build(story)
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/curriculum')
def get_curriculum():
    """Get curriculum hierarchy - test version"""
    try:
        return jsonify(SAMPLE_CURRICULUM)
    except Exception as e:
        logger.error(f"Error getting curriculum: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Promptitron Web Interface (Test Mode)")
    print("Access the application at: http://localhost:5000")
    print("This is a test version - backend services simulated")
    app.run(host='0.0.0.0', port=5000, debug=True)