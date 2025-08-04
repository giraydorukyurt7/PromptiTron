
"""Curriculum Details Display System
Shows detailed curriculum information for selected topics
"""

from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from core.curriculum_loader import curriculum_loader
import logging

logger = logging.getLogger(__name__)
console = Console()

class CurriculumDetailsDisplay:
    """Mufredat detay gosterim sistemi"""
    
    def __init__(self):
        pass
        
    def show_curriculum_details(self, subject_name: str, subject_code: str, grade: str, unit_code: str, subtopic_code: str):
        """Secilen mufredat detaylarini goster"""
        try:
            console.print(f"\n[bold cyan]📋 MUFREDAT DETAYI[/bold cyan]")
            console.print(Panel(f"{subject_name} > {grade}. Sinif > {unit_code} > {subtopic_code}", title="Secim"))
            
            # Curriculum'dan detay bilgileri al
            details = self._get_curriculum_details(subject_name, subject_code, grade, unit_code, subtopic_code)
            
            if not details:
                console.print("[red]Bu secim icin detay bilgi bulunamadi[/red]")
                return
                
            # Detaylari goster
            self._display_details(details)
            
        except Exception as e:
            logger.error(f"Error showing curriculum details: {e}")
            console.print(f"[red]Detay gosteriminde hata: {e}[/red]")
            
    def _get_curriculum_details(self, subject_name: str, subject_code: str, grade: str, unit_code: str, subtopic_code: str) -> Dict[str, Any]:
        """Curriculum'dan detay bilgileri al"""
        try:
            subject_data = curriculum_loader.curriculum_data.get(subject_name, {})
            
            if 'yks' not in subject_data:
                return {}
                
            yks_data = subject_data['yks']
            
            # Subject key'i bul
            subject_key = None
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
            details = {
                "subject": subject_name,
                "grade": grade,
                "unit_code": unit_code,
                "subtopic_code": subtopic_code,
                "content": {},
                "keywords": [],
                "concepts": []
            }
            
            # Icerigi al
            if isinstance(grade_data, dict):
                if 'alt' in grade_data and unit_code in grade_data['alt']:
                    # Matematik tipi yapi
                    unit_data = grade_data['alt'][unit_code]
                    
                    if subtopic_code == "ALL":
                        # Tum alt konular
                        details["content"] = unit_data
                    else:
                        # Spesifik alt konu
                        if isinstance(unit_data, dict) and 'alt' in unit_data and subtopic_code in unit_data['alt']:
                            details["content"] = unit_data['alt'][subtopic_code]
                        else:
                            details["content"] = unit_data
                            
                elif unit_code in grade_data:
                    # Cografya tipi yapi
                    unit_data = grade_data[unit_code]
                    
                    if subtopic_code == "ALL":
                        details["content"] = unit_data
                    elif isinstance(unit_data, dict) and subtopic_code in unit_data:
                        details["content"] = unit_data[subtopic_code]
                    else:
                        details["content"] = unit_data
            
            # Anahtar kelimeleri cikar
            self._extract_keywords(details)
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting curriculum details: {e}")
            return {}
            
    def _extract_keywords(self, details: Dict[str, Any]):
        """Icerikten anahtar kelimeleri cikar"""
        try:
            content = details.get("content", {})
            keywords = set()
            concepts = set()
            
            if isinstance(content, dict):
                # Baslik
                if 'baslik' in content:
                    title = content['baslik']
                    if title:
                        keywords.add(title)
                        
                # Terimler ve kavramlar
                if 'terimler_ve_kavramlar' in content:
                    terms = content['terimler_ve_kavramlar']
                    if terms:
                        concepts.update(terms.split(', '))
                        
                # Sembol ve gosterimler
                if 'sembol_ve_gosterimler' in content:
                    symbols = content['sembol_ve_gosterimler']
                    if symbols:
                        keywords.update(symbols.split(', '))
                        
                # Aciklamalar
                if 'aciklama' in content:
                    explanations = content['aciklama']
                    if isinstance(explanations, dict):
                        for exp in explanations.values():
                            if isinstance(exp, str) and len(exp) > 10:
                                # Onemli kelimeleri cikar
                                words = exp.split()[:5]  # Ilk 5 kelime
                                keywords.update(words)
                                
            details["keywords"] = list(keywords)[:10]  # Ilk 10 anahtar kelime
            details["concepts"] = list(concepts)[:10]  # Ilk 10 kavram
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            
    def _display_details(self, details: Dict[str, Any]):
        """Detaylari formatlanmis sekilde goster"""
        try:
            content = details.get("content", {})
            
            # Ana bilgiler
            info_table = Table(title="Konu Bilgileri")
            info_table.add_column("Ozellik", style="cyan")
            info_table.add_column("Deger", style="white")
            
            info_table.add_row("Ders", details.get("subject", ""))
            info_table.add_row("Sinif", f"{details.get('grade', '')}. Sinif")
            info_table.add_row("Unite", details.get("unit_code", ""))
            info_table.add_row("Alt Konu", details.get("subtopic_code", ""))
            
            console.print(info_table)
            
            # Icerik detaylari
            if isinstance(content, dict):
                console.print(f"\n[bold green]📖 ICERIK DETAYLARI[/bold green]")
                
                # Baslik
                if 'baslik' in content and content['baslik']:
                    console.print(f"[bold]Baslik:[/bold] {content['baslik']}")
                    
                # Terimler ve kavramlar
                if 'terimler_ve_kavramlar' in content and content['terimler_ve_kavramlar']:
                    console.print(f"\n[bold yellow]🏷️  Terimler ve Kavramlar:[/bold yellow]")
                    console.print(content['terimler_ve_kavramlar'])
                    
                # Sembol ve gosterimler
                if 'sembol_ve_gosterimler' in content and content['sembol_ve_gosterimler']:
                    console.print(f"\n[bold blue]🔣 Sembol ve Gosterimler:[/bold blue]")
                    console.print(content['sembol_ve_gosterimler'])
                    
                # Aciklamalar
                if 'aciklama' in content and content['aciklama']:
                    console.print(f"\n[bold magenta]💡 Aciklamalar:[/bold magenta]")
                    explanations = content['aciklama']
                    
                    if isinstance(explanations, dict):
                        for key, explanation in explanations.items():
                            if explanation:
                                console.print(f"  • [{key}] {explanation}")
                    elif isinstance(explanations, str):
                        console.print(f"  {explanations}")
                        
            # Anahtar kelimeler
            keywords = details.get("keywords", [])
            if keywords:
                console.print(f"\n[bold cyan]🔑 Anahtar Kelimeler:[/bold cyan]")
                console.print(", ".join(keywords))
                
            # Kavramlar
            concepts = details.get("concepts", [])
            if concepts:
                console.print(f"\n[bold green]📚 Kavramlar:[/bold green]")
                console.print(", ".join(concepts))
                
        except Exception as e:
            logger.error(f"Error displaying details: {e}")
            console.print(f"[red]Gosterim hatasi: {e}[/red]")

# Global instance
curriculum_details = CurriculumDetailsDisplay()