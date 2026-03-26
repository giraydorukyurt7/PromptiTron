import time
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

class DocumentAnalyzer:
    async def analyze_document(self):
        """Doküman analizi yap - Gelişmiş AI özellikleri ile"""
        self.console.print(Panel("[bold blue]Document Analysis - AI Enhanced[/bold blue]"))
        self.console.print("[dim]✨ Soru çıkarma, özetleme ve YKS konu genişletme desteği[/dim]")
        
        # File path input
        file_path = Prompt.ask("Analiz edilecek dosyanın tam yolu veya web sitesi URL'si (http:// ile başlamalı)")
        
        # Check if file exists (skip for URLs)
        from pathlib import Path
        if not file_path.startswith(('http://', 'https://')) and not Path(file_path).exists():
            self.console.print(f"[red]❌ Dosya bulunamadı: {file_path}[/red]")
            return
        
        # Analysis type selection
        analysis_choices = {
            "1. Genel Analiz": "general",
            "2. Eğitim Analizi": "educational", 
            "3. Soru Analizi": "question_analysis"
        }
        
        self.console.print("\n[bold cyan]Analiz Türü:[/bold cyan]")
        self.console.print("  1. Genel Analiz - Temel doküman analizi")
        self.console.print("  2. Eğitim Analizi - YKS odaklı eğitim analizi (Önerilen)")
        self.console.print("  3. Soru Analizi - Test ve sınav soruları analizi")
        
        analysis_display = Prompt.ask("Analiz türü seçin", choices=list(analysis_choices.keys()), default="2. Eğitim Analizi")
        analysis_type = analysis_choices[analysis_display]
        
        # Advanced options
        self.console.print("\n[bold cyan]Gelişmiş Özellikler:[/bold cyan]")
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
            console=self.console
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
            self.console.print(f"\n[bold green]✅ Doküman Analizi Tamamlandı[/bold green]")
            self.console.print(f"[green]✨ Gelişmiş özellikler aktif: Soru çıkarma: {extract_questions}, Özetleme: {summarize}, Konu genişletme: {expand_topics}[/green]")
            
            # File info
            file_info = result.get("file_info", {})
            self.console.print(f"\n[bold]📁 Dosya Bilgileri:[/bold]")
            self.console.print(f"  📝 Ad: {file_info.get('name', 'Unknown')}")
            self.console.print(f"  📏 Boyut: {file_info.get('size', 0)} bytes")
            self.console.print(f"  📄 Tür: {file_info.get('type', 'Unknown')}")
            self.console.print(f"  🎯 Format: {file_info.get('format', 'Unknown')}")
            
            # Analysis results - Show full text
            if result.get("analysis"):
                self.console.print(f"\n[bold]🔍 Analiz Sonucu:[/bold]")
                analysis_text = result["analysis"]
                self.console.print(analysis_text)  # Show full text
                self.console.print(f"[dim](Toplam analiz uzunluğu: {len(analysis_text)} karakter)[/dim]")
            
            # Structured data
            structured_data = result.get("structured_data", {})
            if structured_data:
                self.console.print(f"\n[bold]📊 Yapılandırılmış Veri:[/bold]")
                self.console.print(f"  📚 Ders: {structured_data.get('subject', 'Belirtilmemiş')}")
                self.console.print(f"  📈 Zorluk: {structured_data.get('difficulty_level', 'Belirtilmemiş')}")
                self.console.print(f"  🎓 Seviye: {structured_data.get('education_level', 'Belirtilmemiş')}")
                
                topics = structured_data.get('topics', [])
                if topics:
                    self.console.print(f"  🏷️ Konular: {', '.join(topics[:5])}{'...' if len(topics) > 5 else ''}")
                
                concepts = structured_data.get('key_concepts', [])
                if concepts:
                    self.console.print(f"  💡 Anahtar Kavramlar: {', '.join(concepts[:3])}{'...' if len(concepts) > 3 else ''}")
                
                if structured_data.get('exam_relevance'):
                    self.console.print(f"  📝 Sınav Uygunluğu: {structured_data['exam_relevance']}")
            
            # Educational metadata
            edu_metadata = result.get("educational_metadata", {})
            if edu_metadata:
                self.console.print(f"\n[bold]🎓 Eğitim Metadatası:[/bold]")
                
                if edu_metadata.get('content_length'):
                    self.console.print(f"  📏 İçerik Uzunluğu: {edu_metadata['content_length']} karakter")
                
                if edu_metadata.get('reading_time_minutes'):
                    self.console.print(f"  ⏱️ Okuma Süresi: ~{edu_metadata['reading_time_minutes']} dakika")
                
                if edu_metadata.get('complexity_score'):
                    complexity = edu_metadata['complexity_score']
                    self.console.print(f"  🧠 Karmaşıklık Skoru: {complexity:.2f}/1.0")
                    if complexity < 0.3:
                        self.console.print(f"    [green]→ Kolay seviye[/green]")
                    elif complexity < 0.7:
                        self.console.print(f"    [yellow]→ Orta seviye[/yellow]")
                    else:
                        self.console.print(f"    [red]→ Zor seviye[/red]")
                
                recommendations = edu_metadata.get('study_recommendations', [])
                if recommendations:
                    self.console.print(f"  💡 Çalışma Önerileri:")
                    for rec in recommendations[:3]:
                        self.console.print(f"    • {rec}")
                
                assessments = edu_metadata.get('assessment_suggestions', [])
                if assessments:
                    self.console.print(f"  📝 Değerlendirme Önerileri:")
                    for assess in assessments[:3]:
                        self.console.print(f"    • {assess}")
            
            # Enhanced features results - Show full text
            if result.get("summary"):
                self.console.print(f"\n[bold]📝 Doküman Özeti:[/bold]")
                summary = result["summary"]
                self.console.print(summary)  # Show full text
                self.console.print(f"[dim](Toplam özet uzunluğu: {len(summary)} karakter)[/dim]")
            
            if result.get("extracted_questions"):
                questions = result["extracted_questions"]
                self.console.print(f"\n[bold]❓ Çıkarılan Sorular ({len(questions)} adet):[/bold]")
                for i, q in enumerate(questions, 1):  # Show all questions
                    if isinstance(q, dict):
                        self.console.print(f"\n[cyan]Soru {i}:[/cyan]")
                        if "question" in q:
                            self.console.print(f"📝 {q['question']}")
                        elif "soru_metni" in q:
                            self.console.print(f"📝 {q['soru_metni']}")
                        
                        # Show options if available
                        if "options" in q or "secenekler" in q:
                            options = q.get("options", q.get("secenekler", {}))
                            self.console.print("[bold]Seçenekler:[/bold]")
                            for key, value in options.items():
                                self.console.print(f"  {key}) {value}")
                        
                        # Show correct answer
                        if "correct_answer" in q or "dogru_cevap" in q:
                            answer = q.get("correct_answer", q.get("dogru_cevap", ""))
                            self.console.print(f"[green]✓ Doğru Cevap: {answer}[/green]")
                        
                        # Show explanation
                        if "explanation" in q or "aciklama" in q:
                            explanation = q.get("explanation", q.get("aciklama", ""))
                            self.console.print(f"[dim]💡 Açıklama: {explanation}[/dim]")
                    else:
                        self.console.print(f"\n[cyan]Soru {i}:[/cyan] {str(q)}")
                    self.console.print("[dim]" + "─" * 50 + "[/dim]")
            
            if result.get("expanded_topics"):
                expanded = result["expanded_topics"]
                self.console.print(f"\n[bold]📚 YKS Konu Genişletmesi:[/bold]")
                self.console.print(f"  🎯 Ders: {expanded.get('subject', 'Belirtilmemiş')}")
                self.console.print(f"  📝 Ana Konu: {expanded.get('main_topic', 'Belirtilmemiş')}")
                expanded_content = expanded.get('expanded_content', '')
                if expanded_content:
                    self.console.print(f"\n{expanded_content}")  # Show full content
                    self.console.print(f"[dim](Toplam genişletme uzunluğu: {len(expanded_content)} karakter)[/dim]")
            
            # Show JSON file info if available
            if result.get("json_file"):
                self.console.print(f"\n[bold green]💾 Tam Sonuçlar JSON Dosyasına Kaydedildi:[/bold green]")
                self.console.print(f"[dim]📁 Dosya: {result['json_file']}[/dim]")
                self.console.print(f"[dim]📋 Bu dosyada tüm analiz sonuçları tam haliyle bulunur[/dim]")
            
            self.console.print(f"\n[dim]⏱️ Analiz süresi: {analysis_time:.2f} saniye[/dim]")
            
        else:
            self.console.print(f"[red]❌ Analiz hatası: {result.get('error', 'Bilinmeyen hata')}[/red]")
            self.log_mcp_activity(
                "Document Analysis Failed",
                tool="DocumentUnderstanding",
                result=result.get("error", "Unknown error")
            )

    async def analyze_content(self):
        """İçerik analizi yap"""
        self.console.print(Panel("[bold red]Content Analysis[/bold red]"))
        
        content = Prompt.ask("Enter content to analyze")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
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
            self.console.print(f"\n[bold]Analysis Result:[/bold]")
            self.console.print(result["analysis"])
            
            self.log_mcp_activity(
                "Analysis Completed",
                tool="ContentAnalyzer",
                result="Success"
            )
        else:
            self.console.print(f"[red]Error: {result.get('error', 'Unknown error')}[/red]")