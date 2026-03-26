import asyncio
import sys
from pathlib import Path
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from .ai_assistant import AIAssistant
from .question_generator import QuestionGenerator
from .study_planner import StudyPlanner
from .knowledge_search import KnowledgeSearch
from .system_status import SystemStatus
from .content_analysis.document_analyzer import DocumentAnalyzer
from .content_analysis.web_analyzer import WebAnalyzer
from .content_analysis.youtube_analyzer import YouTubeAnalyzer
from .curriculum_manager import CurriculumManager
from .export_manager import ExportManager

# Import systems
from core.rag_system import rag_system
from core.agents import agent_system
from core.conversation_memory import conversation_memory

class ConsoleManager(AIAssistant, QuestionGenerator, StudyPlanner, KnowledgeSearch, 
                    SystemStatus, DocumentAnalyzer, WebAnalyzer, YouTubeAnalyzer, 
                    CurriculumManager, ExportManager):
    
    def __init__(self, console):
        self.console = console
        self.session_id = self.generate_session_id()
        self.conversation_history = []
        self.current_mode = "ai_assistant"
        self._systems_initialized = False

    async def initialize_systems(self):
        """Initialize all systems with optimizations"""
        if self._systems_initialized:
            self.console.print("[dim]Systems already initialized, skipping...[/dim]")
            return
        
        self.console.print("\n[cyan]🚀 Starting optimized system initialization...[/cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            # Initialize RAG system first (optimized with caching)
            task1 = progress.add_task("Loading vectorstore and embeddings cache...", total=None)
            
            # Force initialize RAG system which has caching
            await rag_system.load_curriculum_data(force_reload=False)  # Use cache
            progress.update(task1, description="✓ RAG system with cached data")
            
            # Initialize agent system (with lazy loading)
            task2 = progress.add_task("Preparing agent system...", total=None)
            # Agent system now uses lazy loading, so this is very fast
            progress.update(task2, description="✓ Agent system (lazy loaded)")
            
            # Initialize other systems
            task3 = progress.add_task("Loading conversation memory...", total=None)
            progress.update(task3, description="✓ Conversation memory ready")
            
            progress.stop()
        
        self._systems_initialized = True
        self.console.print("[green]✅ All systems initialized with optimizations![/green]")

    def generate_session_id(self) -> str:
        """Generate a new session ID"""
        import uuid
        return str(uuid.uuid4())
    
    def display_menu(self):
        """Ana menüyü göster"""
        from rich.table import Table
        
        table = Table(title="Ana Menü", show_header=False, expand=False)
        table.add_column("", style="cyan", width=3)
        table.add_column("", style="white")
        
        table.add_row("1", "🤖 AI Asistan")
        table.add_row("2", "❓ Soru Üretici")
        table.add_row("3", "📚 Çalışma Planı Oluştur")
        table.add_row("4", "🔍 Bilgi Arama")
        table.add_row("5", "📊 İçerik Analizi")
        table.add_row("6", "📄 Doküman Analizi")
        table.add_row("7", "🌐 Web Sitesi Analizi")
        table.add_row("8", "📹 YouTube Video Analizi")
        table.add_row("9", "📖 Müfredat Göster")
        table.add_row("10", "💾 Konuşmayı Dışa Aktar")
        table.add_row("11", "📊 Sistem Durumu")
        table.add_row("12", "⚙️ Ayarlar")
        table.add_row("0", "🚪 Çıkış")
        
        self.console.print(table)
    
    async def run(self):
        """Ana döngü"""
        self.console.print(Panel.fit(
            "[bold cyan]Welcome to Promptitron Console[/bold cyan]\n"
            "AI-Powered Educational Assistant",
            border_style="cyan"
        ))
        
        # Initialize systems on first run
        await self.initialize_systems()
        
        while True:
            self.display_menu()
            choice = Prompt.ask("\n[bold]Seçenek girin[/bold]", choices=["1","2","3","4","5","6","7","8","9","10","11","12","0"])
            
            if choice == "0":
                if Confirm.ask("Çıkmak istediğinizden emin misiniz?"):
                    self.console.print("[bold green]Görüşmek üzere! 👋[/bold green]")
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
                await self.analyze_website()
            elif choice == "8":
                await self.analyze_youtube_video()
            elif choice == "9":
                await self.show_curriculum()
            elif choice == "10":
                await self.export_conversation()
            elif choice == "11":
                await self.show_system_status()
            elif choice == "12":
                self.console.print("[yellow]Settings coming soon...[/yellow]")
            
            self.console.print("\n" + "="*50 + "\n")