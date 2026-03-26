"""
YouTube Video Analysis System using Gemini 2.5
Analyzes YouTube videos for educational content and YKS curriculum compliance
"""

import logging
from typing import Dict, Any, List, Optional, Union
import re
from datetime import datetime
import json
import requests
import yt_dlp

from core.gemini_client import gemini_client
from core.rag_system import rag_system

logger = logging.getLogger(__name__)

class YouTubeAnalyzer:
    """YouTube video content analyzer for educational materials"""
    
    def __init__(self):
        # YKS subject keywords for curriculum compliance
        self.yks_subjects = {
            'matematik': ['matematik', 'geometri', 'integral', 'türev', 'limit', 'fonksiyon', 'denklem', 'hesap', 'sayı'],
            'fizik': ['fizik', 'kuvvet', 'hareket', 'enerji', 'elektrik', 'manyetik', 'dalga', 'ışık', 'atom', 'basınç'],
            'kimya': ['kimya', 'element', 'bileşik', 'reaksiyon', 'asit', 'baz', 'mol', 'orbital', 'periyodik', 'çözelti'],
            'biyoloji': ['biyoloji', 'hücre', 'dna', 'gen', 'protein', 'enzim', 'fotosentez', 'solunum', 'ekosistem', 'evrim'],
            'türkçe': ['türkçe', 'edebiyat', 'şiir', 'roman', 'dil bilgisi', 'cümle', 'anlam', 'yazım', 'şair', 'yazar'],
            'tarih': ['tarih', 'osmanlı', 'selçuklu', 'cumhuriyet', 'savaş', 'devlet', 'medeniyet', 'sultan', 'padişah'],
            'coğrafya': ['coğrafya', 'iklim', 'harita', 'kıta', 'nüfus', 'ekonomi', 'doğal kaynak', 'jeoloji', 'toprak'],
            'felsefe': ['felsefe', 'mantık', 'ahlak', 'varlık', 'bilgi', 'düşünce', 'doğruluk', 'güzellik', 'adalet'],
            'din': ['din', 'islam', 'kuran', 'peygamber', 'ibadet', 'ahlak', 'iman', 'allah', 'namaz', 'oruç']
        }
        
        self.curriculum_check_prompt = """Bu YouTube video içeriğini YKS müfredatı açısından değerlendir:

Video İçeriği: {content}

Değerlendirme kriterleri:
1. İçerik YKS derslerinden herhangi biriyle (Matematik, Fizik, Kimya, Biyoloji, Türkçe, Tarih, Coğrafya, Felsefe, Din) ilgili mi?
2. Eğitim amaçlı kullanılabilir mi?
3. Lise seviyesinde öğrenciler için uygun mu?
4. Güvenilir ve doğru bilgi içeriyor mu?
5. Video kalitesi eğitim için yeterli mi?

JSON formatında yanıt ver:
{{
    "is_educational": true/false,
    "yks_relevant": true/false,
    "subjects": ["ilgili dersler"],
    "education_level": "lise/üniversite/genel",
    "confidence_score": 0.0-1.0,
    "reason": "değerlendirme açıklaması",
    "video_quality": "iyi/orta/kötü"
}}"""

        self.analysis_prompts = {
            'transcript_analysis': """Bu YouTube videosunu transkribe et ve analiz et.

Video ID: {video_id}
Video URL: {url}

ÖNEMLİ: Bu videodaki gerçek içeriği analiz et. Başka bir video ile karıştırma.

Çıkarılacak bilgiler:
1. Tam ses transkripti (zaman damgalarıyla)
2. Görsel açıklamalar (önemli sahneler)  
3. Ana konular ve başlıklar
4. Önemli kavramlar ve terimler
5. Öğretici içerik analizi
6. Video yapısı ve organizasyon

Bu spesifik video URL'deki içeriği analiz et: {url}
Transkript ve analiz gerçek video içeriğine uygun olmalı.""",

            'educational_analysis': """Bu YouTube video içeriğini eğitim perspektifinden analiz et:

Transkript ve İçerik: {content}

Analiz edilecek noktalar:
1. Ana konu ve içerik özeti
2. Hangi YKS dersine ait
3. Hangi üniteler ve konular kapsanıyor
4. Zorluk seviyesi
5. Öğrenme hedefleri
6. Önemli kavramlar ve terimler
7. Pratik örnekler ve uygulamalar
8. Video eğitim kalitesi
9. Öğrenciler için faydalı noktalar
10. Eksik olan konular

Detaylı eğitim analizi sun.""",

            'question_generation': """Bu YouTube video içeriğinden YKS tarzı sorular üret:

Video İçeriği: {content}
Ders: {subject}

5 adet çoktan seçmeli soru oluştur:
- YKS formatına uygun
- Video içeriğiyle doğrudan ilgili
- Uygun zorluk seviyesinde
- Net ve anlaşılır
- Videodaki spesifik bilgileri test eden

Her soru için:
1. Soru metni
2. 5 seçenek (A-E)
3. Doğru cevap
4. Açıklama ve hangi dakikada geçtiği""",

            'summary_generation': """Bu YouTube videosunun kapsamlı özetini çıkar:

Video İçeriği: {content}

Özet kriterleri:
1. Ana konuları kapsasın
2. Önemli noktaları vurgulasın
3. Zaman damgalarını içersin
4. 300-500 kelime olsun
5. Öğrenci dostu dil kullan
6. Videodaki görsel içerikleri de belirt"""
        }

    async def analyze_youtube_video(
        self,
        url: str,
        analysis_type: str = "full",
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze YouTube video content for educational purposes"""
        try:
            # Validate YouTube URL
            if not self._is_valid_youtube_url(url):
                return {"error": "Geçersiz YouTube URL formatı"}
            
            # Extract video ID and get video info
            video_id = self._extract_video_id(url)
            if not video_id:
                return {"error": "YouTube video ID çıkarılamadı"}
            
            # Get video transcript and analysis using Gemini
            transcript_result = await self._get_video_transcript_and_analysis(url)
            if transcript_result.get("error"):
                return transcript_result
            
            # Check YKS curriculum relevance
            curriculum_check = await self._check_curriculum_relevance(transcript_result["content"])
            
            if not curriculum_check.get("yks_relevant", False):
                return {
                    "error": "Video içeriği YKS müfredatı ile ilgili değil",
                    "curriculum_check": curriculum_check,
                    "suggestion": "Lütfen YKS derslerine uygun bir YouTube videosu seçin"
                }
            
            # Perform educational analysis
            educational_analysis = await self._analyze_educational_content(
                transcript_result, curriculum_check, analysis_type, custom_prompt
            )
            
            # Add to RAG system if successful
            if educational_analysis.get("success"):
                await self._add_video_content_to_rag(url, video_id, transcript_result, educational_analysis)
            
            return {
                "success": True,
                "url": url,
                "video_id": video_id,
                "video_info": {
                    "title": transcript_result.get("title", "YouTube Video"),
                    "duration": transcript_result.get("duration", "Bilinmiyor"),
                    "transcript_length": len(transcript_result.get("transcript", "")),
                    "visual_scenes": len(transcript_result.get("visual_descriptions", []))
                },
                "curriculum_check": curriculum_check,
                "transcript": transcript_result.get("transcript", ""),
                "visual_descriptions": transcript_result.get("visual_descriptions", []),
                "educational_analysis": educational_analysis.get("analysis"),
                "structured_data": educational_analysis.get("structured_data"),
                "generated_questions": educational_analysis.get("questions"),
                "study_materials": educational_analysis.get("study_materials"),
                "timestamps": transcript_result.get("timestamps", [])
            }
            
        except Exception as e:
            logger.error(f"YouTube analysis error: {e}")
            return {"error": str(e)}

    async def _get_real_video_info_and_transcript(self, url: str) -> Dict[str, Any]:
        """Get real video info and transcript using yt-dlp"""
        try:
            video_id = self._extract_video_id(url)
            
            # Configure yt-dlp
            ydl_opts = {
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['tr', 'en'],
                'skip_download': True,
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract video info
                info = ydl.extract_info(url, download=False)
                
                video_info = {
                    'title': info.get('title', 'Unknown Title'),
                    'channel': info.get('uploader', 'Unknown Channel'),
                    'duration': info.get('duration', 0),
                    'description': info.get('description', ''),
                    'view_count': info.get('view_count', 0),
                    'upload_date': info.get('upload_date', '')
                }
                
                # Try to get transcript from automatic captions
                automatic_captions = info.get('automatic_captions', {})
                transcript_text = ""
                transcript_entries = []
                
                # Prefer Turkish, fallback to English
                caption_lang = None
                if 'tr' in automatic_captions:
                    caption_lang = 'tr'
                elif 'en' in automatic_captions:
                    caption_lang = 'en'
                
                if caption_lang:
                    # Get VTT format (easiest to parse)
                    captions = automatic_captions[caption_lang]
                    vtt_caption = None
                    
                    for caption in captions:
                        if caption.get('ext') == 'vtt':
                            vtt_caption = caption
                            break
                    
                    if vtt_caption and vtt_caption.get('url'):
                        try:
                            # Download transcript
                            response = requests.get(vtt_caption['url'], timeout=30)
                            if response.status_code == 200:
                                transcript_text = self._parse_vtt_content(response.text)
                                transcript_entries = self._parse_vtt_to_entries(response.text)
                        except Exception as e:
                            logger.warning(f"Failed to download transcript: {e}")
                
                return {
                    'video_info': video_info,
                    'transcript_text': transcript_text,
                    'transcript_entries': transcript_entries,
                    'caption_language': caption_lang,
                    'has_transcript': len(transcript_text) > 0
                }
                
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return {
                'error': f'Video bilgisi alınamadı: {str(e)}',
                'video_info': None,
                'transcript_text': '',
                'transcript_entries': [],
                'has_transcript': False
            }
    
    def _parse_vtt_content(self, vtt_content: str) -> str:
        """Parse VTT content to extract text"""
        lines = vtt_content.split('\n')
        text_parts = []
        
        for line in lines:
            line = line.strip()
            # Skip VTT headers, timestamps, and empty lines
            if (line and 
                not line.startswith('WEBVTT') and 
                not line.startswith('Kind:') and 
                not line.startswith('Language:') and 
                not '-->' in line and
                not line.startswith('<')):
                # Clean HTML tags and duplicates
                cleaned = re.sub(r'<[^>]+>', '', line)
                if cleaned and cleaned not in text_parts[-5:]:  # Avoid recent duplicates
                    text_parts.append(cleaned)
        
        return ' '.join(text_parts)
    
    def _parse_vtt_to_entries(self, vtt_content: str) -> List[Dict[str, Any]]:
        """Parse VTT content to time-stamped entries"""
        lines = vtt_content.split('\n')
        entries = []
        current_time = None
        
        for line in lines:
            line = line.strip()
            if '-->' in line:
                # Parse timestamp
                time_parts = line.split(' --> ')
                if len(time_parts) >= 2:
                    start_time = self._parse_vtt_time(time_parts[0])
                    current_time = start_time
            elif line and current_time is not None and not line.startswith('<'):
                # Clean text
                cleaned = re.sub(r'<[^>]+>', '', line)
                if cleaned:
                    entries.append({
                        'start': current_time,
                        'text': cleaned
                    })
                    current_time = None
        
        return entries
    
    def _parse_vtt_time(self, time_str: str) -> float:
        """Parse VTT time format to seconds"""
        try:
            # Format: HH:MM:SS.mmm or MM:SS.mmm
            parts = time_str.split(':')
            if len(parts) == 3:  # HH:MM:SS.mmm
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = float(parts[2])
                return hours * 3600 + minutes * 60 + seconds
            elif len(parts) == 2:  # MM:SS.mmm
                minutes = int(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
        except:
            pass
        return 0.0

    async def _get_video_transcript_and_analysis(self, url: str) -> Dict[str, Any]:
        """Get video transcript using real YouTube data and analyze with Gemini"""
        try:
            # Get real video info and transcript
            video_data = await self._get_real_video_info_and_transcript(url)
            
            if video_data.get('error'):
                return video_data
            
            video_info = video_data.get('video_info', {})
            transcript_text = video_data.get('transcript_text', '')
            transcript_entries = video_data.get('transcript_entries', [])
            has_transcript = video_data.get('has_transcript', False)
            
            if not has_transcript:
                return {
                    "error": "Bu video için otomatik transkript bulunamadı",
                    "video_info": video_info,
                    "suggestion": "Video sahibi altyazı/transkript özelliğini etkinleştirmemiş olabilir"
                }
            
            # Now analyze the real transcript with Gemini
            analysis_prompt = f"""Bu YouTube videosunun gerçek transkriptini analiz et:

Video Bilgileri:
- Başlık: {video_info.get('title', 'Bilinmiyor')}
- Kanal: {video_info.get('channel', 'Bilinmiyor')}
- Süre: {video_info.get('duration', 0)} saniye
- Açıklama: {video_info.get('description', '')[:200]}...

Gerçek Video Transkripti:
{transcript_text}

Bu transkripti analiz ederek şunları çıkar:
1. Ana konular ve kavramlar
2. Öğretici içerik özeti
3. Zaman damgaları ile önemli anlar
4. Görsel sahneler (transkripte dayalı tahmin)
5. Eğitim değeri
6. YKS müfredatına uygunluk

Analiz sonucunu detaylı ver."""

            # Analyze with Gemini
            response = await gemini_client.generate_content(
                prompt=analysis_prompt,
                model_name="flash"
            )
            
            if not response.get("success", True):
                return {"error": f"Transkript analizi başarısız: {response.get('error', 'Bilinmeyen hata')}"}
            
            analysis_content = response.get("text", "")
            
            # Format timestamps from transcript entries
            timestamps = []
            for i, entry in enumerate(transcript_entries[:30]):  # First 30 entries
                minutes = int(entry['start']) // 60
                seconds = int(entry['start']) % 60
                timestamps.append(f"{minutes:02d}:{seconds:02d}")
            
            # Combine all information
            full_content = f"""GERÇEK VIDEO BİLGİLERİ:
Başlık: {video_info.get('title', 'Bilinmiyor')}
Kanal: {video_info.get('channel', 'Bilinmiyor')}
Süre: {video_info.get('duration', 0)} saniye ({video_info.get('duration', 0)//60} dakika)
Görüntülenme: {video_info.get('view_count', 0):,}

TRANSKRIPT ({len(transcript_text)} karakter):
{transcript_text}

ANALİZ SONUÇLARI:
{analysis_content}

[GERÇEK VERİ: Bu bilgiler YouTube'dan otomatik olarak çekilmiştir]
[URL: {url}]"""
            
            return {
                "content": full_content,
                "transcript": transcript_text,
                "video_info": video_info,
                "transcript_entries": transcript_entries,
                "title": video_info.get('title', 'YouTube Video'),
                "duration": f"{video_info.get('duration', 0)//60}:{video_info.get('duration', 0)%60:02d}",
                "timestamps": timestamps,
                "real_data": True
            }
            
        except Exception as e:
            logger.error(f"Video transcript error: {e}")
            return {"error": f"Video transkript hatası: {str(e)}"}

    def _parse_transcript_response(self, content: str) -> Dict[str, Any]:
        """Parse Gemini's transcript response"""
        try:
            parsed = {
                "transcript": "",
                "visual_descriptions": [],
                "title": "YouTube Video",
                "duration": "",
                "timestamps": []
            }
            
            lines = content.split('\n')
            current_section = ""
            
            for line in lines:
                line = line.strip()
                
                # Extract title
                if "başlık" in line.lower() or "title" in line.lower():
                    if ":" in line:
                        parsed["title"] = line.split(":", 1)[1].strip()
                
                # Extract timestamps
                timestamp_pattern = r'\b\d{1,2}:\d{2}\b'
                timestamps = re.findall(timestamp_pattern, line)
                if timestamps:
                    parsed["timestamps"].extend(timestamps)
                
                # Collect transcript content
                if line and not line.startswith('#') and not line.startswith('*'):
                    parsed["transcript"] += line + " "
            
            # Clean up transcript
            parsed["transcript"] = parsed["transcript"].strip()
            
            # Extract visual descriptions (lines mentioning visual content)
            visual_keywords = ['görsel', 'sahne', 'ekran', 'gösteriliyor', 'görünüyor']
            for line in lines:
                if any(keyword in line.lower() for keyword in visual_keywords):
                    parsed["visual_descriptions"].append(line.strip())
            
            return parsed
            
        except Exception as e:
            logger.error(f"Transcript parsing error: {e}")
            return {
                "transcript": content,
                "visual_descriptions": [],
                "title": "YouTube Video",
                "duration": "",
                "timestamps": []
            }

    async def _check_curriculum_relevance(self, content: str) -> Dict[str, Any]:
        """Check if video content is relevant to YKS curriculum"""
        try:
            curriculum_prompt = self.curriculum_check_prompt.format(content=content[:3000])
            
            response = await gemini_client.generate_content(
                prompt=curriculum_prompt,
                system_instruction="Sen YKS müfredat uzmanısın. Video içeriklerini eğitim değeri açısından objektif değerlendir."
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
                    "reason": f"{len(subjects_found)} YKS dersi ile ilgili içerik bulundu",
                    "video_quality": "orta"
                }
                
        except Exception as e:
            logger.error(f"Curriculum check error: {e}")
            return {
                "is_educational": False,
                "yks_relevant": False,
                "subjects": [],
                "confidence_score": 0.0,
                "reason": f"Analiz hatası: {str(e)}",
                "video_quality": "bilinmiyor"
            }

    async def _analyze_educational_content(
        self,
        transcript_data: Dict[str, Any],
        curriculum_check: Dict[str, Any],
        analysis_type: str,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive educational analysis"""
        try:
            content = transcript_data["content"]
            subjects = curriculum_check.get("subjects", [])
            primary_subject = subjects[0] if subjects else "genel"
            
            # Educational analysis
            if custom_prompt:
                analysis_prompt = custom_prompt
            else:
                analysis_prompt = self.analysis_prompts['educational_analysis'].format(content=content)
            
            analysis_response = await gemini_client.generate_content(
                prompt=analysis_prompt,
                system_instruction=f"Sen {primary_subject} uzmanısın. Video içeriğini YKS perspektifinden analiz et."
            )
            
            # Extract structured information
            structured_data = await self._extract_structured_info(
                analysis_response.get("text", ""), content, primary_subject
            )
            
            # Generate questions if requested
            questions = []
            if analysis_type in ["full", "questions"]:
                questions = await self._generate_questions_from_video(content, primary_subject)
            
            # Create study materials
            study_materials = await self._create_study_materials(content, structured_data, transcript_data)
            
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

    async def _generate_questions_from_video(self, content: str, subject: str) -> List[Dict[str, Any]]:
        """Generate YKS-style questions from video content"""
        try:
            question_prompt = self.analysis_prompts['question_generation'].format(
                content=content[:2000], subject=subject
            )
            
            response = await gemini_client.generate_content(
                prompt=question_prompt,
                system_instruction=f"Sen {subject} soru hazırlama uzmanısın. YouTube video içeriğinden YKS formatında kaliteli sorular üret."
            )
            
            # Parse questions (simplified)
            questions_text = response.get("text", "")
            questions = []
            
            if questions_text:
                questions.append({
                    "type": "generated_questions",
                    "subject": subject,
                    "content": questions_text,
                    "count": "5 soru",
                    "format": "YKS çoktan seçmeli",
                    "source": "YouTube video"
                })
            
            return questions
            
        except Exception as e:
            logger.error(f"Question generation error: {e}")
            return []

    async def _create_study_materials(self, content: str, structured_data: Dict[str, Any], transcript_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create study materials from video content"""
        try:
            materials = {
                "summary": await self._create_video_summary(content, transcript_data),
                "key_points": self._extract_key_points_from_video(content),
                "concept_map": await self._create_concept_map(content, structured_data),
                "study_plan": self._create_study_recommendations(structured_data),
                "timestamps": transcript_data.get("timestamps", []),
                "visual_notes": transcript_data.get("visual_descriptions", [])
            }
            
            return materials
            
        except Exception as e:
            logger.error(f"Study materials creation error: {e}")
            return {}

    async def _create_video_summary(self, content: str, transcript_data: Dict[str, Any]) -> str:
        """Create video summary"""
        try:
            summary_prompt = self.analysis_prompts['summary_generation'].format(content=content[:2000])
            
            response = await gemini_client.generate_content(
                prompt=summary_prompt,
                system_instruction="Sen eğitim video özetleme uzmanısın."
            )
            
            return response.get("text", "Özet oluşturulamadı")
            
        except Exception as e:
            return f"Özet hatası: {str(e)}"

    def _extract_key_points_from_video(self, content: str) -> List[str]:
        """Extract key points from video content"""
        key_points = []
        
        # Look for educational patterns in transcript
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if (len(line) > 20 and len(line) < 200 and 
                any(indicator in line.lower() for indicator in ['önemli', 'dikkat', 'unutmayın', 'temel', 'ana', 'sonuç'])):
                key_points.append(line)
        
        # Look for numbered points or definitions
        for line in lines:
            line = line.strip()
            if (line.startswith(('1.', '2.', '3.', '-', '•')) or 
                'tanım' in line.lower() or 'formül' in line.lower()):
                if len(line) > 10 and len(line) < 200:
                    key_points.append(line)
        
        return key_points[:10]  # Limit to 10 points

    async def _create_concept_map(self, content: str, structured_data: Dict[str, Any]) -> str:
        """Create concept map representation"""
        try:
            concept_prompt = f"""Bu video içeriği için kavram haritası oluştur:

İçerik: {content[:1000]}
Ana Kavramlar: {structured_data.get('key_concepts', [])}

Kavram haritası formatı:
- Ana konu merkeze
- Alt konular dallanarak
- İlişkiler açık belirtilsin
- Hiyerarşik yapı olsun
- Video'daki zaman referansları eklensin"""
            
            response = await gemini_client.generate_content(
                prompt=concept_prompt,
                system_instruction="Sen video içeriği kavram haritası uzmanısın."
            )
            
            return response.get("text", "Kavram haritası oluşturulamadı")
            
        except Exception as e:
            return f"Kavram haritası hatası: {str(e)}"

    def _create_study_recommendations(self, structured_data: Dict[str, Any]) -> List[str]:
        """Create study recommendations"""
        recommendations = []
        
        difficulty = structured_data.get("difficulty_level", "orta")
        subject = structured_data.get("subject", "")
        
        # Video-specific recommendations
        recommendations.extend([
            "Videoyu not alarak izleyin",
            "Önemli kısımları tekrar izleyin",
            "Videodaki örnekleri kendiniz çözmeye çalışın"
        ])
        
        if difficulty == "zor":
            recommendations.extend([
                "Videoyu hızını yavaşlatarak izleyin",
                "Anlamadığınız kısımları tekrar edin",
                "Ek kaynaklardan konuyu pekiştirin"
            ])
        else:
            recommendations.extend([
                "Video hızını artırarak daha verimli izleyin",
                "İleri seviye sorulara odaklanın"
            ])
        
        return recommendations

    async def _extract_structured_info(self, analysis_text: str, content: str, subject: str) -> Dict[str, Any]:
        """Extract structured information from analysis"""
        try:
            structured_prompt = f"""
            Video analiz metninden yapılandırılmış bilgi çıkar:
            
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
                "exam_relevance": "YKS uygunluğu",
                "video_quality": "eğitim kalitesi değerlendirmesi"
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
                    "estimated_study_time": 45,
                    "exam_relevance": "YKS",
                    "video_quality": "orta"
                }
                
        except Exception as e:
            logger.error(f"Structured info extraction error: {e}")
            return {}

    async def _add_video_content_to_rag(
        self, 
        url: str,
        video_id: str,
        transcript_data: Dict[str, Any], 
        analysis_result: Dict[str, Any]
    ):
        """Add analyzed video content to RAG system"""
        try:
            structured_data = analysis_result.get("structured_data", {})
            topics_list = structured_data.get("topics", [])
            topics_str = ", ".join(topics_list) if isinstance(topics_list, list) else str(topics_list)
            
            document = {
                "content": transcript_data.get("transcript", ""),
                "metadata": {
                    "source_url": url,
                    "source_type": "youtube_video",
                    "video_id": video_id,
                    "title": transcript_data.get("title", ""),
                    "subject": str(structured_data.get("subject", "")),
                    "topics": topics_str,
                    "difficulty": str(structured_data.get("difficulty_level", "")),
                    "upload_date": datetime.now().isoformat(),
                    "analysis": str(analysis_result.get("analysis", ""))[:1000],
                    "video_duration": transcript_data.get("duration", ""),
                    "video_quality": structured_data.get("video_quality", "orta")
                }
            }
            
            await rag_system.add_documents([document], collection_name="youtube_content")
            logger.info(f"Added YouTube video {video_id} to RAG system")
            
        except Exception as e:
            logger.error(f"Error adding video content to RAG: {e}")

    def _is_valid_youtube_url(self, url: str) -> bool:
        """Validate YouTube URL format"""
        youtube_patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'https?://(?:www\.)?youtu\.be/[\w-]+',
            r'https?://(?:www\.)?youtube\.com/embed/[\w-]+',
            r'https?://(?:www\.)?youtube\.com/v/[\w-]+'
        ]
        
        return any(re.match(pattern, url) for pattern in youtube_patterns)

    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        try:
            patterns = [
                r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/)([^&\n?#]+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception:
            return None

# Global YouTube analyzer instance
youtube_analyzer = YouTubeAnalyzer()