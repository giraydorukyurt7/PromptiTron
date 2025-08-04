"""
Promptitron Console Interface
Konsol tabanlı AI Assistant uygulaması

Copyright (c) 2024-2025 PromptiTron Team. All rights reserved.

This file is part of PromptiTron™ Unified Educational AI System.

PROPRIETARY SOFTWARE - DO NOT COPY, DISTRIBUTE, OR MODIFY
This software is the exclusive property of PromptiTron Team.
Unauthorized use, copying, distribution, or modification is strictly prohibited.
For licensing information, contact the PromptiTron Team.

PromptiTron™ is a trademark of the PromptiTron Team.
"""

import os
import sys
import json
import asyncio
import requests
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.panel import Panel
from rich.text import Text
import colorama

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.gemini_client import gemini_client
from core.rag_system import rag_system
from core.agents import agent_system
from core.conversation_memory import conversation_memory
from core.document_understanding import document_understanding
from core.hierarchical_menu import hierarchical_menu
from models.structured_models import *
from config import settings

# Initialize colorama for Windows
colorama.init()

# Console instance with Windows compatibility
import os
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

console = Console(force_terminal=True, width=120, color_system="windows" if sys.platform.startswith('win') else "truecolor")

# Configure logging with Rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)

# API base URL
API_BASE_URL = "http://localhost:8000"

