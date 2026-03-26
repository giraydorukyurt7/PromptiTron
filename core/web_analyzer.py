"""
Web Site Analysis System using Gemini 2.5
Analyzes web pages for educational content and YKS curriculum compliance
"""

import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import requests
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse
import base64
from io import BytesIO

import PIL.Image
from bs4 import BeautifulSoup

from core.gemini_client import gemini_client
from core.rag_system import rag_system

logger = logging.getLogger(__name__)

class WebAnalyzer:
    """Web site content analyzer for educational materials"""
    
    def __init__(self):
        self.supported_domains = []  # Can be configured to whitelist domains
        self.blocked_domains = ['adult', 'gambling', 'spam']  # Safety filter
        
        # YKS subject keywords for curriculum compliance
        self.yks_subjects = {
            'matematik': ['matematik', 'geometri', 'integral', 'türev', 'limit', 'fonksiyon', 'denklem', 'hesap'],
            'fizik': ['fizik', 'kuvvet', 'hareket', 'enerji', 'elektrik', 'manyetik', 'dalga', 'ışık', 'atom'],
            'kimya': ['kimya', 'element', 'bileşik', 'reaksiyon', 'asit', 'baz', 'mol', 'orbital', 'periyodik'],
            'biyoloji': ['biyoloji', 'hücre', 'dna', 'gen', 'protein', 'enzim', 'fotosentez', 'solunum', 'ekosistem'],
            'türkçe': ['türkçe', 'edebiyat', 'şiir', 'roman', 'dil bilgisi', 'cümle', 'anlam', 'yazım'],
            'tarih': ['tarih', 'osmanlı', 'selçuklu', 'cumhuriyet', 'savaş', 'devlet', 'medeniyet'],
            'coğrafya': ['coğrafya', 'iklim', 'harita', 'kıta', 'nüfus', 'ekonomi', 'doğal kaynak'],
            'felsefe': ['felsefe', 'mantık', 'ahlak', 'varlık', 'bilgi', 'düşünce'],
            'din': ['din', 'islam', 'kuran', 'peygamber', 'ibadet', 'ahlak']
        }
        
        self.curriculum_check_prompt = """Bu web sayfası içeriğini YKS müfredatı açısından değerlendir:

İçerik: {content}

Değerlendirme kriterleri:
1. İçerik YKS derslerinden herhangi biriyle (Matematik, Fizik, Kimya, Biyoloji, Türkçe, Tarih, Coğrafya, Felsefe, Din) ilgili mi?
2. Eğitim amaçlı kullanılabilir mi?
3. Lise seviyesinde öğrenciler için uygun mu?
4. Güvenilir ve doğru bilgi içeriyor mu?

JSON formatında yanıt ver:
{{
    "is_educational": true/false,
    "yks_relevant": true/false,
    "subjects": ["ilgili dersler"],
    "education_level": "lise/üniversite/genel",
    "confidence_score": 0.0-1.0,
    "reason": "değerlendirme açıklaması"
}}"""

        self.analysis_prompts = {
            'content_extraction': """Bu web sayfasından eğitim içeriğini çıkar:

HTML İçerik: {html_content}

Çıkarılacak bilgiler:
1. Ana metin içeriği
2. Başlıklar ve alt başlıklar
3. Listeler ve numaralandırmalar
4. Tablolar (varsa)
5. Resim açıklamaları
6. Video/medya açıklamaları

Sonucu düzenli metin formatında ver.""",

            'educational_analysis': """Bu web içeriğini eğitim perspektifinden analiz et:

İçerik: {content}

Analiz edilecek noktalar:
1. Ana konu ve içerik özeti
2. Hangi YKS dersine ait
3. Hangi üniteler ve konular kapsanıyor
4. Zorluk seviyesi
5. Öğrenme hedefleri
6. Önemli kavramlar ve terimler
7. Pratik örnekler
8. Öğrenciler için faydalı noktalar

Detaylı eğitim analizi sun.""",

            'question_generation': """Bu içerikten YKS tarzı sorular üret:

İçerik: {content}
Ders: {subject}

5 adet çoktan seçmeli soru oluştur:
- YKS formatına uygun
- İçerikle doğrudan ilgili
- Uygun zorluk seviyesinde
- Net ve anlaşılır

Her soru için:
1. Soru metni
2. 5 seçenek (A-E)
3. Doğru cevap
4. Açıklama"""
        }

    async def analyze_website(
        self,
        url: str,
        analysis_type: str = "full",
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze website content for educational purposes"""
        try:
            # Validate URL
            if not self._is_valid_url(url):
                return {"error": "Geçersiz URL formatı"}
            
            # Check domain safety
            if not self._is_safe_domain(url):
                return {"error": "Bu domain güvenli değil veya engellenmiş"}
            
            # Fetch web content
            web_content = await self._fetch_web_content(url)
            if web_content.get("error"):
                return web_content
            
            # Extract and clean content
            extracted_content = await self._extract_content(web_content)
            if extracted_content.get("error"):
                return extracted_content
            
            # Check YKS curriculum relevance
            curriculum_check = await self._check_curriculum_relevance(extracted_content["content"])
            
            if not curriculum_check.get("yks_relevant", False):
                return {
                    "error": "İçerik YKS müfredatı ile ilgili değil",
                    "curriculum_check": curriculum_check,
                    "suggestion": "Lütfen YKS derslerine uygun bir web sitesi seçin"
                }
            
            # Perform educational analysis
            educational_analysis = await self._analyze_educational_content(
                extracted_content, curriculum_check, analysis_type, custom_prompt
            )
            
            # Add to RAG system if successful
            if educational_analysis.get("success"):
                await self._add_web_content_to_rag(url, extracted_content, educational_analysis)
            
            return {
                "success": True,
                "url": url,
                "content_info": {
                    "title": web_content.get("title", ""),
                    "word_count": len(extracted_content["content"].split()),
                    "images_count": len(extracted_content.get("images", [])),
                    "links_count": len(extracted_content.get("links", []))
                },
                "curriculum_check": curriculum_check,
                "educational_analysis": educational_analysis.get("analysis"),
                "structured_data": educational_analysis.get("structured_data"),
                "generated_questions": educational_analysis.get("questions"),
                "study_materials": educational_analysis.get("study_materials")
            }
            
        except Exception as e:
            logger.error(f"Web analysis error: {e}")
            return {"error": str(e)}

    async def _fetch_web_content(self, url: str) -> Dict[str, Any]:
        """Fetch content from web URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return {
                "html": response.text,
                "title": self._extract_title(response.text),
                "status_code": response.status_code,
                "final_url": response.url
            }
            
        except requests.RequestException as e:
            logger.error(f"Web fetch error: {e}")
            return {"error": f"Web sitesi yüklenemedi: {str(e)}"}

    async def _extract_content(self, web_content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract meaningful content from HTML"""
        try:
            html = web_content["html"]
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'advertisement']):
                element.decompose()
            
            # Extract main content using Gemini
            content_extraction_prompt = self.analysis_prompts['content_extraction'].format(
                html_content=str(soup)[:10000]  # Limit HTML size for API
            )
            
            extraction_response = await gemini_client.generate_content(
                prompt=content_extraction_prompt,
                system_instruction="Sen web içerik çıkarma uzmanısın. HTML'den sadece eğitim amaçlı değerli içerikleri çıkar."
            )
            
            main_content = extraction_response.get("text", "")
            
            # Extract images for vision analysis
            images = []
            img_tags = soup.find_all('img', src=True)
            for img in img_tags[:5]:  # Limit to 5 images
                img_info = await self._analyze_image_from_url(
                    urljoin(web_content["final_url"], img['src'])
                )
                if img_info:
                    images.append(img_info)
            
            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                if link.text.strip():
                    links.append({
                        "text": link.text.strip(),
                        "url": urljoin(web_content["final_url"], link['href'])
                    })
            
            return {
                "content": main_content,
                "raw_text": soup.get_text(),
                "images": images,
                "links": links[:10],  # Limit links
                "title": web_content.get("title", "")
            }
            
        except Exception as e:
            logger.error(f"Content extraction error: {e}")
            return {"error": f"İçerik çıkarılamadı: {str(e)}"}

    async def _analyze_image_from_url(self, image_url: str) -> Optional[Dict[str, Any]]:
        """Analyze image from URL using Gemini Vision"""
        try:
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                image = PIL.Image.open(BytesIO(response.content))
                
                # Use Gemini Vision
                vision_prompt = """Bu görseli eğitim perspektifinden analiz et:

1. Görsel içerik açıklaması
2. Eğitim amaçlı değeri
3. Hangi YKS dersiyle ilgili
4. Önemli bilgi ve kavramlar
5. Öğrenciler için faydalı mı?

Kısa ve öz analiz sun."""
                
                analysis = await gemini_client.generate_content(
                    prompt=vision_prompt,
                    images=[image]
                )
                
                return {
                    "url": image_url,
                    "analysis": analysis.get("text", ""),
                    "size": f"{image.width}x{image.height}",
                    "format": image.format
                }
                
        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            return None

    async def _check_curriculum_relevance(self, content: str) -> Dict[str, Any]:
        """Check if content is relevant to YKS curriculum"""
        try:
            curriculum_prompt = self.curriculum_check_prompt.format(content=content[:3000])
            
            response = await gemini_client.generate_content(
                prompt=curriculum_prompt,
                system_instruction="Sen YKS müfredat uzmanısın. İçerikleri eğitim değeri açısından objektif değerlendir."
            )
            
            try:
                import json
                result = json.loads(response.get("text", "{}"))
                return result
            except json.JSONDecodeError:
                # Fallback analysis
                content_lower = content.lower()
                subjects_found = []
                total_score = 0
                
                for subject, keywords in self.yks_subjects.items():
                    score = sum(1 for keyword in keywords if keyword in content_lower)
                    if score > 0:
                        subjects_found.append(subject)
                        total_score += score
                
                return {
                    "is_educational": len(subjects_found) > 0,
                    "yks_relevant": len(subjects_found) > 0,
                    "subjects": subjects_found,
                    "education_level": "lise",
                    "confidence_score": min(total_score / 10, 1.0),
                    "reason": f"{len(subjects_found)} YKS dersi ile ilgili içerik bulundu"
                }
                
        except Exception as e:
            logger.error(f"Curriculum check error: {e}")
            return {
                "is_educational": False,
                "yks_relevant": False,
                "subjects": [],
                "confidence_score": 0.0,
                "reason": f"Analiz hatası: {str(e)}"
            }

    async def _analyze_educational_content(
        self,
        content_data: Dict[str, Any],
        curriculum_check: Dict[str, Any],
        analysis_type: str,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive educational analysis"""
        try:
            content = content_data["content"]
            subjects = curriculum_check.get("subjects", [])
            primary_subject = subjects[0] if subjects else "genel"
            
            # Educational analysis
            if custom_prompt:
                analysis_prompt = custom_prompt
            else:
                analysis_prompt = self.analysis_prompts['educational_analysis'].format(content=content)
            
            analysis_response = await gemini_client.generate_content(
                prompt=analysis_prompt,
                system_instruction=f"Sen {primary_subject} uzmanısın. İçeriği YKS perspektifinden analiz et."
            )
            
            # Extract structured information
            structured_data = await self._extract_structured_info(
                analysis_response.get("text", ""), content, primary_subject
            )
            
            # Generate questions if requested
            questions = []
            if analysis_type in ["full", "questions"]:
                questions = await self._generate_questions_from_content(content, primary_subject)
            
            # Create study materials
            study_materials = await self._create_study_materials(content, structured_data)
            
            return {
                "success": True,
                "analysis": analysis_response.get("text", ""),
                "structured_data": structured_data,
                "questions": questions,
                "study_materials": study_materials
            }
            
        except Exception as e:
            logger.error(f"Educational analysis error: {e}")
            return {"error": str(e)}

    async def _generate_questions_from_content(self, content: str, subject: str) -> List[Dict[str, Any]]:
        """Generate YKS-style questions from content"""
        try:
            question_prompt = self.analysis_prompts['question_generation'].format(
                content=content[:2000], subject=subject
            )
            
            response = await gemini_client.generate_content(
                prompt=question_prompt,
                system_instruction=f"Sen {subject} soru hazırlama uzmanısın. YKS formatında kaliteli sorular üret."
            )
            
            # Parse questions (simplified)
            questions_text = response.get("text", "")
            questions = []
            
            # Basic parsing - could be enhanced
            if questions_text:
                questions.append({
                    "type": "generated_questions",
                    "subject": subject,
                    "content": questions_text,
                    "count": "5 soru",
                    "format": "YKS çoktan seçmeli"
                })
            
            return questions
            
        except Exception as e:
            logger.error(f"Question generation error: {e}")
            return []

    async def _create_study_materials(self, content: str, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create study materials from web content"""
        try:
            materials = {
                "summary": await self._create_summary(content),
                "key_points": self._extract_key_points(content),
                "concept_map": await self._create_concept_map(content, structured_data),
                "study_plan": self._create_study_recommendations(structured_data)
            }
            
            return materials
            
        except Exception as e:
            logger.error(f"Study materials creation error: {e}")
            return {}

    async def _create_summary(self, content: str) -> str:
        """Create content summary"""
        try:
            summary_prompt = f"""Bu içeriğin özet bir sunumunu hazırla:

İçerik: {content[:1500]}

Özet kriterleri:
1. Ana konuları kapsasın
2. Önemli noktaları vurgulasın
3. 200-300 kelime olsun
4. Öğrenci dostu dil kullan"""
            
            response = await gemini_client.generate_content(
                prompt=summary_prompt,
                system_instruction="Sen eğitim içeriği özetleme uzmanısın."
            )
            
            return response.get("text", "Özet oluşturulamadı")
            
        except Exception as e:
            return f"Özet hatası: {str(e)}"

    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from content"""
        # Simple extraction based on patterns
        key_points = []
        
        # Look for numbered lists, bullet points, etc.
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if (line.startswith(('1.', '2.', '3.', '•', '-', '*')) or 
                'önemli' in line.lower() or 'dikkat' in line.lower()):
                if len(line) > 10 and len(line) < 200:
                    key_points.append(line)
        
        return key_points[:10]  # Limit to 10 points

    async def _create_concept_map(self, content: str, structured_data: Dict[str, Any]) -> str:
        """Create concept map representation"""
        try:
            concept_prompt = f"""Bu içerik için kavram haritası oluştur:

İçerik: {content[:1000]}
Ana Kavramlar: {structured_data.get('key_concepts', [])}

Kavram haritası formatı:
- Ana konu merkeze
- Alt konular dallanarak
- İlişkiler açık belirtilsin
- Hiyerarşik yapı olsun"""
            
            response = await gemini_client.generate_content(
                prompt=concept_prompt,
                system_instruction="Sen kavram haritası uzmanısın."
            )
            
            return response.get("text", "Kavram haritası oluşturulamadı")
            
        except Exception as e:
            return f"Kavram haritası hatası: {str(e)}"

    def _create_study_recommendations(self, structured_data: Dict[str, Any]) -> List[str]:
        """Create study recommendations"""
        recommendations = []
        
        difficulty = structured_data.get("difficulty_level", "orta")
        subject = structured_data.get("subject", "")
        
        if difficulty == "zor":
            recommendations.extend([
                "Bu konuyu küçük parçalara bölerek çalış",
                "Ön koşul konuları gözden geçir",
                "Bol bol örnek çöz"
            ])
        else:
            recommendations.extend([
                "Ana kavramları pekiştir",
                "Pratik sorular çöz",
                "Özet çıkar ve tekrar et"
            ])
        
        return recommendations

    async def _extract_structured_info(self, analysis_text: str, content: str, subject: str) -> Dict[str, Any]:
        """Extract structured information from analysis"""
        try:
            structured_prompt = f"""
            Analiz metninden yapılandırılmış bilgi çıkar:
            
            Analiz: {analysis_text}
            Ders: {subject}
            
            JSON formatında şu bilgileri çıkar:
            {{
                "subject": "ana ders",
                "topics": ["konu1", "konu2"],
                "difficulty_level": "kolay/orta/zor",
                "key_concepts": ["kavram1", "kavram2"],
                "learning_objectives": ["hedef1", "hedef2"],
                "estimated_study_time": "dakika cinsinden süre",
                "exam_relevance": "YKS uygunluğu"
            }}
            """
            
            response = await gemini_client.generate_content(
                prompt=structured_prompt,
                system_instruction="JSON formatında yanıt ver."
            )
            
            try:
                import json
                return json.loads(response.get("text", "{}"))
            except json.JSONDecodeError:
                return {
                    "subject": subject,
                    "topics": [],
                    "difficulty_level": "orta",
                    "key_concepts": [],
                    "learning_objectives": [],
                    "estimated_study_time": 30,
                    "exam_relevance": "YKS"
                }
                
        except Exception as e:
            logger.error(f"Structured info extraction error: {e}")
            return {}

    async def _add_web_content_to_rag(
        self, 
        url: str, 
        content_data: Dict[str, Any], 
        analysis_result: Dict[str, Any]
    ):
        """Add analyzed web content to RAG system"""
        try:
            structured_data = analysis_result.get("structured_data", {})
            topics_list = structured_data.get("topics", [])
            topics_str = ", ".join(topics_list) if isinstance(topics_list, list) else str(topics_list)
            
            document = {
                "content": content_data.get("content", ""),
                "metadata": {
                    "source_url": url,
                    "source_type": "website",
                    "title": content_data.get("title", ""),
                    "subject": str(structured_data.get("subject", "")),
                    "topics": topics_str,
                    "difficulty": str(structured_data.get("difficulty_level", "")),
                    "upload_date": datetime.now().isoformat(),
                    "analysis": str(analysis_result.get("analysis", ""))[:1000]
                }
            }
            
            await rag_system.add_documents([document], collection_name="web_content")
            logger.info(f"Added web content from {url} to RAG system")
            
        except Exception as e:
            logger.error(f"Error adding web content to RAG: {e}")

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _is_safe_domain(self, url: str) -> bool:
        """Check if domain is safe for educational content"""
        try:
            domain = urlparse(url).netloc.lower()
            
            # Check blocked domains
            for blocked in self.blocked_domains:
                if blocked in domain:
                    return False
            
            # If whitelist exists, check it
            if self.supported_domains:
                return any(allowed in domain for allowed in self.supported_domains)
            
            return True
            
        except Exception:
            return False

    def _extract_title(self, html: str) -> str:
        """Extract title from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            title_tag = soup.find('title')
            return title_tag.text.strip() if title_tag else "Başlık Bulunamadı"
        except Exception:
            return "Başlık Bulunamadı"

# Global web analyzer instance
web_analyzer = WebAnalyzer()