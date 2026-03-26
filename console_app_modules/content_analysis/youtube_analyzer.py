import time
from datetime import datetime
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

class YouTubeAnalyzer:
    async def analyze_youtube_video(self):
        """YouTube video analizi yap - YKS müfredat uygunluk kontrolü ile"""
        self.console.print(Panel("[bold blue]📺 YouTube Video Analysis - YKS Curriculum Check[/bold blue]"))
        self.console.print("[dim]✨ YouTube videosunu transkribe edip YKS müfredatına uygunluk açısından analiz eder[/dim]")
        
        # Info about new reliable system
        self.console.print()
        self.console.print("[green]✨ YENİ: YouTube otomatik transkriptleri kullanılıyor![/green]")
        self.console.print("[green]   Gerçek video verileri ve otomatik altyazılar analiz edilir.[/green]")
        self.console.print("[yellow]   Not: Transkript olmayan videolar analiz edilemez.[/yellow]")
        self.console.print()
        
        # YouTube URL input with validation
        while True:
            url = Prompt.ask("Analiz edilecek YouTube video URL'si")
            
            if not url.startswith(('http://', 'https://')):
                self.console.print("[red]❌ Geçersiz URL formatı. YouTube linki ile başlamalıdır.[/red]")
                continue
            
            # YouTube URL validation - improved patterns
            youtube_patterns = [
                'youtube.com/watch?v=',
                'youtu.be/',
                'youtube.com/embed/',
                'youtube.com/v/',
                'm.youtube.com/watch?v='
            ]
            
            if not any(pattern in url for pattern in youtube_patterns):
                self.console.print("[red]❌ Geçerli bir YouTube URL'si girin.[/red]")
                continue
            
            break
        
        # Analysis type selection
        analysis_choices = {
            "1. Tam Analiz": "full",
            "2. Hızlı Kontrol": "quick", 
            "3. Sadece Transkript": "transcript_only"
        }
        
        self.console.print("\n[bold cyan]Analiz Türü:[/bold cyan]")
        self.console.print("  1. Tam Analiz - Transkript + eğitim analizi + soru üretimi (Önerilen)")
        self.console.print("  2. Hızlı Kontrol - Temel transkript ve analiz")
        self.console.print("  3. Sadece Transkript - Video transkribe et")
        
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
            task = progress.add_task("YouTube video analiz ediliyor...", total=None)
            
            try:
                # Import YouTube analyzer
                from core.youtube_analyzer import youtube_analyzer
                
                progress.update(task, description="Video transkribe ediliyor...")
                
                # Analyze YouTube video
                result = await youtube_analyzer.analyze_youtube_video(
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
            self.console.print("[red]❌ YouTube video analizi başarısız oldu.[/red]")
            return
        
        # Show curriculum check results
        curriculum_check = result.get("curriculum_check", {})
        yks_relevant = curriculum_check.get("yks_relevant", False)
        
        self.console.print("\n" + "="*60)
        self.console.print(Panel("[bold green]📊 YKS Müfredat Uygunluk Kontrolü[/bold green]"))
        
        if yks_relevant:
            self.console.print("[green]✅ Video içeriği YKS müfredatına uygun[/green]")
            self.console.print(f"[cyan]🎯 İlgili Dersler: {', '.join(curriculum_check.get('subjects', []))}[/cyan]")
            self.console.print(f"[blue]🎖️ Güven Skoru: {curriculum_check.get('confidence_score', 0):.2f}/1.0[/blue]")
            self.console.print(f"[dim]Eğitim Seviyesi: {curriculum_check.get('education_level', 'Belirtilmemiş')}[/dim]")
            self.console.print(f"[dim]Video Kalitesi: {curriculum_check.get('video_quality', 'Belirtilmemiş')}[/dim]")
        else:
            self.console.print("[red]❌ Video içeriği YKS müfredat dışı[/red]")
            self.console.print(f"[yellow]⚠️ Sebep: {curriculum_check.get('reason', 'Belirtilmemiş')}[/yellow]")
            self.console.print("[dim]Bu YouTube videosu YKS dersleriyle ilgili eğitim içeriği içermiyor.[/dim]")
            return
        
        # Show video info
        video_info = result.get("video_info", {})
        self.console.print(f"\n[bold cyan]📹 Video Bilgileri:[/bold cyan]")
        self.console.print(f"  📝 Başlık: {video_info.get('title', 'YouTube Video')}")
        self.console.print(f"  ⏱️ Süre: {video_info.get('duration', 'Bilinmiyor')}")
        self.console.print(f"  📄 Transkript Uzunluğu: {video_info.get('transcript_length', 0)} karakter")
        self.console.print(f"  🎬 Görsel Sahne Sayısı: {video_info.get('visual_scenes', 0)}")
        
        # Show transcript (partial)
        transcript = result.get("transcript", "")
        if transcript:
            self.console.print(f"\n[bold cyan]🎙️ Video Transkripti:[/bold cyan]")
            if len(transcript) > 1000:
                self.console.print(transcript[:1000] + "...")
                self.console.print(f"[dim]... (Tam transkript {len(transcript)} karakter - JSON dosyasında)[/dim]")
            else:
                self.console.print(transcript)
        
        # Show timestamps
        timestamps = result.get("timestamps", [])
        if timestamps:
            self.console.print(f"\n[bold cyan]⏰ Önemli Zaman Damgaları:[/bold cyan]")
            for i, timestamp in enumerate(timestamps[:10], 1):  # Show first 10
                self.console.print(f"  {i}. {timestamp}")
            if len(timestamps) > 10:
                self.console.print(f"  ... ve {len(timestamps)-10} zaman damgası daha")
        
        # Show visual descriptions
        visual_descriptions = result.get("visual_descriptions", [])
        if visual_descriptions:
            self.console.print(f"\n[bold cyan]🎨 Görsel Açıklamalar:[/bold cyan]")
            for i, desc in enumerate(visual_descriptions[:5], 1):  # Show first 5
                self.console.print(f"  {i}. {desc}")
            if len(visual_descriptions) > 5:
                self.console.print(f"  ... ve {len(visual_descriptions)-5} görsel açıklama daha")
        
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
                self.console.print(f"\n[green]📝 Video Özeti:[/green]")
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
                self.console.print(f"\n[green]📋 Video İzleme Önerileri ({len(study_plan)} adet):[/green]")
                for i, recommendation in enumerate(study_plan, 1):
                    self.console.print(f"  {i}. {recommendation}")
            
            # Show visual notes
            visual_notes = study_materials.get("visual_notes", [])
            if visual_notes:
                self.console.print(f"\n[green]🖼️ Görsel Notlar ({len(visual_notes)} adet):[/green]")
                for i, note in enumerate(visual_notes, 1):
                    self.console.print(f"  {i}. {note}")
        
        # Save results option
        if Confirm.ask("\n💾 Analiz sonuçlarını JSON dosyasına kaydetmek ister misiniz?", default=True):
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"youtube_analysis_{timestamp}.json"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    import json
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                self.console.print(f"[green]✅ Sonuçlar kaydedildi: {filename}[/green]")
                
            except Exception as e:
                self.console.print(f"[red]❌ Kaydetme hatası: {str(e)}[/red]")
        
        # Show processing summary
        self.console.print(f"\n[bold green]✅ YouTube Video Analizi Tamamlandı![/bold green]")
        self.console.print(f"[dim]📺 Analiz Edilen Video: {url}[/dim]")
        self.console.print(f"[dim]📊 Analiz Türü: {analysis_type}[/dim]")
        self.console.print(f"[dim]⏱️ Video ID: {result.get('video_id', 'Bilinmiyor')}[/dim]")
        
        # Show data source info
        if result.get('real_data'):
            self.console.print(f"\n[green]✅ Gerçek YouTube Verisi:[/green]")
            self.console.print(f"[green]   Video bilgileri ve transkript YouTube'dan alındı.[/green]")
            self.console.print(f"[green]   Bu analiz %100 doğru video içeriğine dayanmaktadır.[/green]")
        
        # Show next steps
        self.console.print(f"\n[cyan]💡 Öneriler:[/cyan]")
        if curriculum_check.get('yks_relevant'):
            self.console.print("  • Bu videoyu YKS hazırlığınızda kullanabilirsiniz")
            self.console.print("  • Videoyu not alarak tekrar izleyebilirsiniz")
            self.console.print("  • JSON dosyasında transkript ve detaylı bilgileri bulabilirsiniz")
            self.console.print("  • Benzer eğitim videolarını arayabilirsiniz")
        else:
            self.console.print("  • Daha uygun eğitim videoları aramayı deneyebilirsiniz")
            self.console.print("  • YKS müfredatına uygun kanalları takip edin")
        
        if questions:
            self.console.print("  • Üretilen soruları çözerek videoyu pekiştirebilirsiniz")
        
        if timestamps:
            self.console.print("  • Zaman damgalarını kullanarak önemli kısımları tekrar izleyebilirsiniz")