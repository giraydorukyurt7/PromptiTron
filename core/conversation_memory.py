"""
Advanced conversation memory system for personalized learning
Integrates with Gemini AI for context-aware responses
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from pydantic import BaseModel, Field
from enum import Enum

from core.gemini_client import gemini_client
from core.rag_system import rag_system

logger = logging.getLogger(__name__)

class ConversationType(str, Enum):
    QUESTION_ANSWER = "question_answer"
    STUDY_PLANNING = "study_planning"
    PRACTICE_SESSION = "practice_session"
    PROGRESS_TRACKING = "progress_tracking"
    GENERAL_CHAT = "general_chat"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ConversationMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class ConversationSummary(BaseModel):
    key_topics: List[str] = Field(description="Main topics discussed")
    learning_objectives: List[str] = Field(description="What student was trying to learn")
    student_understanding: str = Field(description="Assessment of student's understanding level")
    weak_areas_identified: List[str] = Field(description="Areas where student showed difficulty")
    recommended_next_steps: List[str] = Field(description="Recommended next learning steps")
    conversation_sentiment: str = Field(description="Overall sentiment (positive/neutral/frustrated)")

class StudentProfile(BaseModel):
    student_id: str
    grade_level: int
    exam_target: str  # YKS, LGS
    strong_subjects: List[str] = []
    weak_subjects: List[str] = []
    learning_style: str = "visual"  # visual, auditory, kinesthetic
    study_goals: List[str] = []
    difficulty_preference: str = "medium"  # easy, medium, hard
    recent_topics: List[str] = []
    last_activity: Optional[datetime] = None
    total_study_time: int = 0  # minutes
    questions_asked: int = 0
    concepts_mastered: List[str] = []
    performance_trends: Dict[str, List[float]] = {}  # subject -> scores over time

class ConversationMemorySystem:
    def __init__(self):
        """Initialize conversation memory system"""
        self.conversations: Dict[str, List[ConversationMessage]] = {}
        self.summaries: Dict[str, List[ConversationSummary]] = {}
        self.student_profiles: Dict[str, StudentProfile] = {}
        self.max_conversation_length = 20  # Optimize: 50 -> 20
        self.summary_threshold = 8  # Optimize: 10 -> 8
        self.auto_cleanup_threshold = 100  # New: Auto cleanup
        
        logger.info("Conversation memory system initialized")
    
    async def add_message(
        self,
        session_id: str,
        role: MessageRole,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a message to conversation memory"""
        try:
            if session_id not in self.conversations:
                self.conversations[session_id] = []
            
            message = ConversationMessage(
                role=role,
                content=content,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
            
            self.conversations[session_id].append(message)
            
            # Maintain conversation length limit
            if len(self.conversations[session_id]) > self.max_conversation_length:
                await self._summarize_old_messages(session_id)
                self.conversations[session_id] = self.conversations[session_id][-self.max_conversation_length:]
            
            # Auto-summarize if needed
            if len(self.conversations[session_id]) % self.summary_threshold == 0:
                await self._create_conversation_summary(session_id)
            
            # Auto-cleanup if needed (every 20 messages)
            if len(self.conversations[session_id]) % 20 == 0:
                await self.auto_cleanup_memory()
            
            # Add to RAG memory for future retrieval
            if role == MessageRole.USER:
                # Find corresponding assistant response
                assistant_response = ""
                for i in range(len(self.conversations[session_id]) - 1, -1, -1):
                    if self.conversations[session_id][i].role == MessageRole.ASSISTANT:
                        assistant_response = self.conversations[session_id][i].content
                        break
                
                if assistant_response:
                    await rag_system.add_conversation_to_memory(
                        user_message=content,
                        ai_response=assistant_response,
                        metadata={
                            "session_id": session_id,
                            "timestamp": datetime.now().isoformat(),
                            "conversation_type": metadata.get("type", "general")
                        }
                    )
            
        except Exception as e:
            logger.error(f"Error adding message to memory: {str(e)}")
    
    async def get_conversation_context(
        self,
        session_id: str,
        max_messages: int = 10,
        include_summaries: bool = True
    ) -> List[Dict[str, str]]:
        """Get recent conversation context for the AI"""
        try:
            context = []
            
            # Add summaries if requested
            if include_summaries and session_id in self.summaries:
                for summary in self.summaries[session_id][-2:]:  # Last 2 summaries
                    context.append({
                        "role": "system",
                        "content": f"Previous conversation summary: {summary.model_dump_json()}"
                    })
            
            # Add recent messages
            if session_id in self.conversations:
                recent_messages = self.conversations[session_id][-max_messages:]
                for msg in recent_messages:
                    context.append({
                        "role": msg.role.value,
                        "content": msg.content
                    })
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting conversation context: {str(e)}")
            return []
    
    async def update_student_profile(
        self,
        student_id: str,
        updates: Dict[str, Any]
    ) -> StudentProfile:
        """Update student profile based on conversation analysis"""
        try:
            if student_id not in self.student_profiles:
                self.student_profiles[student_id] = StudentProfile(
                    student_id=student_id,
                    grade_level=updates.get("grade_level", 10),
                    exam_target=updates.get("exam_target", "YKS")
                )
            
            profile = self.student_profiles[student_id]
            
            # Update profile fields
            for key, value in updates.items():
                if hasattr(profile, key):
                    if key in ["strong_subjects", "weak_subjects", "recent_topics", "concepts_mastered"]:
                        # For list fields, extend rather than replace
                        current_list = getattr(profile, key)
                        if isinstance(value, list):
                            # Add new items, maintain uniqueness
                            updated_list = list(set(current_list + value))
                            setattr(profile, key, updated_list[-10:])  # Keep last 10
                    elif key == "performance_trends":
                        # Merge performance trends
                        current_trends = profile.performance_trends
                        for subject, scores in value.items():
                            if subject not in current_trends:
                                current_trends[subject] = []
                            current_trends[subject].extend(scores)
                            # Keep last 20 scores
                            current_trends[subject] = current_trends[subject][-20:]
                    else:
                        setattr(profile, key, value)
            
            profile.last_activity = datetime.now()
            
            # Update statistics
            if "study_time" in updates:
                profile.total_study_time += updates["study_time"]
            if "questions_asked" in updates:
                profile.questions_asked += updates["questions_asked"]
            
            return profile
            
        except Exception as e:
            logger.error(f"Error updating student profile: {str(e)}")
            return self.student_profiles.get(student_id)
    
    async def analyze_conversation_for_insights(
        self,
        session_id: str,
        student_id: str
    ) -> Dict[str, Any]:
        """Analyze conversation to extract learning insights"""
        try:
            if session_id not in self.conversations:
                return {"error": "No conversation found"}
            
            # Get recent conversation
            messages = self.conversations[session_id][-20:]  # Last 20 messages
            conversation_text = "\n".join([
                f"{msg.role.value}: {msg.content}" for msg in messages
            ])
            
            # Use Gemini to analyze conversation
            analysis_prompt = f"""
            Aşağıdaki öğrenci sohbetini analiz et ve öğrenme durumu hakkında bilgi çıkar:

            Sohbet:
            {conversation_text}

            Analiz et:
            1. Öğrencinin güçlü olduğu konular
            2. Zayıf olduğu konular
            3. Öğrenme stili tercihleri
            4. Motivasyon durumu
            5. Anlamakta zorlandığı kavramlar
            6. Öneriler

            JSON formatında detaylı analiz ver.
            """
            
            response = await gemini_client.generate_structured_output(
                prompt=analysis_prompt,
                response_model=ConversationSummary,
                system_instruction="Sen deneyimli bir eğitim analisti ve öğrenci rehberisin."
            )
            
            # Update student profile based on analysis
            profile_updates = {
                "weak_subjects": response.weak_areas_identified,
                "recent_topics": response.key_topics,
                "learning_style": self._infer_learning_style(conversation_text)
            }
            
            await self.update_student_profile(student_id, profile_updates)
            
            return {
                "analysis": response,
                "profile_updated": True,
                "recommendations": response.recommended_next_steps
            }
            
        except Exception as e:
            logger.error(f"Error analyzing conversation: {str(e)}")
            return {"error": str(e)}
    
    async def get_personalized_context(
        self,
        session_id: str,
        student_id: str,
        current_query: str
    ) -> Dict[str, Any]:
        """Get personalized context for generating responses"""
        try:
            # Get student profile
            profile = self.student_profiles.get(student_id)
            
            # Get conversation context
            conversation_context = await self.get_conversation_context(session_id)
            
            # Get relevant past conversations
            relevant_conversations = await rag_system.get_relevant_conversations(
                current_query=current_query,
                user_id=student_id,
                top_k=3
            )
            
            # Build personalized context
            context = {
                "student_profile": profile.model_dump() if profile else None,
                "conversation_history": conversation_context,
                "relevant_past_conversations": relevant_conversations,
                "personalization_hints": self._generate_personalization_hints(profile, current_query),
                "adaptive_difficulty": self._calculate_adaptive_difficulty(profile)
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting personalized context: {str(e)}")
            return {}
    
    async def _create_conversation_summary(self, session_id: str) -> None:
        """Create a summary of recent conversation"""
        try:
            if session_id not in self.conversations:
                return
            
            messages = self.conversations[session_id][-self.summary_threshold:]
            conversation_text = "\n".join([
                f"{msg.role.value}: {msg.content}" for msg in messages
            ])
            
            summary_prompt = f"""
            Bu sohbet bölümünü özetle:
            {conversation_text}
            
            Önemli noktalar:
            - Konuşulan ana konular
            - Öğrenme hedefleri
            - Öğrencinin anlama seviyesi
            - Zayıf alanlar
            - Önerilen adımlar
            - Genel duygu durumu (pozitif/nötr/frustre)
            """
            
            response = await gemini_client.generate_structured_output(
                prompt=summary_prompt,
                response_model=ConversationSummary,
                system_instruction="Sen sohbet özetlemede uzman bir eğitim danışmanısın."
            )
            
            if session_id not in self.summaries:
                self.summaries[session_id] = []
            
            self.summaries[session_id].append(response)
            
            # Keep only last 5 summaries
            self.summaries[session_id] = self.summaries[session_id][-5:]
            
        except Exception as e:
            logger.error(f"Error creating conversation summary: {str(e)}")
    
    async def _summarize_old_messages(self, session_id: str) -> None:
        """Summarize old messages before removing them"""
        try:
            if session_id not in self.conversations:
                return
            
            old_messages = self.conversations[session_id][:10]  # First 10 messages
            conversation_text = "\n".join([
                f"{msg.role.value}: {msg.content}" for msg in old_messages
            ])
            
            # Create summary and store it
            await self._create_conversation_summary(session_id)
            
        except Exception as e:
            logger.error(f"Error summarizing old messages: {str(e)}")
    
    def _infer_learning_style(self, conversation_text: str) -> str:
        """Infer learning style from conversation patterns"""
        # Simple heuristics for learning style detection
        visual_keywords = ["görsel", "resim", "diyagram", "şekil", "grafik", "görüyorum", "şema"]
        auditory_keywords = ["dinleme", "açıklama", "anlatma", "duyuyorum", "ses", "konuşma"]
        kinesthetic_keywords = ["yaparak", "deneyim", "uygulama", "pratik", "hareket", "deney"]
        
        text_lower = conversation_text.lower()
        
        visual_count = sum(1 for keyword in visual_keywords if keyword in text_lower)
        auditory_count = sum(1 for keyword in auditory_keywords if keyword in text_lower)
        kinesthetic_count = sum(1 for keyword in kinesthetic_keywords if keyword in text_lower)
        
        if visual_count > auditory_count and visual_count > kinesthetic_count:
            return "visual"
        elif auditory_count > kinesthetic_count:
            return "auditory"
        else:
            return "kinesthetic"
    
    def _generate_personalization_hints(
        self,
        profile: Optional[StudentProfile],
        current_query: str
    ) -> List[str]:
        """Generate hints for personalizing responses"""
        hints = []
        
        if not profile:
            return ["Yeni öğrenci - temel seviyeden başla"]
        
        # Learning style hints
        if profile.learning_style == "visual":
            hints.append("Görsel örnekler, diyagramlar ve şemalar kullan")
        elif profile.learning_style == "auditory":
            hints.append("Açık anlatımlar ve adım adım açıklamalar ver")
        else:
            hints.append("Pratik uygulamalar ve hands-on örnekler sun")
        
        # Subject-specific hints
        if profile.weak_subjects:
            hints.append(f"Zayıf konulara odaklan: {', '.join(profile.weak_subjects)}")
        
        # Difficulty hints
        if profile.difficulty_preference == "easy":
            hints.append("Basit örneklerle başla, yavaş yavaş zorlaştır")
        elif profile.difficulty_preference == "hard":
            hints.append("Zorlu örnekler ve derin analiz sun")
        
        # Exam-specific hints
        if profile.exam_target == "YKS":
            hints.append("YKS formatında sorular ve stratejiler ver")
        elif profile.exam_target == "LGS":
            hints.append("LGS seviyesine uygun açıklamalar yap")
        
        # Performance-based hints
        if profile.performance_trends:
            improving_subjects = []
            declining_subjects = []
            
            for subject, scores in profile.performance_trends.items():
                if len(scores) >= 3:
                    recent_trend = scores[-3:]
                    if all(recent_trend[i] <= recent_trend[i+1] for i in range(len(recent_trend)-1)):
                        improving_subjects.append(subject)
                    elif all(recent_trend[i] >= recent_trend[i+1] for i in range(len(recent_trend)-1)):
                        declining_subjects.append(subject)
            
            if improving_subjects:
                hints.append(f"Gelişim gösteren konular: {', '.join(improving_subjects)} - Motive et")
            if declining_subjects:
                hints.append(f"Düşüş gösteren konular: {', '.join(declining_subjects)} - Ekstra destek ver")
        
        # Time-based hints
        if profile.last_activity:
            days_since_last = (datetime.now() - profile.last_activity).days
            if days_since_last > 7:
                hints.append("Uzun aradan sonra dönüş - Kısa tekrar yap")
        
        return hints
    
    def _calculate_adaptive_difficulty(self, profile: Optional[StudentProfile]) -> str:
        """Calculate adaptive difficulty based on student performance"""
        if not profile or not profile.performance_trends:
            return "medium"
        
        # Calculate average recent performance
        all_recent_scores = []
        for scores in profile.performance_trends.values():
            if scores:
                all_recent_scores.extend(scores[-5:])  # Last 5 scores from each subject
        
        if not all_recent_scores:
            return "medium"
        
        avg_score = sum(all_recent_scores) / len(all_recent_scores)
        
        if avg_score >= 0.8:
            return "hard"
        elif avg_score >= 0.6:
            return "medium"
        else:
            return "easy"
    
    async def auto_cleanup_memory(self) -> None:
        """Automatic memory cleanup for performance optimization"""
        try:
            total_conversations = sum(len(msgs) for msgs in self.conversations.values())
            
            if total_conversations > self.auto_cleanup_threshold:
                # Clean old conversations (keep only recent sessions)
                sessions_by_activity = []
                for session_id, messages in self.conversations.items():
                    if messages:
                        last_activity = messages[-1].timestamp
                        sessions_by_activity.append((session_id, last_activity))
                
                # Sort by activity, keep most recent 50 sessions
                sessions_by_activity.sort(key=lambda x: x[1], reverse=True)
                sessions_to_keep = {s[0] for s in sessions_by_activity[:50]}
                
                # Remove old sessions
                old_sessions = set(self.conversations.keys()) - sessions_to_keep
                for session_id in old_sessions:
                    del self.conversations[session_id]
                    if session_id in self.summaries:
                        del self.summaries[session_id]
                
                logger.info(f"Cleaned {len(old_sessions)} old conversation sessions")
                
        except Exception as e:
            logger.error(f"Error in auto cleanup: {e}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        return {
            "total_sessions": len(self.conversations),
            "total_messages": sum(len(msgs) for msgs in self.conversations.values()),
            "total_summaries": sum(len(summ) for summ in self.summaries.values()),
            "student_profiles": len(self.student_profiles),
            "memory_efficiency": f"{self.max_conversation_length}/{50}" # Current vs old limit
        }

# Global conversation memory system
conversation_memory = ConversationMemorySystem()