class ConsoleManager:
    """Konsol tabanlı uygulama yöneticisi"""
    
    def __init__(self):
        self.session_id = self.generate_session_id()
        self.conversation_history = []
        self.current_mode = "ai_assistant"
        
    def generate_session_id(self) -> str:
        """Generate a new session ID"""
        import uuid
        return str(uuid.uuid4())
    
    def log_http_request(self, method: str, url: str, status_code: int, response_time: float, error: str = None):
        """HTTP isteklerini konsola logla"""
        if error:
            console.print(f"[red][X] {method} {url} - ERROR: {error}[/red]")
        elif status_code >= 200 and status_code < 300:
            console.print(f"[green][OK] {method} {url} - {status_code} ({response_time:.2f}s)[/green]")
        elif status_code >= 400 and status_code < 500:
            console.print(f"[yellow][\!] {method} {url} - {status_code} ({response_time:.2f}s)[/yellow]")
        else:
            console.print(f"[red][ERR] {method} {url} - {status_code} ({response_time:.2f}s)[/red]")
    
    def log_langgraph_activity(self, activity: str, data: dict = None, node: str = None, state: dict = None):
        """LangGraph aktivitelerini detaylı olarak logla"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"[blue][LG] [{timestamp}] LangGraph: {activity}"
        if node:
            msg += f" (Node: {node})"
        msg += "[/blue]"
        console.print(msg)
        
        if data:
            console.print(f"[dim]  Data: {json.dumps(data, indent=2, ensure_ascii=False)}[/dim]")
        if state:
            console.print(f"[dim]  State: {json.dumps(state, indent=2, ensure_ascii=False)}[/dim]")
    
    def log_langchain_activity(self, activity: str, data: dict = None, chain_type: str = None, tokens: int = None):
        """LangChain aktivitelerini detaylı olarak logla"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"[magenta][LC] [{timestamp}] LangChain: {activity}"
        if chain_type:
            msg += f" (Chain: {chain_type})"
        if tokens:
            msg += f" (Tokens: {tokens})"
        msg += "[/magenta]"
        console.print(msg)
        
        if data:
            console.print(f"[dim]  Input: {json.dumps(data, indent=2, ensure_ascii=False)}[/dim]")
    
    def log_crewai_activity(self, activity: str, agent: str = None, task: str = None, status: str = None, result: str = None):
        """CrewAI aktivitelerini detaylı olarak logla"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"[cyan][AI] [{timestamp}] CrewAI: {activity}"
        if agent:
            msg += f" - Agent: {agent}"
        if task:
            msg += f" - Task: {task}"
        if status:
            msg += f" - Status: {status}"
        msg += "[/cyan]"
        console.print(msg)
        
        if result:
            console.print(f"[dim]  Result: {result[:100]}{'...' if len(result) > 100 else ''}[/dim]")
    
    def log_mcp_activity(self, activity: str, tool: str = None, params: dict = None, result: str = None, duration: float = None):
        """MCP aktivitelerini detaylı olarak logla"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"[yellow][MCP] [{timestamp}] MCP: {activity}"
        if tool:
            msg += f" - Tool: {tool}"
        if duration:
            msg += f" ({duration:.2f}s)"
        msg += "[/yellow]"
        console.print(msg)
        
        if params:
            console.print(f"[dim]  Params: {json.dumps(params, indent=2, ensure_ascii=False)}[/dim]")
        if result:
            console.print(f"[dim]  Result: {result[:150]}{'...' if len(result) > 150 else ''}[/dim]")
    
    def log_rag_activity(self, activity: str, query: str = None, results_count: int = None, collection: str = None):
        """RAG aktivitelerini logla"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"[green][RAG] [{timestamp}] RAG: {activity}"
        if collection:
            msg += f" (Collection: {collection})"
        if results_count is not None:
            msg += f" - Found {results_count} results"
        msg += "[/green]"
        console.print(msg)
        
        if query:
            console.print(f"[dim]  Query: {query}[/dim]")
    
    def log_gemini_activity(self, activity: str, model: str = None, tokens_used: int = None, response_time: float = None):
        """Gemini aktivitelerini logla"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"[purple][BRAIN] [{timestamp}] Gemini: {activity}"
        if model:
            msg += f" (Model: {model})"
        if tokens_used:
            msg += f" - Tokens: {tokens_used}"
        if response_time:
            msg += f" ({response_time:.2f}s)"
        msg += "[/purple]"
        console.print(msg)
    
    async def call_api(self, endpoint: str, method: str = "POST", data: dict = None) -> dict:
        """Make API calls to the FastAPI backend with logging"""
        import time
        start_time = time.time()
        
        try:
            url = f"{API_BASE_URL}{endpoint}"
            
            # Log request
            console.print(f"\n[dim]-> {method} {url}[/dim]")
            if data:
                console.print(f"[dim]  Request Data: {json.dumps(data, indent=2)}[/dim]")
            
            if method.upper() == "GET":
                response = requests.get(url, params=data)
            elif method.upper() == "POST":
                response = requests.post(url, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = time.time() - start_time
            
            # Log response
            self.log_http_request(method, url, response.status_code, response_time)
            
            if response.status_code == 200:
                result = response.json()
                console.print(f"[dim]  Response: {json.dumps(result, indent=2)[:200]}...[/dim]")
                return result
            else:
                error_text = response.text
                self.log_http_request(method, url, response.status_code, response_time, error_text)
                return {"error": f"API call failed: {response.status_code}", "details": error_text}
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_http_request(method, url, 0, response_time, str(e))
            return {"error": str(e)}
    
    def display_menu(self):
        """Ana menüyü göster"""
        table = Table(title="🎓 Promptitron Console Menu", show_header=False)
        table.add_column("Seçenek", style="cyan", width=12)
        table.add_column("Açıklama", style="white")
        
        table.add_row("1", "🤖 AI Asistan Modu - Ders soruları sorun ve açıklama alın")
        table.add_row("2", "❓ Soru Oluştur - Tüm derslerden test soruları üretin")
        table.add_row("3", "📅 Çalışma Planı - Kişiselleştirilmiş YKS hazırlık planı")
        table.add_row("4", "🔍 Bilgi Ara - Müfredat ve konu bilgilerinde arama")
        table.add_row("5", "📊 İçerik Analizi - Metin zorluk analizi")
        table.add_row("6", "📄 Doküman Analizi - PDF, Word analizi + soru çıkarma")
        table.add_row("7", "📚 Müfredat Göster - Ders müfredatlarını inceleyin")
        table.add_row("8", "📤 Geçmiş Dışa Aktar - Konuşma geçmişinizi kaydedin")
        table.add_row("9", "⚙️ Sistem Durumu - API ve servis durumları")
        table.add_row("10", "🛠️ Ayarlar - Konfigürasyon seçenekleri")
        table.add_row("0", "🚪 Çıkış - Uygulamadan çıkın")
        
        console.print(table)
    
    async def ai_assistant_mode(self):
        """AI Assistant modu - Expert routing ile"""
        console.print(Panel("[bold green]AI Assistant Mode[/bold green]"))
        
        # Mod seçimi
        console.print("\n[bold cyan]Asistan Modu Seçimi:[/bold cyan]")
        console.print("1. 📚 Normal Mod - Doğrudan cevaplar ve açıklamalar")
        console.print("2. 🎓 Sokratik Mod - Sorularla öğrenme ve keşfetme")
        console.print("3. ← Ana Menüye Dön")
        
        mode_choice = Prompt.ask("\nSeçiminiz", choices=["1", "2", "3"])
        
        if mode_choice == "3":
            return
        
        socratic_mode = (mode_choice == "2")
        
        if socratic_mode:
            console.print(Panel("[bold magenta]🎓 Sokratik Mod Aktif[/bold magenta]"))
            console.print("[dim]Bu modda size doğrudan cevap vermek yerine, düşündürücü sorular soracağım.[/dim]")
            console.print("[dim]Amacım sizin kendi cevabınızı bulmanıza yardımcı olmak.[/dim]")
            
            # Import Socratic agent
            from core.socratic_agent import socratic_agent
            
            # Konu seçimi
            topic = Prompt.ask("\n[bold]Hangi konuda konuşmak istersiniz?[/bold]")
            socratic_context = {"topic": topic}
        else:
            console.print(Panel("[bold green]📚 Normal Asistan Modu[/bold green]"))
            console.print("[dim]Type 'exit' to return to menu, 'expert list' to see available experts[/dim]")
        
        console.print("[dim]Çıkmak için 'exit' yazın[/dim]\n")
        
        while True:
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
            
            if user_input.lower() == 'exit':
                if socratic_mode:
                    # Sokratik mod özeti
                    if Confirm.ask("\nKonuşma özetini görmek ister misiniz?"):
                        summary = socratic_agent.get_conversation_summary()
                        console.print(Panel(summary, title="Konuşma Özeti", border_style="cyan"))
                    socratic_agent.reset_memory()
                break
            elif user_input.lower() == 'expert list' and not socratic_mode:
                console.print("\n[bold cyan]🎓 Mevcut Uzmanlar:[/bold cyan]")
                experts = [
                    "Matematik Uzmanı", "Fizik Uzmanı", "Kimya Uzmanı", "Biyoloji Uzmanı",
                    "Türk Dili ve Edebiyatı Uzmanı", "Tarih Uzmanı", "Coğrafya Uzmanı", 
                    "Felsefe Uzmanı", "Din Kültürü Uzmanı", "İnkılap ve Atatürkçülük Uzmanı", 
                    "Genel Eğitim Uzmanı"
                ]
                for expert in experts:
                    console.print(f"  • {expert}")
                console.print("\n[dim]İpucu: Sorunuzun başına ders adını yazarak o uzmanla konuşabilirsiniz[/dim]")
                console.print("[dim]Örnek: 'matematik türev konusunu açıkla' veya 'edebiyat cumhuriyet dönemi'[/dim]")
                continue
            
            # Process request
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Processing...", total=None)
                
                if socratic_mode:
                    # Sokratik mod için özel işlem
                    start_time = time.time()
                    result = await socratic_agent.process(user_input, socratic_context)
                    processing_time = time.time() - start_time
                else:
                    # Normal mod - API çağrısı
                    # Log detailed activity
                    self.log_langgraph_activity(
                        "Intent Classification", 
                        {"input": user_input[:100] + "..." if len(user_input) > 100 else user_input},
                        node="classifier"
                    )
                    
                    self.log_langchain_activity(
                        "Chat Request Processing",
                        {"session_id": self.session_id, "use_memory": True},
                        chain_type="ConversationalRetrieval"
                    )
                    
                    start_time = time.time()
                    result = await self.call_api("/chat", "POST", {
                        "message": user_input,
                        "session_id": self.session_id,
                        "use_memory": True
                    })
                    processing_time = time.time() - start_time
                    
                    # Log completion
                    if result.get("success"):
                        self.log_gemini_activity(
                            "Response Generated",
                            model="gemini-2.5-flash",
                            response_time=processing_time
                        )
                
                progress.stop()
            
            # Display response
            if "response" in result:
                if socratic_mode:
                    console.print(f"\n[bold magenta]Sokrates[/bold magenta]: {result['response']}")
                    
                    # Sokratik ipuçları göster (sadece debug modda)
                    if result.get("hints") and settings.DEBUG:
                        console.print("\n[dim]Öğretmen için ipuçları:[/dim]")
                        for hint in result["hints"]:
                            console.print(f"[dim]{hint}[/dim]")
                else:
                    console.print(f"\n[bold magenta]Assistant[/bold magenta]: {result['response']}")
                
                # Save to conversation history
                self.conversation_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "user": user_input,
                    "assistant": result['response'],
                    "system_used": result.get("system_used", "Unknown"),
                    "processing_time": processing_time
                })
                
                # Log detailed agent activities
                if result.get("system_used"):
                    if "CrewAI" in result["system_used"]:
                        self.log_crewai_activity(
                            "Task Completed", 
                            agent=result.get("agent_used", "Unknown"),
                            status="success",
                            result=result['response']
                        )
                    elif "Gemini" in result["system_used"]:
                        self.log_gemini_activity(
                            "Direct Response",
                            model="gemini-2.5-flash"
                        )
                
                # Log tool usage
                if result.get("tools_used"):
                    for tool in result["tools_used"]:
                        self.log_mcp_activity(
                            "Tool Execution Completed", 
                            tool=tool,
                            result="Success"
                        )
                        
                # Log memory operations
                if result.get("use_memory"):
                    self.log_langchain_activity(
                        "Memory Updated",
                        {"session_id": self.session_id},
                        chain_type="ConversationMemory"
                    )
            else:
                console.print(f"[red]Error: {result.get('error', 'Unknown error')}[/red]")
                # Log error details
                self.log_http_request("POST", "/chat", 500, 0, result.get('error'))
    
    async def generate_questions(self):
        """Hiyerarşik soru oluşturma sistemi"""
        from core.unified_curriculum import unified_curriculum
        
        console.print(Panel("[bold yellow]🎯 HIYERAŞİK SORU OLUŞTURMA SİSTEMİ[/bold yellow]"))
        
        # 1. Ders Seçimi
        subject_result = hierarchical_menu.show_subject_selection()
        if not subject_result:
            return
        subject_name, subject_code = subject_result
        
        # 2. Sınıf Seçimi
        grade = hierarchical_menu.show_grade_selection(subject_name, subject_code)
        if not grade:
            return
            
        # 3. Ünite Seçimi
        unit_result = hierarchical_menu.show_unit_selection(subject_name, subject_code, grade)
        if not unit_result:
            return
        unit_code, unit_title = unit_result
        
        # 4. Alt Konu Seçimi
        subtopic_result = hierarchical_menu.show_subtopic_selection(subject_name, subject_code, grade, unit_code)
        if not subtopic_result:
            return
        subtopic_code, subtopic_title = subtopic_result
        
        # 5. Soru Parametreleri
        console.print(f"\n[bold cyan]📝 SORU PARAMETRELERİ[/bold cyan]")
        console.print(Panel(f"Seçilen: {subject_name} > {grade}. Sınıf > {unit_code} > {subtopic_code}", title="Seçim Özeti"))
        
        # Zorluk seviyesi
        difficulty_choices = {
            "1. Kolay": "easy",
            "2. Orta": "medium", 
            "3. Zor": "hard"
        }
        
        console.print("\n[bold cyan]Zorluk Seviyeleri:[/bold cyan]")
        for choice in difficulty_choices.keys():
            console.print(f"  {choice}")
            
        difficulty_display = Prompt.ask("\nZorluk seviyesi", choices=list(difficulty_choices.keys()), default="2. Orta")
        difficulty = difficulty_choices[difficulty_display]
        
        # Soru tipi
        question_type_choices = {
            "1. Çoktan Seçmeli": "multiple_choice",
            "2. Doğru-Yanlış": "true_false",
            "3. Boşluk Doldurma": "fill_blank",
            "4. Kısa Cevap": "short_answer",
            "5. Açık Uçlu": "essay"
        }
        
        console.print("\n[bold cyan]Soru Tipleri:[/bold cyan]")
        for choice in question_type_choices.keys():
            console.print(f"  {choice}")
            
        question_type_display = Prompt.ask("\nSoru tipi", choices=list(question_type_choices.keys()), default="1. Çoktan Seçmeli")
        question_type = question_type_choices[question_type_display]
        
        count = int(Prompt.ask("Soru sayısı", default="3"))
        
        # Otomatik TYT/AYT seçimi - 9-10. sınıf TYT, 11-12. sınıf AYT
        grade_num = int(grade)
        if grade_num in [9, 10]:
            exam_type = "TYT"
        elif grade_num in [11, 12]:
            exam_type = "AYT"
        else:
            exam_type = "TYT"  # Default
        
        # Detaylı konu bilgisi oluştur
        detailed_topic = f"{subject_name} {grade}. Sınıf {unit_code}"
        if subtopic_code != "ALL":
            detailed_topic += f" {subtopic_code}"
            
        console.print(f"\n[bold green]🎯 SORU OLUŞTURMA BAŞLADI[/bold green]")
        console.print(f"Konu: {detailed_topic}")
        console.print(f"Zorluk: {difficulty}, Tip: {question_type}, Sayı: {count}")
        console.print(f"Sınav Tipi: {exam_type} (Sınıf {grade} için otomatik seçildi)")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Hiyerarşik sorular oluşturuluyor...", total=None)
            
            # Log detailed question generation process
            self.log_crewai_activity(
                "Hierarchical Question Generation Started",
                agent="UnifiedAgentSystem",
                task=f"{subject_name} - {detailed_topic}",
                status="processing"
            )
            
            self.log_rag_activity(
                "Hierarchical Curriculum Search",
                query=detailed_topic,
                collection="curriculum"
            )
            
            self.log_langchain_activity(
                "Hierarchical Question Generation Chain", 
                {
                    "subject": subject_code,
                    "topic": detailed_topic,
                    "difficulty": difficulty,
                    "count": count,
                    "grade": grade,
                    "unit": unit_code,
                    "subtopic": subtopic_code
                },
                chain_type="HierarchicalQuestionGeneration"
            )
            
            start_time = time.time()
            result = await self.call_api("/generate/questions", "POST", {
                "subject": subject_code,
                "topic": detailed_topic,
                "difficulty": difficulty,
                "question_type": question_type,
                "count": count,
                "exam_type": exam_type
            })
            generation_time = time.time() - start_time
            
            progress.stop()
            
            # Log completion
            if result.get("success"):
                self.log_crewai_activity(
                    "Question Generation Completed",
                    agent="QuestionGeneratorAgent",
                    status="completed",
                    result=f"Generated {len(result.get('questions', []))} questions"
                )
                self.log_gemini_activity(
                    "Questions Generated",
                    model="gemini-2.5-flash",
                    response_time=generation_time
                )
        
        if "questions" in result:
            questions = result["questions"]
            
            # Handle both string and list formats
            if isinstance(questions, str):
                # If questions is a string, display it as raw text
                console.print(f"\n[bold]Generated Questions:[/bold]")
                console.print(questions)
            elif isinstance(questions, list):
                # If questions is a list, process each question
                for i, question in enumerate(questions, 1):
                    console.print(f"\n[bold]Question {i}:[/bold]")
                    
                    if isinstance(question, dict):
                        console.print(question.get("question_text", str(question)))
                        
                        if question.get("options"):
                            for opt_key, opt_value in question["options"].items():
                                console.print(f"  {opt_key}) {opt_value}")
                        
                        console.print(f"[green]Answer: {question.get('correct_answer', '')}[/green]")
                        if question.get("explanation"):
                            console.print(f"[dim]Explanation: {question['explanation']}[/dim]")
                    else:
                        # Handle string questions in list
                        console.print(str(question))
            else:
                console.print(f"[yellow]Questions format: {type(questions)}[/yellow]")
                console.print(str(questions))
        else:
            console.print(f"[red]Error: {result.get('error', 'Unknown error')}[/red]")
            
            # Show raw response for debugging if available
            if "raw_response" in result:
                console.print(f"\n[dim]Raw Response:[/dim]")
                console.print(result["raw_response"][:500] + "..." if len(result["raw_response"]) > 500 else result["raw_response"])
    
    async def create_study_plan(self):
        """Çalışma planı oluştur"""
        console.print(Panel("[bold cyan]Study Plan Creation[/bold cyan]"))
        
        # User-friendly exam choices
        exam_choices = {
            "1. TYT (Temel Yeterlilik Testı)": "TYT",
            "2. AYT (Alan Yeterlilik Testi)": "AYT", 
            "3. YKS (Hem TYT hem AYT)": "YKS"
        }
        
        console.print("\n[bold cyan]Hedef Sınavlar:[/bold cyan]")
        for choice in exam_choices.keys():
            console.print(f"  {choice}")
            
        exam_display = Prompt.ask("\nHedef sınav", choices=list(exam_choices.keys()), default="1. TYT (Temel Yeterlilik Testı)")
        target_exam = exam_choices[exam_display]
        
        duration_weeks = int(Prompt.ask("Kaç haftalık plan? (hafta)", default="12"))
        daily_hours = int(Prompt.ask("Günde kaç saat çalışacaksınız?", default="6"))
        
        # Subject selection for weak/strong areas
        all_subjects = ["Matematik", "Fizik", "Kimya", "Biyoloji", "Türkçe", "Edebiyat", "Tarih", "Coğrafya", "Felsefe", "Din Kültürü", "İnkılap Tarihi"]
        
        console.print(f"\n[bold cyan]Mevcut Dersler:[/bold cyan]")
        for i, subject in enumerate(all_subjects, 1):
            console.print(f"  {i}. {subject}")
        
        weak_input = Prompt.ask("\nZayıf olduğunuz dersleri seçin (virgül ile ayırın, örn: 1,3,5)", default="")
        strong_input = Prompt.ask("Güçlü olduğunuz dersleri seçin (virgül ile ayırın, örn: 2,4,6)", default="")
        
        # Subject name mapping to API format
        subject_mapping = {
            "matematik": "matematik",
            "fizik": "fizik", 
            "kimya": "kimya",
            "biyoloji": "biyoloji",
            "türkçe": "turkce",
            "edebiyat": "edebiyat",
            "tarih": "tarih",
            "coğrafya": "cografya", 
            "felsefe": "felsefe",
            "din kültürü": "din_kulturu",
            "i̇nkılap tarihi": "inkilap_tarihi"
        }
        
        # Convert numbers to subject names
        weak_subjects = []
        if weak_input.strip():
            for item in weak_input.split(","):
                # Extract just the number from inputs like "1. Matematik" or "1"
                num_str = item.strip()
                # Remove any text after number
                if ". " in num_str:
                    num_str = num_str.split(". ")[0]
                # Extract first number found
                num_match = re.search(r'(\d+)', num_str)
                if num_match:
                    try:
                        idx = int(num_match.group(1)) - 1
                        if 0 <= idx < len(all_subjects):
                            subject_name = all_subjects[idx].lower()
                            mapped_subject = subject_mapping.get(subject_name, subject_name)
                            weak_subjects.append(mapped_subject)
                    except ValueError:
                        pass
        
        strong_subjects = []
        if strong_input.strip():
            for item in strong_input.split(","):
                # Extract just the number from inputs like "8. Coğrafya" or "8"
                num_str = item.strip()
                # Remove any text after number
                if ". " in num_str:
                    num_str = num_str.split(". ")[0]
                # Extract first number found
                num_match = re.search(r'(\d+)', num_str)
                if num_match:
                    try:
                        idx = int(num_match.group(1)) - 1
                        if 0 <= idx < len(all_subjects):
                            subject_name = all_subjects[idx].lower()
                            mapped_subject = subject_mapping.get(subject_name, subject_name)
                            strong_subjects.append(mapped_subject)
                    except ValueError:
                        pass
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Creating study plan...", total=None)
            
            # Log detailed study plan creation
            self.log_crewai_activity(
                "Study Plan Creation Started",
                agent="StudyPlannerAgent",
                task=f"{target_exam} - {duration_weeks} weeks",
                status="analyzing"
            )
            
            self.log_mcp_activity(
                "Profile Analysis",
                tool="StudentProfileAnalyzer",
                params={
                    "weak_subjects": weak_subjects,
                    "strong_subjects": strong_subjects,
                    "daily_hours": daily_hours
                }
            )
            
            start_time = time.time()
            result = await self.call_api("/generate/study-plan", "POST", {
                "student_profile": {
                    "student_id": self.session_id,
                    "target_exam": target_exam,
                    "weak_subjects": [s.strip() for s in weak_subjects if s.strip()],
                    "strong_subjects": [s.strip() for s in strong_subjects if s.strip()],
                    "daily_hours": daily_hours
                },
                "target_exam": target_exam,
                "duration_weeks": duration_weeks,
                "daily_hours": daily_hours
            })
            planning_time = time.time() - start_time
            
            progress.stop()
            
            # Log completion
            if result.get("success"):
                self.log_crewai_activity(
                    "Study Plan Created",
                    agent="StudyPlannerAgent", 
                    status="completed",
                    result=f"Created {duration_weeks}-week plan"
                )
                self.log_mcp_activity(
                    "Plan Optimization Completed",
                    tool="StudyPlanOptimizer",
                    duration=planning_time
                )
        
        if "study_plan" in result:
            plan = result["study_plan"]
            
            # Handle both string and dict responses
            if isinstance(plan, str):
                # If plan is a string, display it as formatted text
                console.print(f"\n[bold green]📅 KİŞİSELLEŞTİRİLMİŞ ÇALIŞMA PLANI[/bold green]")
                console.print(Panel(plan, title=f"{duration_weeks} Haftalık YKS Çalışma Planı", expand=False))
                
                # Show summary
                console.print(f"\n[bold]Plan Özeti:[/bold]")
                console.print(f"• Hedef Sınav: {target_exam}")
                console.print(f"• Süre: {duration_weeks} hafta")
                console.print(f"• Günlük Çalışma: {daily_hours} saat")
                if weak_subjects:
                    console.print(f"• Zayıf Dersler: {', '.join([s.replace('_', ' ').title() for s in weak_subjects])}")
                if strong_subjects:
                    console.print(f"• Güçlü Dersler: {', '.join([s.replace('_', ' ').title() for s in strong_subjects])}")
                    
            elif isinstance(plan, dict):
                # Handle structured plan format
                console.print(f"\n[bold]Study Plan: {plan.get('plan_name', 'Custom Plan')}[/bold]")
                console.print(f"Duration: {plan.get('duration_weeks', 0)} weeks")
                console.print(f"Daily Hours: {plan.get('daily_hours', 0)}")
                
                if plan.get("weekly_schedule"):
                    for week in plan["weekly_schedule"]:
                        console.print(f"\n[bold]Week {week.get('week_number', 0)}:[/bold]")
                        for day in week.get("days", []):
                            console.print(f"  {day.get('day', '')}: {', '.join(day.get('subjects', []))}")
        else:
            console.print(f"[red]Error: {result.get('error', 'Unknown error')}[/red]")
    
    async def search_knowledge(self):
        """Bilgi tabanında arama - Expert routing ile"""
        console.print(Panel("[bold green]Knowledge Base Search[/bold green]"))
        
        console.print("\n[bold cyan]Arama Modları:[/bold cyan]")
        console.print("  1. Genel Arama - Tüm konularda ara")
        console.print("  2. Uzman Araması - Belirli ders uzmanı ile ara")
        
        search_mode = Prompt.ask("Arama modu", choices=["1", "2"], default="1")
        
        if search_mode == "2":
            # Subject-specific expert search
            subject_choices = {
                "1. Matematik": "matematik",
                "2. Fizik": "fizik", 
                "3. Kimya": "kimya",
                "4. Biyoloji": "biyoloji",
                "5. Türk Dili ve Edebiyatı": "turk_dili_ve_edebiyati",
                "6. Tarih": "tarih",
                "7. Coğrafya": "cografya",
                "8. Felsefe": "felsefe",
                "9. Din Kültürü": "din_kulturu",
                "10. İnkılap ve Atatürkçülük": "inkilap_ve_ataturkculuk"
            }
            
            console.print("\n[bold cyan]Uzman Dersleri:[/bold cyan]")
            for choice in subject_choices.keys():
                console.print(f"  {choice}")
            
            subject_display = Prompt.ask("Hangi dersin uzmanı ile arama yapmak istiyorsunuz?", 
                                       choices=list(subject_choices.keys()))
            selected_subject = subject_choices[subject_display]
            
            console.print(f"\n[bold cyan]{subject_display} Uzmanı ile Arama:[/bold cyan]")
            console.print("  • Konu bazlı sorular sorabilirsiniz")
            console.print("  • Kavramları açıklattırabilirsiniz") 
            console.print("  • Örnekler isteyebilirsiniz")
        
        query = Prompt.ask("\nArama sorgusu/Sorunuz")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Searching...", total=None)
            
            # Log detailed search process
            self.log_rag_activity(
                "Knowledge Base Search Started",
                query=query,
                collection="all"
            )
            
            if search_mode == "2":
                # Expert-guided search
                self.log_crewai_activity(
                    f"Expert Search - {selected_subject.title()} Uzmanı",
                    agent=f"{selected_subject.title()}Expert",
                    task=query,
                    status="processing"
                )
                
                # Use AI assistant with subject context
                start_time = time.time()
                result = await self.call_api("/chat", "POST", {
                    "message": f"[{selected_subject.upper()} UZMANI] {query}",
                    "context": {"subject": selected_subject, "search_mode": "expert"},
                    "session_id": self.session_id
                })
                search_time = time.time() - start_time
                progress.remove_task(task)
                
                if result.get("success", True) and not result.get("error"):
                    
                    console.print(f"\n[bold green]🎓 {subject_display} Uzmanı Yanıtı:[/bold green]")
                    console.print(result.get('response', 'Yanıt alınamadı'))
                    
                    if result.get('system_used'):
                        console.print(f"\n[dim]Sistem: {result['system_used']}[/dim]")
                        
                    self.log_crewai_activity(
                        f"Expert Search Completed - {selected_subject.title()}",
                        agent=f"{selected_subject.title()}Expert",
                        task=query,
                        status="completed",
                        result=result.get('response', '')[:100] + "..."
                    )
                else:
                    console.print(f"[red]Uzman arama hatası: {result.get('error', 'Bilinmeyen hata')}[/red]")
                    
            else:
                # General RAG search
                self.log_langchain_activity(
                    "Vector Search", 
                    {"query": query},
                    chain_type="RetrievalQA"
                )
            
            self.log_mcp_activity(
                "Semantic Search",
                tool="ChromaDBRetriever",
                params={"query": query, "top_k": 5}
            )
            
            start_time = time.time()
            result = await self.call_api("/search", "POST", {
                "query": query,
                "filters": {},
                "n_results": 5
            })
            search_time = time.time() - start_time
            
            progress.stop()
            
            # Log search results
            if result.get("results"):
                results_count = len(result["results"])
                self.log_rag_activity(
                    "Search Completed",
                    query=query,
                    results_count=results_count
                )
                self.log_mcp_activity(
                    "Results Retrieved",
                    tool="ChromaDBRetriever",
                    result=f"Found {results_count} relevant documents",
                    duration=search_time
                )
        
        if "results" in result:
            if result["results"]:
                console.print(f"\n[green]🔍 {len(result['results'])} sonuç bulundu:[/green]")
                for i, item in enumerate(result["results"], 1):
                    console.print(f"\n[bold cyan]📄 Sonuç {i}:[/bold cyan]")
                    console.print(f"[dim]📊 Benzerlik: {item.get('score', 0):.2f}[/dim]")
                    content = item.get('content', '')
                    if len(content) > 300:
                        console.print(f"📝 İçerik: {content[:300]}...")
                        console.print(f"[dim]({len(content)} karakter, kesik gösterim)[/dim]")
                    else:
                        console.print(f"📝 İçerik: {content}")
                    
                    if item.get("metadata"):
                        metadata = item["metadata"]
                        console.print(f"[dim]📚 Kaynak: {metadata.get('source', 'Bilinmeyen')}[/dim]")
                        if metadata.get('subject'):
                            console.print(f"[dim]📖 Ders: {metadata.get('subject').title()}[/dim]")
                    console.print("[dim]" + "─" * 50 + "[/dim]")
            else:
                console.print(f"\n[yellow]⚠️ '{query}' için sonuç bulunamadı.[/yellow]")
                console.print("[dim]💡 Öneriler:[/dim]")
                console.print("[dim]  • Daha genel terimler kullanın[/dim]")
                console.print("[dim]  • Türkçe anahtar kelimeler deneyin[/dim]")
                console.print("[dim]  • Farklı ders adları ile arayın[/dim]")
                
                # Show total indexed documents if available
                if result.get("total_indexed"):
                    console.print(f"[dim]📊 Toplam {result['total_indexed']} doküman indexli[/dim]")
        else:
            console.print(f"[red]❌ Arama hatası: {result.get('error', 'Bilinmeyen hata')}[/red]")
    
    async def show_system_status(self):
        """Sistem durumunu detaylı olarak göster"""
        console.print(Panel("[bold blue]System Status[/bold blue]"))
        
        # Log system check
        self.log_mcp_activity("System Health Check", tool="HealthMonitor")
        
        # API Health Check
        result = await self.call_api("/health", "GET")
        
        table = Table(title="Component Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details")
        
        # API Status
        if result.get("status") == "healthy":
            table.add_row("API Server", "[OK] Online", f"Version: {result.get('version', 'Unknown')}")
            self.log_mcp_activity("Health Check", tool="APIServer", result="Healthy")
        else:
            table.add_row("API Server", "[ERR] Offline", "Connection failed")
            self.log_mcp_activity("Health Check", tool="APIServer", result="Failed")
        
        # Check components with detailed logging
        services = result.get("services", {})
        for service_name, service_status in services.items():
            if service_status == "healthy":
                table.add_row(service_name, "[green][OK] Healthy[/green]", "Operational")
                self.log_mcp_activity("Service Check", tool=service_name, result="Healthy")
            else:
                table.add_row(service_name, "[red][ERR] Error[/red]", str(service_status))
                self.log_mcp_activity("Service Check", tool=service_name, result=f"Error: {service_status}")
        
        console.print(table)
        
        # Get additional stats
        stats_result = await self.call_api("/stats", "GET")
        if stats_result:
            console.print("\n[bold]System Statistics:[/bold]")
            console.print(f"Total Conversations: {stats_result.get('total_conversations', 0)}")
            console.print(f"Total Students: {stats_result.get('total_students', 0)}")
            console.print(f"System Uptime: {stats_result.get('uptime', 'Unknown')}")
            
            self.log_rag_activity(
                "Statistics Retrieved",
                results_count=stats_result.get('total_conversations', 0)
            )
    
    async def run(self):
        """Ana döngü"""
        console.print(Panel.fit(
            "[bold cyan]Welcome to Promptitron Console[/bold cyan]\n"
            "AI-Powered Educational Assistant",
            border_style="cyan"
        ))
        
        while True:
            self.display_menu()
            choice = Prompt.ask("\n[bold]Seçenek girin[/bold]", choices=["1","2","3","4","5","6","7","8","9","10","0"])
            
            if choice == "0":
                if Confirm.ask("Çıkmak istediğinizden emin misiniz?"):
                    console.print("[bold green]Görüşmek üzere! 👋[/bold green]")
                    break
            elif choice == "1":
                await self.ai_assistant_mode()
            elif choice == "2":
                await self.generate_questions()
            elif choice == "3":
                await self.create_study_plan()
            elif choice == "4":
                await self.search_knowledge()
            elif choice == "5":
                await self.analyze_content()
            elif choice == "6":
                await self.analyze_document()
            elif choice == "7":
                await self.show_curriculum()
            elif choice == "8":
                await self.export_conversation()
            elif choice == "9":
                await self.show_system_status()
            elif choice == "10":
                console.print("[yellow]Settings coming soon...[/yellow]")
            
            console.print("\n" + "="*50 + "\n")
    
    async def analyze_content(self):
        """İçerik analizi yap"""
        console.print(Panel("[bold red]Content Analysis[/bold red]"))
        
        content = Prompt.ask("Enter content to analyze")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Analyzing content...", total=None)
            
            self.log_mcp_activity(
                "Content Analysis Started",
                tool="ContentAnalyzer",
                params={"content_length": len(content)}
            )
            
            result = await self.call_api("/analyze/content", "POST", {
                "content": content,
                "analysis_type": "comprehensive",
                "include_suggestions": True
            })
            
            progress.stop()
        
        if result.get("analysis"):
            console.print(f"\n[bold]Analysis Result:[/bold]")
            console.print(result["analysis"])
            
            self.log_mcp_activity(
                "Analysis Completed",
                tool="ContentAnalyzer",
                result="Success"
            )
        else:
            console.print(f"[red]Error: {result.get('error', 'Unknown error')}[/red]")
    
    async def show_curriculum(self):
        """Hiyerarşik müfredat göster sistemi"""
        from core.unified_curriculum import unified_curriculum
        
        console.print(Panel("[bold green]📚 HIYERAŞİK MÜFREDAT GÖSTERİM SİSTEMİ[/bold green]"))
        
        console.print("\n[bold cyan]Müfredat Görüntüleme Modları:[/bold cyan]")
        console.print("  1. Hiyerarşik Gezinti - Kademeli müfredat seçimi")
        console.print("  2. Uzman İncelemesi - Dersin uzmanı ile müfredat analizi")
        console.print("  3. Genel Görüntüleme - Tüm derslerin özeti")
        
        browse_mode = Prompt.ask("Görüntüleme modu", choices=["1", "2", "3"], default="1")
        
        if browse_mode == "1":
            # Hiyerarşik gezinti
            await self._hierarchical_curriculum_browse()
        elif browse_mode == "2":
            # Uzman incelemesi
            await self._expert_curriculum_analysis()
        else:
            # Genel görüntüleme
            await self._general_curriculum_overview()
            
    async def _hierarchical_curriculum_browse(self):
        """Hiyerarşik müfredat gezintisi"""
        from core.unified_curriculum import unified_curriculum
        
        # 1. Ders Seçimi
        subject_result = hierarchical_menu.show_subject_selection()
        if not subject_result:
            return
        subject_name, subject_code = subject_result
        
        # 2. Sınıf Seçimi
        grade = hierarchical_menu.show_grade_selection(subject_name, subject_code)
        if not grade:
            return
            
        # 3. Ünite Seçimi
        unit_result = hierarchical_menu.show_unit_selection(subject_name, subject_code, grade)
        if not unit_result:
            return
        unit_code, unit_title = unit_result
        
        # 4. Alt Konu Seçimi (opsiyonel)
        subtopic_result = hierarchical_menu.show_subtopic_selection(subject_name, subject_code, grade, unit_code)
        if not subtopic_result:
            return
        subtopic_code, subtopic_title = subtopic_result
        
        # 5. Detay Görüntüleme
        await self._show_curriculum_details(subject_name, subject_code, grade, unit_code, subtopic_code)
            
    async def _expert_curriculum_analysis(self):
        """Uzman ile müfredat analizi - hiyerarşik seçim"""
        from core.unified_curriculum import unified_curriculum
        
        # Hiyerarşik seçim ile uzman analizi
        subject_result = hierarchical_menu.show_subject_selection()
        if not subject_result:
            return
        subject_name, subject_code = subject_result
        
        console.print(f"\n[bold green]🎓 {subject_name} Uzmanı ile Müfredat İncelemesi[/bold green]")
        
        # Müfredat verilerini al
        curriculum_data = None
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Müfredat verileri yükleniyor...", total=None)
            
            curriculum_response = await self.call_api("/curriculum", "GET")
            if curriculum_response.get('success') and curriculum_response.get('data'):
                curriculum_data = curriculum_response['data']
                
            progress.stop()
        
        # İstatistikleri göster
        if curriculum_data:
            subjects_info = curriculum_data.get('subjects', {})
            if subject_code in subjects_info:
                topic_count = subjects_info[subject_code].get('topic_count', 0)
                console.print(f"[dim]📊 Müfredat: {topic_count} konu bulundu[/dim]")
        
        # Uzman analizi
        expert_query = f
