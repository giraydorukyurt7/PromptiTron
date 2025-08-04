from typing import Dict, Any, List, Optional, Annotated, Sequence, TypedDict
from dataclasses import dataclass
import operator
import logging
import json
from enum import Enum

from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool, StructuredTool

from core.gemini_client import gemini_client
from core.rag_system import rag_system
from core.chains import UnifiedChains
from config import settings
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()

# Agent State Definition
class AgentState(TypedDict):
    messages: Annotated[Sequence[Dict[str, Any]], operator.add]
    current_task: str
    context: Dict[str, Any]
    results: Dict[str, Any]
    next_action: str
    expert: Optional[str]

# Expert Types
class ExpertType(str, Enum):
    MATH = "matematik"
    PHYSICS = "fizik"
    CHEMISTRY = "kimya"
    BIOLOGY = "biyoloji"
    TURKISH_LITERATURE = "turk_dili_ve_edebiyati"
    HISTORY = "tarih"
    GEOGRAPHY = "cografya"
    PHILOSOPHY = "felsefe"
    RELIGION = "din_kulturu"
    REVOLUTION = "inkilap_ve_ataturkculuk"
    GENERAL = "genel"
    METHODOLOGY = "metodoloji"

# Expert Configuration
@dataclass
class Expert:
    name: str
    type: ExpertType
    description: str
    system_instruction: str
    preferred_model: str = "flash"
    expertise_keywords: List[str] = None

# Agent Types
@dataclass
class AgentType:
    name: str
    description: str
    tools: List[Tool]
    system_prompt: str
    role: str
    goal: str
    backstory: str

