import time
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from .utils.hierarchical_menu import hierarchical_menu

class QuestionGenerator:
    async def generate_questions(self):
        """Hiyerarşik soru oluşturma sistemi"""
        from core.unified_curriculum import unified_curriculum
        
        self.console.print(Panel("[bold yellow]🎯 HIYERAŞİK SORU OLUŞTURMA SİSTEMİ[/bold yellow]"))
        
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
        self.console.print(f"\n[bold cyan]📝 SORU PARAMETRELERİ[/bold cyan]")
        self.console.print(Panel(f"Seçilen: {subject_name} > {grade}. Sınıf > {unit_code} > {subtopic_code}", title="Seçim Özeti"))
        
        # Zorluk seviyesi
        difficulty_choices = {
            "1. Kolay": "easy",
            "2. Orta": "medium", 
            "3. Zor": "hard"
        }
        
        self.console.print("\n[bold cyan]Zorluk Seviyeleri:[/bold cyan]")
        for choice in difficulty_choices.keys():
            self.console.print(f"  {choice}")
            
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
        
        self.console.print("\n[bold cyan]Soru Tipleri:[/bold cyan]")
        for choice in question_type_choices.keys():
            self.console.print(f"  {choice}")
            
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
            
        self.console.print(f"\n[bold green]🎯 SORU OLUŞTURMA BAŞLADI[/bold green]")
        self.console.print(f"Konu: {detailed_topic}")
        self.console.print(f"Zorluk: {difficulty}, Tip: {question_type}, Sayı: {count}")
        self.console.print(f"Sınav Tipi: {exam_type} (Sınıf {grade} için otomatik seçildi)")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
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
                self.console.print(f"\n[bold]Generated Questions:[/bold]")
                self.console.print(questions)
            elif isinstance(questions, list):
                # If questions is a list, process each question
                for i, question in enumerate(questions, 1):
                    self.console.print(f"\n[bold]Question {i}:[/bold]")
                    
                    if isinstance(question, dict):
                        self.console.print(question.get("question_text", str(question)))
                        
                        if question.get("options"):
                            for opt_key, opt_value in question["options"].items():
                                self.console.print(f"  {opt_key}) {opt_value}")
                        
                        self.console.print(f"[green]Answer: {question.get('correct_answer', '')}[/green]")
                        if question.get("explanation"):
                            self.console.print(f"[dim]Explanation: {question['explanation']}[/dim]")
                    else:
                        # Handle string questions in list
                        self.console.print(str(question))
            else:
                self.console.print(f"[yellow]Questions format: {type(questions)}[/yellow]")
                self.console.print(str(questions))
        else:
            self.console.print(f"[red]Error: {result.get('error', 'Unknown error')}[/red]")
            
            # Show raw response for debugging if available
            if "raw_response" in result:
                self.console.print(f"\n[dim]Raw Response:[/dim]")
                self.console.print(result["raw_response"][:500] + "..." if len(result["raw_response"]) > 500 else result["raw_response"])