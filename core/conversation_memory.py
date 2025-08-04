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
        pass
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
        pass
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
        pass
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
        pass
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
            Asagidaki ogrenci sohbetini analiz et ve ogrenme durumu hakkinda bilgi cikar:

            Sohbet:
            {conversation_text}

            Analiz et:
            1. Ogrencinin guclu oldugu konular
            2. Zayif oldugu konular
            3. Ogrenme stili tercihleri
            4. Motivasyon durumu
            5. Anlamakta zorlandigi kavramlar
            6. Oneriler

            JSON formatinda detayli analiz ver.
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
        pass
        try:
            if session_id not in self.conversations:
                return
            
            messages = self.conversations[session_id][-self.summary_threshold:]
            conversation_text = "\n".join([
                f"{msg.role.value}: {msg.content}" for msg in messages
            ])
            
            summary_prompt = f"""
            Bu sohbet bolumunu ozetle:
            {conversation_text}
            
            Onemli noktalar:
            - Konusulan ana konular
            - Ogrenme hedefleri
            - Ogrencinin anlama seviyesi
            - Zayif alanlar
            - Onerilen adimlar
            - Genel duygu durumu (pozitif/notr/frustre)
            response = await gemini_client.generate_structured_output(
                prompt=summary_prompt,
                response_model=ConversationSummary,
                system_instruction="Sen sohbet ozetlemede uzman bir egitim danismanisin."
            )
            
            if session_id not in self.summaries:
                self.summaries[session_id] = []
            
            self.summaries[session_id].append(response)
            
            # Keep only last 5 summaries
            self.summaries[session_id] = self.summaries[session_id][-5:]
            
        except Exception as e:
            logger.error(f"Error creating conversation summary: {str(e)}")
    
    async def _summarize_old_messages(self, session_id: str) -> None:
        pass
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
        pass
        # Simple heuristics for learning style detection
        visual_keywords = ["gorsel", "resim", "diyagram", "sekil", "grafik", "goruyorum", "sema"]
        auditory_keywords = ["dinleme", "aciklama", "anlatma", "duyuyorum", "ses", "konusma"]
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
        pass
        hints = []
        
        if not profile:
            return ["Yeni ogrenci - temel seviyeden basla"]
        
        # Learning style hints
        if profile.learning_style == "visual":
            hints.append("Gorsel ornekler, diyagramlar ve semalar kullan")
        elif profile.learning_style == "auditory":
            hints.append("Acik anlatimlar ve adim adim aciklamalar ver")
        else:
            hints.append("Pratik uygulamalar ve hands-on ornekler sun")
        
        # Subject-specific hints
        if profile.weak_subjects:
            hints.append(f"Zayif konulara odaklan: {', '.join(profile.weak_subjects)}")
        
        # Difficulty hints
        if profile.difficulty_preference == "easy":
            hints.append("Basit orneklerle basla, yavas yavas zorlastir")
        elif profile.difficulty_preference == "hard":
            hints.append("Zorlu ornekler ve derin analiz sun")
        
        # Exam-specific hints
        if profile.exam_target == "YKS":
            hints.append("YKS formatinda sorular ve stratejiler ver")
        elif profile.exam_target == "LGS":
            hints.append("LGS seviyesine uygun aciklamalar yap")
        
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
                hints.append(f"Gelisim gosteren konular: {', '.join(improving_subjects)} - Motive et")
            if declining_subjects:
                hints.append(f"Dusus gosteren konular: {', '.join(declining_subjects)} - Ekstra destek ver")
        
        # Time-based hints
        if profile.last_activity:
            days_since_last = (datetime.now() - profile.last_activity).days
            if days_since_last > 7:
                hints.append("Uzun aradan sonra donus - Kisa tekrar yap")
        
        return hints
    
    def _calculate_adaptive_difficulty(self, profile: Optional[StudentProfile]) -> str:
        pass
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
        pass
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
        pass
        return {
            "total_sessions": len(self.conversations),
            "total_messages": sum(len(msgs) for msgs in self.conversations.values()),
            "total_summaries": sum(len(summ) for summ in self.summaries.values()),
            "student_profiles": len(self.student_profiles),
            "memory_efficiency": f"{self.max_conversation_length}/{50}" # Current vs old limit
        }

# Global conversation memory system
conversation_memory = ConversationMemorySystem()