"""
Socratic Method Agent
Sokratik yontemle ogretim yapan uzman ajan
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage
from config import settings

logger = logging.getLogger(__name__)

class SocraticAgent:
    """Sokratik yontemle ogretim yapan ajan"""
    
    def __init__(self):
        """Sokratik ajan baslatma"""
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.7,
            max_output_tokens=1024
        )
        
        self.system_prompt = """Sen Sokratik yontemle ogretim yapan bir egitmensin. 
        
        Sokratik Yontem Prensipleri:
        1. ASLA dogrudan cevap verme - bunun yerine yonlendirici sorular sor
        2. Ogrenciyi kendi cevabini bulmaya yonlendir
        3. Mantikli dusunmeyi ve sorgulama becerisini gelistir
        4. Her sorunla ogrencinin anlayisini derinlestir
        5. Ogrencinin var olan bilgisinden yola cik
        
        Soru Sorma Teknikleri:
        - "Sence neden boyle olabilir?"
        - "Bu durumda ne olmasini beklerdin?"
        - "Baska hangi ornekler verebilirsin?"
        - "Bu fikre nasil ulastin?"
        - "Bunun tersini dusunursek ne olur?"
        - "Bu kural her zaman gecerli mi?"
        
        Onemli Kurallar:
        - Ogrenci yanlis cevap verse bile dogrudan duzeltme
        - Onun yerine dogru cevaba yonlendirecek sorular sor
        - Sabirli ve destekleyici ol
        - Her zaman Turkce konus
        - Kisa ve anlasilir sorular sor
        
        Ogrenci "bilmiyorum" derse:
        - Daha basit sorularla basla
        - Ipuclari ver ama cevabi soyleme
        - Gunluk hayattan orneklerle iliskilendir
"""self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        self.memory = ConversationBufferMemory(
            memory_key="history",
            return_messages=True
        )
        
        self.chain = self.prompt | self.llm
        
        logger.info("Sokratik ajan baslatildi")
    
    async def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Sokratik yontemle yanit uret"""
        try:
            # Konusma gecmisini al
            messages = self.memory.chat_memory.messages
            
            # Giris mesaji ekle
            if not messages and context and context.get("topic"):
                intro_message = f"Bugun {context['topic']} hakkinda konusalim. Bu konuda ne bildigini merak ediyorum."
                messages.append(AIMessage(content=intro_message))
            
            # Kullanici mesajini ekle
            messages.append(HumanMessage(content=user_input))
            
            # Yanit uret
            response = await self.chain.ainvoke({
                "history": messages[:-1],  # Son mesaj haric tum gecmis
                "input": user_input
            })
            
            # Bellege kaydet
            self.memory.chat_memory.add_user_message(user_input)
            self.memory.chat_memory.add_ai_message(response.content)
            
            # Sokratik ipuclari ekle
            hints = self._generate_socratic_hints(user_input, response.content)
            
            return {
                "success": True,
                "response": response.content,
                "mode": "socratic",
                "hints": hints,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Sokratik ajan hatasi: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "Uzgunum, bir hata olustu. Lutfen tekrar deneyin."
            }
    
    def _generate_socratic_hints(self, user_input: str, ai_response: str) -> List[str]:
        """Ogretmen icin Sokratik ipuclari uret"""
        hints = []
        
        # Kullanici "bilmiyorum" dediyse
        if "bilmiyorum" in user_input.lower() or "emin degilim" in user_input.lower():
            hints.append("Ipucu: Daha basit sorularla baslayin")
            hints.append("Ipucu: Gunluk hayattan ornekler verin")
        
        # Kisa cevaplar icin
        if len(user_input) < 20:
            hints.append("Ipucu: Dusuncelerini genisletmesi icin sorular sorun")
            hints.append("Ipucu: 'Neden?' veya 'Nasil?' sorulari kullanin")
        
        # Soru isareti yoksa
        if "?" not in ai_response:
            hints.append("Dikkat: Sokratik yontemde her zaman soru sormalisiniz")
        
        return hints
    
    def reset_memory(self):
        """Konusma bellegini sifirla"""
        self.memory.clear()
        logger.info("Sokratik ajan bellegi temizlendi")
    
    def get_conversation_summary(self) -> str:
        """Konusma ozetini al"""
        messages = self.memory.chat_memory.messages
        if not messages:
            return "Henuz konusma yok"
        
        summary = "Sokratik Diyalog Ozeti:\n\n"
        for i, msg in enumerate(messages):
            if isinstance(msg, HumanMessage):
                summary += f"Ogrenci: {msg.content}\n"
            else:
                summary += f"Sokrates: {msg.content}\n"
            summary += "\n"
        
        return summary

# Global Sokratik ajan instance
socratic_agent = SocraticAgent()