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
            role="Matematik Uzmani",
            goal="YKS matematik sorularini cozmek, kavramlari aciklamak ve ogrencilere yardimci olmak",
            backstory="""Sen deneyimli bir matematik ogretmenisin. YKS sinavi formatini cok iyi biliyorsun ve 
            ogrencilerin matematik konularinda zorlandiklari alanlari anlayabiliyorsun. Karmasik matematik 
            problemlerini basit adimlara bolerek aciklayabilir, kavramsal anlayisi destekleyebilirsin.
            Sadece curriculum_access tool'u ile matematik mufredatini kontrol et ve bu kapsamda yanit ver.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.llm
        )
        
        # Physics Expert Agent
        physics_agent = Agent(
            role="Fizik Uzmani",
            goal="Fizik kavramlarini anlasilir sekilde aciklamak ve YKS fizik sorularinda yardimci olmak",
            backstory="""Sen fizik alaninda uzman bir egitmensin. Karmasik fizik kavramlarini gunluk yasam 
            ornekleriyle aciklayabilir, formullerin arkasindaki mantigi anlatabilirsin. YKS fizik mufredatini 
            ve soru tiplerini cok iyi biliyorsun.
            Sadece curriculum_access tool'u ile fizik mufredatini kontrol et ve bu kapsamda yanit ver.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.llm
        )
        
        # Chemistry Expert Agent
        chemistry_agent = Agent(
            role="Kimya Uzmani",
            goal="Kimya konularini ogretmek ve YKS kimya sorularinda rehberlik etmek",
            backstory="""Sen kimya alaninda uzman bir ogretmensin. Atom yapisindan organik kimyaya kadar 
            tum konularda derin bilgiye sahipsin. Kimyasal reaksiyonlari ve mekanizmalari anlasilir sekilde 
            aciklayabilir, laboratuvar deneyimleriyle destekleyebilirsin.
            Sadece curriculum_access tool'u ile kimya mufredatini kontrol et ve bu kapsamda yanit ver.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.llm
        )
        
        # Biology Expert Agent
        biology_agent = Agent(
            role="Biyoloji Uzmani",
            goal="Biyoloji konularini ogretmek ve YKS biyoloji sorularinda yardimci olmak",
            backstory="""Sen biyoloji alaninda uzman bir egitimcisin. Hucre biyolojisinden ekolojiye kadar 
            tum konularda detayli bilgiye sahipsin. Canli sistemlerin isleyisini anlasilir orneklerle 
            aciklayabilir, guncel bilimsel gelismeleri de takip ediyorsun.
            Sadece curriculum_access tool'u ile biyoloji mufredatini kontrol et ve bu kapsamda yanit ver.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.llm
        )
        
        # Study Plan Coordinator Agent
        coordinator_agent = Agent(
            role="Calisma Plani Koordinatoru",
            goal="Ogrenciler icin kisisellestirilmis calisma planlari olusturmak",
            backstory="""Sen deneyimli bir egitim danismanisin. Ogrencilerin guclu ve zayif yonlerini analiz 
            ederek en etkili calisma stratejilerini belirleyebilirsin. YKS sinav sistemini cok iyi bilir, 
            zaman yonetimi ve verimli calisma teknikleri konusunda uzmansin.""",
            verbose=True,
            allow_delegation=True,
            tools=self.tools,
            llm=self.llm
        )
        
        # Turkish Language and Literature Expert Agent
        turkish_agent = Agent(
            role="Turkce ve Edebiyat Uzmani",
            goal="Turkce dil bilgisi ve edebiyat konularinda rehberlik etmek, YKS TYT Turkce sorularinda yardimci olmak",
            backstory="""Sen Turkce dil bilgisi ve edebiyat alaninda uzman bir ogretmensin. Dil bilgisi kurallari, 
            cumle yapilari, anlatim bozukluklari ve edebiyat tarihini cok iyi biliyorsun. YKS TYT Turkce 
            mufredatini takip eder, metin analizi ve dil bilgisi konularinda detayli aciklamalar yapabilirsin.
            Sadece curriculum_access tool'u ile Turkce mufredatini kontrol et ve bu kapsamda yanit ver.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.llm
        )
        
        # History Expert Agent
        history_agent = Agent(
            role="Tarih Uzmani", 
            goal="Tarih konularini ogretmek ve YKS AYT tarih sorularinda yardimci olmak",
            backstory="""Sen tarih alaninda uzman bir ogretmensin. Turk tarihi, dunya tarihi, siyasi tarih ve 
            kultur tarihi konularinda derin bilgiye sahipsin. YKS AYT tarih mufredatini cok iyi bilir, 
            tarihi olaylari sebep-sonuc iliskileri icinde aciklayabilirsin.
            Sadece curriculum_access tool'u ile tarih mufredatini kontrol et ve bu kapsamda yanit ver.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools, 
            llm=self.llm
        )
        
        # Geography Expert Agent
        geography_agent = Agent(
            role="Cografya Uzmani",
            goal="Cografya konularini ogretmek ve YKS AYT cografya sorularinda rehberlik etmek", 
            backstory="""Sen cografya alaninda uzman bir egitmensin. Fiziki cografya, beseri cografya, 
            ekonomik cografya ve Turkiye cografyasi konularinda uzman bilgiye sahipsin. YKS AYT cografya 
            mufredatini takip eder, haritalar ve istatistiklerle destekleyebilirsin.
            Sadece curriculum_access tool'u ile cografya mufredatini kontrol et ve bu kapsamda yanit ver.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.llm
        )
        
        # Philosophy Expert Agent  
        philosophy_agent = Agent(
            role="Felsefe Uzmani",
            goal="Felsefe konularini ogretmek ve YKS AYT felsefe sorularinda yardimci olmak",
            backstory="""Sen felsefe alaninda uzman bir ogretmensin. Antik felsefeden modern felsefeye kadar 
            tum donemleri bilir, felsefi akimlari ve dusunurleri tanirsin. YKS AYT felsefe mufredatina uygun 
            sekilde karmasik felsefi kavramlari anlasilir orneklerle aciklayabilirsin.
            Sadece curriculum_access tool'u ile felsefe mufredatini kontrol et ve bu kapsamda yanit ver.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.llm
        )
        
        # Religious Culture Expert Agent
        religion_agent = Agent(
            role="Din Kulturu Uzmani",
            goal="Din kulturu ve ahlak konularinda egitim vermek ve YKS AYT sorularinda yardimci olmak",
            backstory="""Sen din kulturu ve ahlak bilgisi alaninda uzman bir ogretmensin. Islam tarihi, 
            din sosyolojisi, ahlak felsefesi ve karsilastirmali dinler konularinda bilgiye sahipsin. 
            YKS AYT din kulturu mufredatini takip eder, hosgorulu ve bilimsel yaklasimla konulari aciklarsin.
            Sadece curriculum_access tool'u ile din kulturu mufredatini kontrol et ve bu kapsamda yanit ver.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.llm
        )
        
        # Revolution History Expert Agent
        revolution_agent = Agent(
            role="Inkilap Tarihi Uzmani",
            goal="T.C. Inkilap Tarihi ve Ataturkculuk konularinda egitim vermek ve YKS sorularinda yardimci olmak",
            backstory="""Sen T.C. Inkilap Tarihi ve Ataturkculuk alaninda uzman bir ogretmensin. Milli Mucadele 
            donemi, Ataturk ilke ve inkilaplari, Cumhuriyet'in kurulus felsefesi konularinda derin bilgiye sahipsin. 
            YKS mufredatina uygun sekilde Turkiye Cumhuriyeti'nin modernlesme surecini aciklayabilirsin.
            Sadece curriculum_access tool'u ile inkilap tarihi mufredatini kontrol et ve bu kapsamda yanit ver.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.llm
        )

        # Content Analyst Agent
        analyst_agent = Agent(
            role="Icerik Analisti",
            goal="Egitim iceriklerini analiz etmek ve degerlendirmek",
            backstory="""Sen egitim icerikleri konusunda uzman bir analistsin. Metinlerin zorluk seviyesini, 
            mufredata uygunlugunu ve ogrenci seviyesine uygunlugunu degerlendirebilirsin. Halusinasyon 
            tespiti ve icerik kalitesi kontrolu yapabilirsin.""",
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
            elif expert_type in ["study_plan", "calisma_plani"]:
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
                description=f
"""Kullanici sorusu: {query}
                
                Baglam: {context or {}}
                
                Lutfen bu soruya alanin uzmani olarak detayli ve yardimci bir yanit ver. 
                YKS sinavi formatini ve Turkiye egitim sistemini goz onunde bulundur.
                Gerekiyorsa RAG sistemini kullanarak ek bilgi ara.
                Gerekiyorsa mufredat verilerine eris.
                
                Yanitinda sunlari icer:
                1. Ana soruya dogrudan yanit
                2. Gerekirse adim adim aciklama
                3. Ilgili kavramlarin aciklamasi
                4. Ogrenci icin pratik oneriler
                5. Ilgili kaynaklar veya konular
                """,
                agent=agent,
                expected_output="Ogrenci sorusuna uygun, detayli ve egitici bir yanit"
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
                "response": "Uzgunum, sorunu islerken bir hata olustu. Lutfen tekrar deneyin."
            }
    
    def _classify_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """Classify query to determine appropriate expert"""
        query_lower = query.lower()
        
        # Math keywords
        math_keywords = [
            "matematik", "math", "sayi", "hesap", "turev", "integral", "geometri", 
            "trigonometri", "logaritma", "fonksiyon", "denklem", "grafik", "limit",
            "olasilik", "istatistik", "matris"
        ]
        
        # Physics keywords  
        physics_keywords = [
            "fizik", "physics", "kuvvet", "hareket", "enerji", "elektrik", "manyetik",
            "dalga", "isik", "ses", "basinc", "sicaklik", "atom", "cekim", "momentum"
        ]
        
        # Chemistry keywords
        chemistry_keywords = [
            "kimya", "chemistry", "element", "bilesik", "reaksiyon", "asit", "baz",
            "mol", "orbital", "bag", "cozelti", "kataliz", "organik", "periyodik"
        ]
        
        # Biology keywords
        biology_keywords = [
            "biyoloji", "biology", "hucre", "dna", "gen", "protein", "enzim",
            "fotosentez", "solunum", "dolasim", "sinir", "hormon", "ekosistem"
        ]
        
        # Study plan keywords
        study_keywords = [
            "plan", "calisma", "program", "takvim", "strateji", "hedef", "zaman"
        ]
        
        # Analysis keywords
        analysis_keywords = [
            "analiz", "degerlendir", "incele", "kontrol", "test", "olc"
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
                {subject_normalized} dersi icin {topic} konusunda YKS seviyesinde {count} adet coktan secmeli 
                soru olustur. Zorluk seviyesi: {difficulty}
                
                Her soru icin su formati kullan:
                
                Soru 1:
                [Soru metni buraya]
                
                A) [Secenek A]
                B) [Secenek B]  
                C) [Secenek C]
                D) [Secenek D]
                E) [Secenek E]
                
                Dogru Cevap: [Harf]
                Aciklama: [Detayli aciklama]
                
                ---
                
                Mufredata uygun, net ve anlasilir sorular olustur.
                """,
                agent=agent,
                expected_output=f"{count} adet YKS seviyesinde coktan secmeli soru"
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
                    if re.match(r'(?:Dogru\s*[Cc]evap|[Cc]evap|Answer)[:=]\s*([A-E])', line, re.IGNORECASE):
                        correct_match = re.search(r'([A-E])', line)
                        if correct_match:
                            correct_answer = correct_match.group(1)
                        current_section = "answer"
                        continue
                    
                    # Check for explanation
                    if re.match(r'(?:Aciklama|[Ee]xplanation)[:=]', line, re.IGNORECASE):
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
                        "explanation": explanation or "Aciklama bulunamadi",
                        "question_id": f"q_{i}",
                        "subject": "edebiyat",  # Will be updated by caller
                        "topic": "cumhuriyet_edebiyati"  # Will be updated by caller
                    }
                    questions.append(question_obj)
            
            # If parsing failed, create fallback questions
            if not questions:
                for i in range(expected_count):
                    questions.append({
                        "question_text": f"Soru {i+1}: (Parsing basarisiz - ham metin: {text[:100]}...)",
                        "options": {
                            "A": "Secenek A",
                            "B": "Secenek B", 
                            "C": "Secenek C",
                            "D": "Secenek D",
                            "E": "Secenek E"
                        },
                        "correct_answer": "A",
                        "explanation": "Aciklama parse edilemedi",
                        "question_id": f"fallback_{i+1}"
                    })
            
            logger.info(f"Parsed {len(questions)} questions from text")
            return questions
            
        except Exception as e:
            logger.error(f"Question parsing error: {e}")
            # Return fallback questions
            return [{
                "question_text": f"Soru {i+1}: Parse hatasi olustu",
                "options": {"A": "Secenek A", "B": "Secenek B", "C": "Secenek C", "D": "Secenek D", "E": "Secenek E"},
                "correct_answer": "A",
                "explanation": f"Parse hatasi: {str(e)}",
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
                Ogrenci Profili: {student_profile}
                
                Bu ogrenci profilini analiz et:
                1. Guclu ve zayif yonleri belirle
                2. Hedef sinav tipini degerlendir
                3. Mevcut durumu asses et
                4. Onerilen focus alanlarini belirle
                """,
                agent=analyst,
                expected_output="Ogrenci analiz raporu"
            )
            
            # Planning task
            planning_task = Task(
                description=f"""
                Ogrenci analiz raporu: {{analysis_task.output}}
                
                Bu rapora dayali olarak detayli calisma plani olustur:
                1. Haftalik calisma programi
                2. Gunluk ders dagilimi
                3. Zayif konulara ozel focus
                4. Deneme sinavi programi
                5. Motivasyon stratejileri
                6. Ilerleme takip metrikleri
                
                Plan 12 haftalik olsun ve uygulanabilir olsun.
                """,
                agent=coordinator,
                expected_output="Detayli calisma plani"
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
                "agents_used": ["Icerik Analisti", "Calisma Plani Koordinatoru"]
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
                Icerik: {content}
                Analiz Turu: {analysis_type}
                
                Bu icerigi kapsamli olarak analiz et:
                1. Zorluk seviyesi degerlendirmesi
                2. Mufredata uygunluk kontrolu
                3. Kavramsal dogruluk kontrolu
                4. Halusinasyon tespiti
                5. Ogrenci seviyesine uygunluk
                6. Iyilestirme onerileri
                7. Alternatif aciklama yontemleri
                
                Detayli analiz raporu hazirla.
                """,
                agent=analyst,
                expected_output="Kapsamli icerik analiz raporu"
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