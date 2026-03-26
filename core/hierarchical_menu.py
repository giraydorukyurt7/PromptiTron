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
    """Kademeli menü sistemi - müfredat ve soru oluşturma için"""
    
    def __init__(self):
        self.subjects = {
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
        
    def show_subject_selection(self) -> Optional[Tuple[str, str]]:
        """1. Adım: Ders seçimi"""
        console.print("\n[bold cyan]📚 DERS SEÇİMİ[/bold cyan]")
        console.print(Panel("Hangi dersten işlem yapmak istiyorsunuz?", title="Adım 1/5"))
        
        # Dersleri listele
        for choice in self.subjects.keys():
            console.print(f"  {choice}")
        console.print("  0. ← Geri Dön")
        
        try:
            selection = Prompt.ask(
                "\nSeçiminiz", 
                choices=list(self.subjects.keys()) + ["0. ← Geri Dön"]
            )
            
            if selection == "0. ← Geri Dön":
                return None
                
            subject_code = self.subjects[selection]
            subject_name = selection.split(". ")[1]
            
            console.print(f"[green]✓ Seçilen ders: {subject_name}[/green]")
            return subject_name, subject_code
            
        except KeyboardInterrupt:
            return None
            
    def show_grade_selection(self, subject_name: str, subject_code: str) -> Optional[str]:
        """2. Adım: Sınıf seçimi"""
        console.print(f"\n[bold cyan]🎓 SINIF SEÇİMİ - {subject_name}[/bold cyan]")
        console.print(Panel("Hangi sınıf seviyesini seçiyorsunuz?", title="Adım 2/5"))
        
        # Curriculum'dan sınıfları al
        available_grades = self._get_available_grades(subject_name, subject_code)
        
        if not available_grades:
            console.print("[red]Bu ders için sınıf bilgisi bulunamadı[/red]")
            return None
            
        # Sınıfları listele
        grade_choices = {}
        for i, grade in enumerate(available_grades, 1):
            choice_text = f"{i}. {grade}. Sınıf"
            grade_choices[choice_text] = grade
            console.print(f"  {choice_text}")
        console.print("  0. ← Geri Dön")
        
        try:
            selection = Prompt.ask(
                "\nSeçiminiz",
                choices=list(grade_choices.keys()) + ["0. ← Geri Dön"]
            )
            
            if selection == "0. ← Geri Dön":
                return None
                
            selected_grade = grade_choices[selection]
            console.print(f"[green]✓ Seçilen sınıf: {selected_grade}. Sınıf[/green]")
            return selected_grade
            
        except KeyboardInterrupt:
            return None
            
    def show_unit_selection(self, subject_name: str, subject_code: str, grade: str) -> Optional[Tuple[str, str]]:
        """3. Adım: Ünite seçimi"""
        console.print(f"\n[bold cyan]📖 ÜNİTE SEÇİMİ - {subject_name} {grade}. Sınıf[/bold cyan]")
        console.print(Panel("Hangi üniteden işlem yapmak istiyorsunuz?", title="Adım 3/5"))
        
        # Curriculum'dan üniteleri al
        available_units = self._get_available_units(subject_name, subject_code, grade)
        
        if not available_units:
            console.print("[red]Bu sınıf için ünite bilgisi bulunamadı[/red]")
            return None
            
        # Üniteleri listele
        unit_choices = {}
        for i, (unit_code, unit_title) in enumerate(available_units.items(), 1):
            choice_text = f"{i}. {unit_code}"
            if unit_title:
                choice_text += f" - {unit_title[:60]}..."
            unit_choices[choice_text] = (unit_code, unit_title)
            console.print(f"  {choice_text}")
        console.print("  0. ← Geri Dön")
        
        try:
            selection = Prompt.ask(
                "\nSeçiminiz",
                choices=list(unit_choices.keys()) + ["0. ← Geri Dön"]
            )
            
            if selection == "0. ← Geri Dön":
                return None
                
            unit_code, unit_title = unit_choices[selection]
            console.print(f"[green]✓ Seçilen ünite: {unit_code}[/green]")
            return unit_code, unit_title
            
        except KeyboardInterrupt:
            return None
            
    def show_subtopic_selection(self, subject_name: str, subject_code: str, grade: str, unit_code: str) -> Optional[Tuple[str, str]]:
        """4. Adım: Alt konu seçimi"""
        console.print(f"\n[bold cyan]🔍 ALT KONU SEÇİMİ - {subject_name} {grade}. Sınıf > {unit_code}[/bold cyan]")
        console.print(Panel("Hangi alt konudan işlem yapmak istiyorsunuz?", title="Adım 4/5"))
        
        # Curriculum'dan alt konuları al
        available_subtopics = self._get_available_subtopics(subject_name, subject_code, grade, unit_code)
        
        if not available_subtopics:
            console.print("[yellow]Bu ünite için alt konu bulunamadı, doğrudan ünite ile devam ediliyor[/yellow]")
            return unit_code, f"{unit_code} - Genel"
            
        # Alt konuları listele
        subtopic_choices = {}
        for i, (subtopic_code, subtopic_title) in enumerate(available_subtopics.items(), 1):
            choice_text = f"{i}. {subtopic_code}"
            if subtopic_title:
                choice_text += f" - {subtopic_title[:50]}..."
            subtopic_choices[choice_text] = (subtopic_code, subtopic_title)
            console.print(f"  {choice_text}")
        console.print("  98. Tüm Alt Konular")
        console.print("  0. ← Geri Dön")
        
        try:
            all_choices = list(subtopic_choices.keys()) + ["98. Tüm Alt Konular", "0. ← Geri Dön"]
            selection = Prompt.ask("\nSeçiminiz", choices=all_choices)
            
            if selection == "0. ← Geri Dön":
                return None
            elif selection == "98. Tüm Alt Konular":
                console.print(f"[green]✓ Seçilen: Tüm alt konular[/green]")
                return "ALL", f"{unit_code} - Tüm Alt Konular"
                
            subtopic_code, subtopic_title = subtopic_choices[selection]
            console.print(f"[green]✓ Seçilen alt konu: {subtopic_code}[/green]")
            return subtopic_code, subtopic_title
            
        except KeyboardInterrupt:
            return None
            
    def show_action_selection(self, context: Dict[str, Any]) -> Optional[str]:
        """5. Adım: İşlem seçimi"""
        subject_name = context.get('subject_name', '')
        grade = context.get('grade', '')
        unit_code = context.get('unit_code', '')
        subtopic_code = context.get('subtopic_code', '')
        
        console.print(f"\n[bold cyan]⚡ İŞLEM SEÇİMİ[/bold cyan]")
        console.print(Panel(f"{subject_name} > {grade}. Sınıf > {unit_code} > {subtopic_code}", title="Adım 5/5"))
        
        actions = {
            "1. 📝 Soru Oluştur": "generate_questions",
            "2. 📚 Müfredat Detayını Göster": "show_curriculum",
            "3. 🎯 Uzmanla Danış": "consult_expert"
        }
        
        for choice in actions.keys():
            console.print(f"  {choice}")
        console.print("  0. ← Geri Dön")
        
        try:
            selection = Prompt.ask(
                "\nSeçiminiz",
                choices=list(actions.keys()) + ["0. ← Geri Dön"]
            )
            
            if selection == "0. ← Geri Dön":
                return None
                
            action = actions[selection]
            console.print(f"[green]✓ Seçilen işlem: {selection}[/green]")
            return action
            
        except KeyboardInterrupt:
            return None
            
    def _get_available_grades(self, subject_name: str, subject_code: str) -> List[str]:
        """Curriculum'dan mevcut sınıfları al"""
        try:
            # Subject name mapping - curriculum'daki gerçek isimler
            name_mapping = {
                "Matematik": "Matematik",
                "Fizik": "Fizik",
                "Kimya": "Kimya",
                "Biyoloji": "Biyoloji",
                "Türk Dili ve Edebiyatı": "Türk Dili ve Edebiyatı",
                "Tarih": "Tarih",
                "Coğrafya": "Coğrafya",
                "Felsefe": "Felsefe",
                "Din Kültürü": "Din Kültürü",
                "İnkılap ve Atatürkçülük": "İnkılap ve Atatürkçülük"
            }
            
            actual_subject_name = name_mapping.get(subject_name, subject_name)
            
            # Curriculum loader'dan subject data'yı al
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
            
            # Sınıf anahtarlarını al ve sırala
            grades = []
            for key in curriculum_data.keys():
                if key.isdigit():
                    grades.append(key)
                    
            return sorted(grades, key=int)
            
        except Exception as e:
            logger.error(f"Error getting grades for {subject_name}: {e}")
            return []
            
    def _get_available_units(self, subject_name: str, subject_code: str, grade: str) -> Dict[str, str]:
        """Curriculum'dan mevcut üniteleri al"""
        try:
            # Subject name mapping
            name_mapping = {
                "Matematik": "Matematik", "Fizik": "Fizik", "Kimya": "Kimya", "Biyoloji": "Biyoloji",
                "Türk Dili ve Edebiyatı": "Türk Dili ve Edebiyatı", "Tarih": "Tarih",
                "Coğrafya": "Coğrafya", "Felsefe": "Felsefe", "Din Kültürü": "Din Kulturu",
                "İnkılap ve Atatürkçülük": "İnkılap ve Atatürkçülük"
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
                    # Matematik tipi yapı
                    alt_data = grade_data['alt']
                    for unit_code, unit_info in alt_data.items():
                        if isinstance(unit_info, dict):
                            title = unit_info.get('baslik', '')
                            units[unit_code] = title
                else:
                    # Coğrafya tipi yapı - doğrudan üniteler
                    for unit_code, unit_info in grade_data.items():
                        if isinstance(unit_info, dict):
                            # Unit title'ı bul
                            title = unit_code  # Varsayılan olarak kod
                            units[unit_code] = title
                            
            return units
            
        except Exception as e:
            logger.error(f"Error getting units for {subject_name} grade {grade}: {e}")
            return {}
            
    def _get_available_subtopics(self, subject_name: str, subject_code: str, grade: str, unit_code: str) -> Dict[str, str]:
        """Curriculum'dan mevcut alt konuları al"""
        try:
            # Subject name mapping
            name_mapping = {
                "Matematik": "Matematik", "Fizik": "Fizik", "Kimya": "Kimya", "Biyoloji": "Biyoloji",
                "Türk Dili ve Edebiyatı": "Türk Dili ve Edebiyatı", "Tarih": "Tarih",
                "Coğrafya": "Coğrafya", "Felsefe": "Felsefe", "Din Kültürü": "Din Kulturu",
                "İnkılap ve Atatürkçülük": "İnkılap ve Atatürkçülük"
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
                    # Matematik tipi yapı
                    unit_data = grade_data['alt'][unit_code]
                    if isinstance(unit_data, dict) and 'alt' in unit_data:
                        for subtopic_code, subtopic_info in unit_data['alt'].items():
                            if isinstance(subtopic_info, dict):
                                title = subtopic_info.get('baslik', '')
                                subtopics[subtopic_code] = title
                elif unit_code in grade_data:
                    # Coğrafya tipi yapı
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