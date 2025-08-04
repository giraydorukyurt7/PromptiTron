
"""
Unified Chains System
"""
from typing import Dict, Any, List, Optional
import json
from config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferWindowMemory
from models.structured_models import QuizQuestion, StudyPlan, ConceptMap

class UnifiedChains:
    def __init__(self):
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=settings.TEMPERATURE,
            max_output_tokens=settings.MAX_OUTPUT_TOKENS
        )
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize chains
        self._initialize_chains()
        
        logger.info("Unified chains initialized successfully")
    
    def _initialize_chains(self):
        pass
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
        pass
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Sen Sokratik yontemle ogreten deneyimli bir YKS ogretmenisin.
            
            Gorevin:
            1. Ogrenciye dogrudan cevap vermek yerine yonlendirici sorular sor
            2. Ogrencinin kendi basina dusunmesini ve kesfetmesini sagla
            3. Yanlis cevaplarda bile ogrenciyi cesaretlendir
            4. Adim adim ilerle ve her adimda ogrencinin anladigindan emin ol
            5. Kavramlari gunluk hayattan orneklerle iliskilendir
            
            Konusma Tarzi:
            - Samimi ve destekleyici ol
            - Kisa ve net sorular sor
            - Ogrencinin seviyesine uygun dil kullan
            
            Baglam: {context}
        parser = PydanticOutputParser(pydantic_object=StudyPlan)
        
        prompt = PromptTemplate(
            template="""YKS'ye hazirlanan bir ogrenci icin haftalik calisma plani olustur.

            Ogrenci Bilgileri:
            - Hedef: {target_exam}
            - Kalan Sure: {remaining_days} gun
            - Guclu Konular: {strong_subjects}
            - Zayif Konular: {weak_subjects}
            - Gunluk Calisma Suresi: {daily_hours} saat
            
            Plan Ozellikleri:
            - Dengeli konu dagilimi
            - Zayif konulara daha fazla zaman
            - Tekrar ve pekistirme zamanlari
            - Dinlenme aralari
            
            {format_instructions}
            
            Calisma plani pratik, uygulanabilir ve motivasyon saglayici olmali.""",
            input_variables=["target_exam", "remaining_days", "strong_subjects", 
                           "weak_subjects", "daily_hours"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        return prompt | self.llm | OutputFixingParser.from_llm(parser=parser, llm=self.llm)
    
    def _create_quiz_chain(self):
        pass
        parser = PydanticOutputParser(pydantic_object=QuizQuestion)
        
        prompt = PromptTemplate(
            template="""YKS {exam_type} sinavi icin {subject} dersi {topic} konusunda 
            {difficulty} zorlukta bir soru hazirla.
            
            Soru ozellikleri:
            - Gercek YKS formatina uygun olmali
            - Net ve anlasilir olmali
            - Celdiriciler mantikli olmali
            - Aciklama detayli ve ogretici olmali
            - Gorsel betimlemeler icerebilir
            
            Konu Detayi: {topic_detail}
            
            {format_instructions}""",
            input_variables=["exam_type", "subject", "topic", "difficulty", "topic_detail"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        return prompt | self.llm | OutputFixingParser.from_llm(parser=parser, llm=self.llm)
    
    def _create_explanation_chain(self):
        pass
        parser = PydanticOutputParser(pydantic_object=ConceptExplanation)
        
        prompt = PromptTemplate(
            template="""YKS ogrencisi icin {subject} dersi {topic} konusunu acikla.
            
            Aciklama ozellikleri:
            - Basit ve anlasilir dil kullan
            - Gorsel betimlemeler ekle
            - Gunluk hayattan ornekler ver
            - Formulleri adim adim acikla
            - Onemli noktalari vurgula
            - Sik yapilan hatalari belirt
            
            Aciklama Stili: {style}
            Detay Seviyesi: {detail_level}
            
            {format_instructions}""",
            input_variables=["subject", "topic", "style", "detail_level"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        return prompt | self.llm | OutputFixingParser.from_llm(parser=parser, llm=self.llm)
    
    def _create_summary_chain(self):
        pass
        prompt = PromptTemplate(
            template="""Asagidaki icerigi YKS ogrencisi icin ozetle:
            
            Icerik: {content}
            
            Ozet Formati: {format}
            Vurgulanacak Noktalar: {emphasis_points}
            
            Ozet ozellikleri:
            - Ana kavramlari vurgula
            - Formulleri ve tanimlari koru
            - Mantiksal sira takip et
            - YKS'de cikabilecek noktalara odaklan
            - Gorsel ipuclari ekle""",
            input_variables=["content", "format", "emphasis_points"]
        )
        
        return prompt | self.llm
    
    def _create_concept_map_chain(self):
        pass
        parser = PydanticOutputParser(pydantic_object=ConceptMap)
        
        prompt = PromptTemplate(
            template="""YKS {subject} dersi {topic} konusu icin kavram haritasi olustur.
            
            Harita ozellikleri:
            - Hiyerarsik yapi olmali
            - Kavramlar arasi iliskiler net olmali
            - YKS mufredatina uygun olmali
            - Ogrenmeyi kolaylastirici olmali
            - Alt konular detayli olmali
            
            {format_instructions}""",
            input_variables=["subject", "topic"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        return prompt | self.llm | OutputFixingParser.from_llm(parser=parser, llm=self.llm)
    
    def _create_motivation_chain(self):
        pass
        prompt = PromptTemplate(
            template="""YKS'ye hazirlanan ogrenciye motivasyon sagla.
            
            Ogrenci Durumu: {student_situation}
            Mevcut Zorluklar: {challenges}
            
            Motivasyon ozellikleri:
            - Gercekci ve yapici ol
            - Basari hikayeleri paylas
            - Somut oneriler sun
            - Cesaretlendirici ol
            - Hedef odakli yaklas""",
            input_variables=["student_situation", "challenges"]
        )
        
        return prompt | self.llm
    
    def _create_problem_solving_chain(self):
        pass
        prompt = PromptTemplate(
            template="""{subject} dersi problemi:
            {problem}
            
            Bu problemi adim adim coz:
            1. Verilenler ve istenenler
            2. Cozum stratejisi
            3. Adim adim cozum
            4. Sonuc ve kontrol
            5. Alternatif cozum yollari
            
            Cozum Stili: {solution_style}
            Detay Seviyesi: {detail_level}
            
            Not: Her adimi acikla ve formulleri detaylandir.""",
        try:
            chat_history = self.memory.chat_memory.messages if hasattr(self.memory, 'chat_memory') else ""
            
            response = await self.socratic_chain.ainvoke({
                "input": user_input,
                "context": context or "",
                "chat_history": str(chat_history)
            })
            
            # Save to memory
            self.memory.save_context({"input": user_input}, {"output": response.content})
            
            return response.content
            
        except Exception as e:
            logger.error(f"Socratic chain error: {str(e)}")
            return "Uzgunum, bir hata olustu. Sorunuzu tekrar sorabilir misiniz?"
    
    async def generate_study_plan(self, student_info: Dict[str, Any]) -> StudyPlan:
        pass
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
        pass
        try:
            # Set defaults
            quiz_params.setdefault("topic_detail", "")
            
            response = await self.quiz_chain.ainvoke(quiz_params)
            return response
            
        except Exception as e:
            logger.error(f"Quiz chain error: {str(e)}")
            raise
    
    async def explain_concept(self, explanation_params: Dict[str, Any]) -> str:
        pass
        try:
            response = await self.explanation_chain.ainvoke(explanation_params)
            
            # Format structured explanation
            formatted = f"**{response.topic}**\n\n"
            formatted += f"📖 **Tanim:** {response.definition}\n\n"
            formatted += "📌 **Onemli Noktalar:**\n"
            for point in response.key_points:
                formatted += f"• {point}\n"
            formatted += "\n💡 **Ornekler:**\n"
            for example in response.examples:
                formatted += f"• {example}\n"
            formatted += "\n⚠️ **Sik Yapilan Hatalar:**\n"
            for mistake in response.common_mistakes:
                formatted += f"• {mistake}\n"
            formatted += "\n✨ **Ipuclari:**\n"
            for tip in response.tips:
                formatted += f"• {tip}\n"
            
            return formatted
            
        except Exception as e:
            logger.error(f"Explanation chain error: {str(e)}")
            return await self._fallback_explain(explanation_params)
    
    async def _fallback_explain(self, params: Dict[str, Any]) -> str:
        pass
        prompt = f"{params['subject']} dersi {params['topic']} konusunu acikla."
        response = await self.llm.ainvoke(prompt)
        return response.content
    
    async def summarize_content(self, summary_params: Dict[str, Any]) -> str:
        pass
        try:
            response = await self.summary_chain.ainvoke(summary_params)
            return response.content
            
        except Exception as e:
            logger.error(f"Summary chain error: {str(e)}")
            raise
    
    async def generate_concept_map(self, map_params: Dict[str, Any]) -> ConceptMap:
        pass
        try:
            response = await self.concept_map_chain.ainvoke(map_params)
            return response
            
        except Exception as e:
            logger.error(f"Concept map chain error: {str(e)}")
            raise
    
    async def provide_motivation(self, motivation_params: Dict[str, Any]) -> str:
        pass
        try:
            response = await self.motivation_chain.ainvoke(motivation_params)
            return response.content
            
        except Exception as e:
            logger.error(f"Motivation chain error: {str(e)}")
            return "Basarabilirsin! Her adim seni hedefe yaklastiriyor. 💪"
    
    async def solve_problem(self, problem_params: Dict[str, Any]) -> str:
        pass
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
        pass
        self.memory.clear()

# Global chains instance
chains = UnifiedChains()