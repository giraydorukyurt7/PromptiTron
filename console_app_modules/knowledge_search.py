from rich.prompt import Prompt

class KnowledgeSearch:
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
            
            self.console.print(f"\n[bold cyan]{subject_display} Uzmanı ile Arama:[/bold cyan]")
            self.console.print("  • Konu bazlı sorular sorabilirsiniz")
            self.console.print("  • Kavramları açıklattırabilirsiniz") 
            self.console.print("  • Örnekler isteyebilirsiniz")
        
        query = Prompt.ask("\nArama sorgusu/Sorunuz")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
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
                    
                    self.console.print(f"\n[bold green]🎓 {subject_display} Uzmanı Yanıtı:[/bold green]")
                    self.console.print(result.get('response', 'Yanıt alınamadı'))
                    
                    if result.get('system_used'):
                        self.console.print(f"\n[dim]Sistem: {result['system_used']}[/dim]")
                        
                    self.log_crewai_activity(
                        f"Expert Search Completed - {selected_subject.title()}",
                        agent=f"{selected_subject.title()}Expert",
                        task=query,
                        status="completed",
                        result=result.get('response', '')[:100] + "..."
                    )
                else:
                    self.console.print(f"[red]Uzman arama hatası: {result.get('error', 'Bilinmeyen hata')}[/red]")
                    
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
                self.console.print(f"\n[green]🔍 {len(result['results'])} sonuç bulundu:[/green]")
                for i, item in enumerate(result["results"], 1):
                    self.console.print(f"\n[bold cyan]📄 Sonuç {i}:[/bold cyan]")
                    self.console.print(f"[dim]📊 Benzerlik: {item.get('score', 0):.2f}[/dim]")
                    content = item.get('content', '')
                    if len(content) > 300:
                        self.console.print(f"📝 İçerik: {content[:300]}...")
                        self.console.print(f"[dim]({len(content)} karakter, kesik gösterim)[/dim]")
                    else:
                        self.console.print(f"📝 İçerik: {content}")
                    
                    if item.get("metadata"):
                        metadata = item["metadata"]
                        self.console.print(f"[dim]📚 Kaynak: {metadata.get('source', 'Bilinmeyen')}[/dim]")
                        if metadata.get('subject'):
                            self.console.print(f"[dim]📖 Ders: {metadata.get('subject').title()}[/dim]")
                    self.console.print("[dim]" + "─" * 50 + "[/dim]")
            else:
                self.console.print(f"\n[yellow]⚠️ '{query}' için sonuç bulunamadı.[/yellow]")
                self.console.print("[dim]💡 Öneriler:[/dim]")
                self.console.print("[dim]  • Daha genel terimler kullanın[/dim]")
                self.console.print("[dim]  • Türkçe anahtar kelimeler deneyin[/dim]")
                self.console.print("[dim]  • Farklı ders adları ile arayın[/dim]")
                
                # Show total indexed documents if available
                if result.get("total_indexed"):
                    self.console.print(f"[dim]📊 Toplam {result['total_indexed']} doküman indexli[/dim]")
        else:
            self.console.print(f"[red]❌ Arama hatası: {result.get('error', 'Bilinmeyen hata')}[/red]")