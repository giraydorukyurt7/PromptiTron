"""
Unified Curriculum Management System
Combines curriculum loading, display, and navigation into a single optimized system
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core.curriculum_loader import curriculum_loader
from core.curriculum_details import curriculum_details
from core.hierarchical_menu import HierarchicalMenuSystem

logger = logging.getLogger(__name__)
console = Console()

class UnifiedCurriculumSystem:
    """Unified system for all curriculum operations"""
    
    def __init__(self):
        """Initialize unified curriculum system"""
        self.loader = curriculum_loader
        self.details_display = curriculum_details
        self.navigation = HierarchicalMenuSystem()
        self.cache = {}  # Performance cache
        
        logger.info("Unified curriculum system initialized")
    
    async def get_curriculum_with_navigation(
        self, 
        subject: str, 
        include_navigation: bool = True
    ) -> Dict[str, Any]:
        """
        Get curriculum data with integrated navigation structure
        
        Args:
            subject: Subject name
            include_navigation: Whether to include navigation tree
            
        Returns:
            Combined curriculum data and navigation
        """
        try:
            cache_key = f"{subject}_{include_navigation}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Get curriculum data
            curriculum_data = self.loader.get_subject_topics(subject)
            
            result = {
                "subject": subject,
                "total_topics": len(curriculum_data),
                "curriculum_data": curriculum_data,
                "success": True
            }
            
            if include_navigation:
                # Build navigation structure
                navigation_tree = self._build_navigation_tree(curriculum_data, subject)
                result["navigation"] = navigation_tree
                result["navigation_summary"] = self._get_navigation_summary(navigation_tree)
            
            # Cache result for performance
            self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting curriculum with navigation: {e}")
            return {
                "subject": subject,
                "error": str(e),
                "success": False
            }
    
    def get_subject_structure(self, subject: str) -> Dict[str, Any]:
        """Get hierarchical structure of a subject"""
        try:
            topics = self.loader.get_subject_topics(subject)
            
            # Group by grade and unit
            structure = {}
            for topic in topics:
                grade = topic.get('grade', 'Unknown')
                path_parts = topic.get('path', '').split('.')
                unit = path_parts[0] if path_parts else 'Unknown'
                
                if grade not in structure:
                    structure[grade] = {}
                if unit not in structure[grade]:
                    structure[grade][unit] = []
                
                structure[grade][unit].append({
                    'code': topic.get('code', ''),
                    'title': topic.get('title', ''),
                    'path': topic.get('path', '')
                })
            
            return {
                "subject": subject,
                "structure": structure,
                "grades": list(structure.keys()),
                "total_grades": len(structure)
            }
            
        except Exception as e:
            logger.error(f"Error getting subject structure: {e}")
            return {"error": str(e)}
    
    def show_curriculum_browser(self, subject: str = None) -> Optional[Dict[str, Any]]:
        """Interactive curriculum browser with unified interface"""
        try:
            if not subject:
                # Show subject selection
                console.print(Panel("[bold cyan]📚 MÜFREDAT TARAYICıSı[/bold cyan]", title="Unified Curriculum"))
                
                # Get available subjects
                summary = self.loader.get_curriculum_summary()
                subjects = list(summary.get("subjects", {}).keys())
                
                if not subjects:
                    console.print("[red]Hiç müfredat yüklenmemiş![/red]")
                    return None
                
                # Display subjects with stats
                table = Table(title="Mevcut Dersler")
                table.add_column("Ders", style="cyan")
                table.add_column("Konu Sayısı", style="green")
                table.add_column("Sınıflar", style="yellow")
                
                for subj in subjects:
                    subj_info = summary["subjects"][subj]
                    grades = ", ".join(subj_info.get("grades", []))
                    table.add_row(subj, str(subj_info.get("topic_count", 0)), grades)
                
                console.print(table)
                return {"available_subjects": subjects, "summary": summary}
            
            else:
                # Show specific subject
                return self._show_subject_details(subject)
                
        except Exception as e:
            logger.error(f"Error in curriculum browser: {e}")
            console.print(f"[red]Hata: {e}[/red]")
            return {"error": str(e)}
    
    def get_topic_details_unified(
        self, 
        subject: str, 
        topic_path: str = None,
        topic_code: str = None
    ) -> Dict[str, Any]:
        """Get detailed topic information with unified approach"""
        try:
            # Find topic by path or code
            topics = self.loader.get_subject_topics(subject)
            target_topic = None
            
            for topic in topics:
                if topic_path and topic.get('path') == topic_path:
                    target_topic = topic
                    break
                elif topic_code and topic.get('code') == topic_code:
                    target_topic = topic
                    break
            
            if not target_topic:
                return {"error": "Topic not found", "subject": subject}
            
            # Enhance with related topics
            related_topics = self._find_related_topics(target_topic, topics)
            
            return {
                "subject": subject,
                "topic": target_topic,
                "related_topics": related_topics[:5],  # Top 5 related
                "navigation_path": self._build_navigation_path(target_topic),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error getting topic details: {e}")
            return {"error": str(e)}
    
    def search_curriculum_unified(
        self,
        query: str,
        subject: str = None,
        include_content: bool = True
    ) -> Dict[str, Any]:
        """Unified curriculum search with enhanced results"""
        try:
            # Use loader's search with enhancements
            results = self.loader.search_topics(query, subject)
            
            # Group results by subject
            results_by_subject = {}
            for result in results:
                subj = result["subject"]
                if subj not in results_by_subject:
                    results_by_subject[subj] = []
                results_by_subject[subj].append(result)
            
            # Add search analytics
            search_analytics = {
                "total_results": len(results),
                "subjects_found": len(results_by_subject),
                "top_relevance": results[0].get("relevance_score", 0) if results else 0,
                "query_terms": query.split()
            }
            
            return {
                "query": query,
                "results": results[:20],  # Limit results
                "results_by_subject": results_by_subject,
                "analytics": search_analytics,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error in unified search: {e}")
            return {"error": str(e)}
    
    def _build_navigation_tree(self, topics: List[Dict], subject: str) -> Dict[str, Any]:
        """Build hierarchical navigation tree"""
        tree = {
            "subject": subject,
            "grades": {},
            "total_paths": len(set(topic.get('path', '') for topic in topics))
        }
        
        for topic in topics:
            grade = topic.get('grade', 'Unknown')
            path_parts = topic.get('path', '').split('.')
            
            # Initialize grade if not exists
            if grade not in tree["grades"]:
                tree["grades"][grade] = {"units": {}, "topic_count": 0}
            
            tree["grades"][grade]["topic_count"] += 1
            
            # Build unit structure
            if path_parts and len(path_parts) > 0:
                unit = path_parts[0]
                if unit not in tree["grades"][grade]["units"]:
                    tree["grades"][grade]["units"][unit] = {
                        "topics": [],
                        "subtopics": set()
                    }
                
                tree["grades"][grade]["units"][unit]["topics"].append({
                    "code": topic.get('code', ''),
                    "title": topic.get('title', ''),
                    "path": topic.get('path', '')
                })
                
                # Add subtopics
                if len(path_parts) > 1:
                    tree["grades"][grade]["units"][unit]["subtopics"].add(path_parts[1])
        
        # Convert sets to lists for JSON serialization
        for grade_data in tree["grades"].values():
            for unit_data in grade_data["units"].values():
                unit_data["subtopics"] = list(unit_data["subtopics"])
        
        return tree
    
    def _get_navigation_summary(self, navigation_tree: Dict[str, Any]) -> Dict[str, Any]:
        """Get summary statistics from navigation tree"""
        total_grades = len(navigation_tree.get("grades", {}))
        total_units = sum(
            len(grade_data.get("units", {}))
            for grade_data in navigation_tree.get("grades", {}).values()
        )
        total_topics = sum(
            grade_data.get("topic_count", 0)
            for grade_data in navigation_tree.get("grades", {}).values()
        )
        
        return {
            "total_grades": total_grades,
            "total_units": total_units,
            "total_topics": total_topics,
            "avg_topics_per_grade": round(total_topics / total_grades, 1) if total_grades > 0 else 0
        }
    
    def _show_subject_details(self, subject: str) -> Dict[str, Any]:
        """Show detailed subject information"""
        try:
            curriculum_data = self.get_curriculum_with_navigation(subject)
            
            if not curriculum_data.get("success"):
                return curriculum_data
            
            # Display subject overview
            console.print(f"\n[bold cyan]📖 {subject} MÜFREDATı[/bold cyan]")
            
            nav_summary = curriculum_data.get("navigation_summary", {})
            
            # Subject stats table
            stats_table = Table(title="Müfredat İstatistikleri")
            stats_table.add_column("Özellik", style="cyan")
            stats_table.add_column("Değer", style="green")
            
            stats_table.add_row("Toplam Konu", str(curriculum_data.get("total_topics", 0)))
            stats_table.add_row("Sınıf Sayısı", str(nav_summary.get("total_grades", 0)))
            stats_table.add_row("Ünite Sayısı", str(nav_summary.get("total_units", 0)))
            stats_table.add_row("Ortalama Konu/Sınıf", str(nav_summary.get("avg_topics_per_grade", 0)))
            
            console.print(stats_table)
            
            return curriculum_data
            
        except Exception as e:
            logger.error(f"Error showing subject details: {e}")
            return {"error": str(e)}
    
    def _find_related_topics(self, target_topic: Dict, all_topics: List[Dict]) -> List[Dict]:
        """Find topics related to the target topic"""
        related = []
        target_grade = target_topic.get('grade', '')
        target_path_parts = target_topic.get('path', '').split('.')
        target_unit = target_path_parts[0] if target_path_parts else ''
        
        for topic in all_topics:
            if topic == target_topic:
                continue
            
            score = 0
            
            # Same grade bonus
            if topic.get('grade') == target_grade:
                score += 3
            
            # Same unit bonus
            topic_path_parts = topic.get('path', '').split('.')
            topic_unit = topic_path_parts[0] if topic_path_parts else ''
            if topic_unit == target_unit:
                score += 5
            
            # Similar path bonus
            common_path_parts = 0
            for i in range(min(len(target_path_parts), len(topic_path_parts))):
                if target_path_parts[i] == topic_path_parts[i]:
                    common_path_parts += 1
                else:
                    break
            score += common_path_parts * 2
            
            if score > 0:
                topic_copy = topic.copy()
                topic_copy['relatedness_score'] = score
                related.append(topic_copy)
        
        # Sort by relatedness score
        related.sort(key=lambda x: x['relatedness_score'], reverse=True)
        return related
    
    def _build_navigation_path(self, topic: Dict) -> List[str]:
        """Build breadcrumb navigation path for a topic"""
        path_parts = topic.get('path', '').split('.')
        navigation_path = [topic.get('subject', '')]
        
        if topic.get('grade'):
            navigation_path.append(topic['grade'])
        
        navigation_path.extend(path_parts)
        navigation_path.append(topic.get('title', ''))
        
        return navigation_path
    
    def clear_cache(self):
        """Clear performance cache"""
        self.cache.clear()
        logger.info("Unified curriculum cache cleared")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get unified system statistics"""
        loader_summary = self.loader.get_curriculum_summary()
        
        return {
            "unified_curriculum_stats": {
                "cache_size": len(self.cache),
                "subjects_loaded": loader_summary.get("total_subjects", 0),
                "total_topics": loader_summary.get("total_topics", 0),
                "subjects": list(loader_summary.get("subjects", {}).keys())
            },
            "loader_stats": loader_summary,
            "system_status": "active"
        }

# Global unified curriculum system
unified_curriculum = UnifiedCurriculumSystem()