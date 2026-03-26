from rich.prompt import Prompt
from .utils.hierarchical_menu import hierarchical_menu

class CurriculumManager:
    
    async def show_curriculum(self):
        """Hiyerarşik müfredat göster sistemi"""
        from core.unified_curriculum import unified_curriculum
        
        console.print(Panel("[bold green]📚 HIYERAŞİK MÜFREDAT GÖSTERİM SİSTEMİ[/bold green]"))
        
        # Ensure curriculum is loaded
        if not unified_curriculum.loader.curriculum_data:
            self.console.print("[yellow]Müfredat verileri yükleniyor...[/yellow]")
            success = unified_curriculum.loader.load_all_curriculum()
            if not success:
                self.console.print("[red]Müfredat verileri yüklenemedi![/red]")
                return
            self.console.print("[green]✓ Müfredat verileri yüklendi[/green]")
        
        self.console.print("\n[bold cyan]Müfredat Görüntüleme Modları:[/bold cyan]")
        self.console.print("  1. Hiyerarşik Gezinti - Kademeli müfredat seçimi")
        self.console.print("  2. Uzman İncelemesi - Dersin uzmanı ile müfredat analizi")
        self.console.print("  3. Genel Görüntüleme - Tüm derslerin özeti")
        
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
        
        self.console.print(f"\n[bold green]🎓 {subject_name} Uzmanı ile Müfredat İncelemesi[/bold green]")
        
        # Müfredat verilerini al
        curriculum_data = None
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
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
                self.console.print(f"[dim]📊 Müfredat: {topic_count} konu bulundu[/dim]")
        
        # Uzman analizi
        expert_query = f"""
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
            console=self.console
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
                self.console.print(f"\n[bold green]📚 {subject_name} Müfredat Analizi:[/bold green]")
                self.console.print(response_data.get('response', 'Müfredat bilgisi alınamadı'))
                
                if response_data.get('system_used'):
                    self.console.print(f"\n[dim]🎓 Uzman: {response_data['system_used']}[/dim]")
            else:
                self.console.print(f"[red]Uzman müfredat analizi hatası: {response_data.get('error', 'Bilinmeyen hata')}[/red]")
    
    async def _general_curriculum_overview(self):
        """Genel müfredat özeti"""
        self.log_rag_activity("Curriculum Data Access", collection="curriculum")
        
        result = await self.call_api("/curriculum", "GET")
        
        if result.get("success"):
            # API returns summary and curriculum data directly
            summary = result.get("summary", {})
            curriculum_data = result.get("curriculum", {})
            
            self.console.print(f"\n[bold green]📊 GENEL MÜFREDAT ÖZETİ[/bold green]")
            self.console.print(f"Toplam Ders: {summary.get('total_subjects', 0)}")
            self.console.print(f"Toplam Konu: {summary.get('total_topics', 0)}")
            
            # Dersleri göster
            table = Table(title="Mevcut Dersler")
            table.add_column("Ders", style="cyan")
            table.add_column("Konu Sayısı", style="green")
            table.add_column("Sınıflar", style="yellow")
            
            # Use curriculum data directly from API
            for subject, info in curriculum_data.items():
                # Get grades from the grades dict
                grades_dict = info.get("grades", {})
                grade_list = list(grades_dict.keys())
                grades_str = ", ".join(sorted(grade_list))
                
                table.add_row(
                    subject,
                    str(info.get("total_topics", 0)),
                    grades_str
                )
            
            self.console.print(table)
            
            # Also show subjects from summary if available
            if summary.get("subjects"):
                self.console.print(f"\n[bold]Ders Detayları:[/bold]")
                for subject, details in summary.get("subjects", {}).items():
                    self.console.print(f"  • {subject}: {details.get('topic_count', 0)} konu")
            
            self.log_rag_activity(
                "General Curriculum Overview Displayed",
                results_count=len(curriculum_data)
            )
        else:
            self.console.print(f"[red]Error: {result.get('error', 'Unknown error')}[/red]")
            
    async def _show_curriculum_details(self, subject_name: str, subject_code: str, grade: str, unit_code: str, subtopic_code: str):
        """Müfredat detaylarını göster"""
        from core.curriculum_details import curriculum_details
        
        curriculum_details.show_curriculum_details(subject_name, subject_code, grade, unit_code, subtopic_code)