"""
Copyright (c) 2024-2025 PromptiTron Team. All rights reserved.

This file is part of PromptiTron™ Unified Educational AI System.

PROPRIETARY SOFTWARE - DO NOT COPY, DISTRIBUTE, OR MODIFY
This software is the exclusive property of PromptiTron Team.
Unauthorized use, copying, distribution, or modification is strictly prohibited.
For licensing information, contact the PromptiTron Team.

PromptiTron™ is a trademark of the PromptiTron Team.
"""
        {subject_name} müfredatını detaylı analiz et:
        1. Temel konuları ve kavramları listele
        2. Sınıf seviyelerine göre konuları grupla  
        3. YKS'de çıkma olasılığı yüksek konuları belirt
        4. Çalışma stratejisi ve öncelik sırası öner
        5. Zor kavramları öğrenmek için pratik öneriler ver
        
        Müfredat verilerini kullanarak kapsamlı bir analiz sun.
        """
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Uzman müfredatı analiz ediyor...", total=None)
            
            response_data = await self.call_api("/chat", "POST", {
                "message": f"[{subject_name.upper()} UZMANI] {expert_query}",
                "context": {
                    "subject": subject_code, 
                    "mode": "curriculum_review",
                    "curriculum_data": curriculum_data
                },
                "session_id": self.session_id
            })
            
            progress.stop()
            
            if response_data.get('success'):
                console.print(f"\n[bold green]📚 {subject_name} Müfredat Analizi:[/bold green]")
                console.print(response_data.get('response', 'Müfredat bilgisi alınamadı'))
                
                if response_data.get('system_used'):
                    console.print(f"\n[dim]🎓 Uzman: {response_data['system_used']}[/dim]")
            else:
                console.print(f"[red]Uzman müfredat analizi hatası: {response_data.get('error', 'Bilinmeyen hata')}[/red]")
    
    async def _general_curriculum_overview(self):
        """Genel müfredat özeti"""
        self.log_rag_activity("Curriculum Data Access", collection="curriculum")
        
        result = await self.call_api("/curriculum", "GET")
        
        if result.get("success"):
            data = result.get("data", {})
            summary = data.get("summary", {}) if isinstance(data, dict) else {}
            
            console.print(f"\n[bold green]📊 GENEL MÜFREDAT ÖZETİ[/bold green]")
            console.print(f"Toplam Ders: {summary.get('total_subjects', 0)}")
            console.print(f"Toplam Konu: {summary.get('total_topics', 0)}")
            
            # Dersleri göster
            table = Table(title="Mevcut Dersler")
            table.add_column("Ders", style="cyan")
            table.add_column("Konu Sayısı", style="green")
            table.add_column("Sınıflar", style="yellow")
            
            subjects = summary.get("subjects", {})
            for subject, info in subjects.items():
                grades = ", ".join(info.get("grades", []))
                table.add_row(
                    subject,
                    str(info.get("topic_count", 0)),
                    grades
                )
            
            console.print(table)
            
            self.log_rag_activity(
                "General Curriculum Overview Displayed",
                results_count=len(subjects)
            )
        else:
            console.print(f"[red]Error: {result.get('error', 'Unknown error')}[/red]")
            
    async def _show_curriculum_details(self, subject_name: str, subject_code: str, grade: str, unit_code: str, subtopic_code: str):
        """Müfredat detaylarını göster"""
        from core.curriculum_details import curriculum_details
        
        curriculum_details.show_curriculum_details(subject_name, subject_code, grade, unit_code, subtopic_code)
    
    async def export_conversation(self):
        """Konuşma geçmişini dışa aktar"""
        console.print(Panel("[bold yellow]Export Conversation[/bold yellow]"))
        
        # Check if there's any conversation history
        if not self.conversation_history:
            console.print("[yellow]⚠️ Henüz hiç konuşma yapılmamış.[/yellow]")
            console.print("[dim]Önce AI Assistant modunda soru sorun, sonra export yapın.[/dim]")
            return
        
        console.print(f"[green]📄 {len(self.conversation_history)} konuşma bulundu.[/green]")
        
        # User-friendly format selection
        format_choices = {
            "1. Markdown (.md)": "markdown",
            "2. JSON (.json)": "json", 
            "3. Text (.txt)": "txt"
        }
        
        console.print("\n[bold cyan]Export Formatları:[/bold cyan]")
        for choice in format_choices.keys():
            console.print(f"  {choice}")
            
        format_display = Prompt.ask("\nFormat seçin", choices=list(format_choices.keys()), default="1. Markdown (.md)")
        format_choice = format_choices[format_display]
        
        self.log_mcp_activity(
            "Export Started",
            tool="DataExporter",
            params={"format": format_choice}
        )
        
        # Create export data
        export_data = {
            "session_id": self.session_id,
            "export_time": datetime.now().isoformat(),
            "conversation_count": len(self.conversation_history),
            "history": self.conversation_history
        }
        
        filename = f"conversation_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_choice}"
        
        if format_choice == "json":
            import json
            content = json.dumps(export_data, indent=2, ensure_ascii=False)
        elif format_choice == "markdown":
            content = f"# 🎓 Promptitron Konuşma Geçmişi\n\n"
            content += f"**📅 Export Zamanı:** {export_data['export_time']}\n"
            content += f"**🆔 Session ID:** {export_data['session_id']}\n"
            content += f"**💬 Toplam Konuşma:** {export_data['conversation_count']}\n\n"
            content += "---\n\n"
            
            for i, item in enumerate(self.conversation_history, 1):
                timestamp = item.get('timestamp', 'Unknown')
                content += f"## 💬 Konuşma {i}\n\n"
                content += f"**⏰ Zaman:** {timestamp}\n"
                content += f"**🔧 Sistem:** {item.get('system_used', 'Unknown')}\n"
                if item.get('processing_time'):
                    content += f"**⚡ İşlem Süresi:** {item['processing_time']:.2f}s\n"
                content += "\n"
                content += f"**👤 Kullanıcı:**\n{item.get('user', '')}\n\n"
                content += f"**🤖 Asistan:**\n{item.get('assistant', '')}\n\n"
                content += "---\n\n"
        else:  # txt
            content = f"PROMPTITRON KONUŞMA GEÇMİŞİ\n"
            content += "=" * 50 + "\n"
            content += f"Export Zamanı: {export_data['export_time']}\n"
            content += f"Session ID: {export_data['session_id']}\n"
            content += f"Toplam Konuşma: {export_data['conversation_count']}\n"
            content += "=" * 50 + "\n\n"
            
            for i, item in enumerate(self.conversation_history, 1):
                timestamp = item.get('timestamp', 'Unknown')
                content += f"KONUŞMA {i}\n"
                content += f"Zaman: {timestamp}\n"
                content += f"Sistem: {item.get('system_used', 'Unknown')}\n"
                if item.get('processing_time'):
                    content += f"İşlem Süresi: {item['processing_time']:.2f}s\n"
                content += f"\nKullanıcı: {item.get('user', '')}\n"
                content += f"Asistan: {item.get('assistant', '')}\n\n"
                content += "-" * 30 + "\n\n"
        
        # Save file
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Get file size for better feedback
            import os
            file_size = os.path.getsize(filename)
            file_size_kb = file_size / 1024
            
            console.print(f"[green]✅ Export başarılı![/green]")
            console.print(f"[dim]📁 Dosya: {filename}[/dim]")
            console.print(f"[dim]📏 Boyut: {file_size_kb:.1f} KB[/dim]")
            console.print(f"[dim]💬 {len(self.conversation_history)} konuşma export edildi[/dim]")
            
            self.log_mcp_activity(
                "Export Completed",
                tool="DataExporter",
                result=f"Saved to {filename} ({file_size_kb:.1f} KB)"
            )
        except Exception as e:
            console.print(f"[red]Export failed: {e}[/red]")
            self.log_mcp_activity(
                "Export Failed",
                tool="DataExporter",
                result=str(e)
            )
    
    async def analyze_document(self):
        """Doküman analizi yap - Gelişmiş AI özellikleri ile"""
        console.print(Panel("[bold blue]Document Analysis - AI Enhanced[/bold blue]"))
        console.print("[dim]✨ Soru çıkarma, özetleme ve YKS konu genişletme desteği[/dim]")
        
        # File path input
        file_path = Prompt.ask("Analiz edilecek dosyanın tam yolu")
        
        # Check if file exists
        from pathlib import Path
        if not Path(file_path).exists():
            console.print(f"[red]❌ Dosya bulunamadı: {file_path}[/red]")
            return
        
        # Analysis type selection
        analysis_choices = {
            "1. Genel Analiz": "general",
            "2. Eğitim Analizi": "educational", 
            "3. Soru Analizi": "question_analysis"
        }
        
        console.print("\n[bold cyan]Analiz Türü:[/bold cyan]")
        console.print("  1. Genel Analiz - Temel doküman analizi")
        console.print("  2. Eğitim Analizi - YKS odaklı eğitim analizi (Önerilen)")
        console.print("  3. Soru Analizi - Test ve sınav soruları analizi")
        
        analysis_display = Prompt.ask("Analiz türü seçin", choices=list(analysis_choices.keys()), default="2. Eğitim Analizi")
        analysis_type = analysis_choices[analysis_display]
        
        # Advanced options
        console.print("\n[bold cyan]Gelişmiş Özellikler:[/bold cyan]")
        extract_questions = Confirm.ask("🤔 Dokümandan soru çıkar?", default=False)
        summarize = Confirm.ask("📝 Dokümanı özetle?", default=True)
        expand_topics = Confirm.ask("📚 YKS standartlarında konu genişlet?", default=False)
        
        # Custom prompt option
        use_custom = Confirm.ask("Özel analiz talimatı vermek ister misiniz?", default=False)
        custom_prompt = None
        if use_custom:
            custom_prompt = Prompt.ask("Özel analiz talimatınızı girin")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Doküman analiz ediliyor...", total=None)
            
            self.log_mcp_activity(
                "Document Analysis Started",
                tool="DocumentUnderstanding",
                params={"file_path": file_path, "analysis_type": analysis_type}
            )
            
            start_time = time.time()
            result = await self.call_api("/document/analyze", "POST", {
                "file_path": file_path,
                "analysis_type": analysis_type,
                "custom_prompt": custom_prompt,
                "extract_questions": extract_questions,
                "summarize": summarize,
                "expand_topics": expand_topics
            })
            analysis_time = time.time() - start_time
            
            progress.stop()
            
            if result.get("success"):
                self.log_mcp_activity(
                    "Document Analysis Completed",
                    tool="DocumentUnderstanding",
                    result="Success",
                    duration=analysis_time
                )
        
        if result.get("success"):
            console.print(f"\n[bold green]✅ Doküman Analizi Tamamlandı[/bold green]")
            console.print(f"[green]✨ Gelişmiş özellikler aktif: Soru çıkarma: {extract_questions}, Özetleme: {summarize}, Konu genişletme: {expand_topics}[/green]")
            
            # File info
            file_info = result.get("file_info", {})
            console.print(f"\n[bold]📁 Dosya Bilgileri:[/bold]")
            console.print(f"  📝 Ad: {file_info.get('name', 'Unknown')}")
            console.print(f"  📏 Boyut: {file_info.get('size', 0)} bytes")
            console.print(f"  📄 Tür: {file_info.get('type', 'Unknown')}")
            console.print(f"  🎯 Format: {file_info.get('format', 'Unknown')}")
            
            # Analysis results
            if result.get("analysis"):
                console.print(f"\n[bold]🔍 Analiz Sonucu:[/bold]")
                analysis_text = result["analysis"]
                if len(analysis_text) > 1000:
                    console.print(analysis_text[:1000] + "...")
                    console.print(f"[dim](Analiz çok uzun, ilk 1000 karakter gösteriliyor. Toplam: {len(analysis_text)} karakter)[/dim]")
                else:
                    console.print(analysis_text)
            
            # Structured data
            structured_data = result.get("structured_data", {})
            if structured_data:
                console.print(f"\n[bold]📊 Yapılandırılmış Veri:[/bold]")
                console.print(f"  📚 Ders: {structured_data.get('subject', 'Belirtilmemiş')}")
                console.print(f"  📈 Zorluk: {structured_data.get('difficulty_level', 'Belirtilmemiş')}")
                console.print(f"  🎓 Seviye: {structured_data.get('education_level', 'Belirtilmemiş')}")
                
                topics = structured_data.get('topics', [])
                if topics:
                    console.print(f"  🏷️ Konular: {', '.join(topics[:5])}{'...' if len(topics) > 5 else ''}")
                
                concepts = structured_data.get('key_concepts', [])
                if concepts:
                    console.print(f"  💡 Anahtar Kavramlar: {', '.join(concepts[:3])}{'...' if len(concepts) > 3 else ''}")
                
                if structured_data.get('exam_relevance'):
                    console.print(f"  📝 Sınav Uygunluğu: {structured_data['exam_relevance']}")
            
            # Educational metadata
            edu_metadata = result.get("educational_metadata", {})
            if edu_metadata:
                console.print(f"\n[bold]🎓 Eğitim Metadatası:[/bold]")
                
                if edu_metadata.get('content_length'):
                    console.print(f"  📏 İçerik Uzunluğu: {edu_metadata['content_length']} karakter")
                
                if edu_metadata.get('reading_time_minutes'):
                    console.print(f"  ⏱️ Okuma Süresi: ~{edu_metadata['reading_time_minutes']} dakika")
                
                if edu_metadata.get('complexity_score'):
                    complexity = edu_metadata['complexity_score']
                    console.print(f"  🧠 Karmaşıklık Skoru: {complexity:.2f}/1.0")
                    if complexity < 0.3:
                        console.print(f"    [green]→ Kolay seviye[/green]")
                    elif complexity < 0.7:
                        console.print(f"    [yellow]→ Orta seviye[/yellow]")
                    else:
                        console.print(f"    [red]→ Zor seviye[/red]")
                
                recommendations = edu_metadata.get('study_recommendations', [])
                if recommendations:
                    console.print(f"  💡 Çalışma Önerileri:")
                    for rec in recommendations[:3]:
                        console.print(f"    • {rec}")
                
                assessments = edu_metadata.get('assessment_suggestions', [])
                if assessments:
                    console.print(f"  📝 Değerlendirme Önerileri:")
                    for assess in assessments[:3]:
                        console.print(f"    • {assess}")
            
            # Enhanced features results
            if result.get("summary"):
                console.print(f"\n[bold]📝 Doküman Özeti:[/bold]")
                summary = result["summary"]
                if len(summary) > 800:
                    console.print(summary[:800] + "...")
                    console.print(f"[dim](Özet çok uzun, ilk 800 karakter gösteriliyor. Toplam: {len(summary)} karakter)[/dim]")
                else:
                    console.print(summary)
            
            if result.get("extracted_questions"):
                questions = result["extracted_questions"]
                console.print(f"\n[bold]❓ Çıkarılan Sorular ({len(questions)} adet):[/bold]")
                for i, q in enumerate(questions[:3], 1):  # Show first 3 questions
                    if isinstance(q, dict) and "question" in q:
                        console.print(f"\n[cyan]Soru {i}:[/cyan] {q['question'][:200]}{'...' if len(q.get('question', '')) > 200 else ''}")
                    else:
                        console.print(f"\n[cyan]Soru {i}:[/cyan] {str(q)[:200]}...")
                if len(questions) > 3:
                    console.print(f"[dim]... ve {len(questions)-3} soru daha[/dim]")
            
            if result.get("expanded_topics"):
                expanded = result["expanded_topics"]
                console.print(f"\n[bold]📚 YKS Konu Genişletmesi:[/bold]")
                console.print(f"  🎯 Ders: {expanded.get('subject', 'Belirtilmemiş')}")
                console.print(f"  📝 Ana Konu: {expanded.get('main_topic', 'Belirtilmemiş')}")
                expanded_content = expanded.get('expanded_content', '')
                if expanded_content:
                    if len(expanded_content) > 1000:
                        console.print(f"\n{expanded_content[:1000]}...")
                        console.print(f"[dim](Genişletme çok uzun, ilk 1000 karakter gösteriliyor. Toplam: {len(expanded_content)} karakter)[/dim]")
                    else:
                        console.print(f"\n{expanded_content}")
            
            console.print(f"\n[dim]⏱️ Analiz süresi: {analysis_time:.2f} saniye[/dim]")
            
        else:
            console.print(f"[red]❌ Analiz hatası: {result.get('error', 'Bilinmeyen hata')}[/red]")
            self.log_mcp_activity(
                "Document Analysis Failed",
                tool="DocumentUnderstanding",
                result=result.get("error", "Unknown error")
            )

def main():
    """Main entry point"""
    try:
        manager = ConsoleManager()
        asyncio.run(manager.run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        logger.exception("Unhandled exception")

if __name__ == "__main__":
    main()