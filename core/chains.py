"""
Unified LangChain chains for educational content generation
Provides structured prompts and output models
"""

from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from config import settings
import logging

logger = logging.getLogger(__name__)

# Output Models
class StudyPlan(BaseModel):
    week_number: int = Field(description="Hafta numarası")
    subjects: List[Dict[str, Any]] = Field(description="Çalışılacak konular")
    daily_schedule: Dict[str, List[str]] = Field(description="Günlük program")
    goals: List[str] = Field(description="Haftalık hedefler")

class QuizQuestion(BaseModel):
    question: str = Field(description="Soru metni")
    options: Dict[str, str] = Field(description="Seçenekler (A, B, C, D, E)")
    correct_answer: str = Field(description="Doğru cevap")
    explanation: str = Field(description="Açıklama")
    difficulty: str = Field(description="Zorluk seviyesi")
    topic: str = Field(description="Konu")

class ConceptMap(BaseModel):
    main_topic: str = Field(description="Ana konu")
    subtopics: List[Dict[str, Any]] = Field(description="Alt konular")
    connections: List[Dict[str, str]] = Field(description="Bağlantılar")

class ConceptExplanation(BaseModel):
    topic: str = Field(description="Konu")
    definition: str = Field(description="Tanım")
    key_points: List[str] = Field(description="Önemli noktalar")
    examples: List[str] = Field(description="Örnekler")
    common_mistakes: List[str] = Field(description="Sık yapılan hatalar")
    tips: List[str] = Field(description="İpuçları")

