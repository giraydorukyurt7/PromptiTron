"""
Socratic Method Agent
Sokratik yöntemle öğretim yapan uzman ajan
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
    """Sokratik yöntemle öğretim yapan ajan"""
    
    def __init__(self):
        """Sokratik ajan başlatma"""
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.7,
            max_output_tokens=1024
        )
        
        self.system_prompt = """Sen Sokratik yöntemle öğretim yapan bir eğitmensin. 
        
        Sokratik Yöntem Prensipleri:
        1. ASLA doğrudan cevap verme - bunun yerine yönlendirici sorular sor
        2. Öğrenciyi kendi cevabını bulmaya yönlendir
        3. Mantıklı düşünmeyi ve sorgulama becerisini geliştir
        4. Her sorunla öğrencinin anlayışını derinleştir
        5. Öğrencinin var olan bilgisinden yola çık
        
        Soru Sorma Teknikleri:
        - "Sence neden böyle olabilir?"
        - "Bu durumda ne olmasını beklerdin?"
        - "Başka hangi örnekler verebilirsin?"
        - "Bu fikre nasıl ulaştın?"
        - "Bunun tersini düşünürsek ne olur?"
        - "Bu kural her zaman geçerli mi?"
        
        Önemli Kurallar:
        - Öğrenci yanlış cevap verse bile doğrudan düzeltme
        - Onun yerine doğru cevaba yönlendirecek sorular sor
        - Sabırlı ve destekleyici ol
        - Her zaman Türkçe konuş
        - Kısa ve anlaşılır sorular sor
        
        Öğrenci "bilmiyorum" derse:
        - Daha basit sorularla başla
        - İpuçları ver ama cevabı söyleme
        - Günlük hayattan örneklerle ilişkilendir"""
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        self.memory = ConversationBufferMemory(
            memory_key="history",
            return_messages=True
        )
        
        self.chain = self.prompt | self.llm
        
        logger.info("Sokratik ajan başlatıldı")
    
    async def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Sokratik yöntemle yanıt üret"""
        try:
            # Konuşma geçmişini al
            messages = self.memory.chat_memory.messages
            
            # Giriş mesajı ekle
            if not messages and context and context.get("topic"):
                intro_message = f"Bugün {context['topic']} hakkında konuşalım. Bu konuda ne bildiğini merak ediyorum."
                messages.append(AIMessage(content=intro_message))
            
            # Kullanıcı mesajını ekle
            messages.append(HumanMessage(content=user_input))
            
            # Yanıt üret
            response = await self.chain.ainvoke({
                "history": messages[:-1],  # Son mesaj hariç tüm geçmiş
                "input": user_input
            })
            
            # Belleğe kaydet
            self.memory.chat_memory.add_user_message(user_input)
            self.memory.chat_memory.add_ai_message(response.content)
            
            # Sokratik ipuçları ekle
            hints = self._generate_socratic_hints(user_input, response.content)
            
            return {
                "success": True,
                "response": response.content,
                "mode": "socratic",
                "hints": hints,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Sokratik ajan hatası: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin."
            }
    
    def _generate_socratic_hints(self, user_input: str, ai_response: str) -> List[str]:
        """Öğretmen için Sokratik ipuçları üret"""
        hints = []
        
        # Kullanıcı "bilmiyorum" dediyse
        if "bilmiyorum" in user_input.lower() or "emin değilim" in user_input.lower():
            hints.append("İpucu: Daha basit sorularla başlayın")
            hints.append("İpucu: Günlük hayattan örnekler verin")
        
        # Kısa cevaplar için
        if len(user_input) < 20:
            hints.append("İpucu: Düşüncelerini genişletmesi için sorular sorun")
            hints.append("İpucu: 'Neden?' veya 'Nasıl?' soruları kullanın")
        
        # Soru işareti yoksa
        if "?" not in ai_response:
            hints.append("Dikkat: Sokratik yöntemde her zaman soru sormalısınız")
        
        return hints
    
    def reset_memory(self):
        """Konuşma belleğini sıfırla"""
        self.memory.clear()
        logger.info("Sokratik ajan belleği temizlendi")
    
    def get_conversation_summary(self) -> str:
        """Konuşma özetini al"""
        messages = self.memory.chat_memory.messages
        if not messages:
            return "Henüz konuşma yok"
        
        summary = "Sokratik Diyalog Özeti:\n\n"
        for i, msg in enumerate(messages):
            if isinstance(msg, HumanMessage):
                summary += f"Öğrenci: {msg.content}\n"
            else:
                summary += f"Sokrates: {msg.content}\n"
            summary += "\n"
        
        return summary

# Global Sokratik ajan instance
socratic_agent = SocraticAgent()