"""
Unified Agent System combining LangGraph, Crew AI, and Expert Router
Provides comprehensive educational AI agent capabilities
"""

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
from core.web_analyzer import web_analyzer
from core.youtube_analyzer import youtube_analyzer
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
    WEB_ANALYZER = "web_analizi"
    YOUTUBE_ANALYZER = "youtube_analizi"

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
        """Initialize unified agent system with all capabilities and lazy loading"""
        # Check if system is already initialized from cache
        self._initialized = False
        
        # Initialize LLM only when needed
        self._llm = None
        self._chains = None
        self._workflow = None
        
        # Initialize experts (lightweight)
        self._initialize_experts()
        
        # Initialize tools only when needed
        self._tools_initialized = False
        
        # Initialize agents only when needed
        self._agents_initialized = False
        
        logger.info("Unified agent system prepared for lazy initialization")
        try:
            console.print("[cyan]Unified Agent System: Prepared with lazy loading[/cyan]")
        except UnicodeEncodeError:
            print("Unified Agent System: Prepared with lazy loading")
    
    @property
    def llm(self):
        """Lazy load LLM"""
        if self._llm is None:
            logger.info("Initializing LLM...")
            self._llm = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                temperature=settings.TEMPERATURE,
                google_api_key=settings.GOOGLE_API_KEY
            )
        return self._llm
    
    @property 
    def chains(self):
        """Lazy load chains"""
        if self._chains is None:
            logger.info("Initializing chains...")
            self._chains = UnifiedChains()
        return self._chains
    
    @property
    def workflow(self):
        """Lazy load workflow"""
        if self._workflow is None:
            logger.info("Building workflow...")
            self._ensure_tools_initialized()
            self._ensure_agents_initialized()
            self._workflow = self._build_workflow()
        return self._workflow
    
    def _ensure_tools_initialized(self):
        """Ensure tools are initialized"""
        if not self._tools_initialized:
            logger.info("Initializing tools...")
            self._initialize_tools()
            self._tools_initialized = True
    
    def _ensure_agents_initialized(self):
        """Ensure agents are initialized"""
        if not self._agents_initialized:
            logger.info("Initializing agents...")
            self._ensure_tools_initialized()
            self._initialize_agents()
            self._agents_initialized = True
            
    def initialize_if_needed(self):
        """Initialize system components if not already done"""
        if not self._initialized:
            logger.info("Full system initialization...")
            self._ensure_tools_initialized()
            self._ensure_agents_initialized()
            # Trigger workflow property to build it
            _ = self.workflow
            self._initialized = True
            logger.info("Unified agent system fully initialized")
            try:
                console.print("[cyan]Unified Agent System: Fully initialized[/cyan]")
            except UnicodeEncodeError:
                print("Unified Agent System: Fully initialized")
    
    def _initialize_experts(self):
        """Initialize subject matter experts"""
        self.experts = {
            ExpertType.MATH: Expert(
                name="Matematik Uzmanı",
                type=ExpertType.MATH,
                description="Matematik konularında uzman",
                system_instruction="""Sen deneyimli bir matematik öğretmenisin. 
                YKS matematik müfredatına hakimsin. Konuları adım adım açıklar, 
                problem çözme stratejileri öğretirsin. RAG sistemini kullanarak 
                müfredat bilgilerini kontrol et ve ona uygun açıklamalar yap.""",
                expertise_keywords=["matematik", "geometri", "integral", "türev", "limit", "fonksiyon"]
            ),
            ExpertType.PHYSICS: Expert(
                name="Fizik Uzmanı",
                type=ExpertType.PHYSICS,
                description="Fizik konularında uzman",
                system_instruction="""Sen deneyimli bir fizik öğretmenisin.
                Fizik kavramlarını günlük hayattan örneklerle açıklar,
                formülleri ve problem çözümlerini detaylı anlatırsın.
                RAG sistemini kullanarak müfredat bilgilerini kontrol et.""",
                expertise_keywords=["fizik", "mekanik", "elektrik", "optik", "dalga", "atom"]
            ),
            ExpertType.CHEMISTRY: Expert(
                name="Kimya Uzmanı",
                type=ExpertType.CHEMISTRY,
                description="Kimya konularında uzman",
                system_instruction="""Sen deneyimli bir kimya öğretmenisin.
                Kimyasal kavramları, reaksiyonları ve hesaplamaları
                anlaşılır şekilde açıklarsın. RAG sistemini kullanarak 
                müfredat bilgilerini kontrol et.""",
                expertise_keywords=["kimya", "atom", "periyodik", "reaksiyon", "mol", "asit", "baz"]
            ),
            ExpertType.BIOLOGY: Expert(
                name="Biyoloji Uzmanı",
                type=ExpertType.BIOLOGY,
                description="Biyoloji konularında uzman",
                system_instruction="""Sen deneyimli bir biyoloji öğretmenisin.
                Canlılar dünyasını, sistemleri ve süreçleri
                görsel betimlemelerle açıklarsın. RAG sistemini kullanarak 
                müfredat bilgilerini kontrol et.""",
                expertise_keywords=["biyoloji", "hücre", "genetik", "evrim", "ekoloji", "sistem"]
            ),
            ExpertType.TURKISH_LITERATURE: Expert(
                name="Türk Dili ve Edebiyatı Uzmanı",
                type=ExpertType.TURKISH_LITERATURE,
                description="Türk dili ve edebiyatı uzmanı",
                system_instruction="""Sen Türk Dili ve Edebiyatı konusunda uzman bir öğretmensin.
                Türkçe dil bilgisi kuralları, cümle yapıları, anlatım tekniklerinin yanı sıra
                Türk edebiyatı, edebi akımlar, şairler, yazarlar, edebi türler ve dönemler 
                hakkında kapsamlı bilgiye sahipsin. RAG sistemini kullanarak müfredat 
                bilgilerini kontrol et ve öğrencilere hem dil bilgisi hem de edebiyat 
                konularında yardımcı ol.""",
                expertise_keywords=["türkçe", "türk dili", "edebiyat", "dil bilgisi", "şiir", "roman", "öykü", "tiyatro", "makale", "cumhuriyet", "cümle", "anlam", "anlatım", "yazım"]
            ),
            ExpertType.HISTORY: Expert(
                name="Tarih Uzmanı",
                type=ExpertType.HISTORY,
                description="Tarih konularında uzman",
                system_instruction="""Sen tarih konusunda uzman bir öğretmensin.
                Türk tarihi, dünya tarihi, uygarlıklar ve önemli olaylar hakkında
                detaylı bilgiye sahipsin. RAG sistemini kullanarak müfredat 
                bilgilerini kontrol et.""",
                expertise_keywords=["tarih", "osmanlı", "selçuklu", "cumhuriyet", "uygarlık", "savaş"]
            ),
            ExpertType.GEOGRAPHY: Expert(
                name="Coğrafya Uzmanı",
                type=ExpertType.GEOGRAPHY,
                description="Coğrafya konularında uzman",
                system_instruction="""Sen coğrafya konusunda uzman bir öğretmensin.
                Fiziki coğrafya, beşeri coğrafya, Türkiye coğrafyası ve dünya coğrafyası
                konularında kapsamlı bilgiye sahipsin. RAG sistemini kullanarak 
                müfredat bilgilerini kontrol et.""",
                expertise_keywords=["coğrafya", "iklim", "toprak", "nüfus", "göç", "şehir", "kıta"]
            ),
            ExpertType.PHILOSOPHY: Expert(
                name="Felsefe Uzmanı",
                type=ExpertType.PHILOSOPHY,
                description="Felsefe konularında uzman",
                system_instruction="""Sen felsefe konusunda uzman bir öğretmensin.
                Mantık, etik, estetik, bilgi felsefesi ve İslam felsefesi konularında
                derin bilgiye sahipsin. RAG sistemini kullanarak müfredat 
                bilgilerini kontrol et.""",
                expertise_keywords=["felsefe", "mantık", "etik", "estetik", "bilgi", "varlık", "değer"]
            ),
            ExpertType.RELIGION: Expert(
                name="Din Kültürü Uzmanı",
                type=ExpertType.RELIGION,
                description="Din kültürü ve ahlak bilgisi uzmanı",
                system_instruction="""Sen din kültürü ve ahlak bilgisi konusunda uzman bir öğretmensin.
                İslam tarihi, ibadetler, ahlak, din sosyolojisi konularında bilgiye sahipsin.
                RAG sistemini kullanarak müfredat bilgilerini kontrol et.""",
                expertise_keywords=["din", "İslam", "ahlak", "ibadet", "peygamber", "kuran"]
            ),
            ExpertType.REVOLUTION: Expert(
                name="İnkılap ve Atatürkçülük Uzmanı",
                type=ExpertType.REVOLUTION,
                description="T.C. İnkılap Tarihi ve Atatürkçülük uzmanı",
                system_instruction="""Sen T.C. İnkılap Tarihi ve Atatürkçülük konusunda uzman bir öğretmensin.
                Milli Mücadele, Atatürk ilke ve inkılapları, Cumhuriyet tarihi konularında
                kapsamlı bilgiye sahipsin. RAG sistemini kullanarak müfredat bilgilerini kontrol et.""",
                expertise_keywords=["inkılap", "atatürk", "atatürkçülük", "cumhuriyet", "milli mücadele", "reform"]
            ),
            ExpertType.METHODOLOGY: Expert(
                name="Öğretim Yöntemleri Uzmanı",
                type=ExpertType.METHODOLOGY,
                description="Eğitim metodolojisi uzmanı",
                system_instruction="""Sen eğitim metodolojisi konusunda uzman bir öğretmensin.
                Öğretim yöntemleri, ölçme değerlendirme, eğitim psikolojisi konularında
                kapsamlı bilgiye sahipsin. RAG sistemini kullanarak müfredat bilgilerini kontrol et.""",
                expertise_keywords=["metodoloji", "öğretim", "ölçme", "değerlendirme", "eğitim", "yöntem"]
            ),
            ExpertType.GENERAL: Expert(
                name="Genel Eğitim Uzmanı",
                type=ExpertType.GENERAL,
                description="Genel eğitim ve rehberlik uzmanı",
                system_instruction="""Sen deneyimli bir eğitim danışmanısın.
                Çalışma teknikleri, motivasyon ve genel akademik konularda yardımcı olursun.
                RAG sistemini kullanarak tüm müfredat bilgilerini kontrol edebilirsin.""",
                expertise_keywords=["çalışma", "plan", "motivasyon", "strateji", "yks", "sınav"]
            ),
            ExpertType.WEB_ANALYZER: Expert(
                name="Web İçerik Analiz Uzmanı",
                type=ExpertType.WEB_ANALYZER,
                description="Web sitesi içerik analizi ve YKS uygunluk kontrolü uzmanı",
                system_instruction="""Sen web sitesi içerik analizi uzmanısın.
                Web sayfalarındaki metinleri ve görselleri YKS müfredatına uygunluk açısından değerlendirirsin.
                Eğitim değeri olan içerikleri tespit edip, diğer dokümanlarla aynı analizleri yaparsın.
                İçerik YKS dersleri ile ilgili değilse red edersin.""",
                expertise_keywords=["web", "site", "url", "link", "internet", "sayfa", "online"]
            ),
            ExpertType.YOUTUBE_ANALYZER: Expert(
                name="YouTube Video Analiz Uzmanı",
                type=ExpertType.YOUTUBE_ANALYZER,
                description="YouTube video transkript ve içerik analizi uzmanı",
                system_instruction="""Sen YouTube video analizi uzmanısın.
                YouTube videolarını transkribe eder, YKS müfredatına uygunluk açısından değerlendirirsin.
                Video içeriklerini eğitim değeri açısından analiz eder, soru çıkarır ve çalışma materyali hazırlarsın.
                Görsel ve ses içeriklerini birleştirerek kapsamlı eğitim analizi yaparsın.""",
                expertise_keywords=["youtube", "video", "transkript", "görsel", "ses", "multimedia", "izle"]
            )
        }
    
    def _initialize_tools(self):
        """Initialize all available tools"""
        # RAG search tool
        self.search_tool = StructuredTool.from_function(
            func=self._search_knowledge_base,
            name="search_knowledge",
            description="Bilgi bankasında arama yap"
        )
        
        # Quiz generation tool
        self.quiz_tool = StructuredTool.from_function(
            func=self._generate_quiz,
            name="generate_quiz",
            description="Quiz sorusu oluştur"
        )
        
        # Concept explanation tool
        self.explain_tool = StructuredTool.from_function(
            func=self._explain_concept,
            name="explain_concept",
            description="Kavram açıklaması yap"
        )
        
        # Study plan tool
        self.plan_tool = StructuredTool.from_function(
            func=self._create_study_plan,
            name="create_study_plan",
            description="Çalışma planı oluştur"
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
            description="Kavram haritası oluştur"
        )
        
        # Web analysis tool
        self.web_analysis_tool = StructuredTool.from_function(
            func=self._analyze_website,
            name="analyze_website",
            description="Web sitesi içeriği analiz et"
        )
        
        # YouTube analysis tool
        self.youtube_analysis_tool = StructuredTool.from_function(
            func=self._analyze_youtube_video,
            name="analyze_youtube_video",
            description="YouTube video analiz et"
        )
        
        # All tools list
        self.all_tools = [
            self.search_tool,
            self.quiz_tool,
            self.explain_tool,
            self.plan_tool,
            self.analyze_tool,
            self.mindmap_tool,
            self.web_analysis_tool,
            self.youtube_analysis_tool
        ]
    
    def _initialize_agents(self):
        """Initialize specialized agents"""
        self.agents = {
            "tutor": AgentType(
                name="YKS Öğretmen",
                description="Sokratik yöntemle öğreten eğitim asistanı",
                tools=[self.search_tool, self.explain_tool],
                system_prompt="""Sen deneyimli bir YKS öğretmenisin.
                Sokratik yöntemle öğrencilere yardımcı ol.""",
                role="Eğitmen",
                goal="Öğrencilerin konuları derinlemesine anlamalarını sağlamak",
                backstory="Yıllarca öğrenci yetiştirmiş deneyimli bir eğitmen"
            ),
            
            "content_creator": AgentType(
                name="İçerik Üretici",
                description="Eğitim materyali üreten ajan",
                tools=[self.quiz_tool, self.mindmap_tool],
                system_prompt="""Sen YKS içerik uzmanısın.
                Kaliteli eğitim materyalleri üret.""",
                role="İçerik Uzmanı",
                goal="Etkili öğrenme materyalleri oluşturmak",
                backstory="Eğitim içeriği tasarımında uzman"
            ),
            
            "planner": AgentType(
                name="Çalışma Planlayıcı",
                description="Kişiselleştirilmiş planlar oluşturan ajan",
                tools=[self.plan_tool, self.search_tool],
                system_prompt="""Sen YKS çalışma koçusun.
                Öğrencilere özel planlar oluştur.""",
                role="Çalışma Koçu",
                goal="Etkili ve uygulanabilir çalışma planları oluşturmak",
                backstory="Başarılı öğrenciler yetiştirmiş deneyimli koç"
            ),
            
            "analyzer": AgentType(
                name="Performans Analizcisi",
                description="Öğrenci performansını analiz eden ajan",
                tools=[self.analyze_tool, self.search_tool],
                system_prompt="""Sen YKS performans uzmanısın.
                Detaylı analizler ve öneriler sun.""",
                role="Performans Uzmanı",
                goal="Öğrenci gelişimini optimize etmek",
                backstory="Veri analizi ve öğrenci değerlendirmede uzman"
            ),
            
            "web_analyzer": AgentType(
                name="Web İçerik Analizcisi",
                description="Web sitesi içeriklerini analiz eden ajan",
                tools=[self.web_analysis_tool, self.search_tool],
                system_prompt="""Sen web içerik analiz uzmanısın.
                Web sitelerini YKS müfredatına uygunluk açısından değerlendirirsin.""",
                role="Web Analiz Uzmanı",
                goal="Web içeriklerini eğitim amaçlı değerlendirmek",
                backstory="Web analizi ve eğitim içerik değerlendirmede uzman"
            ),
            
            "youtube_analyzer": AgentType(
                name="YouTube Video Analizcisi",
                description="YouTube videolarını analiz eden ajan",
                tools=[self.youtube_analysis_tool, self.search_tool],
                system_prompt="""Sen YouTube video analiz uzmanısın.
                Videoları transkribe eder ve YKS müfredatına uygunluk açısından değerlendirirsin.""",
                role="YouTube Analiz Uzmanı",
                goal="Video içeriklerini eğitim amaçlı değerlendirmek",
                backstory="Video analizi ve eğitim multimedya değerlendirmede uzman"
            )
        }
    
    def _build_workflow(self) -> StateGraph:
        """Build the agent workflow using LangGraph"""
        workflow = StateGraph(AgentState)
        
        # Define nodes
        workflow.add_node("router", self._route_request)
        workflow.add_node("expert_selector", self._select_expert)
        workflow.add_node("tutor", self._run_tutor_agent)
        workflow.add_node("content_creator", self._run_content_creator)
        workflow.add_node("planner", self._run_planner)
        workflow.add_node("analyzer", self._run_analyzer)
        workflow.add_node("web_analyzer", self._run_web_analyzer)
        workflow.add_node("youtube_analyzer", self._run_youtube_analyzer)
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
                "web_analyzer": "web_analyzer",
                "youtube_analyzer": "youtube_analyzer",
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
        workflow.add_edge("web_analyzer", "finalizer")
        workflow.add_edge("youtube_analyzer", "finalizer")
        workflow.add_edge("expert_handler", "finalizer")
        workflow.add_edge("finalizer", END)
        
        return workflow.compile()
    
    async def _route_request(self, state: AgentState) -> AgentState:
        """Route request to appropriate handler"""
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
            if any(word in message_lower for word in ["youtube", "video", "izle", "transkript"]):
                state["current_task"] = "youtube_analyzer"
            elif any(word in message_lower for word in ["web", "site", "url", "link", "internet", "sayfa"]):
                state["current_task"] = "web_analyzer"
            elif any(word in message_lower for word in ["test", "soru", "quiz"]):
                state["current_task"] = "content_creator"
            elif any(word in message_lower for word in ["plan", "program", "çalışma"]):
                state["current_task"] = "planner"
            elif any(word in message_lower for word in ["analiz", "performans", "başarı"]):
                state["current_task"] = "analyzer"
            else:
                state["current_task"] = "tutor"
        
        return state
    
    def _determine_next_node(self, state: AgentState) -> str:
        """Determine next node in workflow"""
        next_action = state.get("next_action")
        if next_action:
            return next_action
        
        task = state.get("current_task", "tutor")
        return task if task in self.agents else "tutor"
    
    def _classify_query_advanced(self, query: str, context: Dict[str, Any] = None) -> str:
        """Advanced query classification from CrewAI system"""
        query_lower = query.lower()
        
        # Enhanced keyword sets from CrewAI
        classification_map = {
            ExpertType.MATH: [
                "matematik", "math", "sayı", "hesap", "türev", "integral", "geometri", 
                "trigonometri", "logaritma", "fonksiyon", "denklem", "grafik", "limit",
                "olasılık", "istatistik", "matris", "cebirsel", "koordinat", "açı"
            ],
            ExpertType.PHYSICS: [
                "fizik", "physics", "kuvvet", "hareket", "enerji", "elektrik", "manyetik",
                "dalga", "ışık", "ses", "basınç", "sıcaklık", "atom", "çekim", "momentum",
                "kinetik", "potansiyel", "newton", "ohm", "volt", "joule"
            ],
            ExpertType.CHEMISTRY: [
                "kimya", "chemistry", "element", "bileşik", "reaksiyon", "asit", "baz",
                "mol", "orbital", "bağ", "çözelti", "kataliz", "organik", "periyodik",
                "elektron", "proton", "nötron", "iyonik", "kovalent"
            ],
            ExpertType.BIOLOGY: [
                "biyoloji", "biology", "hücre", "dna", "gen", "protein", "enzim",
                "fotosentez", "solunum", "dolaşım", "sinir", "hormon", "ekosistem",
                "mitoz", "mayoz", "kalıtım", "adaptasyon", "evrim"
            ],
            ExpertType.TURKISH_LITERATURE: [
                "türkçe", "edebiyat", "şiir", "roman", "hikaye", "dil", "gramer",
                "anlam", "sözcük", "cümle", "metin", "yazar", "şair", "edebi"
            ],
            ExpertType.HISTORY: [
                "tarih", "history", "osmanlı", "selçuklu", "cumhuriyet", "savaş",
                "devlet", "sultan", "padişah", "millet", "medeniyet", "kültür"
            ],
            ExpertType.GEOGRAPHY: [
                "coğrafya", "geography", "iklim", "harita", "kıta", "ülke", "şehir",
                "nüfus", "ekonomi", "doğal", "kaynak", "jeoloji", "toprak"
            ],
            ExpertType.PHILOSOPHY: [
                "felsefe", "philosophy", "düşünce", "mantık", "ahlak", "varlık",
                "bilgi", "doğruluk", "güzellik", "adalet", "özgürlük"
            ],
            ExpertType.RELIGION: [
                "din", "islam", "kuran", "peygamber", "namaz", "oruç", "hac",
                "zakat", "ibadet", "ahlak", "iman", "allah"
            ],
            ExpertType.REVOLUTION: [
                "inkılap", "atatürk", "atatürkçülük", "cumhuriyet", "milli mücadele",
                "reform", "modernleşme", "laik", "milliyetçi"
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
                    if keyword in ["matematik", "fizik", "kimya", "biyoloji", "türkçe", "tarih", "coğrafya", "felsefe"]:
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
        study_keywords = ["plan", "çalışma", "program", "takvim", "strateji", "hedef", "zaman"]
        if any(keyword in query_lower for keyword in study_keywords):
            return ExpertType.GENERAL.value
        
        return ExpertType.GENERAL.value

    async def _select_expert(self, state: AgentState) -> AgentState:
        """Enhanced expert selection with advanced classification"""
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
        """Run selected expert"""
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
                ExpertType.TURKISH_LITERATURE: "Türk Dili ve Edebiyatı",
                ExpertType.HISTORY: "Tarih",
                ExpertType.GEOGRAPHY: "Coğrafya",
                ExpertType.PHILOSOPHY: "Felsefe",
                ExpertType.RELIGION: "Din Kültürü",
                ExpertType.REVOLUTION: "İnkılap ve Atatürkçülük"
            }
            
            if expert_type in subject_mapping:
                subject_name = subject_mapping[expert_type]
                curriculum_topics = curriculum_loader.get_subject_topics(subject_name)
                
                if curriculum_topics:
                    # Get relevant curriculum topics
                    relevant_topics = []
                    for topic in curriculum_topics[:10]:  # Limit to first 10 topics
                        relevant_topics.append(f"- {topic.get('title', '')}: {topic.get('content', '')[:200]}...")
                    
                    curriculum_context = f"\n\nMüfredat Bilgisi ({subject_name}):\n" + "\n".join(relevant_topics)
                    
        except Exception as e:
            logger.error(f"Error getting curriculum context: {e}")
        
        # Enhanced context with both RAG and curriculum data
        full_context = f"RAG Bağlamı: {rag_context}{curriculum_context}"
        
        # Generate expert response
        response = await gemini_client.generate_content(
            prompt=f"Bağlam: {full_context}\n\nSoru: {user_message}",
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
        """Run tutor agent"""
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
        """Run content creator agent"""
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
        """Run planner agent"""
        student_info = state.get("context", {}).get("student_info", {
            "target_exam": "YKS",
            "remaining_days": 180,
            "daily_hours": 6
        })
        
        plan = await self._create_study_plan(student_info)
        state["results"]["study_plan"] = plan
        return state
    
    async def _run_analyzer(self, state: AgentState) -> AgentState:
        """Run analyzer agent"""
        performance_data = state.get("context", {}).get("performance_data", {})
        
        analysis = await self._analyze_performance(performance_data)
        state["results"]["analysis"] = analysis
        return state
    
    async def _finalize_response(self, state: AgentState) -> AgentState:
        """Finalize and format response"""
        results = state.get("results", {})
        
        # Combine all results
        final_response = []
        
        # Add expert response if available
        if "expert_response" in results:
            expert_info = results["expert_response"]
            response = expert_info["response"]
            expert_name = expert_info["expert"]
            final_response.append(f"{response}\n\n---\n*{expert_name} tarafından sağlanmıştır*")
        
        # Add other responses
        for key, value in results.items():
            if key != "expert_response" and value:
                final_response.append(str(value))
        
        # Create final message
        state["messages"].append({
            "role": "assistant",
            "content": "\n\n".join(final_response) if final_response else "Üzgünüm, bir yanıt oluşturamadım."
        })
        
        return state
    
    # Tool implementation methods
    async def _search_knowledge_base(self, query: str, filters: Optional[Dict] = None) -> str:
        """Search in knowledge base"""
        results = await rag_system.search(query, n_results=3, filter_metadata=filters)
        
        if not results:
            return "İlgili bilgi bulunamadı."
        
        formatted_results = []
        for result in results:
            formatted_results.append(f"- {result['content']}")
        
        return "\n".join(formatted_results)
    
    async def _generate_quiz(self, topic: str, count: int = 5, difficulty: str = "orta") -> str:
        """Generate quiz questions"""
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
        """Explain a concept"""
        return await self.chains.explain_concept({
            "subject": concept.split("-")[0] if "-" in concept else "Genel",
            "topic": concept,
            "style": style,
            "detail_level": "high" if style == "detailed" else "medium"
        })
    
    async def _create_study_plan(self, student_info: Dict[str, Any]) -> str:
        """Create personalized study plan"""
        plan = await self.chains.generate_study_plan(student_info)
        return json.dumps(plan.dict(), ensure_ascii=False, indent=2)
    
    async def _analyze_performance(self, performance_data: Dict[str, Any]) -> str:
        """Analyze student performance"""
        if not performance_data:
            return "Analiz için yeterli veri bulunmuyor."
        
        # Generate analysis using AI
        prompt = f"""
        Öğrenci performans verilerini analiz et:
        {json.dumps(performance_data, ensure_ascii=False, indent=2)}
        
        Detaylı analiz sun:
        1. Güçlü yönler
        2. Geliştirilmesi gereken alanlar
        3. Öneriler
        """
        
        response = await gemini_client.generate_content(
            prompt=prompt,
            system_instruction="Sen deneyimli bir eğitim performans analistisi."
        )
        
        return response["text"]
    
    async def _create_mindmap(self, topic: str) -> str:
        """Create mind map for topic"""
        concept_map = await self.chains.generate_concept_map({
            "subject": topic.split("-")[0] if "-" in topic else "Genel",
            "topic": topic
        })
        return json.dumps(concept_map.dict(), ensure_ascii=False, indent=2)
    
    async def _analyze_website(self, url: str, analysis_type: str = "full") -> str:
        """Analyze website content using web analyzer"""
        try:
            result = await web_analyzer.analyze_website(
                url=url,
                analysis_type=analysis_type
            )
            
            if result.get("error"):
                return f"Web analizi hatası: {result['error']}"
            
            # Format result for display
            formatted_result = {
                "başarılı": result.get("success", False),
                "url": result.get("url", ""),
                "içerik_bilgisi": result.get("content_info", {}),
                "müfredat_uygunluk": result.get("curriculum_check", {}),
                "eğitim_analizi": result.get("educational_analysis", ""),
                "oluşturulan_sorular": len(result.get("generated_questions", [])),
                "çalışma_materyalleri": bool(result.get("study_materials"))
            }
            
            return json.dumps(formatted_result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"Website analysis error: {e}")
            return f"Web sitesi analizi sırasında hata: {str(e)}"
    
    async def _run_web_analyzer(self, state: AgentState) -> AgentState:
        """Run web analyzer agent"""
        user_message = state["messages"][-1]["content"]
        
        # Extract URL from message
        import re
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, user_message)
        
        if not urls:
            result = "Lütfen analiz edilecek web sitesi URL'sini belirtin."
        else:
            url = urls[0]  # Use first URL found
            result = await self._analyze_website(url)
        
        state["results"]["web_analysis"] = result
        return state
    
    async def _analyze_youtube_video(self, url: str, analysis_type: str = "full") -> str:
        """Analyze YouTube video using YouTube analyzer"""
        try:
            result = await youtube_analyzer.analyze_youtube_video(
                url=url,
                analysis_type=analysis_type
            )
            
            if result.get("error"):
                return f"YouTube analizi hatası: {result['error']}"
            
            # Format result for display
            formatted_result = {
                "başarılı": result.get("success", False),
                "video_url": result.get("url", ""),
                "video_id": result.get("video_id", ""),
                "video_bilgisi": result.get("video_info", {}),
                "müfredat_uygunluk": result.get("curriculum_check", {}),
                "transkript_uzunluk": len(result.get("transcript", "")),
                "eğitim_analizi": result.get("educational_analysis", ""),
                "oluşturulan_sorular": len(result.get("generated_questions", [])),
                "çalışma_materyalleri": bool(result.get("study_materials")),
                "zaman_damgaları": len(result.get("timestamps", []))
            }
            
            return json.dumps(formatted_result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"YouTube analysis error: {e}")
            return f"YouTube video analizi sırasında hata: {str(e)}"
    
    async def _run_youtube_analyzer(self, state: AgentState) -> AgentState:
        """Run YouTube analyzer agent"""
        user_message = state["messages"][-1]["content"]
        
        # Extract YouTube URL from message
        import re
        youtube_patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'https?://(?:www\.)?youtu\.be/[\w-]+',
            r'https?://(?:www\.)?youtube\.com/embed/[\w-]+',
            r'https?://(?:www\.)?youtube\.com/v/[\w-]+'
        ]
        
        urls = []
        for pattern in youtube_patterns:
            urls.extend(re.findall(pattern, user_message))
        
        if not urls:
            result = "Lütfen analiz edilecek YouTube video URL'sini belirtin."
        else:
            url = urls[0]  # Use first URL found
            result = await self._analyze_youtube_video(url)
        
        state["results"]["youtube_analysis"] = result
        return state
    
    def _extract_topic(self, message: str) -> str:
        """Extract topic from user message"""
        keywords = ["matematik", "fizik", "kimya", "biyoloji", "geometri", "türkçe"]
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
        """
        Process user message through the unified agent system
        
        Args:
            message: User message
            context: Additional context
            session_id: Session identifier
        
        Returns:
            Response dictionary
        """
        try:
            # Initialize system if needed (lazy loading)
            self.initialize_if_needed()
            
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
                "response": "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.",
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
        """
        Get collaborative response from multiple experts
        Enhanced feature from CrewAI system
        """
        try:
            if not expert_types:
                # Auto-select relevant experts based on query
                primary_expert = self._classify_query_advanced(query, context)
                expert_types = [ExpertType(primary_expert)]
                
                # Add complementary experts for complex queries
                if any(word in query.lower() for word in ["karşılaştır", "fark", "benzer", "ilişki"]):
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
        """Get response from a specific expert"""
        try:
            expert = self.experts[expert_type]
            
            # Get relevant context
            rag_results = await rag_system.search(query, n_results=2)
            rag_context = "\n".join([doc["content"] for doc in rag_results])
            
            # Build enhanced prompt
            prompt = f"""Soru: {query}

Bağlam Bilgiler:
{rag_context}

Lütfen {expert.name} perspektifinden yanıtla."""
            
            response = await gemini_client.generate_content(
                prompt=prompt,
                system_instruction=expert.system_instruction
            )
            
            return response.get("text", "Yanıt oluşturulamadı.")
            
        except Exception as e:
            logger.error(f"Error getting expert response: {e}")
            return f"Üzgünüm, {expert_type.value} uzmanından yanıt alınamadı."
    
    def _calculate_response_confidence(
        self, 
        response: str, 
        expert_type: ExpertType, 
        query: str
    ) -> float:
        """Calculate confidence score for expert response"""
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
            if any(indicator in response.lower() for indicator in ["örneğin", "şöyle ki", "çünkü", "nedeni"]):
                confidence += 0.1
            
            return min(confidence, 1.0)
            
        except Exception:
            return 0.5
    
    async def _synthesize_expert_responses(
        self, 
        expert_responses: List[Dict], 
        query: str
    ) -> Dict[str, Any]:
        """Synthesize multiple expert responses into coherent answer"""
        try:
            # Prepare synthesis prompt
            expert_texts = []
            for i, er in enumerate(expert_responses):
                expert_texts.append(f"{er['expert'].title()} Uzmanı ({er['confidence']:.2f} güven):\n{er['response']}")
            
            combined_responses = "\n\n---\n\n".join(expert_texts)
            
            synthesis_prompt = f"""Aşağıdaki uzman görüşlerini sentezleyerek tutarlı ve kapsamlı bir yanıt oluştur:

Soru: {query}

Uzman Görüşleri:
{combined_responses}

Sentez kuralları:
1. Uzmanların ortak noktalarını vurgula
2. Farklı perspektifleri dengele
3. Çelişkiler varsa açıkla
4. Kapsamlı ama öz bir yanıt ver
5. Her uzmanın katkısını belirt"""

            synthesis_response = await gemini_client.generate_content(
                prompt=synthesis_prompt,
                system_instruction="Sen uzman görüşlerini sentezleyen deneyimli bir koordinatörsün."
            )
            
            # Calculate synthesis confidence (average of expert confidences)
            avg_confidence = sum(er["confidence"] for er in expert_responses) / len(expert_responses)
            
            return {
                "response": synthesis_response.get("text", "Sentez oluşturulamadı."),
                "confidence": avg_confidence
            }
            
        except Exception as e:
            logger.error(f"Error in synthesis: {e}")
            # Fallback: return highest confidence response
            best_response = max(expert_responses, key=lambda x: x["confidence"])
            return {
                "response": best_response["response"],
                "confidence": best_response["confidence"]
            }

# Global agent system instance
agent_system = UnifiedAgentSystem()