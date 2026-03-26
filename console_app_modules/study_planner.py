from rich.prompt import Prompt

class StudyPlanner:
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
                self.console.print(f"\n[bold green]📅 KİŞİSELLEŞTİRİLMİŞ ÇALIŞMA PLANI[/bold green]")
                self.console.print(Panel(plan, title=f"{duration_weeks} Haftalık YKS Çalışma Planı", expand=False))
                
                # Show summary
                self.console.print(f"\n[bold]Plan Özeti:[/bold]")
                self.console.print(f"• Hedef Sınav: {target_exam}")
                self.console.print(f"• Süre: {duration_weeks} hafta")
                self.console.print(f"• Günlük Çalışma: {daily_hours} saat")
                if weak_subjects:
                    self.console.print(f"• Zayıf Dersler: {', '.join([s.replace('_', ' ').title() for s in weak_subjects])}")
                if strong_subjects:
                    self.console.print(f"• Güçlü Dersler: {', '.join([s.replace('_', ' ').title() for s in strong_subjects])}")
                    
            elif isinstance(plan, dict):
                # Handle structured plan format
                self.console.print(f"\n[bold]Study Plan: {plan.get('plan_name', 'Custom Plan')}[/bold]")
                self.console.print(f"Duration: {plan.get('duration_weeks', 0)} weeks")
                self.console.print(f"Daily Hours: {plan.get('daily_hours', 0)}")
                
                if plan.get("weekly_schedule"):
                    for week in plan["weekly_schedule"]:
                        self.console.print(f"\n[bold]Week {week.get('week_number', 0)}:[/bold]")
                        for day in week.get("days", []):
                            self.console.print(f"  {day.get('day', '')}: {', '.join(day.get('subjects', []))}")
        else:
            self.console.print(f"[red]Error: {result.get('error', 'Unknown error')}[/red]")