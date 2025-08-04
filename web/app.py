
"""
Copyright (c) 2024-2025 PromptiTron Team. All rights reserved.

This file is part of PromptiTron™ Unified Educational AI System.

PROPRIETARY SOFTWARE - DO NOT COPY, DISTRIBUTE, OR MODIFY
This software is the exclusive property of PromptiTron Team.
Unauthorized use, copying, distribution, or modification is strictly prohibited.
For licensing information, contact the PromptiTron Team.

PromptiTron™ is a trademark of the PromptiTron Team.
"""
Promptitron Unified Web Interface
Flask-based web application with AI Assistant and Manual modes
"""

import os
import sys
import json
import asyncio
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from flask import Flask, render_template, request, jsonify, session, send_file, flash, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from markupsafe import Markup
import markdown2
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.gemini_client import gemini_client
from core.rag_system import rag_system
from core.agents import agent_system
from core.conversation_memory import conversation_memory
from models.structured_models import *
from config import settings

# Initialize Flask app
app = Flask(__name__)
app.secret_key = settings.SECRET_KEY
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API base URL
API_BASE_URL = "http://localhost:5008"

# Upload configurations
UPLOAD_FOLDER = settings.UPLOAD_DIR
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'md', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = settings.MAX_UPLOAD_SIZE

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class WebUIManager:
    """Manages web UI interactions and API calls"""
    
    def __init__(self):
        self.session_id = None
        self.student_profile = {}
        self.conversation_history = []
        
    def generate_session_id(self) -> str:
        """Generate a new session ID"""
        import uuid
        return str(uuid.uuid4())
    
    async def call_api(self, endpoint: str, method: str = "POST", data: dict = None) -> dict:
        """Make API calls to the FastAPI backend"""
        try:
            url = f"{API_BASE_URL}{endpoint}"
            
            if method.upper() == "GET":
                response = requests.get(url, params=data)
            elif method.upper() == "POST":
                response = requests.post(url, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == 200:
                return response.json()
            else:
                error_text = response.text
                logger.error(f"API call failed: {response.status_code} - {error_text}")
                return {"error": f"API call failed: {response.status_code}", "details": error_text}
                
        except Exception as e:
            logger.error(f"Error calling API: {str(e)}")
            return {"error": str(e)}
    
    def process_ai_assistant_request(self, user_input: str, context: dict = None) -> dict:
        """Process request through AI Assistant flow"""
        try:
            # Determine intent and route to appropriate expert
            intent = self.classify_intent(user_input)
            
            # Prepare request data
            request_data = {
                "message": user_input,
                "session_id": self.session_id,
                "use_memory": True,
                "context": context or {}
            }
            
            # Route to appropriate endpoint based on intent
            if intent["type"] == "question_generation":
                return self.generate_questions(intent["subject"], intent["topic"])
            elif intent["type"] == "study_plan":
                return self.create_study_plan(intent["profile"])
            elif intent["type"] == "content_analysis":
                return self.analyze_content(user_input)
            else:
                # Default to chat
                return asyncio.run(self.call_api("/chat", "POST", request_data))
                
        except Exception as e:
            logger.error(f"Error in AI assistant: {str(e)}")
            return {"error": str(e)}
    
    def classify_intent(self, user_input: str) -> dict:
        """Classify user intent for intelligent routing"""
        user_lower = user_input.lower()
        
        # Intent patterns
        if any(word in user_lower for word in ["soru", "test", "quiz", "sorular"]):
            return {
                "type": "question_generation",
                "subject": self.extract_subject(user_input),
                "topic": self.extract_topic(user_input)
            }
        elif any(word in user_lower for word in ["plan", "çalışma", "program", "takvim"]):
            return {
                "type": "study_plan",
                "profile": self.get_current_profile()
            }
        elif any(word in user_lower for word in ["analiz", "değerlendir", "incele"]):
            return {
                "type": "content_analysis"
            }
        else:
            return {"type": "chat"}
    
    def extract_subject(self, text: str) -> str:
        """Extract subject from user input"""
        subjects = {
            "matematik": "MATEMATIK",
            "fizik": "FIZIK", 
            "kimya": "KIMYA",
            "biyoloji": "BIYOLOJI",
            "tarih": "TARIH",
            "coğrafya": "COGRAFYA",
            "türkçe": "TURK_DILI_VE_EDEBIYATI",
            "felsefe": "FELSEFE"
        }
        
        text_lower = text.lower()
        for key, value in subjects.items():
            if key in text_lower:
                return value
        return "MATEMATIK"  # Default
    
    def extract_topic(self, text: str) -> str:
        """Extract topic from user input"""
        # Simple topic extraction - can be enhanced with NLP
        words = text.split()
        # Return last noun-like word as topic
        return words[-1] if words else "genel"
    
    def get_current_profile(self) -> dict:
        """Get current student profile"""
        return self.student_profile or {
            "student_id": self.session_id,
            "target_exam": "TYT",
            "weak_subjects": [],
            "strong_subjects": [],
            "daily_hours": 6
        }
    
    def generate_questions(self, subject: str, topic: str) -> dict:
        """Generate questions using API"""
        data = {
            "subject": subject,
            "topic": topic,
            "difficulty": "MEDIUM",
            "question_type": "MULTIPLE_CHOICE",
            "count": 3,
            "exam_type": "TYT"
        }
        return asyncio.run(self.call_api("/generate/questions", "POST", data))
    
    def create_study_plan(self, profile: dict) -> dict:
        """Create study plan using API"""
        data = {
            "student_profile": profile,
            "target_exam": "TYT",
            "duration_weeks": 12,
            "daily_hours": profile.get("daily_hours", 6)
        }
        return asyncio.run(self.call_api("/generate/study-plan", "POST", data))
    
    def analyze_content(self, content: str) -> dict:
        """Analyze content using API"""
        data = {
            "content": content,
            "analysis_type": "comprehensive",
            "include_suggestions": True
        }
        return asyncio.run(self.call_api("/analyze/content", "POST", data))

# Global UI manager
ui_manager = WebUIManager()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_pdf_report(content: str, title: str = "Rapor") -> str:
    """Generate PDF report from content"""
    try:
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{title}_{timestamp}.pdf"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Create PDF
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 20))
        
        # Content
        content_style = styles['Normal']
        content_style.fontSize = 12
        content_style.leading = 16
        
        # Convert markdown to HTML and then to PDF paragraphs
        html_content = markdown2.markdown(content)
        # Simple conversion - can be enhanced
        paragraphs = html_content.split('\n')
        
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para, content_style))
                story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        
        return filename
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return None

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
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return jsonify({
            "status": "healthy" if response.status_code == 200 else "unhealthy",
            "backend_status": response.status_code,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/ai-assistant', methods=['POST'])
def ai_assistant():
    """AI Assistant endpoint"""
    try:
        data = request.json
        user_input = data.get('message', '')
        context = data.get('context', {})
        
        if not user_input:
            return jsonify({"error": "Message is required"}), 400
        
        # Process through AI assistant
        result = ui_manager.process_ai_assistant_request(user_input, context)
        
        # Add to conversation history
        ui_manager.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "assistant": result.get('response', result.get('error', 'No response')),
            "type": "ai_assistant"
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in AI assistant: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/manual/<operation>', methods=['POST'])
def manual_operation(operation):
    """Manual operation endpoints"""
    try:
        data = request.json or {}
        
        # Route to appropriate operation
        if operation == 'chat':
            result = asyncio.run(ui_manager.call_api("/chat", "POST", data))
        elif operation == 'generate-questions':
            result = asyncio.run(ui_manager.call_api("/generate/questions", "POST", data))
        elif operation == 'generate-study-plan':
            result = asyncio.run(ui_manager.call_api("/generate/study-plan", "POST", data))
        elif operation == 'search':
            result = asyncio.run(ui_manager.call_api("/search", "POST", data))
        elif operation == 'analyze-content':
            result = asyncio.run(ui_manager.call_api("/analyze/content", "POST", data))
        else:
            return jsonify({"error": f"Unknown operation: {operation}"}), 400
        
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
    """File upload endpoint"""
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
            
            # Process file through API
            with open(filepath, 'rb') as f:
                files = {'file': (filename, f, file.content_type)}
                response = requests.post(
                    f"{API_BASE_URL}/upload/document",
                    files=files,
                    data={'description': request.form.get('description', '')}
                )
            
            if response.status_code == 200:
                return jsonify({
                    "message": "File uploaded successfully",
                    "filename": filename,
                    "result": response.json()
                })
            else:
                return jsonify({"error": "Failed to process file"}), 500
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
        
        # Prepare content
        if format == 'json':
            filename = f"conversation_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(ui_manager.conversation_history, f, ensure_ascii=False, indent=2)
                
        elif format == 'markdown':
            filename = f"conversation_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            content = "# Promptitron Konuşma Geçmişi\n\n"
            for item in ui_manager.conversation_history:
                content += f"## {item['timestamp']}\n\n"
                if item['type'] == 'ai_assistant':
                    content += f"**Kullanıcı:** {item['user']}\n\n"
                    content += f"**Asistan:** {item['assistant']}\n\n"
                else:
                    content += f"**İşlem:** {item['operation']}\n\n"
                    content += f"**Giriş:** ```json\n{json.dumps(item['input'], ensure_ascii=False, indent=2)}\n```\n\n"
                content += "---\n\n"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                
        elif format == 'pdf':
            content = ""
            for item in ui_manager.conversation_history:
                if item['type'] == 'ai_assistant':
                    content += f"Kullanıcı: {item['user']}\n\n"
                    content += f"Asistan: {item['assistant']}\n\n"
                content += "---\n\n"
            
            filename = generate_pdf_report(content, "Konuşma Geçmişi")
            if not filename:
                return jsonify({"error": "Failed to generate PDF"}), 500
            filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/curriculum')
def get_curriculum():
    """Get curriculum hierarchy using enhanced loader"""
    try:
        from core.curriculum_loader import curriculum_loader
        
        # Ensure curriculum is loaded
        if not curriculum_loader.curriculum_data:
            success = curriculum_loader.load_all_curriculum()
            if not success:
                return jsonify({"error": "Failed to load curriculum"}), 500
        
        # Get curriculum summary for web interface
        summary = curriculum_loader.get_curriculum_summary()
        
        # Prepare data for frontend
        curriculum_data = {}
        for subject in curriculum_loader.curriculum_data.keys():
            topics = curriculum_loader.get_subject_topics(subject)
            
            # Group topics by grade
            grades = {}
            for topic in topics:
                grade = topic.get('grade', 'Genel')
                if grade not in grades:
                    grades[grade] = []
                
                grades[grade].append({
                    "code": topic['code'],
                    "title": topic['title'],
                    "content": topic['content'][:100] + "..." if len(topic['content']) > 100 else topic['content'],
                    "terms": topic.get('terms', ''),
                    "path": topic['path']
                })
            
            curriculum_data[subject] = {
                "total_topics": len(topics),
                "grades": grades,
                "summary": f"{len(topics)} konular {len(grades)} sınıf seviyesinde"
            }
        
        return jsonify({
            "success": True,
            "summary": summary,
            "curriculum": curriculum_data
        })
        
    except Exception as e:
        logger.error(f"Error getting curriculum: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)