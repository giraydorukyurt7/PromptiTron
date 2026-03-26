"""
Curriculum router for handling curriculum-related endpoints
Includes: /curriculum, /curriculum/questions, /curriculum/summarize, /curriculum/concept-map, /curriculum/explain, /curriculum/socratic
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
import logging
import uuid

# Import models
from pydantic import BaseModel
# Import from api models instead of root models
from ...models.enums import DifficultyLevel, QuestionType, ExamType

# Import core modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from core.gemini_client import gemini_client
from core.agents import agent_system
from core.rag_system import rag_system
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/curriculum",
    tags=["curriculum"],
    responses={404: {"description": "Not found"}}
)

# Curriculum-based Service Request Models
class CurriculumQuestionRequest(BaseModel):
    selected_topics: List[Dict[str, Any]]  # Selected curriculum topics with metadata
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    question_type: QuestionType = QuestionType.MULTIPLE_CHOICE
    count: int = 5
    exam_type: ExamType = ExamType.TYT

class TopicSummaryRequest(BaseModel):
    selected_topics: List[Dict[str, Any]]  # Selected curriculum topics with metadata
    summary_style: str = "detailed"  # detailed, brief, bullet_points
    include_examples: bool = True

class ConceptMapRequest(BaseModel):
    selected_topics: List[Dict[str, Any]]  # Selected curriculum topics with metadata
    map_type: str = "hierarchical"  # hierarchical, network, flowchart
    include_connections: bool = True

class TopicExplanationRequest(BaseModel):
    selected_topics: List[Dict[str, Any]]  # Selected curriculum topics with metadata
    explanation_level: str = "comprehensive"  # basic, comprehensive, advanced
    include_examples: bool = True
    include_formulas: bool = True

class SocraticRequest(BaseModel):
    message: str
    selected_topics: Optional[List[Dict[str, Any]]] = None  # Optional curriculum context
    topic: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

@router.get("/")
async def get_curriculum():
    """Get curriculum data"""
    try:
        from core.unified_curriculum import unified_curriculum
        
        # Ensure curriculum is loaded
        if not unified_curriculum.loader.curriculum_data:
            logger.info("Curriculum not loaded, loading now...")
            success = unified_curriculum.loader.load_all_curriculum()
            if not success:
                logger.error("Failed to load curriculum data")
                return {"success": False, "error": "Failed to load curriculum"}
            logger.info(f"Curriculum loaded successfully, {len(unified_curriculum.loader.curriculum_data)} subjects")
        
        # Get curriculum summary
        summary = unified_curriculum.loader.get_curriculum_summary()
        
        # Log summary data
        logger.info(f"Curriculum summary: {summary}")
        
        # Prepare data for API
        curriculum_data = {}
        for subject in unified_curriculum.loader.curriculum_data.keys():
            topics = unified_curriculum.loader.get_subject_topics(subject)
            
            # Skip empty subjects
            if not topics:
                logger.warning(f"No topics found for subject: {subject}")
                continue
            
            # Group topics by grade
            grades = {}
            for topic in topics:
                grade = topic.get('grade', 'Genel')
                if grade not in grades:
                    grades[grade] = []
                
                grades[grade].append({
                    "code": topic.get('code', ''),
                    "title": topic.get('title', ''),
                    "content": topic.get('content', '')[:100] + "..." if len(topic.get('content', '')) > 100 else topic.get('content', ''),
                    "terms": topic.get('terms', ''),
                    "path": topic.get('path', '')
                })
            
            curriculum_data[subject] = {
                "total_topics": len(topics),
                "grades": grades,
                "summary": f"{len(topics)} topics across {len(grades)} grade levels"
            }
        
        # Create a more detailed response
        response_data = {
            "success": True,
            "summary": summary,
            "curriculum": curriculum_data,
            "data": {
                "summary": summary,
                "subjects": curriculum_data
            }
        }
        
        logger.info(f"Curriculum endpoint returning {len(curriculum_data)} subjects with data")
        return response_data
        
    except Exception as e:
        logger.error(f"Curriculum error: {str(e)}")
        return {"success": False, "error": str(e)}

# Curriculum-based Question Generation
@router.post("/questions")
async def generate_curriculum_questions(request: CurriculumQuestionRequest):
    """Generate questions based on selected curriculum topics"""
    try:
        # Extract subject and topic information from selected topics
        subjects = []
        topics = []
        detailed_context = []
        
        for topic_data in request.selected_topics:
            if topic_data.get("ders"):
                subjects.append(topic_data["ders"])
            if topic_data.get("title"):
                topics.append(topic_data["title"])
            
            # Build detailed context from curriculum data
            context_parts = []
            if topic_data.get("title"):
                context_parts.append(f"Başlık: {topic_data['title']}")
            if topic_data.get("sinif"):
                context_parts.append(f"Sınıf: {topic_data['sinif']}")
            if topic_data.get("konu"):
                context_parts.append(f"Konu: {topic_data['konu']}")
            if topic_data.get("aciklama"):
                context_parts.append(f"Açıklama: {topic_data['aciklama']}")
            
            detailed_context.append(" | ".join(context_parts))
        
        # Create comprehensive prompt with curriculum context
        curriculum_context = "\n".join(detailed_context)
        main_subject = subjects[0] if subjects else "Genel"
        main_topic = " ve ".join(topics[:3]) if topics else "Seçilen Konular"
        
        question_prompt = f"""
        Seçilen müfredat konularına dayalı {request.count} adet {request.difficulty.value} seviyesinde 
        {request.question_type.value} tipi soru oluştur:

        Müfredat Bağlamı:
        {curriculum_context}

        Ana Ders: {main_subject}
        Ana Konular: {main_topic}
        
        Sorular YKS {request.exam_type.value} standardında olmalı ve seçilen müfredat kazanımlarını doğrudan kapsayacak şekilde hazırlanmalı.
        
        Her soru için JSON formatında şunları içer:
        1. "soru_metni": Tam soru metni
        2. "siklar": A-E arası seçenekler (çoktan seçmeli ise)
        3. "dogru_cevap": Doğru seçeneğin harfi
        4. "aciklama": Detaylı çözüm açıklaması
        5. "kazanim": Hangi müfredat kazanımını test ettiği
        
        JSON array formatında döndür.
        """
        
        # Use agent system for sophisticated question generation
        agent_response = await agent_system.process_message(
            message=question_prompt,
            context={
                "task_type": "curriculum_question_generation",
                "selected_topics": request.selected_topics,
                "difficulty": request.difficulty.value,
                "question_type": request.question_type.value,
                "count": request.count,
                "exam_type": request.exam_type.value,
                "curriculum_context": curriculum_context
            }
        )
        
        if agent_response.get("success"):
            return {
                "success": True,
                "questions": agent_response.get("response"),
                "agent_used": agent_response.get("system_used"),
                "selected_topics_count": len(request.selected_topics),
                "main_subject": main_subject,
                "main_topic": main_topic,
                "count": request.count,
                "curriculum_based": True
            }
        else:
            # Fallback to basic generation with curriculum context
            response = await gemini_client.generate_content_with_rag(
                prompt=question_prompt,
                system_instruction=f"Sen YKS {request.exam_type.value} müfredat uzmanı soru hazırlayıcısısın. Seçilen müfredat kazanımlarına dayalı sorular hazırlarsın.",
                use_rag=True,
                rag_collections=["curriculum"],
                validation_level="high",
                validation_type="educational"
            )
            
            return {
                "success": True,
                "questions": response.get("text", "Sorular oluşturulamadı"),
                "agent_used": "Gemini RAG Fallback",
                "selected_topics_count": len(request.selected_topics),
                "main_subject": main_subject,
                "main_topic": main_topic,
                "count": request.count,
                "curriculum_based": True
            }
            
    except Exception as e:
        logger.error(f"Curriculum question generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Topic Summary Generation
@router.post("/summarize")
async def summarize_curriculum_topics(request: TopicSummaryRequest):
    """Generate comprehensive summaries of selected curriculum topics"""
    try:
        # Build context from selected topics
        topics_context = []
        subjects = set()
        grades = set()
        
        for topic_data in request.selected_topics:
            context_parts = []
            
            if topic_data.get("ders"):
                subjects.add(topic_data["ders"])
                context_parts.append(f"Ders: {topic_data['ders']}")
            if topic_data.get("sinif"):
                grades.add(topic_data["sinif"])
                context_parts.append(f"Sınıf: {topic_data['sinif']}")
            if topic_data.get("title"):
                context_parts.append(f"Konu: {topic_data['title']}")
            if topic_data.get("aciklama"):
                context_parts.append(f"Detay: {topic_data['aciklama']}")
                
            topics_context.append(" | ".join(context_parts))
        
        curriculum_context = "\n".join(topics_context)
        main_subjects = ", ".join(subjects)
        grade_levels = ", ".join(grades)
        
        summary_prompt = f"""
        Seçilen müfredat konularının {request.summary_style} özetini hazırla:

        Müfredat Konuları:
        {curriculum_context}

        Ana Dersler: {main_subjects}
        Sınıf Seviyeleri: {grade_levels}
        
        Özet Stili: {request.summary_style}
        Örnekler Dahil: {"Evet" if request.include_examples else "Hayır"}
        
        Özet şunları içermeli:
        1. Konuların genel tanımı ve kapsamı
        2. Aralarındaki ilişkiler ve bağlantılar
        3. Önemli kavramlar ve terimler
        4. YKS'deki önemi ve soru türleri
        {"5. Pratik örnekler ve uygulamalar" if request.include_examples else ""}
        
        YKS öğrencisi için anlaşılır ve kapsamlı bir özet hazırla.
        """
        
        response = await gemini_client.generate_content_with_rag(
            prompt=summary_prompt,
            system_instruction="Sen YKS müfredat uzmanısın. Seçilen konuları kapsamlı ve anlaşılır şekilde özetlersin.",
            use_rag=True,
            rag_collections=["curriculum"],
            validation_level="medium",
            validation_type="educational"
        )
        
        return {
            "success": True,
            "summary": response.get("text", "Özet oluşturulamadı"),
            "summary_style": request.summary_style,
            "topics_count": len(request.selected_topics),
            "subjects": list(subjects),
            "grade_levels": list(grades),
            "include_examples": request.include_examples,
            "curriculum_based": True
        }
        
    except Exception as e:
        logger.error(f"Topic summary generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Concept Map Generation
@router.post("/concept-map")
async def generate_concept_map(request: ConceptMapRequest):
    """Generate concept maps for selected curriculum topics"""
    try:
        # Extract topic information
        topics_info = []
        main_concepts = []
        subjects = set()
        
        for topic_data in request.selected_topics:
            topic_info = {
                "title": topic_data.get("title", ""),
                "subject": topic_data.get("ders", ""),
                "grade": topic_data.get("sinif", ""),
                "details": topic_data.get("aciklama", "")
            }
            topics_info.append(topic_info)
            
            if topic_data.get("title"):
                main_concepts.append(topic_data["title"])
            if topic_data.get("ders"):
                subjects.add(topic_data["ders"])
        
        concept_map_prompt = f"""
        Seçilen müfredat konuları için {request.map_type} tipi kavram haritası oluştur:

        Konular:
        {chr(10).join([f"- {info['subject']} ({info['grade']}. Sınıf): {info['title']} - {info['details']}" for info in topics_info])}

        Ana Kavramlar: {", ".join(main_concepts)}
        Harita Tipi: {request.map_type}
        Bağlantılar Dahil: {"Evet" if request.include_connections else "Hayır"}
        
        Kavram haritası şu formatı kullansın:
        
        1. **Merkezi Kavramlar**: Ana konular ve temel kavramlar
        2. **Alt Kavramlar**: Detay konular ve özel terimler  
        3. **Bağlantılar**: Kavramlar arası ilişkiler ve bağlantılar
        4. **Örnekler**: Her kavram için somut örnekler
        5. **YKS İlişkisi**: Her kavramın YKS'deki yeri ve önemi
        
        {"6. **Konular Arası Bağlantılar**: Farklı konuların birbiriyle ilişkisi" if request.include_connections else ""}
        
        Görsel olarak düzenlenmiş, hiyerarşik yapıda bir kavram haritası hazırla.
        ASCII karakterlerle diyagram da ekle.
        """
        
        response = await gemini_client.generate_content_with_rag(
            prompt=concept_map_prompt,
            system_instruction="Sen eğitim uzmanısın. Kavram haritaları ve görsel öğrenme materyalleri hazırlama konusunda uzmansın.",
            use_rag=True,
            rag_collections=["curriculum"],
            validation_level="medium",
            validation_type="educational"
        )
        
        return {
            "success": True,
            "concept_map": response.get("text", "Kavram haritası oluşturulamadı"),
            "map_type": request.map_type,
            "topics_count": len(request.selected_topics),
            "main_concepts": main_concepts,
            "subjects": list(subjects),
            "include_connections": request.include_connections,
            "curriculum_based": True
        }
        
    except Exception as e:
        logger.error(f"Concept map generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Topic Explanation
@router.post("/explain")
async def explain_curriculum_topics(request: TopicExplanationRequest):
    """Generate detailed explanations of selected curriculum topics"""
    try:
        # Build comprehensive context
        topics_context = []
        subjects = set()
        grades = set()
        all_concepts = []
        
        for topic_data in request.selected_topics:
            context_info = {
                "subject": topic_data.get("ders", ""),
                "grade": topic_data.get("sinif", ""),
                "title": topic_data.get("title", ""),
                "details": topic_data.get("aciklama", ""),
                "konu": topic_data.get("konu", ""),
                "kazanim": topic_data.get("kazanim", "")
            }
            
            topics_context.append(context_info)
            
            if context_info["subject"]:
                subjects.add(context_info["subject"])
            if context_info["grade"]:
                grades.add(context_info["grade"])
            if context_info["title"]:
                all_concepts.append(context_info["title"])
        
        explanation_prompt = f"""
        Seçilen müfredat konularının {request.explanation_level} seviyesinde detaylı anlatımını hazırla:

        Seçilen Konular:
        {chr(10).join([f"• {ctx['subject']} ({ctx['grade']}. Sınıf) - {ctx['title']}: {ctx['details']}" for ctx in topics_context])}

        Anlatım Seviyesi: {request.explanation_level}
        Örnekler Dahil: {"Evet" if request.include_examples else "Hayır"}
        Formüller Dahil: {"Evet" if request.include_formulas else "Hayır"}
        
        Her konu için şu yapıyı kullan:
        
        ## [KONU BAŞLIĞI]
        
        ### 1. Tanım ve Temel Kavramlar
        - Konunun tanımı
        - Temel terimlerin açıklaması
        - Önemli kavramlar
        
        ### 2. Detaylı Açıklama
        - Konunun derinlemesine incelenmesi
        - Alt başlıklar ve detaylar
        - İlgili teoriler ve yaklaşımlar
        
        {"### 3. Formüller ve Matematiksel İfadeler" if request.include_formulas else ""}
        {"- Önemli formüller ve denklemler" if request.include_formulas else ""}
        {"- Hesaplama yöntemleri" if request.include_formulas else ""}
        
        {"### 4. Örnekler ve Uygulamalar" if request.include_examples else ""}
        {"- Günlük hayattan örnekler" if request.include_examples else ""}
        {"- Pratik uygulamalar" if request.include_examples else ""}
        {"- Örnek problemler" if request.include_examples else ""}
        
        ### 5. YKS'deki Yeri
        - Bu konudan nasıl sorular çıkar
        - Sık görülen soru tipleri
        - Çözüm stratejileri
        
        ### 6. Dikkat Edilmesi Gerekenler
        - Sık yapılan hatalar
        - Önemli noktalar
        - Çalışma önerileri
        
        ### 7. İlgili Konularla Bağlantılar
        - Önkoşul konular
        - İlgili diğer konular
        - Konuların birbiriyle ilişkisi
        
        YKS öğrencisi için anlaşılır, kapsamlı ve sistematik bir anlatım hazırla.
        """
        
        response = await gemini_client.generate_content_with_rag(
            prompt=explanation_prompt,
            system_instruction=f"Sen {list(subjects)[0] if subjects else 'Genel'} dersi YKS uzmanısın. Kapsamlı ve anlaşılır konu anlatımları hazırlarsın.",
            use_rag=True,
            rag_collections=["curriculum"],
            validation_level="high",
            validation_type="educational"
        )
        
        return {
            "success": True,
            "explanation": response.get("text", "Konu anlatımı oluşturulamadı"),
            "explanation_level": request.explanation_level,
            "topics_count": len(request.selected_topics),
            "subjects": list(subjects),
            "grade_levels": list(grades),
            "include_examples": request.include_examples,
            "include_formulas": request.include_formulas,
            "curriculum_based": True
        }
        
    except Exception as e:
        logger.error(f"Topic explanation generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced Socratic Mode with Curriculum Support
@router.post("/socratic")
async def curriculum_socratic_dialogue(request: SocraticRequest):
    """Socratic dialogue endpoint with curriculum context support"""
    try:
        # Build curriculum context if topics are selected
        curriculum_context = ""
        if request.selected_topics:
            context_parts = []
            for topic_data in request.selected_topics:
                if topic_data.get("title"):
                    part = f"- {topic_data['title']}"
                    if topic_data.get("ders"):
                        part += f" ({topic_data['ders']})"
                    if topic_data.get("sinif"):
                        part += f" - {topic_data['sinif']}. Sınıf"
                    context_parts.append(part)
            
            curriculum_context = f"""
            Seçilen Müfredat Konuları:
            {chr(10).join(context_parts)}
            
            Bu konular bağlamında Sokratik diyalog gerçekleştir.
            """
        
        # Prepare enhanced context
        context = request.context or {}
        context["curriculum_context"] = curriculum_context
        context["mode"] = "socratic"
        
        if request.topic:
            context["topic"] = request.topic
        if request.selected_topics:
            context["selected_topics"] = request.selected_topics
            
        # Create Socratic prompt
        socratic_prompt = f"""
        {curriculum_context}
        
        Öğrenci sorusu/yanıtı: {request.message}
        
        Sokratik yöntemle rehberlik et:
        1. Öğrenciyi düşündürücü sorularla yönlendir
        2. Doğrudan cevap verme, keşfetmesine yardım et
        3. Küçük ipuçları ve rehberlik sağla
        4. Öğrencinin yanıtlarını analiz et ve devam et
        5. Kritik düşünmeyi teşvik et
        
        Müfredat konularından hareketle derin öğrenmeyi destekle.
        """
        
        # Use agent system with Socratic approach
        agent_response = await agent_system.process_message(
            message=socratic_prompt,
            context=context
        )
        
        if agent_response.get("success"):
            # Extract hints and guidance from response
            response_text = agent_response.get("response", "")
            hints = []
            
            # Simple hint extraction (can be enhanced)
            if "ipucu" in response_text.lower():
                hints.append("Bu konuda daha derin düşünmeye devam et")
            if "soru" in response_text.lower() and "?" in response_text:
                hints.append("Soru sorma becerinizi geliştiriyorsunuz")
                
            return {
                "success": True,
                "response": response_text,
                "mode": "socratic",
                "hints": hints,
                "session_id": request.session_id or str(uuid.uuid4()),
                "curriculum_context_used": bool(curriculum_context),
                "agent_used": agent_response.get("system_used", "Socratic Agent")
            }
        else:
            # Fallback Socratic approach
            fallback_response = await gemini_client.generate_content(
                prompt=socratic_prompt,
                system_instruction="Sen Sokratik öğretim uzmanısın. Öğrencileri soru sorarak öğrenmeye yönlendirirsin."
            )
            
            return {
                "success": True,
                "response": fallback_response.get("text", "Sokratik diyalog devam edemiyor."),
                "mode": "socratic",
                "hints": ["Düşünmeye devam et", "Sorular sormaya çalış"],
                "session_id": request.session_id or str(uuid.uuid4()),
                "curriculum_context_used": bool(curriculum_context),
                "agent_used": "Gemini Socratic Fallback"
            }
        
    except Exception as e:
        logger.error(f"Curriculum Socratic dialogue error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))