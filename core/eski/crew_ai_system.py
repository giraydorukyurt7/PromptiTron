"""
CrewAI Integration for Promptitron
Multi-agent system with specialized educational agents
"""

import os
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from langchain.tools import Tool
from crewai.llm import LLM

from config import settings
from core.gemini_client import gemini_client
from core.rag_system import rag_system
from models.structured_models import *

logger = logging.getLogger(__name__)

class RAGSearchTool(BaseTool):
    """Tool for searching through RAG system"""
    name: str = "rag_search"
    description: str = "Search through knowledge base using RAG system"

    def _run(self, query: str, collection_names: Optional[List[str]] = None) -> str:
        """Search the RAG system"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            results = loop.run_until_complete(
                rag_system.search(
                    query=query,
                    collection_names=collection_names,
                    n_results=5
                )
            )
            
            # Format results for agent
            formatted_results = []
            for result in results:
                formatted_results.append(f"Content: {result['content']}\nMetadata: {result.get('metadata', {})}")
            
            return "\n\n".join(formatted_results)
            
        except Exception as e:
            logger.error(f"RAG search error: {e}")
            return f"Search failed: {str(e)}"
    
    async def _arun(self, query: str, collection_names: Optional[List[str]] = None) -> str:
        """Async version of search"""
        try:
            results = await rag_system.search(
                query=query,
                collection_names=collection_names,
                n_results=5
            )
            
            formatted_results = []
            for result in results:
                formatted_results.append(f"Content: {result['content']}\nMetadata: {result.get('metadata', {})}")
            
            return "\n\n".join(formatted_results)
            
        except Exception as e:
            logger.error(f"RAG search error: {e}")
            return f"Search failed: {str(e)}"

class CurriculumTool(BaseTool):
    """Tool for accessing curriculum data"""
    name: str = "curriculum_access"
    description: str = "Access YKS curriculum data and learning objectives"

    def _run(self, subject: str, topic: Optional[str] = None) -> str:
        """Get curriculum data"""
        try:
            import json
            
            from .curriculum_loader import curriculum_loader
            
            # Ensure curriculum is loaded
            if not curriculum_loader.curriculum_data:
                curriculum_loader.load_all_curriculum()
            
            # Search for relevant content
            if topic:
                # Search for specific topic
                results = curriculum_loader.search_topics(topic, subject)
                if results:
                    relevant_content = []
                    for result in results[:5]:  # Top 5 results
                        content = f"Subject: {result['subject']}\n"
                        content += f"Grade: {result['grade']}\n"
                        content += f"Title: {result['title']}\n"
                        content += f"Content: {result['content']}\n"
                        if result.get('terms'):
                            content += f"Terms: {result['terms']}\n"
                        relevant_content.append(content)
                    return "\n\n".join(relevant_content)
            else:
                # Get all topics for subject
                topics = curriculum_loader.get_subject_topics(subject)
                if topics:
                    relevant_content = []
                    for topic_data in topics[:10]:  # Top 10 topics
                        content = f"Subject: {topic_data['subject']}\n"
                        content += f"Grade: {topic_data['grade']}\n"  
                        content += f"Title: {topic_data['title']}\n"
                        content += f"Content: {topic_data['content'][:200]}...\n"
                        relevant_content.append(content)
                    return "\n\n".join(relevant_content)
            
            return f"No curriculum data found for {subject}" + (f" - {topic}" if topic else "")
            
        except Exception as e:
            logger.error(f"Curriculum access error: {e}")
            return f"Curriculum access failed: {str(e)}"
    
    async def _arun(self, subject: str, topic: Optional[str] = None) -> str:
        """Async version"""
        return self._run(subject, topic)

class CrewAISystem:
    """CrewAI multi-agent system for educational tasks"""
    
    def __init__(self):
        # CrewAI LLM with proper Gemini format
        self.llm = LLM(
            model="gemini/gemini-2.5-flash",
            api_key=settings.GOOGLE_API_KEY,
            temperature=0.7
        )
        
        self.tools = [
            RAGSearchTool(),
            CurriculumTool()
        ]
        
        self.agents = self._create_agents()
        self.crews = self._create_crews()
        
    def _create_agents(self) -> Dict[str, Agent]:
        """Create specialized educational agents"""
        
        # Mathematics Expert Agent
        math_agent = Agent(
            role="Matematik Uzmanı",
            goal="YKS matematik sorularını çözmek, kavramları açıklamak ve öğrencilere yardımcı olmak",
            backstory="""Sen deneyimli bir matematik öğretmenisin. YKS sınavı formatını çok iyi biliyorsun ve 
            öğrencilerin matematik konularında zorlandıkları alanları anlayabiliyorsun. Karmaşık matematik 
            problemlerini basit adımlara bölerek açıklayabilir, kavramsal anlayışı destekleyebilirsin.
            Sadece curriculum_access tool'u ile matematik müfredatını kontrol et ve bu kapsamda yanıt ver.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.llm
        )
        
        # Physics Expert Agent
        physics_agent = Agent(
            role="Fizik Uzmanı",
            goal="Fizik kavramlarını anlaşılır şekilde açıklamak ve YKS fizik sorularında yardımcı olmak",
            backstory="""Sen fizik alanında uzman bir eğitmensin. Karmaşık fizik kavramlarını günlük yaşam 
            örnekleriyle açıklayabilir, formüllerin arkasındaki mantığı anlatabilirsin. YKS fizik müfredatını 
            ve soru tiplerini çok iyi biliyorsun.
            Sadece curriculum_access tool'u ile fizik müfredatını kontrol et ve bu kapsamda yanıt ver.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.llm
        )
        
        # Chemistry Expert Agent
        chemistry_agent = Agent(
            role="Kimya Uzmanı",
            goal="Kimya konularını öğretmek ve YKS kimya sorularında rehberlik etmek",
            backstory="""Sen kimya alanında uzman bir öğretmensin. Atom yapısından organik kimyaya kadar 
            tüm konularda derin bilgiye sahipsin. Kimyasal reaksiyonları ve mekanizmaları anlaşılır şekilde 
            açıklayabilir, laboratuvar deneyimleriyle destekleyebilirsin.
            Sadece curriculum_access tool'u ile kimya müfredatını kontrol et ve bu kapsamda yanıt ver.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.llm
        )
        
        # Biology Expert Agent
        biology_agent = Agent(
            role="Biyoloji Uzmanı",
            goal="Biyoloji konularını öğretmek ve YKS biyoloji sorularında yardımcı olmak",
            backstory="""Sen biyoloji alanında uzman bir eğitimcisin. Hücre biyolojisinden ekolojiye kadar 
            tüm konularda detaylı bilgiye sahipsin. Canlı sistemlerin işleyişini anlaşılır örneklerle 
            açıklayabilir, güncel bilimsel gelişmeleri de takip ediyorsun.
            Sadece curriculum_access tool'u ile biyoloji müfredatını kontrol et ve bu kapsamda yanıt ver.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.llm
        )
        
        # Study Plan Coordinator Agent
        coordinator_agent = Agent(
            role="Çalışma Planı Koordinatörü",
            goal="Öğrenciler için kişiselleştirilmiş çalışma planları oluşturmak",
            backstory="""Sen deneyimli bir eğitim danışmanısın. Öğrencilerin güçlü ve zayıf yönlerini analiz 
            ederek en etkili çalışma stratejilerini belirleyebilirsin. YKS sınav sistemini çok iyi bilir, 
            zaman yönetimi ve verimli çalışma teknikleri konusunda uzmansın.""",
            verbose=True,
            allow_delegation=True,
            tools=self.tools,
            llm=self.llm
        )
        
        # Turkish Language and Literature Expert Agent
        turkish_agent = Agent(
            role="Türkçe ve Edebiyat Uzmanı",
            goal="Türkçe dil bilgisi ve edebiyat konularında rehberlik etmek, YKS TYT Türkçe sorularında yardımcı olmak",
            backstory="""Sen Türkçe dil bilgisi ve edebiyat alanında uzman bir öğretmensin. Dil bilgisi kuralları, 
            cümle yapıları, anlatım bozuklukları ve edebiyat tarihini çok iyi biliyorsun. YKS TYT Türkçe 
            müfredatını takip eder, metin analizi ve dil bilgisi konularında detaylı açıklamalar yapabilirsin.
            Sadece curriculum_access tool'u ile Türkçe müfredatını kontrol et ve bu kapsamda yanıt ver.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.llm
        )
        
        # History Expert Agent
        history_agent = Agent(
            role="Tarih Uzmanı", 
            goal="Tarih konularını öğretmek ve YKS AYT tarih sorularında yardımcı olmak",
            backstory="""Sen tarih alanında uzman bir öğretmensin. Türk tarihi, dünya tarihi, siyasi tarih ve 
            kültür tarihi konularında derin bilgiye sahipsin. YKS AYT tarih müfredatını çok iyi bilir, 
            tarihi olayları sebep-sonuç ilişkileri içinde açıklayabilirsin.
            Sadece curriculum_access tool'u ile tarih müfredatını kontrol et ve bu kapsamda yanıt ver.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools, 
            llm=self.llm
        )
        
        # Geography Expert Agent
        geography_agent = Agent(
            role="Coğrafya Uzmanı",
            goal="Coğrafya konularını öğretmek ve YKS AYT coğrafya sorularında rehberlik etmek", 
            backstory="""Sen coğrafya alanında uzman bir eğitmensin. Fiziki coğrafya, beşeri coğrafya, 
            ekonomik coğrafya ve Türkiye coğrafyası konularında uzman bilgiye sahipsin. YKS AYT coğrafya 
            müfredatını takip eder, haritalar ve istatistiklerle destekleyebilirsin.
            Sadece curriculum_access tool'u ile coğrafya müfredatını kontrol et ve bu kapsamda yanıt ver.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.llm
        )
        
        # Philosophy Expert Agent  
        philosophy_agent = Agent(
            role="Felsefe Uzmanı",
            goal="Felsefe konularını öğretmek ve YKS AYT felsefe sorularında yardımcı olmak",
            backstory="""Sen felsefe alanında uzman bir öğretmensin. Antik felsefeden modern felsefeye kadar 
            tüm dönemleri bilir, felsefi akımları ve düşünürleri tanırsın. YKS AYT felsefe müfredatına uygun 
            şekilde karmaşık felsefi kavramları anlaşılır örneklerle açıklayabilirsin.
            Sadece curriculum_access tool'u ile felsefe müfredatını kontrol et ve bu kapsamda yanıt ver.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.llm
        )
        
        # Religious Culture Expert Agent
        religion_agent = Agent(
            role="Din Kültürü Uzmanı",
            goal="Din kültürü ve ahlak konularında eğitim vermek ve YKS AYT sorularında yardımcı olmak",
            backstory="""Sen din kültürü ve ahlak bilgisi alanında uzman bir öğretmensin. İslam tarihi, 
            din sosyolojisi, ahlak felsefesi ve karşılaştırmalı dinler konularında bilgiye sahipsin. 
            YKS AYT din kültürü müfredatını takip eder, hoşgörülü ve bilimsel yaklaşımla konuları açıklarsın.
            Sadece curriculum_access tool'u ile din kültürü müfredatını kontrol et ve bu kapsamda yanıt ver.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.llm
        )
        
        # Revolution History Expert Agent
        revolution_agent = Agent(
            role="İnkılap Tarihi Uzmanı",
            goal="T.C. İnkılap Tarihi ve Atatürkçülük konularında eğitim vermek ve YKS sorularında yardımcı olmak",
            backstory="""Sen T.C. İnkılap Tarihi ve Atatürkçülük alanında uzman bir öğretmensin. Milli Mücadele 
            dönemi, Atatürk ilke ve inkılapları, Cumhuriyet'in kuruluş felsefesi konularında derin bilgiye sahipsin. 
            YKS müfredatına uygun şekilde Türkiye Cumhuriyeti'nin modernleşme sürecini açıklayabilirsin.
            Sadece curriculum_access tool'u ile inkılap tarihi müfredatını kontrol et ve bu kapsamda yanıt ver.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.llm
        )

        # Content Analyst Agent
        analyst_agent = Agent(
            role="İçerik Analisti",
            goal="Eğitim içeriklerini analiz etmek ve değerlendirmek",
            backstory="""Sen eğitim içerikleri konusunda uzman bir analistsin. Metinlerin zorluk seviyesini, 
            müfredata uygunluğunu ve öğrenci seviyesine uygunluğunu değerlendirebilirsin. Halüsinasyon 
            tespiti ve içerik kalitesi kontrolü yapabilirsin.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.llm
        )
        
        return {
            "mathematician": math_agent,
            "physicist": physics_agent,
            "chemist": chemistry_agent,
            "biologist": biology_agent,
            "turkish_expert": turkish_agent,
            "history_expert": history_agent,
            "geography_expert": geography_agent,
            "philosophy_expert": philosophy_agent,
            "religion_expert": religion_agent,
            "revolution_expert": revolution_agent,
            "coordinator": coordinator_agent,
            "analyst": analyst_agent
        }
    
    def _create_crews(self) -> Dict[str, Crew]:
        """Create specialized crews for different tasks"""
        
        # All Subject Expert Crew (All YKS subjects)
        subject_experts_crew = Crew(
            agents=[
                self.agents["mathematician"],
                self.agents["physicist"], 
                self.agents["chemist"],
                self.agents["biologist"],
                self.agents["turkish_expert"],
                self.agents["history_expert"],
                self.agents["geography_expert"],
                self.agents["philosophy_expert"],
                self.agents["religion_expert"],
                self.agents["revolution_expert"]
            ],
            verbose=True,
            process=Process.sequential
        )
        
        # Study Planning Crew
        study_planning_crew = Crew(
            agents=[
                self.agents["coordinator"],
                self.agents["analyst"]
            ],
            verbose=True,
            process=Process.sequential
        )
        
        # Content Analysis Crew
        content_analysis_crew = Crew(
            agents=[self.agents["analyst"]],
            verbose=True,
            process=Process.sequential
        )
        
        return {
            "subject_experts": subject_experts_crew,
            "study_planning": study_planning_crew,
            "content_analysis": content_analysis_crew
        }
    
    async def process_educational_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process educational queries through appropriate expert agents"""
        try:
            # Classify the query to determine which expert to use
            expert_type = self._classify_query(query, context)
            
            if expert_type in ["math", "mathematics", "matematik"]:
                agent = self.agents["mathematician"]
                crew_name = "subject_experts"
            elif expert_type in ["physics", "fizik"]:
                agent = self.agents["physicist"]
                crew_name = "subject_experts"
            elif expert_type in ["chemistry", "kimya"]:
                agent = self.agents["chemist"]
                crew_name = "subject_experts"
            elif expert_type in ["biology", "biyoloji"]:
                agent = self.agents["biologist"]
                crew_name = "subject_experts"
            elif expert_type in ["study_plan", "çalışma_planı"]:
                agent = self.agents["coordinator"]
                crew_name = "study_planning"
            elif expert_type in ["analysis", "analiz"]:
                agent = self.agents["analyst"] 
                crew_name = "content_analysis"
            else:
                # Default to coordinator for general queries
                agent = self.agents["coordinator"]
                crew_name = "study_planning"
            
            # Create task for the selected agent
            task = Task(
                description=f"""
                Kullanıcı sorusu: {query}
                
                Bağlam: {context or {}}
                
                Lütfen bu soruya alanın uzmanı olarak detaylı ve yardımcı bir yanıt ver. 
                YKS sınavı formatını ve Türkiye eğitim sistemini göz önünde bulundur.
                Gerekiyorsa RAG sistemini kullanarak ek bilgi ara.
                Gerekiyorsa müfredat verilerine eriş.
                
                Yanıtında şunları içer:
                1. Ana soruya doğrudan yanıt
                2. Gerekirse adım adım açıklama
                3. İlgili kavramların açıklaması
                4. Öğrenci için pratik öneriler
                5. İlgili kaynaklar veya konular
                """,
                agent=agent,
                expected_output="Öğrenci sorusuna uygun, detaylı ve eğitici bir yanıt"
            )
            
            # Execute task
            crew = self.crews[crew_name]
            crew.tasks = [task]
            
            # Run in thread to avoid blocking
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(crew.kickoff)
                result = future.result(timeout=60)  # 60 second timeout
            
            return {
                "success": True,
                "response": str(result),
                "agent_used": agent.role,
                "crew_used": crew_name,
                "expert_type": expert_type
            }
            
        except Exception as e:
            logger.error(f"CrewAI processing error: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "Üzgünüm, sorunu işlerken bir hata oluştu. Lütfen tekrar deneyin."
            }
    
    def _classify_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """Classify query to determine appropriate expert"""
        query_lower = query.lower()
        
        # Math keywords
        math_keywords = [
            "matematik", "math", "sayı", "hesap", "türev", "integral", "geometri", 
            "trigonometri", "logaritma", "fonksiyon", "denklem", "grafik", "limit",
            "olasılık", "istatistik", "matris"
        ]
        
        # Physics keywords  
        physics_keywords = [
            "fizik", "physics", "kuvvet", "hareket", "enerji", "elektrik", "manyetik",
            "dalga", "ışık", "ses", "basınç", "sıcaklık", "atom", "çekim", "momentum"
        ]
        
        # Chemistry keywords
        chemistry_keywords = [
            "kimya", "chemistry", "element", "bileşik", "reaksiyon", "asit", "baz",
            "mol", "orbital", "bağ", "çözelti", "kataliz", "organik", "periyodik"
        ]
        
        # Biology keywords
        biology_keywords = [
            "biyoloji", "biology", "hücre", "dna", "gen", "protein", "enzim",
            "fotosentez", "solunum", "dolaşım", "sinir", "hormon", "ekosistem"
        ]
        
        # Study plan keywords
        study_keywords = [
            "plan", "çalışma", "program", "takvim", "strateji", "hedef", "zaman"
        ]
        
        # Analysis keywords
        analysis_keywords = [
            "analiz", "değerlendir", "incele", "kontrol", "test", "ölç"
        ]
        
        # Check context for subject hints
        if context:
            subject = context.get("subject", "").lower()
            if "matematik" in subject: return "math"
            if "fizik" in subject: return "physics"
            if "kimya" in subject: return "chemistry" 
            if "biyoloji" in subject: return "biology"
        
        # Check query content
        if any(keyword in query_lower for keyword in math_keywords):
            return "math"
        elif any(keyword in query_lower for keyword in physics_keywords):
            return "physics"
        elif any(keyword in query_lower for keyword in chemistry_keywords):
            return "chemistry"
        elif any(keyword in query_lower for keyword in biology_keywords):
            return "biology"
        elif any(keyword in query_lower for keyword in study_keywords):
            return "study_plan"
        elif any(keyword in query_lower for keyword in analysis_keywords):
            return "analysis"
        else:
            return "general"
    
    async def generate_questions_with_crew(self, subject: str, topic: str, difficulty: str, count: int) -> Dict[str, Any]:
        """Generate questions using CrewAI experts"""
        try:
            # Normalize subject to uppercase
            subject_normalized = subject.upper()
            
            # Select appropriate expert
            expert_mapping = {
                "MATEMATIK": "mathematician",
                "FIZIK": "physicist", 
                "KIMYA": "chemist",
                "BIYOLOJI": "biologist",
                "TURKCE": "turkish_expert",
                "EDEBIYAT": "turkish_expert",
                "TARIH": "history_expert",
                "COGRAFYA": "geography_expert",
                "FELSEFE": "philosophy_expert",
                "DIN_KULTURU": "religion_expert",
                "INKILAP_TARIHI": "revolution_expert"
            }
            
            agent_key = expert_mapping.get(subject_normalized, "turkish_expert")  # Default to turkish_expert for literature
            agent = self.agents[agent_key]
            
            logger.info(f"Question generation: Subject='{subject}' -> Normalized='{subject_normalized}' -> Agent='{agent_key}' -> Role='{agent.role}'")
            
            task = Task(
                description=f"""
                {subject_normalized} dersi için {topic} konusunda YKS seviyesinde {count} adet çoktan seçmeli 
                soru oluştur. Zorluk seviyesi: {difficulty}
                
                Her soru için şu formatı kullan:
                
                Soru 1:
                [Soru metni buraya]
                
                A) [Seçenek A]
                B) [Seçenek B]  
                C) [Seçenek C]
                D) [Seçenek D]
                E) [Seçenek E]
                
                Doğru Cevap: [Harf]
                Açıklama: [Detaylı açıklama]
                
                ---
                
                Müfredata uygun, net ve anlaşılır sorular oluştur.
                """,
                agent=agent,
                expected_output=f"{count} adet YKS seviyesinde çoktan seçmeli soru"
            )
            
            crew = Crew(agents=[agent], tasks=[task], verbose=True)
            
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(crew.kickoff)
                raw_result = future.result(timeout=60)
            
            # Parse the result to extract questions
            questions_text = str(raw_result)
            parsed_questions = self._parse_questions_from_text(questions_text, count)
            
            return {
                "success": True,
                "questions": parsed_questions,
                "agent_used": agent.role,
                "raw_response": questions_text
            }
            
        except Exception as e:
            logger.error(f"Question generation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "questions": []
            }
    
    def _parse_questions_from_text(self, text: str, expected_count: int) -> List[Dict[str, Any]]:
        """Parse questions from raw text response"""
        try:
            questions = []
            
            # Split by question markers or numbers
            import re
            
            # Try to find questions by pattern
            question_pattern = r'(?:Soru\s*\d+:?|^\d+\.|\*\*Soru\s*\d+\*\*)(.*?)(?=(?:Soru\s*\d+:?|^\d+\.|\*\*Soru\s*\d+\*\*)|$)'
            matches = re.findall(question_pattern, text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            
            if not matches:
                # Try simpler splitting by --- or numbers
                parts = re.split(r'---+|(?:^|\n)\d+\.|Soru\s*\d+', text, flags=re.MULTILINE | re.IGNORECASE)
                matches = [part.strip() for part in parts if part.strip()]
            
            for i, match in enumerate(matches[:expected_count], 1):
                question_text = match.strip()
                
                # Extract question content
                lines = question_text.split('\n')
                
                # Find question text (first non-empty line that's not an option)
                question_content = ""
                options = {}
                correct_answer = ""
                explanation = ""
                
                current_section = "question"
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    # Check for options
                    option_match = re.match(r'^([A-E])\)\s*(.+)', line)
                    if option_match:
                        options[option_match.group(1)] = option_match.group(2)
                        current_section = "options"
                        continue
                    
                    # Check for correct answer
                    if re.match(r'(?:Doğru\s*[Cc]evap|[Cc]evap|Answer)[:=]\s*([A-E])', line, re.IGNORECASE):
                        correct_match = re.search(r'([A-E])', line)
                        if correct_match:
                            correct_answer = correct_match.group(1)
                        current_section = "answer"
                        continue
                    
                    # Check for explanation
                    if re.match(r'(?:Açıklama|[Ee]xplanation)[:=]', line, re.IGNORECASE):
                        explanation = line.split(':', 1)[-1].strip()
                        current_section = "explanation"
                        continue
                    
                    # Add to current section
                    if current_section == "question" and not question_content:
                        question_content = line
                    elif current_section == "explanation":
                        explanation += " " + line
                
                # Create question object
                if question_content:
                    question_obj = {
                        "question_text": question_content,
                        "options": options,
                        "correct_answer": correct_answer or "A",  # Default to A if not found
                        "explanation": explanation or "Açıklama bulunamadı",
                        "question_id": f"q_{i}",
                        "subject": "edebiyat",  # Will be updated by caller
                        "topic": "cumhuriyet_edebiyati"  # Will be updated by caller
                    }
                    questions.append(question_obj)
            
            # If parsing failed, create fallback questions
            if not questions:
                for i in range(expected_count):
                    questions.append({
                        "question_text": f"Soru {i+1}: (Parsing başarısız - ham metin: {text[:100]}...)",
                        "options": {
                            "A": "Seçenek A",
                            "B": "Seçenek B", 
                            "C": "Seçenek C",
                            "D": "Seçenek D",
                            "E": "Seçenek E"
                        },
                        "correct_answer": "A",
                        "explanation": "Açıklama parse edilemedi",
                        "question_id": f"fallback_{i+1}"
                    })
            
            logger.info(f"Parsed {len(questions)} questions from text")
            return questions
            
        except Exception as e:
            logger.error(f"Question parsing error: {e}")
            # Return fallback questions
            return [{
                "question_text": f"Soru {i+1}: Parse hatası oluştu",
                "options": {"A": "Seçenek A", "B": "Seçenek B", "C": "Seçenek C", "D": "Seçenek D", "E": "Seçenek E"},
                "correct_answer": "A",
                "explanation": f"Parse hatası: {str(e)}",
                "question_id": f"error_{i+1}"
            } for i in range(expected_count)]
    
    async def create_study_plan_with_crew(self, student_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Create study plan using coordinator agent"""
        try:
            coordinator = self.agents["coordinator"]
            analyst = self.agents["analyst"]
            
            # Analysis task
            analysis_task = Task(
                description=f"""
                Öğrenci Profili: {student_profile}
                
                Bu öğrenci profilini analiz et:
                1. Güçlü ve zayıf yönleri belirle
                2. Hedef sınav tipini değerlendir
                3. Mevcut durumu asses et
                4. Önerilen focus alanlarını belirle
                """,
                agent=analyst,
                expected_output="Öğrenci analiz raporu"
            )
            
            # Planning task
            planning_task = Task(
                description=f"""
                Öğrenci analiz raporu: {{analysis_task.output}}
                
                Bu rapora dayalı olarak detaylı çalışma planı oluştur:
                1. Haftalık çalışma programı
                2. Günlük ders dağılımı
                3. Zayıf konulara özel focus
                4. Deneme sınavı programı
                5. Motivasyon stratejileri
                6. İlerleme takip metrikleri
                
                Plan 12 haftalık olsun ve uygulanabilir olsun.
                """,
                agent=coordinator,
                expected_output="Detaylı çalışma planı"
            )
            
            crew = Crew(
                agents=[analyst, coordinator],
                tasks=[analysis_task, planning_task],
                verbose=True,
                process=Process.sequential
            )
            
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(crew.kickoff)
                result = future.result(timeout=90)
            
            return {
                "success": True,
                "study_plan": str(result),
                "agents_used": ["İçerik Analisti", "Çalışma Planı Koordinatörü"]
            }
            
        except Exception as e:
            logger.error(f"Study plan creation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_content_with_crew(self, content: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze content using analyst agent"""
        try:
            analyst = self.agents["analyst"]
            
            task = Task(
                description=f"""
                İçerik: {content}
                Analiz Türü: {analysis_type}
                
                Bu içeriği kapsamlı olarak analiz et:
                1. Zorluk seviyesi değerlendirmesi
                2. Müfredata uygunluk kontrolü
                3. Kavramsal doğruluk kontrolü
                4. Halüsinasyon tespiti
                5. Öğrenci seviyesine uygunluk
                6. İyileştirme önerileri
                7. Alternatif açıklama yöntemleri
                
                Detaylı analiz raporu hazırla.
                """,
                agent=analyst,
                expected_output="Kapsamlı içerik analiz raporu"
            )
            
            crew = Crew(agents=[analyst], tasks=[task], verbose=True)
            
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(crew.kickoff)
                result = future.result(timeout=60)
            
            return {
                "success": True,
                "analysis": str(result),
                "agent_used": analyst.role
            }
            
        except Exception as e:
            logger.error(f"Content analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Global CrewAI system instance
crew_ai_system = CrewAISystem()