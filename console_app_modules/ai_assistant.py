from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from .utils.api_utils import APIClient

class AIAssistant:
    async def ai_assistant_mode(self):
        """AI Assistant modu - Expert routing ile"""
        self.self.console.print(Panel("[bold green]AI Assistant Mode[/bold green]"))
        
        # Mod seçimi
        self.console.print("\n[bold cyan]Asistan Modu Seçimi:[/bold cyan]")
        self.console.print("1. 📚 Normal Mod - Doğrudan cevaplar ve açıklamalar")
        self.console.print("2. 🎓 Sokratik Mod - Sorularla öğrenme ve keşfetme")
        self.console.print("3. ← Ana Menüye Dön")
        
        mode_choice = Prompt.ask("\nSeçiminiz", choices=["1", "2", "3"])
        
        if mode_choice == "3":
            return
        
        socratic_mode = (mode_choice == "2")
        
        if socratic_mode:
            self.console.print(Panel("[bold magenta]🎓 Sokratik Mod Aktif[/bold magenta]"))
            self.console.print("[dim]Bu modda size doğrudan cevap vermek yerine, düşündürücü sorular soracağım.[/dim]")
            self.console.print("[dim]Amacım sizin kendi cevabınızı bulmanıza yardımcı olmak.[/dim]")
            
            # Import Socratic agent
            from core.socratic_agent import socratic_agent
            
            # Konu seçimi
            topic = Prompt.ask("\n[bold]Hangi konuda konuşmak istersiniz?[/bold]")
            socratic_context = {"topic": topic}
        else:
            self.console.print(Panel("[bold green]📚 Normal Asistan Modu[/bold green]"))
            self.console.print("[dim]Type 'exit' to return to menu, 'expert list' to see available experts[/dim]")
        
        self.console.print("[dim]Çıkmak için 'exit' yazın[/dim]\n")
        
        while True:
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
            
            if user_input.lower() == 'exit':
                if socratic_mode:
                    # Sokratik mod özeti
                    if Confirm.ask("\nKonuşma özetini görmek ister misiniz?"):
                        summary = socratic_agent.get_conversation_summary()
                        self.console.print(Panel(summary, title="Konuşma Özeti", border_style="cyan"))
                    socratic_agent.reset_memory()
                break
            elif user_input.lower() == 'expert list' and not socratic_mode:
                self.console.print("\n[bold cyan]🎓 Mevcut Uzmanlar:[/bold cyan]")
                experts = [
                    "Matematik Uzmanı", "Fizik Uzmanı", "Kimya Uzmanı", "Biyoloji Uzmanı",
                    "Türk Dili ve Edebiyatı Uzmanı", "Tarih Uzmanı", "Coğrafya Uzmanı", 
                    "Felsefe Uzmanı", "Din Kültürü Uzmanı", "İnkılap ve Atatürkçülük Uzmanı", 
                    "Genel Eğitim Uzmanı"
                ]
                for expert in experts:
                    self.console.print(f"  • {expert}")
                self.console.print("\n[dim]İpucu: Sorunuzun başına ders adını yazarak o uzmanla konuşabilirsiniz[/dim]")
                self.console.print("[dim]Örnek: 'matematik türev konusunu açıkla' veya 'edebiyat cumhuriyet dönemi'[/dim]")
                continue
            
            # Process request
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
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
                    api_client=APIClient()
                    result = await api_client.call_api("/chat", "POST", {
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
                    self.console.print(f"\n[bold magenta]Sokrates[/bold magenta]: {result['response']}")
                    
                    # Sokratik ipuçları göster (sadece debug modda)
                    if result.get("hints") and settings.DEBUG:
                        self.console.print("\n[dim]Öğretmen için ipuçları:[/dim]")
                        for hint in result["hints"]:
                            self.console.print(f"[dim]{hint}[/dim]")
                else:
                    self.console.print(f"\n[bold magenta]Assistant[/bold magenta]: {result['response']}")
                
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
                self.console.print(f"[red]Error: {result.get('error', 'Unknown error')}[/red]")
                # Log error details
                self.log_http_request("POST", "/chat", 500, 0, result.get('error'))