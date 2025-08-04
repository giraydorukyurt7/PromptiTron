
"""
Hierarchical Menu System for Curriculum Navigation
Provides step-by-step navigation through curriculum structure
"""
from typing import Dict, List, Any, Optional, Tuple
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from core.curriculum_loader import curriculum_loader
import logging

logger = logging.getLogger(__name__)
console = Console()

class HierarchicalMenuSystem:
    pass
    
    def __init__(self):
        self.subjects = {
            "1. Matematik": "matematik",
            "2. Fizik": "fizik", 
            "3. Kimya": "kimya",
            "4. Biyoloji": "biyoloji",
            "5. Turk Dili ve Edebiyati": "turk_dili_ve_edebiyati",
            "6. Tarih": "tarih",
            "7. Cografya": "cografya",
            "8. Felsefe": "felsefe",
            "9. Din Kulturu": "din_kulturu",
            "10. Inkilap ve Ataturkculuk": "inkilap_ve_ataturkculuk"
        }
        
    def show_subject_selection(self) -> Optional[Tuple[str, str]]:
        pass
        console.print("\n[bold cyan]📚 DERS SECIMI[/bold cyan]")
        console.print(Panel("Hangi dersten islem yapmak istiyorsunuz?", title="Adim 1/5"))
        
        # Dersleri listele
        for choice in self.subjects.keys():
            console.print(f"  {choice}")
        console.print("  0. ← Geri Don")
        
        try:
            selection = Prompt.ask(
                "\nSeciminiz", 
                choices=list(self.subjects.keys()) + ["0. ← Geri Don"]
            )
            
            if selection == "0. ← Geri Don":
                return None
                
            subject_code = self.subjects[selection]
            subject_name = selection.split(". ")[1]
            
            console.print(f"[green]✓ Secilen ders: {subject_name}[/green]")
            return subject_name, subject_code
            
        except KeyboardInterrupt:
            return None
            
    def show_grade_selection(self, subject_name: str, subject_code: str) -> Optional[str]:
        pass
        console.print(f"\n[bold cyan]🎓 SINIF SECIMI - {subject_name}[/bold cyan]")
        console.print(Panel("Hangi sinif seviyesini seciyorsunuz?", title="Adim 2/5"))
        
        # Curriculum'dan siniflari al
        available_grades = self._get_available_grades(subject_name, subject_code)
        
        if not available_grades:
            console.print("[red]Bu ders icin sinif bilgisi bulunamadi[/red]")
            return None
            
        # Siniflari listele
        grade_choices = {}
        for i, grade in enumerate(available_grades, 1):
            choice_text = f"{i}. {grade}. Sinif"
            grade_choices[choice_text] = grade
            console.print(f"  {choice_text}")
        console.print("  0. ← Geri Don")
        
        try:
            selection = Prompt.ask(
                "\nSeciminiz",
                choices=list(grade_choices.keys()) + ["0. ← Geri Don"]
            )
            
            if selection == "0. ← Geri Don":
                return None
                
            selected_grade = grade_choices[selection]
            console.print(f"[green]✓ Secilen sinif: {selected_grade}. Sinif[/green]")
            return selected_grade
            
        except KeyboardInterrupt:
            return None
            
    def show_unit_selection(self, subject_name: str, subject_code: str, grade: str) -> Optional[Tuple[str, str]]:
        pass
        console.print(f"\n[bold cyan]📖 UNITE SECIMI - {subject_name} {grade}. Sinif[/bold cyan]")
        console.print(Panel("Hangi uniteden islem yapmak istiyorsunuz?", title="Adim 3/5"))
        
        # Curriculum'dan uniteleri al
        available_units = self._get_available_units(subject_name, subject_code, grade)
        
        if not available_units:
            console.print("[red]Bu sinif icin unite bilgisi bulunamadi[/red]")
            return None
            
        # Uniteleri listele
        unit_choices = {}
        for i, (unit_code, unit_title) in enumerate(available_units.items(), 1):
            choice_text = f"{i}. {unit_code}"
            if unit_title:
                choice_text += f" - {unit_title[:60]}..."
            unit_choices[choice_text] = (unit_code, unit_title)
            console.print(f"  {choice_text}")
        console.print("  0. ← Geri Don")
        
        try:
            selection = Prompt.ask(
                "\nSeciminiz",
                choices=list(unit_choices.keys()) + ["0. ← Geri Don"]
            )
            
            if selection == "0. ← Geri Don":
                return None
                
            unit_code, unit_title = unit_choices[selection]
            console.print(f"[green]✓ Secilen unite: {unit_code}[/green]")
            return unit_code, unit_title
            
        except KeyboardInterrupt:
            return None
            
    def show_subtopic_selection(self, subject_name: str, subject_code: str, grade: str, unit_code: str) -> Optional[Tuple[str, str]]:
        pass
        console.print(f"\n[bold cyan]🔍 ALT KONU SECIMI - {subject_name} {grade}. Sinif > {unit_code}[/bold cyan]")
        console.print(Panel("Hangi alt konudan islem yapmak istiyorsunuz?", title="Adim 4/5"))
        
        # Curriculum'dan alt konulari al
        available_subtopics = self._get_available_subtopics(subject_name, subject_code, grade, unit_code)
        
        if not available_subtopics:
            console.print("[yellow]Bu unite icin alt konu bulunamadi, dogrudan unite ile devam ediliyor[/yellow]")
            return unit_code, f"{unit_code} - Genel"
            
        # Alt konulari listele
        subtopic_choices = {}
        for i, (subtopic_code, subtopic_title) in enumerate(available_subtopics.items(), 1):
            choice_text = f"{i}. {subtopic_code}"
            if subtopic_title:
                choice_text += f" - {subtopic_title[:50]}..."
            subtopic_choices[choice_text] = (subtopic_code, subtopic_title)
            console.print(f"  {choice_text}")
        console.print("  98. Tum Alt Konular")
        console.print("  0. ← Geri Don")
        
        try:
            all_choices = list(subtopic_choices.keys()) + ["98. Tum Alt Konular", "0. ← Geri Don"]
            selection = Prompt.ask("\nSeciminiz", choices=all_choices)
            
            if selection == "0. ← Geri Don":
                return None
            elif selection == "98. Tum Alt Konular":
                console.print(f"[green]✓ Secilen: Tum alt konular[/green]")
                return "ALL", f"{unit_code} - Tum Alt Konular"
                
            subtopic_code, subtopic_title = subtopic_choices[selection]
            console.print(f"[green]✓ Secilen alt konu: {subtopic_code}[/green]")
            return subtopic_code, subtopic_title
            
        except KeyboardInterrupt:
            return None
            
    def show_action_selection(self, context: Dict[str, Any]) -> Optional[str]:
        pass
        subject_name = context.get('subject_name', '')
        grade = context.get('grade', '')
        unit_code = context.get('unit_code', '')
        subtopic_code = context.get('subtopic_code', '')
        
        console.print(f"\n[bold cyan]⚡ ISLEM SECIMI[/bold cyan]")
        console.print(Panel(f"{subject_name} > {grade}. Sinif > {unit_code} > {subtopic_code}", title="Adim 5/5"))
        
        actions = {
            "1. 📝 Soru Olustur": "generate_questions",
            "2. 📚 Mufredat Detayini Goster": "show_curriculum",
            "3. 🎯 Uzmanla Danis": "consult_expert"
        }
        
        for choice in actions.keys():
            console.print(f"  {choice}")
        console.print("  0. ← Geri Don")
        
        try:
            selection = Prompt.ask(
                "\nSeciminiz",
                choices=list(actions.keys()) + ["0. ← Geri Don"]
            )
            
            if selection == "0. ← Geri Don":
                return None
                
            action = actions[selection]
            console.print(f"[green]✓ Secilen islem: {selection}[/green]")
            return action
            
        except KeyboardInterrupt:
            return None
            
    def _get_available_grades(self, subject_name: str, subject_code: str) -> List[str]:
        pass
        try:
            # Subject name mapping - curriculum'daki gercek isimler
            name_mapping = {
                "Matematik": "Matematik",
                "Fizik": "Fizik",
                "Kimya": "Kimya",
                "Biyoloji": "Biyoloji",
                "Turk Dili ve Edebiyati": "Turk Dili ve Edebiyati",
                "Tarih": "Tarih",
                "Cografya": "Cografya",
                "Felsefe": "Felsefe",
                "Din Kulturu": "Din Kulturu",
                "Inkilap ve Ataturkculuk": "Inkilap ve Ataturkculuk"
            }
            
            actual_subject_name = name_mapping.get(subject_name, subject_name)
            
            # Curriculum loader'dan subject data'yi al
            subject_data = curriculum_loader.curriculum_data.get(actual_subject_name, {})
            
            if 'yks' not in subject_data:
                return []
                
            yks_data = subject_data['yks']
            
            # Subject key'i bul - mapping tablosu kullan
            subject_mapping = {
                "matematik": "matematik",
                "fizik": "fizik",
                "kimya": "kimya",
                "biyoloji": "biyoloji",
                "turk_dili_ve_edebiyati": "turk_dili_ve_edebiyati",
                "tarih": "tarih",
                "cografya": "cografya",
                "felsefe": "felsefe",
                "din_kulturu": "din_kulturu",
                "inkilap_ve_ataturkculuk": "inkilap_ve_ataturkculuk"
            }
            
            subject_key = subject_mapping.get(subject_code)
            if not subject_key or subject_key not in yks_data:
                # Fallback: fuzzy matching
                for key in yks_data.keys():
                    if subject_code in key or key in subject_code:
                        subject_key = key
                        break
            
            if not subject_key or subject_key not in yks_data:
                return []
                
            curriculum_data = yks_data[subject_key]
            
            # Sinif anahtarlarini al ve sirala
            grades = []
            for key in curriculum_data.keys():
                if key.isdigit():
                    grades.append(key)
                    
            return sorted(grades, key=int)
            
        except Exception as e:
            logger.error(f"Error getting grades for {subject_name}: {e}")
            return []
            
    def _get_available_units(self, subject_name: str, subject_code: str, grade: str) -> Dict[str, str]:
        pass
        try:
            # Subject name mapping
            name_mapping = {
                "Matematik": "Matematik", "Fizik": "Fizik", "Kimya": "Kimya", "Biyoloji": "Biyoloji",
                "Turk Dili ve Edebiyati": "Turk Dili ve Edebiyati", "Tarih": "Tarih",
                "Cografya": "Cografya", "Felsefe": "Felsefe", "Din Kulturu": "Din Kulturu",
                "Inkilap ve Ataturkculuk": "Inkilap ve Ataturkculuk"
            }
            actual_subject_name = name_mapping.get(subject_name, subject_name)
            subject_data = curriculum_loader.curriculum_data.get(actual_subject_name, {})
            
            if 'yks' not in subject_data:
                return {}
                
            yks_data = subject_data['yks']
            
            # Subject key'i bul - mapping tablosu kullan
            subject_mapping = {
                "matematik": "matematik",
                "fizik": "fizik",
                "kimya": "kimya",
                "biyoloji": "biyoloji",
                "turk_dili_ve_edebiyati": "turk_dili_ve_edebiyati",
                "tarih": "tarih",
                "cografya": "cografya",
                "felsefe": "felsefe",
                "din_kulturu": "din_kulturu",
                "inkilap_ve_ataturkculuk": "inkilap_ve_ataturkculuk"
            }
            
            subject_key = subject_mapping.get(subject_code)
            if not subject_key or subject_key not in yks_data:
                # Fallback: fuzzy matching
                for key in yks_data.keys():
                    if subject_code in key or key in subject_code:
                        subject_key = key
                        break
                    
            if not subject_key:
                return {}
                
            curriculum_data = yks_data[subject_key]
            
            if grade not in curriculum_data:
                return {}
                
            grade_data = curriculum_data[grade]
            units = {}
            
            if isinstance(grade_data, dict):
                if 'alt' in grade_data:
                    # Matematik tipi yapi
                    alt_data = grade_data['alt']
                    for unit_code, unit_info in alt_data.items():
                        if isinstance(unit_info, dict):
                            title = unit_info.get('baslik', '')
                            units[unit_code] = title
                else:
                    # Cografya tipi yapi - dogrudan uniteler
                    for unit_code, unit_info in grade_data.items():
                        if isinstance(unit_info, dict):
                            # Unit title'i bul
                            title = unit_code  # Varsayilan olarak kod
                            units[unit_code] = title
                            
            return units
            
        except Exception as e:
            logger.error(f"Error getting units for {subject_name} grade {grade}: {e}")
            return {}
            
    def _get_available_subtopics(self, subject_name: str, subject_code: str, grade: str, unit_code: str) -> Dict[str, str]:
        pass
        try:
            # Subject name mapping
            name_mapping = {
                "Matematik": "Matematik", "Fizik": "Fizik", "Kimya": "Kimya", "Biyoloji": "Biyoloji",
                "Turk Dili ve Edebiyati": "Turk Dili ve Edebiyati", "Tarih": "Tarih",
                "Cografya": "Cografya", "Felsefe": "Felsefe", "Din Kulturu": "Din Kulturu",
                "Inkilap ve Ataturkculuk": "Inkilap ve Ataturkculuk"
            }
            actual_subject_name = name_mapping.get(subject_name, subject_name)
            subject_data = curriculum_loader.curriculum_data.get(actual_subject_name, {})
            
            if 'yks' not in subject_data:
                return {}
                
            yks_data = subject_data['yks']
            
            # Subject key'i bul - mapping tablosu kullan
            subject_mapping = {
                "matematik": "matematik",
                "fizik": "fizik",
                "kimya": "kimya",
                "biyoloji": "biyoloji",
                "turk_dili_ve_edebiyati": "turk_dili_ve_edebiyati",
                "tarih": "tarih",
                "cografya": "cografya",
                "felsefe": "felsefe",
                "din_kulturu": "din_kulturu",
                "inkilap_ve_ataturkculuk": "inkilap_ve_ataturkculuk"
            }
            
            subject_key = subject_mapping.get(subject_code)
            if not subject_key or subject_key not in yks_data:
                # Fallback: fuzzy matching
                for key in yks_data.keys():
                    if subject_code in key or key in subject_code:
                        subject_key = key
                        break
                    
            if not subject_key:
                return {}
                
            curriculum_data = yks_data[subject_key]
            
            if grade not in curriculum_data:
                return {}
                
            grade_data = curriculum_data[grade]
            subtopics = {}
            
            if isinstance(grade_data, dict):
                if 'alt' in grade_data and unit_code in grade_data['alt']:
                    # Matematik tipi yapi
                    unit_data = grade_data['alt'][unit_code]
                    if isinstance(unit_data, dict) and 'alt' in unit_data:
                        for subtopic_code, subtopic_info in unit_data['alt'].items():
                            if isinstance(subtopic_info, dict):
                                title = subtopic_info.get('baslik', '')
                                subtopics[subtopic_code] = title
                elif unit_code in grade_data:
                    # Cografya tipi yapi
                    unit_data = grade_data[unit_code]
                    if isinstance(unit_data, dict):
                        for subtopic_code, subtopic_info in unit_data.items():
                            if isinstance(subtopic_info, dict) and 'baslik' in subtopic_info:
                                title = subtopic_info.get('baslik', '')
                                subtopics[subtopic_code] = title
                                
            return subtopics
            
        except Exception as e:
            logger.error(f"Error getting subtopics for {subject_name} grade {grade} unit {unit_code}: {e}")
            return {}

# Global instance
hierarchical_menu = HierarchicalMenuSystem()