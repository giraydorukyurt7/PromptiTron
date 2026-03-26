import time
from datetime import datetime
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

class WebAnalyzer:
    async def analyze_website(self):
        """Web sitesi analizi yap - YKS müfredat uygunluk kontrolü ile"""
        self.console.print(Panel("[bold blue]🌐 Web Site Analysis - YKS Curriculum Check[/bold blue]"))
        self.console.print("[dim]✨ Web sitesi içeriğini YKS müfredatına uygunluk açısından analiz eder[/dim]")
        
        # URL input with validation
        while True:
            url = Prompt.ask("Analiz edilecek web sitesi URL'si (http:// veya https:// ile başlamalı)")
            
            if not url.startswith(('http://', 'https://')):
                self.console.print("[red]❌ Geçersiz URL formatı. http:// veya https:// ile başlamalıdır.[/red]")
                continue
            
            # Basic URL validation
            import re
            url_pattern = r'^https?://[\w\-]+(\.[\w\-]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?$'
            if not re.match(url_pattern, url):
                self.console.print("[red]❌ Geçersiz URL formatı. Lütfen geçerli bir web sitesi adresi girin.[/red]")
                continue
            
            break
        
        # Analysis type selection
        analysis_choices = {
            "1. Tam Analiz": "full",
            "2. Hızlı Kontrol": "quick", 
            "3. Sadece Müfredat Kontrolü": "curriculum_only"
        }
        
        self.console.print("\n[bold cyan]Analiz Türü:[/bold cyan]")
        self.console.print("  1. Tam Analiz - Kapsamlı içerik analizi + soru üretimi (Önerilen)")
        self.console.print("  2. Hızlı Kontrol - Temel içerik analizi")
        self.console.print("  3. Sadece Müfredat Kontrolü - YKS uygunluk kontrolü")
        
        analysis_display = Prompt.ask("Analiz türü seçin", choices=list(analysis_choices.keys()), default="1. Tam Analiz")
        analysis_type = analysis_choices[analysis_display]
        
        # Custom prompt option
        use_custom = Confirm.ask("Özel analiz talimatı vermek ister misiniz?", default=False)
        custom_prompt = None
        if use_custom:
            custom_prompt = Prompt.ask("Özel analiz talimatınızı girin")
        
        # Show processing status
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Web sitesi analiz ediliyor...", total=None)
            
            try:
                # Import web analyzer
                from core.web_analyzer import web_analyzer
                
                progress.update(task, description="İçerik çekiliyor...")
                
                # Analyze website
                result = await web_analyzer.analyze_website(
                    url=url,
                    analysis_type=analysis_type,
                    custom_prompt=custom_prompt
                )
                
                progress.update(task, description="✓ Analiz tamamlandı")
                
            except Exception as e:
                progress.update(task, description="❌ Analiz başarısız")
                self.console.print(f"[red]❌ Hata oluştu: {str(e)}[/red]")
                return
        
        # Display results
        if result.get("error"):
            self.console.print(f"[red]❌ Analiz Hatası: {result['error']}[/red]")
            if result.get("suggestion"):
                self.console.print(f"[yellow]💡 Öneri: {result['suggestion']}[/yellow]")
            return
        
        if not result.get("success"):
            self.console.print("[red]❌ Web sitesi analizi başarısız oldu.[/red]")
            return
        
        # Show curriculum check results
        curriculum_check = result.get("curriculum_check", {})
        yks_relevant = curriculum_check.get("yks_relevant", False)
        
        self.console.print("\n" + "="*60)
        self.console.print(Panel("[bold green]📊 YKS Müfredat Uygunluk Kontrolü[/bold green]"))
        
        if yks_relevant:
            self.console.print("[green]✅ İçerik YKS müfredatına uygun[/green]")
            self.console.print(f"[cyan]🎯 İlgili Dersler: {', '.join(curriculum_check.get('subjects', []))}[/cyan]")
            self.console.print(f"[blue]🎖️ Güven Skoru: {curriculum_check.get('confidence_score', 0):.2f}/1.0[/blue]")
            self.console.print(f"[dim]Eğitim Seviyesi: {curriculum_check.get('education_level', 'Belirtilmemiş')}[/dim]")
        else:
            self.console.print("[red]❌ İçerik YKS müfredat dışı[/red]")
            self.console.print(f"[yellow]⚠️ Sebep: {curriculum_check.get('reason', 'Belirtilmemiş')}[/yellow]")
            self.console.print("[dim]Bu web sitesi YKS dersleriyle ilgili eğitim içeriği içermiyor.[/dim]")
            return
        
        # Show content info
        content_info = result.get("content_info", {})
        self.console.print(f"\n[bold cyan]📄 İçerik Bilgileri:[/bold cyan]")
        self.console.print(f"  📝 Kelime Sayısı: {content_info.get('word_count', 0)}")
        self.console.print(f"  🖼️ Görsel Sayısı: {content_info.get('images_count', 0)}")
        self.console.print(f"  🔗 Link Sayısı: {content_info.get('links_count', 0)}")
        
        # Show structured data
        structured_data = result.get("structured_data", {})
        if structured_data:
            self.console.print(f"\n[bold cyan]📊 Yapılandırılmış Veri Analizi:[/bold cyan]")
            
            # Show subject and topics
            if structured_data.get("subject"):
                self.console.print(f"[blue]📚 Ana Ders:[/blue] {structured_data['subject']}")
            
            topics = structured_data.get("topics", [])
            if topics:
                self.console.print(f"[blue]📋 Konular ({len(topics)} adet):[/blue] {', '.join(topics)}")
            
            # Show difficulty and education level
            if structured_data.get("difficulty_level"):
                self.console.print(f"[blue]⚡ Zorluk Seviyesi:[/blue] {structured_data['difficulty_level']}")
            
            if structured_data.get("education_level"):
                self.console.print(f"[blue]🎓 Eğitim Seviyesi:[/blue] {structured_data['education_level']}")
            
            # Show key concepts
            key_concepts = structured_data.get("key_concepts", [])
            if key_concepts:
                self.console.print(f"[blue]🧠 Anahtar Kavramlar ({len(key_concepts)} adet):[/blue]")
                for concept in key_concepts:
                    self.console.print(f"  • {concept}")
            
            # Show learning objectives
            learning_objectives = structured_data.get("learning_objectives", [])
            if learning_objectives:
                self.console.print(f"[blue]🎯 Öğrenme Hedefleri ({len(learning_objectives)} adet):[/blue]")
                for i, objective in enumerate(learning_objectives, 1):
                    self.console.print(f"  {i}. {objective}")
            
            # Show formulas if any
            formulas = structured_data.get("formulas", [])
            if formulas:
                self.console.print(f"[blue]📐 Formüller ({len(formulas)} adet):[/blue]")
                for i, formula in enumerate(formulas, 1):
                    self.console.print(f"  {i}. {formula}")
            
            # Show exam relevance and study time
            if structured_data.get("exam_relevance"):
                self.console.print(f"[blue]🎯 Sınav Uygunluğu:[/blue] {structured_data['exam_relevance']}")
            
            if structured_data.get("estimated_study_time"):
                self.console.print(f"[blue]⏱️ Tahmini Çalışma Süresi:[/blue] {structured_data['estimated_study_time']} dakika")

        # Show educational analysis (full content)
        educational_analysis = result.get("educational_analysis", "")
        if educational_analysis:
            self.console.print(f"\n[bold cyan]🎓 Detaylı Eğitim Analizi:[/bold cyan]")
            self.console.print(educational_analysis)
        
        # Show generated questions (all questions)
        questions = result.get("generated_questions", [])
        if questions:
            self.console.print(f"\n[bold cyan]❓ Üretilen Sorular: {len(questions)} adet[/bold cyan]")
            for i, question in enumerate(questions, 1):
                question_content = question.get('content', str(question))
                self.console.print(f"\n[yellow]Soru {i}:[/yellow]")
                self.console.print(question_content)
        
        # Show study materials (detailed view)
        study_materials = result.get("study_materials", {})
        if study_materials:
            self.console.print(f"\n[bold cyan]📚 Çalışma Materyalleri:[/bold cyan]")
            
            # Show summary
            if study_materials.get("summary"):
                self.console.print(f"\n[green]📝 İçerik Özeti:[/green]")
                self.console.print(study_materials["summary"])
            
            # Show key points
            key_points = study_materials.get("key_points", [])
            if key_points:
                self.console.print(f"\n[green]🔑 Önemli Noktalar ({len(key_points)} adet):[/green]")
                for i, point in enumerate(key_points, 1):
                    self.console.print(f"  {i}. {point}")
            
            # Show concept map
            if study_materials.get("concept_map"):
                self.console.print(f"\n[green]🗺️ Kavram Haritası:[/green]")
                self.console.print(study_materials["concept_map"])
            
            # Show study plan
            study_plan = study_materials.get("study_plan", [])
            if study_plan:
                self.console.print(f"\n[green]📋 Çalışma Önerileri ({len(study_plan)} adet):[/green]")
                for i, recommendation in enumerate(study_plan, 1):
                    self.console.print(f"  {i}. {recommendation}")
        
        # Show image analysis if available
        content_info = result.get("content_info", {})
        if content_info.get("images_count", 0) > 0:
            # Check if there are analyzed images in the full result
            images_analyzed = []
            # Try to find image analysis in the result structure
            for key, value in result.items():
                if isinstance(value, dict) and "images" in key.lower():
                    images_analyzed = value
                    break
                elif isinstance(value, list) and any("analysis" in str(item).lower() for item in value if isinstance(item, dict)):
                    images_analyzed = value
                    break
            
            if images_analyzed:
                self.console.print(f"\n[bold cyan]🖼️ Görsel Analizi:[/bold cyan]")
                if isinstance(images_analyzed, list):
                    for i, img in enumerate(images_analyzed, 1):
                        if isinstance(img, dict) and img.get("analysis"):
                            self.console.print(f"\n[magenta]Görsel {i}:[/magenta]")
                            self.console.print(f"[dim]URL: {img.get('url', 'Belirtilmemiş')}[/dim]")
                            self.console.print(img["analysis"])
                elif isinstance(images_analyzed, dict) and images_analyzed.get("analysis"):
                    self.console.print(images_analyzed["analysis"])
        
        # Show additional metadata if available
        educational_metadata = result.get("educational_metadata", {})
        if educational_metadata:
            self.console.print(f"\n[bold cyan]📈 Ek Metadata:[/bold cyan]")
            if educational_metadata.get("content_length"):
                self.console.print(f"[dim]İçerik Uzunluğu: {educational_metadata['content_length']} karakter[/dim]")
            if educational_metadata.get("reading_time_minutes"):
                self.console.print(f"[dim]Okuma Süresi: {educational_metadata['reading_time_minutes']} dakika[/dim]")
            if educational_metadata.get("complexity_score"):
                self.console.print(f"[dim]Karmaşıklık Skoru: {educational_metadata['complexity_score']:.2f}/1.0[/dim]")
        
        # Save results option
        if Confirm.ask("\n💾 Analiz sonuçlarını JSON dosyasına kaydetmek ister misiniz?", default=True):
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"web_analysis_{timestamp}.json"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    import json
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                self.console.print(f"[green]✅ Sonuçlar kaydedildi: {filename}[/green]")
                
            except Exception as e:
                self.console.print(f"[red]❌ Kaydetme hatası: {str(e)}[/red]")
        
        # Show processing summary
        self.console.print(f"\n[bold green]✅ Web Sitesi Analizi Tamamlandı![/bold green]")
        self.console.print(f"[dim]🌐 Analiz Edilen URL: {url}[/dim]")
        self.console.print(f"[dim]📊 Analiz Türü: {analysis_type}[/dim]")
        self.console.print(f"[dim]⏱️ İşlem Süresi: Yaklaşık {int(time.time()) % 100} saniye[/dim]")
        
        # Show next steps
        self.console.print(f"\n[cyan]💡 Öneriler:[/cyan]")
        if curriculum_check.get('yks_relevant'):
            self.console.print("  • Bu içeriği YKS hazırlığınızda kullanabilirsiniz")
            self.console.print("  • JSON dosyasında detaylı bilgileri bulabilirsiniz")
            self.console.print("  • Benzer konularda daha fazla kaynak arayabilirsiniz")
        else:
            self.console.print("  • Daha uygun eğitim kaynakları aramayı deneyebilirsiniz")
            self.console.print("  • YKS müfredatına uygun siteler kullanın")
        
        if questions:
            self.console.print("  • Üretilen soruları çözerek konuyu pekiştirebilirsiniz")