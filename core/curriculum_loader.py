"""
Enhanced Curriculum Data Loader for YKS JSON Files
Handles hierarchical curriculum structure properly
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from config import settings

logger = logging.getLogger(__name__)

class CurriculumLoader:
    """Advanced curriculum data loader for hierarchical JSON structure"""
    
    def __init__(self):
        self.curriculum_data = {}
        self.flat_topics = []
        
    def load_all_curriculum(self, json_dir: str = None) -> bool:
        """Load all curriculum JSON files"""
        try:
            json_path = Path(json_dir or settings.JSON_DIR)
            if not json_path.exists():
                logger.error(f"JSON directory not found: {json_path}")
                return False
            
            self.curriculum_data = {}
            self.flat_topics = []
            
            # Process all JSON files
            for json_file in json_path.glob("*.json"):
                try:
                    subject_name = self._extract_subject_name(json_file.name)
                    curriculum_data = self._load_json_file(json_file)
                    
                    if curriculum_data:
                        self.curriculum_data[subject_name] = curriculum_data
                        # Extract and flatten topics
                        topics = self._extract_topics_from_hierarchy(curriculum_data, subject_name)
                        self.flat_topics.extend(topics)
                        
                        logger.info(f"Loaded {len(topics)} topics from {subject_name}")
                        
                        # Debug: Show first few topics for problem subjects
                        if subject_name.lower() in ['coğrafya', 'felsefe'] and len(topics) > 0:
                            logger.debug(f"Sample topics from {subject_name}: {[t['title'][:50] for t in topics[:3]]}")
                        
                except Exception as e:
                    logger.error(f"Error loading {json_file}: {e}")
                    continue
            
            logger.info(f"Total curriculum loaded: {len(self.curriculum_data)} subjects, {len(self.flat_topics)} topics")
            
            # Debug info for empty subjects
            for subject_name, data in self.curriculum_data.items():
                subject_topics = [t for t in self.flat_topics if t['subject'] == subject_name]
                if len(subject_topics) == 0:
                    logger.warning(f"No topics loaded for {subject_name} - checking structure...")
                    # Show structure for debugging
                    if isinstance(data, dict) and 'yks' in str(data):
                        logger.debug(f"Raw data keys for {subject_name}: {list(data.keys()) if isinstance(data, dict) else 'Not dict'}")
                else:
                    logger.info(f"Loaded {len(subject_topics)} topics for {subject_name}")
            
            return len(self.curriculum_data) > 0
            
        except Exception as e:
            logger.error(f"Error loading curriculum: {e}")
            return False
    
    def _load_json_file(self, json_file: Path) -> Optional[Dict]:
        """Load and validate JSON file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate JSON structure
            if not isinstance(data, dict):
                logger.warning(f"Invalid JSON structure in {json_file}")
                return None
                
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {json_file}: {e}")
            return None
        except UnicodeDecodeError as e:
            logger.error(f"Unicode decode error in {json_file}: {e}")
            # Try with different encoding
            try:
                with open(json_file, 'r', encoding='utf-8-sig') as f:
                    return json.load(f)
            except:
                return None
        except Exception as e:
            logger.error(f"Error reading {json_file}: {e}")
            return None
    
    def _extract_subject_name(self, filename: str) -> str:
        """Extract clean subject name from filename"""
        # Remove common prefixes and suffixes
        name = filename.replace('.json', '')
        name = name.replace('kazanimlar_', '')
        
        # Direct filename to subject name mapping for consistency
        filename_mapping = {
            'matematik': 'Matematik',
            'fizik': 'Fizik', 
            'kimya': 'Kimya',
            'biyoloji': 'Biyoloji',
            'tarih': 'Tarih',
            'cografya': 'Coğrafya',
            'felsefe': 'Felsefe',
            'din_kulturu': 'Din Kültürü',
            'turk_dili_ve_edebiyati': 'Türk Dili ve Edebiyatı',
            'inkilap_ve_ataturkculuk': 'İnkılap ve Atatürkçülük'
        }
        
        # Direct mapping from filename
        if name in filename_mapping:
            return filename_mapping[name]
        
        # Fallback - check partial matches
        for key, value in filename_mapping.items():
            if key in name.lower():
                return value
                
        return name.title()
    
    def _extract_topics_from_hierarchy(self, data: Dict, subject: str) -> List[Dict]:
        """Extract topics from hierarchical JSON structure"""
        topics = []
        
        try:
            # Handle YKS curriculum structure
            if 'yks' in data:
                yks_data = data['yks']
                
                # Find subject data (matematik, fizik, etc.)
                subject_key = self._find_subject_key(yks_data, subject)
                if subject_key and subject_key in yks_data:
                    subject_data = yks_data[subject_key]
                    
                    # Different structures for different subjects
                    if subject.lower() in ['matematik', 'fizik', 'kimya', 'biyoloji', 'din kültürü', 'tarih', 'i̇nkılap ve atatürkçülük']:
                        # Grade-based structure (9, 10, 11, 12) with hierarchical 'alt'
                        topics.extend(self._process_grade_levels(subject_data, subject))
                    elif subject.lower() in ['coğrafya', 'felsefe']:
                        # Direct grade->unit->objective structure
                        topics.extend(self._process_standard_grade_structure(subject_data, subject))
                    elif subject.lower() in ['türk dili ve edebiyatı']:
                        # Letter-based structure (A, B, C, etc.)
                        topics.extend(self._process_letter_based_structure(subject_data, subject))
                    else:
                        # Generic processing
                        topics.extend(self._process_generic_structure(subject_data, subject))
            
            # Handle direct subject data structure
            elif isinstance(data, dict):
                topics.extend(self._process_direct_structure(data, subject))
                
        except Exception as e:
            logger.error(f"Error extracting topics from {subject}: {e}")
            
        return topics
    
    def _find_subject_key(self, yks_data: Dict, subject: str) -> Optional[str]:
        """Find the correct subject key in YKS data"""
        subject_lower = subject.lower()
        
        # Enhanced subject mapping with exact JSON keys
        subject_mapping = {
            'coğrafya': ['cografya'],
            'din kültürü': ['din_kulturu'],
            'felsefe': ['felsefe'],
            'türk dili ve edebiyatı': ['turk_dili_ve_edebiyati'],
            'i̇nkılap ve atatürkçülük': ['inkilap_ve_ataturkculuk'],
            'matematik': ['matematik'],
            'fizik': ['fizik'],
            'kimya': ['kimya'],
            'biyoloji': ['biyoloji'],
            'tarih': ['tarih']
        }
        
        # Log available keys for debugging
        logger.debug(f"Available YKS keys: {list(yks_data.keys())}")
        logger.debug(f"Looking for subject: {subject}")
        
        # Direct JSON key matching
        for mapped_subject, keys in subject_mapping.items():
            if subject_lower == mapped_subject:
                for key in keys:
                    if key in yks_data:
                        logger.info(f"Found subject key '{key}' for '{subject}'")
                        return key
        
        # Direct match
        if subject_lower in yks_data:
            return subject_lower
            
        # Fuzzy matching for similar keys
        for key in yks_data.keys():
            # Remove underscores for comparison
            clean_key = key.replace('_', ' ')
            clean_subject = subject_lower.replace('_', ' ')
            
            if clean_subject in clean_key or clean_key in clean_subject:
                logger.info(f"Fuzzy matched subject key '{key}' for '{subject}'")
                return key
        
        logger.warning(f"No subject key found for '{subject}' in available keys: {list(yks_data.keys())}")
        return None
    
    def _process_grade_levels(self, subject_data: Dict, subject: str) -> List[Dict]:
        """Process grade level structure (9, 10, 11, 12 or A, B, C)"""
        topics = []
        
        for grade, grade_data in subject_data.items():
            if isinstance(grade_data, dict):
                # Determine grade label
                if grade in ['A', 'B', 'C']:
                    # Turkish Literature uses A, B, C instead of grades
                    grade_label = f"Düzey {grade}"
                else:
                    grade_label = f"Sınıf {grade}"
                
                if 'alt' in grade_data:
                    # Matematik style structure with 'alt'
                    topics.extend(self._process_curriculum_level(
                        grade_data['alt'], subject, grade_label
                    ))
                else:
                    # Direct structure like physics, chemistry
                    topics.extend(self._process_curriculum_level(
                        grade_data, subject, grade_label
                    ))
                
        return topics
    
    def _process_standard_grade_structure(self, subject_data: Dict, subject: str) -> List[Dict]:
        """Process standard grade structure for Coğrafya and Felsefe"""
        topics = []
        
        for grade, grade_data in subject_data.items():
            if isinstance(grade_data, dict):
                # For Cografya and Felsefe, units are directly under grades
                # Each unit contains learning objectives with codes like 9.1.1, 10.1.1 etc.
                for unit_name, unit_content in grade_data.items():
                    if isinstance(unit_content, dict):
                        # Process each learning objective in the unit
                        for code, objective_data in unit_content.items():
                            if isinstance(objective_data, dict) and 'baslik' in objective_data:
                                topic = {
                                    "subject": subject,
                                    "grade": f"Sınıf {grade}",
                                    "code": code,
                                    "path": f"{grade}.{unit_name}.{code}",
                                    "title": objective_data.get('baslik', ''),
                                    "unit": unit_name,
                                    "terms": "",
                                    "symbols": "",
                                    "content": ""
                                }
                                
                                # Build content from available information
                                content_parts = []
                                if topic['title']:
                                    content_parts.append(f"Başlık: {topic['title']}")
                                if topic['unit']:
                                    content_parts.append(f"Ünite: {topic['unit']}")
                                
                                # Process explanations (aciklama)
                                if 'aciklama' in objective_data:
                                    explanations = self._extract_explanations(objective_data['aciklama'])
                                    if explanations:
                                        content_parts.append(f"Açıklama: {explanations}")
                                
                                topic['content'] = "\n".join(content_parts)
                                
                                if topic['content'].strip():  # Only add if there's content
                                    topics.append(topic)
                
        return topics
    
    def _process_letter_based_structure(self, subject_data: Dict, subject: str) -> List[Dict]:
        """Process letter-based structure for Türk Dili ve Edebiyatı"""
        topics = []
        
        for letter, letter_data in subject_data.items():
            if isinstance(letter_data, dict):
                if 'alt' in letter_data:
                    # Process the 'alt' structure
                    topics.extend(self._process_curriculum_level(
                        letter_data['alt'], subject, f"Bölüm {letter}"
                    ))
                else:
                    # Direct structure
                    topics.extend(self._process_curriculum_level(
                        {letter: letter_data}, subject, f"Bölüm {letter}"
                    ))
                
        return topics
    
    def _process_generic_structure(self, subject_data: Dict, subject: str) -> List[Dict]:
        """Process generic structure for unknown formats"""
        topics = []
        
        # Try to find any hierarchical structure
        for key, value in subject_data.items():
            if isinstance(value, dict):
                topics.extend(self._process_curriculum_level(
                    {key: value}, subject, "Genel"
                ))
                
        return topics
    
    def _process_curriculum_level(self, level_data: Dict, subject: str, grade: str, parent_path: str = "") -> List[Dict]:
        """Recursively process curriculum levels"""
        topics = []
        
        for key, item_data in level_data.items():
            if isinstance(item_data, dict):
                current_path = f"{parent_path}.{key}" if parent_path else key
                
                # Extract topic information
                topic = {
                    "subject": subject,
                    "grade": grade,
                    "code": key,
                    "path": current_path,
                    "title": item_data.get('baslik', ''),
                    "terms": item_data.get('terimler_ve_kavramlar', ''),
                    "symbols": item_data.get('sembol_ve_gosterimler', ''),
                    "content": ""
                }
                
                # Build content from all available information
                content_parts = []
                if topic['title']:
                    content_parts.append(f"Başlık: {topic['title']}")
                if topic['terms']:
                    content_parts.append(f"Terimler: {topic['terms']}")
                if topic['symbols']:
                    content_parts.append(f"Semboller: {topic['symbols']}")
                
                # Process explanations (aciklama)
                if 'aciklama' in item_data:
                    explanations = self._extract_explanations(item_data['aciklama'])
                    if explanations:
                        content_parts.append(f"Açıklama: {explanations}")
                
                topic['content'] = "\n".join(content_parts)
                
                if topic['content'].strip():  # Only add if there's content
                    topics.append(topic)
                
                # Process sub-levels recursively
                if 'alt' in item_data:
                    topics.extend(self._process_curriculum_level(
                        item_data['alt'], subject, grade, current_path
                    ))
                    
        return topics
    
    def _extract_explanations(self, aciklama_data: Any) -> str:
        """Extract explanations from aciklama field"""
        explanations = []
        
        if isinstance(aciklama_data, dict):
            for key, value in aciklama_data.items():
                if isinstance(value, str):
                    explanations.append(f"({key}) {value}")
                    
        elif isinstance(aciklama_data, str):
            explanations.append(aciklama_data)
            
        elif isinstance(aciklama_data, list):
            for item in aciklama_data:
                if isinstance(item, str):
                    explanations.append(item)
                    
        return " ".join(explanations)
    
    def _process_direct_structure(self, data: Dict, subject: str) -> List[Dict]:
        """Process direct structure (non-YKS format)"""
        topics = []
        
        # If data has topics array
        if 'topics' in data and isinstance(data['topics'], list):
            for i, topic_data in enumerate(data['topics']):
                topic = {
                    "subject": subject,
                    "grade": "Genel",
                    "code": f"topic_{i+1}",
                    "path": f"topic_{i+1}",
                    "title": topic_data.get('name', topic_data.get('title', '')),
                    "content": topic_data.get('description', topic_data.get('content', '')),
                    "terms": topic_data.get('terms', ''),
                    "symbols": topic_data.get('symbols', '')
                }
                
                if topic['content'].strip():
                    topics.append(topic)
                    
                # Process subtopics if available
                if 'subtopics' in topic_data:
                    for j, subtopic in enumerate(topic_data['subtopics']):
                        subtopic_obj = {
                            "subject": subject,
                            "grade": "Genel",
                            "code": f"topic_{i+1}_sub_{j+1}",
                            "path": f"topic_{i+1}.subtopic_{j+1}",
                            "title": subtopic.get('name', subtopic.get('title', '')),
                            "content": subtopic.get('description', subtopic.get('content', '')),
                            "parent_topic": topic['title'],
                            "terms": subtopic.get('terms', ''),
                            "symbols": subtopic.get('symbols', '')
                        }
                        
                        if subtopic_obj['content'].strip():
                            topics.append(subtopic_obj)
        
        return topics
    
    def get_subject_topics(self, subject: str) -> List[Dict]:
        """Get all topics for a specific subject"""
        return [topic for topic in self.flat_topics if topic['subject'].lower() == subject.lower()]
    
    def search_topics(self, query: str, subject: str = None) -> List[Dict]:
        """Search topics by query string"""
        query_lower = query.lower()
        results = []
        
        for topic in self.flat_topics:
            # Filter by subject if specified
            if subject and topic['subject'].lower() != subject.lower():
                continue
                
            # Search in title, content, and terms
            search_text = f"{topic['title']} {topic['content']} {topic['terms']}".lower()
            
            if query_lower in search_text:
                # Calculate relevance score
                score = 0
                if query_lower in topic['title'].lower():
                    score += 10
                if query_lower in topic['terms'].lower():
                    score += 5
                if query_lower in topic['content'].lower():
                    score += 1
                    
                topic_copy = topic.copy()
                topic_copy['relevance_score'] = score
                results.append(topic_copy)
        
        # Sort by relevance
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results
    
    def get_curriculum_summary(self) -> Dict[str, Any]:
        """Get summary of loaded curriculum data"""
        summary = {
            "total_subjects": len(self.curriculum_data),
            "total_topics": len(self.flat_topics),
            "subjects": {}
        }
        
        for subject in self.curriculum_data.keys():
            subject_topics = self.get_subject_topics(subject)
            summary["subjects"][subject] = {
                "topic_count": len(subject_topics),
                "grades": list(set(topic.get('grade', 'Unknown') for topic in subject_topics))
            }
            
        return summary

# Global curriculum loader instance
curriculum_loader = CurriculumLoader()