class UnifiedChains:
    def __init__(self):
        """Initialize unified chains with all educational capabilities"""
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=settings.TEMPERATURE,
            max_output_tokens=settings.MAX_OUTPUT_TOKENS
        )
        
        # Initialize memory with new approach
        self.chat_history = ChatMessageHistory()
        self.memory_key = "chat_history"
        
        # Initialize chains
        self._initialize_chains()
        
        logger.info("Unified chains initialized successfully")
    
    def _initialize_chains(self):
        """Initialize all chain templates"""
        # Socratic tutoring chain
        self.socratic_chain = self._create_socratic_chain()
        
        # Study plan chain
        self.study_plan_chain = self._create_study_plan_chain()
        
        # Quiz generation chain
        self.quiz_chain = self._create_quiz_chain()
        
        # Concept explanation chain
        self.explanation_chain = self._create_explanation_chain()
        
        # Summary chain
        self.summary_chain = self._create_summary_chain()
        
        # Concept map chain
        self.concept_map_chain = self._create_concept_map_chain()
        
        # Motivation chain
        self.motivation_chain = self._create_motivation_chain()
        
        # Problem solving chain
        self.problem_solving_chain = self._create_problem_solving_chain()
    
    def _create_socratic_chain(self):
        """Create Socratic tutoring chain"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Sen Sokratik yöntemle öğreten deneyimli bir YKS öğretmenisin.
            
            Görevin:
            1. Öğrenciye doğrudan cevap vermek yerine yönlendirici sorular sor
            2. Öğrencinin kendi başına düşünmesini ve keşfetmesini sağla
            3. Yanlış cevaplarda bile öğrenciyi cesaretlendir
            4. Adım adım ilerle ve her adımda öğrencinin anladığından emin ol
            5. Kavramları günlük hayattan örneklerle ilişkilendir
            
            Konuşma Tarzı:
            - Samimi ve destekleyici ol
            - Kısa ve net sorular sor
            - Öğrencinin seviyesine uygun dil kullan
            
            Bağlam: {context}
            """),
            ("human", "{input}"),
            ("assistant", "{chat_history}")
        ])
        
        return prompt | self.llm
    
    def _create_study_plan_chain(self):
        """Create study plan generation chain"""
        parser = PydanticOutputParser(pydantic_object=StudyPlan)
        
        prompt = PromptTemplate(
            template="""YKS'ye hazırlanan bir öğrenci için haftalık çalışma planı oluştur.

            Öğrenci Bilgileri:
            - Hedef: {target_exam}
            - Kalan Süre: {remaining_days} gün
            - Güçlü Konular: {strong_subjects}
            - Zayıf Konular: {weak_subjects}
            - Günlük Çalışma Süresi: {daily_hours} saat
            
            Plan Özellikleri:
            - Dengeli konu dağılımı
            - Zayıf konulara daha fazla zaman
            - Tekrar ve pekiştirme zamanları
            - Dinlenme araları
            
            {format_instructions}
            
            Çalışma planı pratik, uygulanabilir ve motivasyon sağlayıcı olmalı.""",
            input_variables=["target_exam", "remaining_days", "strong_subjects", 
                           "weak_subjects", "daily_hours"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        return prompt | self.llm | OutputFixingParser.from_llm(parser=parser, llm=self.llm)
    
    def _create_quiz_chain(self):
        """Create quiz generation chain"""
        parser = PydanticOutputParser(pydantic_object=QuizQuestion)
        
        prompt = PromptTemplate(
            template="""YKS {exam_type} sınavı için {subject} dersi {topic} konusunda 
            {difficulty} zorlukta bir soru hazırla.
            
            Soru özellikleri:
            - Gerçek YKS formatına uygun olmalı
            - Net ve anlaşılır olmalı
            - Çeldiriciler mantıklı olmalı
            - Açıklama detaylı ve öğretici olmalı
            - Görsel betimlemeler içerebilir
            
            Konu Detayı: {topic_detail}
            
            {format_instructions}""",
            input_variables=["exam_type", "subject", "topic", "difficulty", "topic_detail"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        return prompt | self.llm | OutputFixingParser.from_llm(parser=parser, llm=self.llm)
    
    def _create_explanation_chain(self):
        """Create concept explanation chain"""
        parser = PydanticOutputParser(pydantic_object=ConceptExplanation)
        
        prompt = PromptTemplate(
            template="""YKS öğrencisi için {subject} dersi {topic} konusunu açıkla.
            
            Açıklama özellikleri:
            - Basit ve anlaşılır dil kullan
            - Görsel betimlemeler ekle
            - Günlük hayattan örnekler ver
            - Formülleri adım adım açıkla
            - Önemli noktaları vurgula
            - Sık yapılan hataları belirt
            
            Açıklama Stili: {style}
            Detay Seviyesi: {detail_level}
            
            {format_instructions}""",
            input_variables=["subject", "topic", "style", "detail_level"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        return prompt | self.llm | OutputFixingParser.from_llm(parser=parser, llm=self.llm)
    
    def _create_summary_chain(self):
        """Create content summary chain"""
        prompt = PromptTemplate(
            template="""Aşağıdaki içeriği YKS öğrencisi için özetle:
            
            İçerik: {content}
            
            Özet Formatı: {format}
            Vurgulanacak Noktalar: {emphasis_points}
            
            Özet özellikleri:
            - Ana kavramları vurgula
            - Formülleri ve tanımları koru
            - Mantıksal sıra takip et
            - YKS'de çıkabilecek noktalara odaklan
            - Görsel ipuçları ekle""",
            input_variables=["content", "format", "emphasis_points"]
        )
        
        return prompt | self.llm
    
    def _create_concept_map_chain(self):
        """Create concept map generation chain"""
        parser = PydanticOutputParser(pydantic_object=ConceptMap)
        
        prompt = PromptTemplate(
            template="""YKS {subject} dersi {topic} konusu için kavram haritası oluştur.
            
            Harita özellikleri:
            - Hiyerarşik yapı olmalı
            - Kavramlar arası ilişkiler net olmalı
            - YKS müfredatına uygun olmalı
            - Öğrenmeyi kolaylaştırıcı olmalı
            - Alt konular detaylı olmalı
            
            {format_instructions}""",
            input_variables=["subject", "topic"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        return prompt | self.llm | OutputFixingParser.from_llm(parser=parser, llm=self.llm)
    
    def _create_motivation_chain(self):
        """Create motivation and support chain"""
        prompt = PromptTemplate(
            template="""YKS'ye hazırlanan öğrenciye motivasyon sağla.
            
            Öğrenci Durumu: {student_situation}
            Mevcut Zorluklar: {challenges}
            
            Motivasyon özellikleri:
            - Gerçekçi ve yapıcı ol
            - Başarı hikayeleri paylaş
            - Somut öneriler sun
            - Cesaretlendirici ol
            - Hedef odaklı yaklaş""",
            input_variables=["student_situation", "challenges"]
        )
        
        return prompt | self.llm
    
    def _create_problem_solving_chain(self):
        """Create problem solving chain"""
        prompt = PromptTemplate(
            template="""{subject} dersi problemi:
            {problem}
            
            Bu problemi adım adım çöz:
            1. Verilenler ve istenenler
            2. Çözüm stratejisi
            3. Adım adım çözüm
            4. Sonuç ve kontrol
            5. Alternatif çözüm yolları
            
            Çözüm Stili: {solution_style}
            Detay Seviyesi: {detail_level}
            
            Not: Her adımı açıkla ve formülleri detaylandır.""",
            input_variables=["subject", "problem", "solution_style", "detail_level"]
        )
        
        return prompt | self.llm
    
    # Chain execution methods
    async def socratic_response(self, user_input: str, context: Optional[str] = None) -> str:
        """Generate Socratic response"""
        try:
            chat_history = self.chat_history.messages if self.chat_history else ""
            
            response = await self.socratic_chain.ainvoke({
                "input": user_input,
                "context": context or "",
                "chat_history": str(chat_history)
            })
            
            # Save to memory
            # Save to chat history
            from langchain_core.messages import HumanMessage, AIMessage
            self.chat_history.add_user_message(user_input)
            self.chat_history.add_ai_message(response.content)
            
            return response.content
            
        except Exception as e:
            logger.error(f"Socratic chain error: {str(e)}")
            return "Üzgünüm, bir hata oluştu. Sorunuzu tekrar sorabilir misiniz?"
    
    async def generate_study_plan(self, student_info: Dict[str, Any]) -> StudyPlan:
        """Generate personalized study plan"""
        try:
            # Set defaults
            student_info.setdefault("strong_subjects", ["Matematik"])
            student_info.setdefault("weak_subjects", ["Fizik"])
            student_info.setdefault("daily_hours", 6)
            
            response = await self.study_plan_chain.ainvoke(student_info)
            return response
            
        except Exception as e:
            logger.error(f"Study plan chain error: {str(e)}")
            raise
    
    async def generate_quiz_question(self, quiz_params: Dict[str, Any]) -> QuizQuestion:
        """Generate quiz question"""
        try:
            # Set defaults
            quiz_params.setdefault("topic_detail", "")
            
            response = await self.quiz_chain.ainvoke(quiz_params)
            return response
            
        except Exception as e:
            logger.error(f"Quiz chain error: {str(e)}")
            raise
    
    async def explain_concept(self, explanation_params: Dict[str, Any]) -> str:
        """Explain a concept with structured output"""
        try:
            response = await self.explanation_chain.ainvoke(explanation_params)
            
            # Format structured explanation
            formatted = f"**{response.topic}**\n\n"
            formatted += f"📖 **Tanım:** {response.definition}\n\n"
            formatted += "📌 **Önemli Noktalar:**\n"
            for point in response.key_points:
                formatted += f"• {point}\n"
            formatted += "\n💡 **Örnekler:**\n"
            for example in response.examples:
                formatted += f"• {example}\n"
            formatted += "\n⚠️ **Sık Yapılan Hatalar:**\n"
            for mistake in response.common_mistakes:
                formatted += f"• {mistake}\n"
            formatted += "\n✨ **İpuçları:**\n"
            for tip in response.tips:
                formatted += f"• {tip}\n"
            
            return formatted
            
        except Exception as e:
            logger.error(f"Explanation chain error: {str(e)}")
            return await self._fallback_explain(explanation_params)
    
    async def _fallback_explain(self, params: Dict[str, Any]) -> str:
        """Fallback explanation without structured output"""
        prompt = f"{params['subject']} dersi {params['topic']} konusunu açıkla."
        response = await self.llm.ainvoke(prompt)
        return response.content
    
    async def summarize_content(self, summary_params: Dict[str, Any]) -> str:
        """Summarize content"""
        try:
            response = await self.summary_chain.ainvoke(summary_params)
            return response.content
            
        except Exception as e:
            logger.error(f"Summary chain error: {str(e)}")
            raise
    
    async def generate_concept_map(self, map_params: Dict[str, Any]) -> ConceptMap:
        """Generate concept map"""
        try:
            response = await self.concept_map_chain.ainvoke(map_params)
            return response
            
        except Exception as e:
            logger.error(f"Concept map chain error: {str(e)}")
            raise
    
    async def provide_motivation(self, motivation_params: Dict[str, Any]) -> str:
        """Provide motivation and support"""
        try:
            response = await self.motivation_chain.ainvoke(motivation_params)
            return response.content
            
        except Exception as e:
            logger.error(f"Motivation chain error: {str(e)}")
            return "Başarabilirsin! Her adım seni hedefe yaklaştırıyor. 💪"
    
    async def solve_problem(self, problem_params: Dict[str, Any]) -> str:
        """Solve educational problem step by step"""
        try:
            # Set defaults
            problem_params.setdefault("solution_style", "detailed")
            problem_params.setdefault("detail_level", "high")
            
            response = await self.problem_solving_chain.ainvoke(problem_params)
            return response.content
            
        except Exception as e:
            logger.error(f"Problem solving chain error: {str(e)}")
            raise
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.chat_history.clear()

# Global chains instance
chains = UnifiedChains()