class UnifiedAgentSystem:
    def __init__(self):
        pass
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            temperature=settings.TEMPERATURE,
            google_api_key=settings.GOOGLE_API_KEY
        )
        
        # Initialize chains
        self.chains = UnifiedChains()
        
        # Initialize experts
        self._initialize_experts()
        
        # Initialize tools
        self._initialize_tools()
        
        # Initialize agents
        self._initialize_agents()
        
        # Build workflow
        self.workflow = self._build_workflow()
        
        logger.info("Unified agent system initialized successfully")
        try:
            console.print("[cyan]Unified Agent System: Initialized successfully[/cyan]")
        except UnicodeEncodeError:
            print("Unified Agent System: Initialized successfully")
    
    def _initialize_experts(self):
        pass
        self.experts = {
            ExpertType.MATH: Expert(
                name="Matematik Uzmani",
                type=ExpertType.MATH,
                description="Matematik konularinda uzman",
                system_instruction="""Sen deneyimli bir matematik ogretmenisin. 
                YKS matematik mufredatina hakimsin. Konulari adim adim aciklar, 
                problem cozme stratejileri ogretirsin. RAG sistemini kullanarak 
                mufredat bilgilerini kontrol et ve ona uygun aciklamalar yap.""",
                expertise_keywords=["matematik", "geometri", "integral", "turev", "limit", "fonksiyon"]
            ),
            ExpertType.PHYSICS: Expert(
                name="Fizik Uzmani",
                type=ExpertType.PHYSICS,
                description="Fizik konularinda uzman",
                system_instruction="""Sen deneyimli bir fizik ogretmenisin.
                Fizik kavramlarini gunluk hayattan orneklerle aciklar,
                formulleri ve problem cozumlerini detayli anlatirsin.
                RAG sistemini kullanarak mufredat bilgilerini kontrol et.""",
                expertise_keywords=["fizik", "mekanik", "elektrik", "optik", "dalga", "atom"]
            ),
            ExpertType.CHEMISTRY: Expert(
                name="Kimya Uzmani",
                type=ExpertType.CHEMISTRY,
                description="Kimya konularinda uzman",
                system_instruction="""Sen deneyimli bir kimya ogretmenisin.
                Kimyasal kavramlari, reaksiyonlari ve hesaplamalari
                anlasilir sekilde aciklarsin. RAG sistemini kullanarak 
                mufredat bilgilerini kontrol et.""",
                expertise_keywords=["kimya", "atom", "periyodik", "reaksiyon", "mol", "asit", "baz"]
            ),
            ExpertType.BIOLOGY: Expert(
                name="Biyoloji Uzmani",
                type=ExpertType.BIOLOGY,
                description="Biyoloji konularinda uzman",
                system_instruction="""Sen deneyimli bir biyoloji ogretmenisin.
                Canlilar dunyasini, sistemleri ve surecleri
                gorsel betimlemelerle aciklarsin. RAG sistemini kullanarak 
                mufredat bilgilerini kontrol et.""",
                expertise_keywords=["biyoloji", "hucre", "genetik", "evrim", "ekoloji", "sistem"]
            ),
            ExpertType.TURKISH_LITERATURE: Expert(
                name="Turk Dili ve Edebiyati Uzmani",
                type=ExpertType.TURKISH_LITERATURE,
                description="Turk dili ve edebiyati uzmani",
                system_instruction="""Sen Turk Dili ve Edebiyati konusunda uzman bir ogretmensin.
                Turkce dil bilgisi kurallari, cumle yapilari, anlatim tekniklerinin yani sira
                Turk edebiyati, edebi akimlar, sairler, yazarlar, edebi turler ve donemler 
                hakkinda kapsamli bilgiye sahipsin. RAG sistemini kullanarak mufredat 
                bilgilerini kontrol et ve ogrencilere hem dil bilgisi hem de edebiyat 
                konularinda yardimci ol.""",
                expertise_keywords=["turkce", "turk dili", "edebiyat", "dil bilgisi", "siir", "roman", "oyku", "tiyatro", "makale", "cumhuriyet", "cumle", "anlam", "anlatim", "yazim"]
            ),
            ExpertType.HISTORY: Expert(
                name="Tarih Uzmani",
                type=ExpertType.HISTORY,
                description="Tarih konularinda uzman",
                system_instruction="""Sen tarih konusunda uzman bir ogretmensin.
                Turk tarihi, dunya tarihi, uygarliklar ve onemli olaylar hakkinda
                detayli bilgiye sahipsin. RAG sistemini kullanarak mufredat 
                bilgilerini kontrol et.""",
                expertise_keywords=["tarih", "osmanli", "selcuklu", "cumhuriyet", "uygarlik", "savas"]
            ),
            ExpertType.GEOGRAPHY: Expert(
                name="Cografya Uzmani",
                type=ExpertType.GEOGRAPHY,
                description="Cografya konularinda uzman",
                system_instruction="""Sen cografya konusunda uzman bir ogretmensin.
                Fiziki cografya, beseri cografya, Turkiye cografyasi ve dunya cografyasi
                konularinda kapsamli bilgiye sahipsin. RAG sistemini kullanarak 
                mufredat bilgilerini kontrol et.""",
                expertise_keywords=["cografya", "iklim", "toprak", "nufus", "goc", "sehir", "kita"]
            ),
            ExpertType.PHILOSOPHY: Expert(
                name="Felsefe Uzmani",
                type=ExpertType.PHILOSOPHY,
                description="Felsefe konularinda uzman",
                system_instruction="""Sen felsefe konusunda uzman bir ogretmensin.
                Mantik, etik, estetik, bilgi felsefesi ve Islam felsefesi konularinda
                derin bilgiye sahipsin. RAG sistemini kullanarak mufredat 
                bilgilerini kontrol et.""",
                expertise_keywords=["felsefe", "mantik", "etik", "estetik", "bilgi", "varlik", "deger"]
            ),
            ExpertType.RELIGION: Expert(
                name="Din Kulturu Uzmani",
                type=ExpertType.RELIGION,
                description="Din kulturu ve ahlak bilgisi uzmani",
                system_instruction="""Sen din kulturu ve ahlak bilgisi konusunda uzman bir ogretmensin.
                Islam tarihi, ibadetler, ahlak, din sosyolojisi konularinda bilgiye sahipsin.
                RAG sistemini kullanarak mufredat bilgilerini kontrol et.""",
                expertise_keywords=["din", "Islam", "ahlak", "ibadet", "peygamber", "kuran"]
            ),
            ExpertType.REVOLUTION: Expert(
                name="Inkilap ve Ataturkculuk Uzmani",
                type=ExpertType.REVOLUTION,
                description="T.C. Inkilap Tarihi ve Ataturkculuk uzmani",
                system_instruction="""Sen T.C. Inkilap Tarihi ve Ataturkculuk konusunda uzman bir ogretmensin.
                Milli Mucadele, Ataturk ilke ve inkilaplari, Cumhuriyet tarihi konularinda
                kapsamli bilgiye sahipsin. RAG sistemini kullanarak mufredat bilgilerini kontrol et.""",
                expertise_keywords=["inkilap", "ataturk", "ataturkculuk", "cumhuriyet", "milli mucadele", "reform"]
            ),
            ExpertType.METHODOLOGY: Expert(
                name="Ogretim Yontemleri Uzmani",
                type=ExpertType.METHODOLOGY,
                description="Egitim metodolojisi uzmani",
                system_instruction="""Sen egitim metodolojisi konusunda uzman bir ogretmensin.
                Ogretim yontemleri, olcme degerlendirme, egitim psikolojisi konularinda
                kapsamli bilgiye sahipsin. RAG sistemini kullanarak mufredat bilgilerini kontrol et.""",
                expertise_keywords=["metodoloji", "ogretim", "olcme", "degerlendirme", "egitim", "yontem"]
            ),
            ExpertType.GENERAL: Expert(
                name="Genel Egitim Uzmani",
                type=ExpertType.GENERAL,
                description="Genel egitim ve rehberlik uzmani",
                system_instruction="""Sen deneyimli bir egitim danismanisin.
                Calisma teknikleri, motivasyon ve genel akademik konularda yardimci olursun.
                RAG sistemini kullanarak tum mufredat bilgilerini kontrol edebilirsin.""",
                expertise_keywords=["calisma", "plan", "motivasyon", "strateji", "yks", "sinav"]
            )
        }
    
    def _initialize_tools(self):
        pass
        # RAG search tool
        self.search_tool = StructuredTool.from_function(
            func=self._search_knowledge_base,
            name="search_knowledge",
            description="Bilgi bankasinda arama yap"
        )
        
        # Quiz generation tool
        self.quiz_tool = StructuredTool.from_function(
            func=self._generate_quiz,
            name="generate_quiz",
            description="Quiz sorusu olustur"
        )
        
        # Concept explanation tool
        self.explain_tool = StructuredTool.from_function(
            func=self._explain_concept,
            name="explain_concept",
            description="Kavram aciklamasi yap"
        )
        
        # Study plan tool
        self.plan_tool = StructuredTool.from_function(
            func=self._create_study_plan,
            name="create_study_plan",
            description="Calisma plani olustur"
        )
        
        # Performance analysis tool
        self.analyze_tool = StructuredTool.from_function(
            func=self._analyze_performance,
            name="analyze_performance",
            description="Performans analizi yap"
        )
        
        # Mind map tool
        self.mindmap_tool = StructuredTool.from_function(
            func=self._create_mindmap,
            name="create_mindmap",
            description="Kavram haritasi olustur"
        )
        
        # All tools list
        self.all_tools = [
            self.search_tool,
            self.quiz_tool,
            self.explain_tool,
            self.plan_tool,
            self.analyze_tool,
            self.mindmap_tool
        ]
    
    def _initialize_agents(self):
        pass
        self.agents = {
            "tutor": AgentType(
                name="YKS Ogretmen",
                description="Sokratik yontemle ogreten egitim asistani",
                tools=[self.search_tool, self.explain_tool],
                system_prompt="""Sen deneyimli bir YKS ogretmenisin.
                Sokratik yontemle ogrencilere yardimci ol.""",
                role="Egitmen",
                goal="Ogrencilerin konulari derinlemesine anlamalarini saglamak",
                backstory="Yillarca ogrenci yetistirmis deneyimli bir egitmen"
            ),
            
            "content_creator": AgentType(
                name="Icerik Uretici",
                description="Egitim materyali ureten ajan",
                tools=[self.quiz_tool, self.mindmap_tool],
                system_prompt="""Sen YKS icerik uzmanisin.
                Kaliteli egitim materyalleri uret.""",
                role="Icerik Uzmani",
                goal="Etkili ogrenme materyalleri olusturmak",
                backstory="Egitim icerigi tasariminda uzman"
            ),
            
            "planner": AgentType(
                name="Calisma Planlayici",
                description="Kisisellestirilmis planlar olusturan ajan",
                tools=[self.plan_tool, self.search_tool],
                system_prompt="""Sen YKS calisma kocusun.
                Ogrencilere ozel planlar olustur.""",
                role="Calisma Kocu",
                goal="Etkili ve uygulanabilir calisma planlari olusturmak",
                backstory="Basarili ogrenciler yetistirmis deneyimli koc"
            ),
            
            "analyzer": AgentType(
                name="Performans Analizcisi",
                description="Ogrenci performansini analiz eden ajan",
                tools=[self.analyze_tool, self.search_tool],
                system_prompt="""Sen YKS performans uzmanisin.
                Detayli analizler ve oneriler sun.""",
                role="Performans Uzmani",
                goal="Ogrenci gelisimini optimize etmek",
                backstory="Veri analizi ve ogrenci degerlendirmede uzman"
            )
        }
    
    def _build_workflow(self) -> StateGraph:
        pass
        workflow = StateGraph(AgentState)
        
        # Define nodes
        workflow.add_node("router", self._route_request)
        workflow.add_node("expert_selector", self._select_expert)
        workflow.add_node("tutor", self._run_tutor_agent)
        workflow.add_node("content_creator", self._run_content_creator)
        workflow.add_node("planner", self._run_planner)
        workflow.add_node("analyzer", self._run_analyzer)
        workflow.add_node("expert_handler", self._run_expert)
        workflow.add_node("finalizer", self._finalize_response)
        
        # Define edges
        workflow.set_entry_point("router")
        
        # Routing logic
        workflow.add_conditional_edges(
            "router",
            self._determine_next_node,
            {
                "expert_selector": "expert_selector",
                "tutor": "tutor",
                "content_creator": "content_creator",
                "planner": "planner",
                "analyzer": "analyzer",
                "end": END
            }
        )
        
        # Expert selection to handler
        workflow.add_edge("expert_selector", "expert_handler")
        
        # All paths lead to finalizer
        workflow.add_edge("tutor", "finalizer")
        workflow.add_edge("content_creator", "finalizer")
        workflow.add_edge("planner", "finalizer")
        workflow.add_edge("analyzer", "finalizer")
        workflow.add_edge("expert_handler", "finalizer")
        workflow.add_edge("finalizer", END)
        
        return workflow.compile()
    
    async def _route_request(self, state: AgentState) -> AgentState:
        pass
        user_message = state["messages"][-1]["content"]
        
        # Check if subject-specific (needs expert)
        subject_keywords = []
        for expert in self.experts.values():
            if expert.expertise_keywords:
                subject_keywords.extend(expert.expertise_keywords)
        
        message_lower = user_message.lower()
        needs_expert = any(keyword in message_lower for keyword in subject_keywords)
        
        if needs_expert:
            state["next_action"] = "expert_selector"
        else:
            # Determine agent type
            if any(word in message_lower for word in ["test", "soru", "quiz"]):
                state["current_task"] = "content_creator"
            elif any(word in message_lower for word in ["plan", "program", "calisma"]):
                state["current_task"] = "planner"
            elif any(word in message_lower for word in ["analiz", "performans", "basari"]):
                state["current_task"] = "analyzer"
            else:
                state["current_task"] = "tutor"
        
        return state
    
    def _determine_next_node(self, state: AgentState) -> str:
        pass
        next_action = state.get("next_action")
        if next_action:
            return next_action
        
        task = state.get("current_task", "tutor")
        return task if task in self.agents else "tutor"
    
    def _classify_query_advanced(self, query: str, context: Dict[str, Any] = None) -> str:
        pass
        query_lower = query.lower()
        
        # Enhanced keyword sets from CrewAI
        classification_map = {
            ExpertType.MATH: [
                "matematik", "math", "sayi", "hesap", "turev", "integral", "geometri", 
                "trigonometri", "logaritma", "fonksiyon", "denklem", "grafik", "limit",
                "olasilik", "istatistik", "matris", "cebirsel", "koordinat", "aci"
            ],
            ExpertType.PHYSICS: [
                "fizik", "physics", "kuvvet", "hareket", "enerji", "elektrik", "manyetik",
                "dalga", "isik", "ses", "basinc", "sicaklik", "atom", "cekim", "momentum",
                "kinetik", "potansiyel", "newton", "ohm", "volt", "joule"
            ],
            ExpertType.CHEMISTRY: [
                "kimya", "chemistry", "element", "bilesik", "reaksiyon", "asit", "baz",
                "mol", "orbital", "bag", "cozelti", "kataliz", "organik", "periyodik",
                "elektron", "proton", "notron", "iyonik", "kovalent"
            ],
            ExpertType.BIOLOGY: [
                "biyoloji", "biology", "hucre", "dna", "gen", "protein", "enzim",
                "fotosentez", "solunum", "dolasim", "sinir", "hormon", "ekosistem",
                "mitoz", "mayoz", "kalitim", "adaptasyon", "evrim"
            ],
            ExpertType.TURKISH_LITERATURE: [
                "turkce", "edebiyat", "siir", "roman", "hikaye", "dil", "gramer",
                "anlam", "sozcuk", "cumle", "metin", "yazar", "sair", "edebi"
            ],
            ExpertType.HISTORY: [
                "tarih", "history", "osmanli", "selcuklu", "cumhuriyet", "savas",
                "devlet", "sultan", "padisah", "millet", "medeniyet", "kultur"
            ],
            ExpertType.GEOGRAPHY: [
                "cografya", "geography", "iklim", "harita", "kita", "ulke", "sehir",
                "nufus", "ekonomi", "dogal", "kaynak", "jeoloji", "toprak"
            ],
            ExpertType.PHILOSOPHY: [
                "felsefe", "philosophy", "dusunce", "mantik", "ahlak", "varlik",
                "bilgi", "dogruluk", "guzellik", "adalet", "ozgurluk"
            ],
            ExpertType.RELIGION: [
                "din", "islam", "kuran", "peygamber", "namaz", "oruc", "hac",
                "zakat", "ibadet", "ahlak", "iman", "allah"
            ],
            ExpertType.REVOLUTION: [
                "inkilap", "ataturk", "ataturkculuk", "cumhuriyet", "milli mucadele",
                "reform", "modernlesme", "laik", "milliyetci"
            ]
        }
        
        # Context-based classification
        if context:
            subject = context.get("subject", "").lower()
            for expert_type, keywords in classification_map.items():
                if any(keyword in subject for keyword in keywords):
                    return expert_type.value
        
        # Multi-level keyword matching with scoring
        expert_scores = {}
        
        for expert_type, keywords in classification_map.items():
            score = 0
            for keyword in keywords:
                if keyword in query_lower:
                    # Primary keywords get higher scores
                    if keyword in ["matematik", "fizik", "kimya", "biyoloji", "turkce", "tarih", "cografya", "felsefe"]:
                        score += 5
                    # Secondary keywords
                    elif len(keyword) > 3:  # Longer, more specific keywords
                        score += 3
                    else:
                        score += 1
            
            if score > 0:
                expert_scores[expert_type] = score
        
        # Return highest scoring expert
        if expert_scores:
            best_expert = max(expert_scores.items(), key=lambda x: x[1])
            return best_expert[0].value
        
        # Fallback patterns
        study_keywords = ["plan", "calisma", "program", "takvim", "strateji", "hedef", "zaman"]
        if any(keyword in query_lower for keyword in study_keywords):
            return ExpertType.GENERAL.value
        
        return ExpertType.GENERAL.value

    async def _select_expert(self, state: AgentState) -> AgentState:
        pass
        user_message = state["messages"][-1]["content"]
        context = state.get("context", {})
        
        # Use advanced classification
        expert_type_str = self._classify_query_advanced(user_message, context)
        
        # Convert string back to enum
        selected_expert = None
        for expert_type, expert in self.experts.items():
            if expert_type.value == expert_type_str:
                selected_expert = expert_type
                break
        
        if not selected_expert:
            selected_expert = ExpertType.GENERAL
        
        # Enhanced scoring with context awareness
        expert_scores = {}
        for expert_type, expert in self.experts.items():
            score = 0
            if expert.expertise_keywords:
                for keyword in expert.expertise_keywords:
                    if keyword in user_message.lower():
                        score += 1
            expert_scores[expert_type] = score
        
        # Select expert with highest score
        selected_expert = max(expert_scores, key=expert_scores.get)
        if expert_scores[selected_expert] == 0:
            selected_expert = ExpertType.GENERAL
        
        state["expert"] = selected_expert
        return state
    
    async def _run_expert(self, state: AgentState) -> AgentState:
        pass
        expert_type = state.get("expert", ExpertType.GENERAL)
        expert = self.experts[expert_type]
        user_message = state["messages"][-1]["content"]
        
        # Get context from RAG
        context_docs = await rag_system.search(
            query=user_message,
            n_results=3
        )
        
        # Build RAG context
        rag_context = "\n".join([doc["content"] for doc in context_docs])
        
        # Get curriculum context for the expert's subject
        curriculum_context = ""
        try:
            from core.curriculum_loader import curriculum_loader
            
            # Map expert type to curriculum subject
            subject_mapping = {
                ExpertType.MATH: "Matematik",
                ExpertType.PHYSICS: "Fizik", 
                ExpertType.CHEMISTRY: "Kimya",
                ExpertType.BIOLOGY: "Biyoloji",
                ExpertType.TURKISH_LITERATURE: "Turk Dili ve Edebiyati",
                ExpertType.HISTORY: "Tarih",
                ExpertType.GEOGRAPHY: "Cografya",
                ExpertType.PHILOSOPHY: "Felsefe",
                ExpertType.RELIGION: "Din Kulturu",
                ExpertType.REVOLUTION: "Inkilap ve Ataturkculuk"
            }
            
            if expert_type in subject_mapping:
                subject_name = subject_mapping[expert_type]
                curriculum_topics = curriculum_loader.get_subject_topics(subject_name)
                
                if curriculum_topics:
                    # Get relevant curriculum topics
                    relevant_topics = []
                    for topic in curriculum_topics[:10]:  # Limit to first 10 topics
                        relevant_topics.append(f"- {topic.get('title', '')}: {topic.get('content', '')[:200]}...")
                    
                    curriculum_context = f"\n\nMufredat Bilgisi ({subject_name}):\n" + "\n".join(relevant_topics)
                    
        except Exception as e:
            logger.error(f"Error getting curriculum context: {e}")
        
        # Enhanced context with both RAG and curriculum data
        full_context = f"RAG Baglami: {rag_context}{curriculum_context}"
        
        # Generate expert response
        response = await gemini_client.generate_content(
            prompt=f"Baglam: {full_context}\n\nSoru: {user_message}",
            system_instruction=expert.system_instruction,
            model_name=expert.preferred_model
        )
        
        state["results"]["expert_response"] = {
            "response": response["text"],
            "expert": expert.name,
            "type": expert.type.value,
            "curriculum_topics_used": len(curriculum_context.split('\n')) - 2 if curriculum_context else 0
        }
        
        return state
    
    async def _run_tutor_agent(self, state: AgentState) -> AgentState:
        pass
        user_message = state["messages"][-1]["content"]
        
        # Get context
        context = await self._search_knowledge_base(user_message)
        
        # Generate Socratic response
        response = await self.chains.socratic_response(
            user_input=user_message,
            context=context
        )
        
        state["results"]["tutor_response"] = response
        return state
    
    async def _run_content_creator(self, state: AgentState) -> AgentState:
        pass
        user_message = state["messages"][-1]["content"]
        
        # Determine content type
        if "test" in user_message.lower() or "soru" in user_message.lower():
            topic = self._extract_topic(user_message)
            content = await self._generate_quiz(topic)
        elif "harita" in user_message.lower():
            topic = self._extract_topic(user_message)
            content = await self._create_mindmap(topic)
        else:
            content = await self._explain_concept(user_message)
        
        state["results"]["content"] = content
        return state
    
    async def _run_planner(self, state: AgentState) -> AgentState:
        pass
        student_info = state.get("context", {}).get("student_info", {
            "target_exam": "YKS",
            "remaining_days": 180,
            "daily_hours": 6
        })
        
        plan = await self._create_study_plan(student_info)
        state["results"]["study_plan"] = plan
        return state
    
    async def _run_analyzer(self, state: AgentState) -> AgentState:
        pass
        performance_data = state.get("context", {}).get("performance_data", {})
        
        analysis = await self._analyze_performance(performance_data)
        state["results"]["analysis"] = analysis
        return state
    
    async def _finalize_response(self, state: AgentState) -> AgentState:
        pass
        results = state.get("results", {})
        
        # Combine all results
        final_response = []
        
        # Add expert response if available
        if "expert_response" in results:
            expert_info = results["expert_response"]
            response = expert_info["response"]
            expert_name = expert_info["expert"]
            final_response.append(f"{response}\n\n---\n*{expert_name} tarafindan saglanmistir*")
        
        # Add other responses
        for key, value in results.items():
            if key != "expert_response" and value:
                final_response.append(str(value))
        
        # Create final message
        state["messages"].append({
            "role": "assistant",
            "content": "\n\n".join(final_response) if final_response else "Uzgunum, bir yanit olusturamadim."
        })
        
        return state
    
    # Tool implementation methods
    async def _search_knowledge_base(self, query: str, filters: Optional[Dict] = None) -> str:
        pass
        results = await rag_system.search(query, n_results=3, filter_metadata=filters)
        
        if not results:
            return "Ilgili bilgi bulunamadi."
        
        formatted_results = []
        for result in results:
            formatted_results.append(f"- {result['content']}")
        
        return "\n".join(formatted_results)
    
    async def _generate_quiz(self, topic: str, count: int = 5, difficulty: str = "orta") -> str:
        pass
        questions = []
        for i in range(count):
            question = await self.chains.generate_quiz_question({
                "exam_type": "TYT/AYT",
                "subject": topic.split("-")[0] if "-" in topic else topic,
                "topic": topic,
                "difficulty": difficulty
            })
            questions.append(question.dict())
        
        return json.dumps(questions, ensure_ascii=False, indent=2)
    
    async def _explain_concept(self, concept: str, style: str = "detailed") -> str:
        pass
        return await self.chains.explain_concept({
            "subject": concept.split("-")[0] if "-" in concept else "Genel",
            "topic": concept,
            "style": style,
            "detail_level": "high" if style == "detailed" else "medium"
        })
    
    async def _create_study_plan(self, student_info: Dict[str, Any]) -> str:
        pass
        plan = await self.chains.generate_study_plan(student_info)
        return json.dumps(plan.dict(), ensure_ascii=False, indent=2)
    
    async def _analyze_performance(self, performance_data: Dict[str, Any]) -> str:
        pass
        if not performance_data:
            return "Analiz icin yeterli veri bulunmuyor."
        
        # Generate analysis using AI
        prompt = f"Ogrenci performans verilerini analiz et:\n{json.dumps(performance_data, ensure_ascii=False, indent=2)}\n\nDetayli analiz sun:\n1. Guclu yonler\n2. Gelistirilmesi gereken alanlar\n3. Oneriler"
        
        # Return the analysis prompt for now
        return prompt
        
    async def _create_mindmap(self, topic: str) -> str:
        pass
        concept_map = await self.chains.generate_concept_map({
            "subject": topic.split("-")[0] if "-" in topic else "Genel",
            "topic": topic
        })
        return json.dumps(concept_map.dict(), ensure_ascii=False, indent=2)
    
    def _extract_topic(self, message: str) -> str:
        pass
        keywords = ["matematik", "fizik", "kimya", "biyoloji", "geometri", "turkce"]
        message_lower = message.lower()
        
        for keyword in keywords:
            if keyword in message_lower:
                return keyword
        
        return "genel"
    
    async def process_message(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        pass
        try:
            # Log agent activity
            console.print(f"[cyan]Agent System: Processing message - Starting unified agent workflow[/cyan]")
            
            # Create initial state
            initial_state = AgentState(
                messages=[{"role": "user", "content": message}],
                current_task="",
                context=context or {},
                results={},
                next_action="",
                expert=None
            )
            
            # Run workflow
            console.print(f"[cyan]Agent System: Invoking LangGraph workflow[/cyan]")
            final_state = await self.workflow.ainvoke(initial_state)
            
            # Extract response
            assistant_message = final_state["messages"][-1]
            
            # Determine which system was used
            system_used = "unified"
            if final_state.get("expert"):
                system_used = f"expert_{final_state['expert']}"
                console.print(f"[cyan]Agent System: Expert agent used - {final_state['expert']}[/cyan]")
            elif final_state.get("current_task"):
                system_used = f"agent_{final_state['current_task']}"
                console.print(f"[cyan]Agent System: Task agent used - {final_state['current_task']}[/cyan]")
            
            return {
                "response": assistant_message["content"],
                "success": True,
                "system_used": system_used,
                "metadata": {
                    "expert": final_state.get("expert"),
                    "agent": final_state.get("current_task"),
                    "session_id": session_id
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "response": "Uzgunum, bir hata olustu. Lutfen tekrar deneyin.",
                "success": False,
                "error": str(e),
                "system_used": "error"
            }
    
    async def collaborative_response(
        self,
        query: str,
        expert_types: List[ExpertType] = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        pass
        try:
            if not expert_types:
                # Auto-select relevant experts based on query
                primary_expert = self._classify_query_advanced(query, context)
                expert_types = [ExpertType(primary_expert)]
                
                # Add complementary experts for complex queries
                if any(word in query.lower() for word in ["karsilastir", "fark", "benzer", "iliski"]):
                    # Add related experts for comparison queries
                    if ExpertType.MATH.value == primary_expert and ExpertType.PHYSICS not in expert_types:
                        expert_types.append(ExpertType.PHYSICS)
                    elif ExpertType.CHEMISTRY.value == primary_expert and ExpertType.BIOLOGY not in expert_types:
                        expert_types.append(ExpertType.BIOLOGY)
            
            # Limit to max 3 experts for performance
            expert_types = expert_types[:3]
            
            # Get responses from each expert
            expert_responses = []
            for expert_type in expert_types:
                if expert_type in self.experts:
                    response = await self._get_expert_response(expert_type, query, context)
                    expert_responses.append({
                        "expert": expert_type.value,
                        "response": response,
                        "confidence": self._calculate_response_confidence(response, expert_type, query)
                    })
            
            # Synthesize responses
            if len(expert_responses) == 1:
                return {
                    "response": expert_responses[0]["response"],
                    "expert_used": expert_responses[0]["expert"],
                    "confidence": expert_responses[0]["confidence"],
                    "collaboration": False
                }
            else:
                synthesized = await self._synthesize_expert_responses(expert_responses, query)
                return {
                    "response": synthesized["response"],
                    "experts_consulted": [er["expert"] for er in expert_responses],
                    "individual_responses": expert_responses,
                    "synthesis_confidence": synthesized["confidence"],
                    "collaboration": True
                }
                
        except Exception as e:
            logger.error(f"Error in collaborative response: {e}")
            return await self.process_message(query, context)  # Fallback to regular processing
    
    async def _get_expert_response(
        self, 
        expert_type: ExpertType, 
        query: str, 
        context: Dict[str, Any] = None
    ) -> str:
        pass
        try:
            expert = self.experts[expert_type]
            
            # Get relevant context
            rag_results = await rag_system.search(query, n_results=2)
            rag_context = "\n".join([doc["content"] for doc in rag_results])
            
            # Build enhanced prompt
            prompt = f"Soru: {query}\n\nBaglam Bilgiler:\n{rag_context}\n\nLutfen {expert.name} perspektifinden yanitla."
            
            response = await gemini_client.generate_content(
                prompt=prompt,
                system_instruction=expert.system_instruction
            )
            
            return response.get("text", "Yanit olusturulamadi.")
            
        except Exception as e:
            logger.error(f"Error getting expert response: {e}")
            return f"Uzgunum, {expert_type.value} uzmanindan yanit alinamadi."
    
    def _calculate_response_confidence(
        self, 
        response: str, 
        expert_type: ExpertType, 
        query: str
    ) -> float:
        pass
        try:
            confidence = 0.5  # Base confidence
            
            # Length-based confidence (longer responses generally more detailed)
            if len(response) > 200:
                confidence += 0.1
            if len(response) > 500:
                confidence += 0.1
            
            # Keyword alignment confidence
            expert_keywords = self.experts[expert_type].expertise_keywords or []
            keyword_matches = sum(1 for keyword in expert_keywords if keyword in query.lower())
            if keyword_matches > 0:
                confidence += min(keyword_matches * 0.1, 0.3)
            
            # Specific indicators in response
            if any(indicator in response.lower() for indicator in ["ornegin", "soyle ki", "cunku", "nedeni"]):
                confidence += 0.1
            
            return min(confidence, 1.0)
            
        except Exception:
            return 0.5
    
    async def _synthesize_expert_responses(
        self, 
        expert_responses: List[Dict], 
        query: str
    ) -> Dict[str, Any]:
        pass
        try:
            # Prepare synthesis prompt
            expert_texts = []
            for i, er in enumerate(expert_responses):
                expert_texts.append(f"{er['expert'].title()} Uzmani ({er['confidence']:.2f} guven):\n{er['response']}")
            
            combined_responses = "\n\n---\n\n".join(expert_texts)
            
            synthesis_prompt = f"Asagidaki uzman goruslerini sentezleyerek tutarli ve kapsamli bir yanit olustur:\n\nSoru: {query}\n\nUzman Gorusleri:\n{combined_responses}\n\nSentez kurallari:\n1. Uzmanlarin ortak noktalarini vurgula\n2. Farkli perspektifleri dengele\n3. Celiskiler varsa acikla\n4. Kapsamli ama oz bir yanit ver\n5. Her uzmanin katkisini belirt"
            
            response = await gemini_client.generate_content(synthesis_prompt)
            
            return {
                "synthesized_response": response.get("text", "Sentez yapilamadi"),
                "expert_count": len(expert_responses),
                "confidence": sum(er["confidence"] for er in expert_responses) / len(expert_responses)
            }
            
        except Exception as e:
            logger.error(f"Error synthesizing expert responses: {e}")
            return {
                "synthesized_response": "Uzman yanitlari sentezlenemedi",
                "expert_count": len(expert_responses),
                "confidence": 0.3
            }

# Global instance
agent_system = UnifiedAgentSystem()
