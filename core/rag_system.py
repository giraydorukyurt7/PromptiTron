"""
Unified RAG System combining basic and enhanced features
Supports multiple search strategies and personalization
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional, Union, Tuple
import json
import logging
from datetime import datetime
import hashlib
from core.gemini_client import gemini_client
from config import settings
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class UnifiedRAGSystem:
    def __init__(self):
        """Initialize unified RAG system with enhanced features"""
        # Initialize ChromaDB with multiple collections
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Create collections for different content types
        self.collections = {
            "curriculum": self._get_or_create_collection("yks_curriculum"),
            "conversations": self._get_or_create_collection("conversations"),
            "documents": self._get_or_create_collection("uploaded_documents"),
            "questions": self._get_or_create_collection("generated_questions")
        }
        
        # Cache for embeddings
        self._embedding_cache = {}
        
        # Vectorstore optimization flags
        self._vectorstore_ready = False
        self._curriculum_loaded = False
        self._last_curriculum_hash = None
        
        # Search configuration
        self.default_search_config = {
            "semantic_weight": 0.7,
            "keyword_weight": 0.3,
            "rerank": True,
            "use_mmr": True,
            "mmr_lambda": 0.7
        }
        
        logger.info("Unified RAG system initialized successfully")
        
        # Check if vectorstore is already populated
        self._check_vectorstore_status()
    
    def _get_or_create_collection(self, name: str) -> chromadb.Collection:
        """Get or create a ChromaDB collection"""
        try:
            return self.client.get_collection(name)
        except:
            return self.client.create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
    
    def _check_vectorstore_status(self):
        """Check if vectorstore is already populated with curriculum data"""
        try:
            curriculum_collection = self.collections.get("curriculum")
            if curriculum_collection:
                count = curriculum_collection.count()
                if count > 0:
                    self._curriculum_loaded = True
                    self._vectorstore_ready = True
                    logger.info(f"✅ Vectorstore already populated with {count} curriculum documents")
                    
                    # Check curriculum hash to detect changes
                    self._check_curriculum_changes()
                else:
                    logger.info("📝 Vectorstore is empty, curriculum will be loaded on first use")
            else:
                logger.warning("❌ Could not access curriculum collection")
        except Exception as e:
            logger.error(f"Error checking vectorstore status: {e}")
    
    def _check_curriculum_changes(self):
        """Check if curriculum data has changed since last load"""
        try:
            from pathlib import Path
            import os
            
            # Calculate hash of curriculum files
            curriculum_hash = self._calculate_curriculum_hash()
            
            # Check if hash file exists
            hash_file = Path(settings.CHROMA_PERSIST_DIR) / "curriculum_hash.txt"
            
            if hash_file.exists():
                with open(hash_file, 'r', encoding='utf-8') as f:
                    stored_hash = f.read().strip()
                
                if stored_hash != curriculum_hash:
                    logger.info("🔄 Curriculum data has changed, will reload on next access")
                    self._curriculum_loaded = False
                    self._vectorstore_ready = False
                else:
                    logger.info("✅ Curriculum data is up to date")
            else:
                # First time, save current hash
                self._save_curriculum_hash(curriculum_hash)
                
            self._last_curriculum_hash = curriculum_hash
            
        except Exception as e:
            logger.error(f"Error checking curriculum changes: {e}")
    
    def _calculate_curriculum_hash(self) -> str:
        """Calculate hash of curriculum files to detect changes"""
        try:
            from pathlib import Path
            import hashlib
            
            curriculum_dir = Path(settings.JSON_DIR)
            if not curriculum_dir.exists():
                return "no_curriculum_dir"
            
            hash_content = []
            
            # Hash all JSON files in curriculum directory
            for json_file in curriculum_dir.rglob("*.json"):
                try:
                    stat = json_file.stat()
                    # Include file path, size and modification time
                    hash_content.append(f"{json_file.name}:{stat.st_size}:{stat.st_mtime}")
                except Exception:
                    continue
            
            # Create hash from all file info
            content_str = "|".join(sorted(hash_content))
            return hashlib.md5(content_str.encode('utf-8')).hexdigest()
            
        except Exception as e:
            logger.error(f"Error calculating curriculum hash: {e}")
            return "hash_error"
    
    def _save_curriculum_hash(self, curriculum_hash: str):
        """Save curriculum hash to file"""
        try:
            from pathlib import Path
            
            hash_file = Path(settings.CHROMA_PERSIST_DIR) / "curriculum_hash.txt"
            hash_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(hash_file, 'w', encoding='utf-8') as f:
                f.write(curriculum_hash)
                
            logger.info("💾 Curriculum hash saved")
        except Exception as e:
            logger.error(f"Error saving curriculum hash: {e}")
    
    def is_vectorstore_ready(self) -> bool:
        """Check if vectorstore is ready for use"""
        return self._vectorstore_ready and self._curriculum_loaded
    
    def get_vectorstore_stats(self) -> Dict[str, Any]:
        """Get vectorstore statistics"""
        stats = {
            "ready": self._vectorstore_ready,
            "curriculum_loaded": self._curriculum_loaded,
            "collections": {}
        }
        
        for name, collection in self.collections.items():
            try:
                stats["collections"][name] = collection.count()
            except Exception as e:
                stats["collections"][name] = f"Error: {e}"
        
        return stats
    
    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        collection_name: str = "curriculum",
        batch_size: int = 100
    ) -> bool:
        """
        Add documents to the RAG system
        
        Args:
            documents: List of documents with 'content' and optional metadata
            collection_name: Collection to add documents to
            batch_size: Batch size for processing
        
        Returns:
            Success status
        """
        try:
            collection = self.collections.get(collection_name)
            if not collection:
                logger.error(f"Collection {collection_name} not found")
                return False
            
            # Process in batches
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                
                # Prepare batch data
                ids = []
                embeddings = []
                metadatas = []
                contents = []
                
                for doc in batch:
                    # Generate unique ID with metadata
                    content = doc["content"]
                    metadata_str = str(doc.get("metadata", {}))
                    doc_id = self._generate_document_id(content + metadata_str)
                    
                    # Ensure uniqueness
                    counter = 0
                    original_id = doc_id
                    while doc_id in ids:
                        counter += 1
                        doc_id = f"{original_id}_{counter}"
                    
                    ids.append(doc_id)
                    
                    # Get content and metadata
                    content = doc["content"]
                    metadata = doc.get("metadata", {})
                    metadata["added_at"] = datetime.now().isoformat()
                    
                    contents.append(content)
                    metadatas.append(metadata)
                    
                    # Generate embedding
                    embedding = await self._get_embedding(content, cache_key=doc_id)
                    embeddings.append(embedding)
                
                # Add to collection
                collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=contents,
                    metadatas=metadatas
                )
                
                logger.info(f"Added batch of {len(batch)} documents to {collection_name}")
            
            return True
            
        except RuntimeError as e:
            if "cannot schedule new futures after shutdown" in str(e):
                logger.warning("Document addition skipped due to shutdown")
                return True  # Return True to indicate graceful shutdown, not failure
            else:
                logger.error(f"Runtime error adding documents: {str(e)}")
                return False
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            return False
    
    async def search(
        self,
        query: str,
        collection_names: Optional[List[str]] = None,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        search_config: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Enhanced search with multiple strategies
        
        Args:
            query: Search query
            collection_names: Collections to search (default: all)
            n_results: Number of results
            filter_metadata: Metadata filters
            search_config: Search configuration
            user_context: User context for personalization
        
        Returns:
            Search results with relevance scores
        """
        try:
            # Use default config if not provided
            config = search_config or self.default_search_config
            
            # Select collections
            if collection_names:
                collections = {name: self.collections[name] 
                             for name in collection_names 
                             if name in self.collections}
            else:
                collections = self.collections
            
            # Generate query embedding
            query_embedding = await self._get_embedding(query)
            
            # Debug: Check collection counts
            for coll_name, collection in collections.items():
                count = collection.count()
                logger.info(f"Collection '{coll_name}' has {count} documents")
            
            # Perform searches across collections
            all_results = []
            
            for coll_name, collection in collections.items():
                # Semantic search
                query_params = {
                    "query_embeddings": [query_embedding],
                    "n_results": n_results * 2  # Get more for reranking
                }
                
                # Only add where clause if filters exist
                if filter_metadata:
                    query_params["where"] = filter_metadata
                
                semantic_results = collection.query(**query_params)
                
                # Process results
                for i in range(len(semantic_results["ids"][0])):
                    result = {
                        "id": semantic_results["ids"][0][i],
                        "content": semantic_results["documents"][0][i],
                        "metadata": semantic_results["metadatas"][0][i],
                        "distance": semantic_results["distances"][0][i],
                        "collection": coll_name,
                        "score": 1 - semantic_results["distances"][0][i]  # Convert distance to similarity
                    }
                    all_results.append(result)
            
            # Apply keyword matching if configured
            if config.get("keyword_weight", 0) > 0:
                all_results = await self._apply_keyword_scoring(query, all_results, config)
            
            # Apply personalization if user context provided
            if user_context:
                all_results = await self._apply_personalization(all_results, user_context)
            
            # Sort by combined score
            all_results.sort(key=lambda x: x["score"], reverse=True)
            
            # Apply MMR if configured
            if config.get("use_mmr", False):
                all_results = self._apply_mmr(
                    all_results, 
                    query_embedding, 
                    n_results, 
                    config.get("mmr_lambda", 0.7)
                )
            
            # Rerank using LLM if configured (temporarily disabled for encoding issues)
            # if config.get("rerank", False) and len(all_results) > 0:
            #     all_results = await self._rerank_with_llm(query, all_results[:n_results * 2])
            
            # Return top results
            return all_results[:n_results]
            
        except Exception as e:
            logger.error(f"Error in search: {str(e)}")
            return []
    
    async def add_conversation_to_memory(
        self,
        user_message: str,
        ai_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add conversation to memory for future retrieval"""
        try:
            # Create conversation document
            conversation = f"User: {user_message}\nAssistant: {ai_response}"
            
            doc = {
                "content": conversation,
                "metadata": {
                    **(metadata or {}),
                    "type": "conversation",
                    "user_message": user_message,
                    "ai_response": ai_response,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            return await self.add_documents([doc], collection_name="conversations")
            
        except Exception as e:
            logger.error(f"Error adding conversation to memory: {str(e)}")
            return False
    
    async def get_relevant_conversations(
        self,
        current_query: str,
        user_id: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Get relevant past conversations"""
        try:
            filters = {"type": "conversation"}
            if user_id:
                filters["user_id"] = user_id
            
            results = await self.search(
                query=current_query,
                collection_names=["conversations"],
                n_results=top_k,
                filter_metadata=filters
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting relevant conversations: {str(e)}")
            return []
    
    async def generate_answer_with_context(
        self,
        question: str,
        context_docs: Optional[List[Dict[str, Any]]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate answer using retrieved context"""
        try:
            # Retrieve context if not provided
            if not context_docs:
                context_docs = await self.search(
                    query=question,
                    n_results=5,
                    user_context=user_context
                )
            
            # Build context
            context_parts = []
            for doc in context_docs:
                content = doc["content"]
                source = doc["metadata"].get("source", "Unknown")
                context_parts.append(f"[Kaynak: {source}]\n{content}")
            
            context = "\n\n".join(context_parts)
            
            # Generate answer
            prompt = f"""Asagidaki baglam bilgilerini kullanarak soruyu cevapla:

Baglam:
{context}

Soru: {question}

Lutfen baglam bilgilerini kullanarak detayli ve dogru bir cevap ver.
"""
            
            response = await gemini_client.generate_content(
                prompt=prompt,
                system_instruction="Sen YKS uzmani bir egitmensin. Verilen baglam bilgilerini kullanarak sorulari dogru ve detayli cevapla."
            )
            
            return response["text"]
            
        except Exception as e:
            logger.error(f"Error generating answer with context: {str(e)}")
            return "Uzgunum, sorunuzu cevaplayamadim."
    
    async def _get_embedding(self, text: str, cache_key: Optional[str] = None) -> List[float]:
        """Get embedding with caching"""
        try:
            # Check cache
            if cache_key and cache_key in self._embedding_cache:
                return self._embedding_cache[cache_key]
            
            # Generate embedding
            embedding = await gemini_client.generate_embeddings(text)
            
            # Cache if key provided
            if cache_key:
                self._embedding_cache[cache_key] = embedding
            
            return embedding
            
        except RuntimeError as e:
            if "cannot schedule new futures after shutdown" in str(e):
                logger.warning("Embedding generation skipped due to shutdown")
                # Re-raise the exception to stop processing during shutdown
                raise
            else:
                logger.error(f"Runtime error getting embedding: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            raise
    
    def _generate_document_id(self, content: str) -> str:
        """Generate unique document ID"""
        return hashlib.md5(content.encode()).hexdigest()
    
    async def _apply_keyword_scoring(
        self,
        query: str,
        results: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply keyword-based scoring"""
        try:
            query_terms = set(query.lower().split())
            
            for result in results:
                content = result["content"].lower()
                
                # Calculate keyword match score
                content_terms = set(content.split())
                common_terms = query_terms.intersection(content_terms)
                keyword_score = len(common_terms) / len(query_terms) if query_terms else 0
                
                # Combine with semantic score
                semantic_weight = config.get("semantic_weight", 0.7)
                keyword_weight = config.get("keyword_weight", 0.3)
                
                result["score"] = (
                    semantic_weight * result["score"] +
                    keyword_weight * keyword_score
                )
            
            return results
            
        except Exception as e:
            logger.error(f"Error applying keyword scoring: {str(e)}")
            return results
    
    async def _apply_personalization(
        self,
        results: List[Dict[str, Any]],
        user_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply personalization based on user context"""
        try:
            # Boost results matching user's weak subjects
            weak_subjects = user_context.get("weak_subjects", [])
            if weak_subjects:
                for result in results:
                    subject = result["metadata"].get("subject", "")
                    if any(weak in subject.lower() for weak in weak_subjects):
                        result["score"] *= 1.2  # Boost by 20%
            
            # Boost results matching user's exam target
            exam_target = user_context.get("exam_target")
            if exam_target:
                for result in results:
                    if exam_target in result["metadata"].get("exam_type", ""):
                        result["score"] *= 1.1  # Boost by 10%
            
            return results
            
        except Exception as e:
            logger.error(f"Error applying personalization: {str(e)}")
            return results
    
    def _apply_mmr(
        self,
        results: List[Dict[str, Any]],
        query_embedding: List[float],
        n_results: int,
        lambda_param: float
    ) -> List[Dict[str, Any]]:
        """Apply Maximum Marginal Relevance for diversity"""
        try:
            if not results:
                return results
            
            # Initialize with first result
            selected = [results[0]]
            candidates = results[1:]
            
            while len(selected) < n_results and candidates:
                # Calculate MMR scores
                mmr_scores = []
                
                for candidate in candidates:
                    # Get candidate embedding
                    cand_embedding = candidate.get("embedding")
                    if not cand_embedding:
                        # Use content to regenerate if needed
                        mmr_scores.append(candidate["score"])
                        continue
                    
                    # Relevance to query
                    relevance = candidate["score"]
                    
                    # Maximum similarity to selected documents
                    max_sim = 0
                    for selected_doc in selected:
                        sel_embedding = selected_doc.get("embedding")
                        if sel_embedding:
                            sim = cosine_similarity(
                                [cand_embedding], 
                                [sel_embedding]
                            )[0][0]
                            max_sim = max(max_sim, sim)
                    
                    # MMR score
                    mmr = lambda_param * relevance - (1 - lambda_param) * max_sim
                    mmr_scores.append(mmr)
                
                # Select best candidate
                best_idx = np.argmax(mmr_scores)
                selected.append(candidates[best_idx])
                candidates.pop(best_idx)
            
            return selected
            
        except Exception as e:
            logger.error(f"Error applying MMR: {str(e)}")
            return results[:n_results]
    
    async def _rerank_with_llm(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rerank results using LLM"""
        try:
            # Prepare reranking prompt
            candidates = []
            for i, result in enumerate(results):
                candidates.append(f"{i+1}. {result['content'][:200]}...")
            
            prompt = f"""Asagidaki sorguya en uygun sonuclari sirala:

Sorgu: {query}

Adaylar:
{chr(10).join(candidates)}

En uygun siralama (sadece numaralari virgulle ayirarak yaz):"""
            
            response = await gemini_client.generate_content(
                prompt=prompt,
                system_instruction="Sen bir arama sonucu siralama uzmanisin.",
                temperature=0.1
            )
            
            # Parse ranking
            try:
                ranking = [int(x.strip()) - 1 for x in response["text"].split(",")]
                reranked = []
                
                for idx in ranking:
                    if 0 <= idx < len(results):
                        reranked.append(results[idx])
                
                # Add any missing results
                for result in results:
                    if result not in reranked:
                        reranked.append(result)
                
                return reranked
                
            except:
                # Return original if parsing fails
                return results
                
        except Exception as e:
            logger.error(f"Error in LLM reranking: {str(e)}")
            return results
    
    async def reload_curriculum_data(self, json_dir: str = None) -> bool:
        """Reload curriculum data - clear existing and load fresh"""
        try:
            logger.info("🔄 Reloading curriculum data - clearing existing collection")
            
            # Clear existing curriculum collection
            await self.clear_collection("curriculum")
            
            # Reset flags
            self._curriculum_loaded = False
            self._vectorstore_ready = False
            
            # Load fresh data (force reload)
            return await self.load_curriculum_data(json_dir, force_reload=True)
            
        except Exception as e:
            logger.error(f"Error reloading curriculum data: {str(e)}")
            return False
    
    async def clear_collection(self, collection_name: str) -> bool:
        """Clear all documents from a collection"""
        try:
            collection = self._get_or_create_collection(collection_name)
            if collection:
                # Get all document IDs
                all_data = collection.get()
                all_ids = all_data.get('ids', [])
                
                if all_ids:
                    collection.delete(ids=all_ids)
                    logger.info(f"Cleared {len(all_ids)} documents from collection '{collection_name}'")
                    return True
                else:
                    logger.info(f"Collection '{collection_name}' was already empty")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error clearing collection {collection_name}: {str(e)}")
            return False

    async def load_curriculum_data(self, json_dir: str = None, force_reload: bool = False) -> bool:
        """Load YKS curriculum data using unified curriculum loader with optimization"""
        try:
            # Check if already loaded and up to date (unless forced)
            if not force_reload and self.is_vectorstore_ready():
                logger.info("⚡ Vectorstore already loaded and ready - skipping curriculum load")
                return True
            
            logger.info("📚 Loading curriculum data into vectorstore...")
            start_time = datetime.now()
            
            from core.curriculum_loader import curriculum_loader
            
            # Use curriculum_loader to load all data consistently
            success = curriculum_loader.load_all_curriculum(json_dir)
            
            if not success:
                logger.error("Failed to load curriculum data via curriculum_loader")
                return False
                
            # Convert curriculum_loader topics to RAG documents
            documents = []
            
            for topic in curriculum_loader.flat_topics:
                # Create comprehensive content from topic data
                content_parts = []
                
                # Add title if available
                if topic.get('title'):
                    content_parts.append(f"Baslik: {topic['title']}")
                    
                # Add content if available
                if topic.get('content'):
                    content_parts.append(f"Icerik: {topic['content']}")
                    
                # Add terms if available
                if topic.get('terms'):
                    content_parts.append(f"Terimler: {topic['terms']}")
                    
                # Add symbols if available
                if topic.get('symbols'):
                    content_parts.append(f"Semboller: {topic['symbols']}")
                
                content = "\n".join(content_parts)
                
                # Create document with rich metadata
                doc = {
                    "content": content,
                    "metadata": {
                        "subject": topic.get('subject', ''),
                        "grade": topic.get('grade', ''),
                        "code": topic.get('code', ''),
                        "path": topic.get('path', ''),
                        "title": topic.get('title', ''),
                        "unit": topic.get('unit', ''),
                        "exam_type": "YKS",
                        "source": "curriculum_loader",
                        "topic_type": "curriculum"
                    }
                }
                
                # Only add if there's meaningful content
                if content.strip():
                    documents.append(doc)
            
            # Add documents to RAG
            if documents:
                success = await self.add_documents(documents, collection_name="curriculum")
                
                if success:
                    # Update status flags
                    self._curriculum_loaded = True
                    self._vectorstore_ready = True
                    
                    # Save curriculum hash to track changes
                    current_hash = self._calculate_curriculum_hash()
                    self._save_curriculum_hash(current_hash)
                    self._last_curriculum_hash = current_hash
                    
                    # Log performance
                    load_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ Loaded {len(documents)} curriculum documents in {load_time:.2f}s")
                    logger.info(f"📊 Total topics processed: {len(curriculum_loader.flat_topics)}")
                    
                    return True
                else:
                    logger.error("Failed to add curriculum documents to vectorstore")
                    return False
            
            logger.warning("No valid curriculum documents found to add to RAG")
            return False
            
        except Exception as e:
            logger.error(f"Error loading curriculum data: {str(e)}")
            return False
    
    def _process_yks_curriculum(self, data: Dict, subject: str, source: str) -> List[Dict]:
        """Process YKS hierarchical curriculum structure"""
        documents = []
        
        try:
            # Handle YKS curriculum structure
            if 'yks' in data:
                yks_data = data['yks']
                
                # Find subject data (matematik, fizik, etc.)
                subject_key = self._find_subject_key(yks_data, subject)
                if subject_key and subject_key in yks_data:
                    subject_data = yks_data[subject_key]
                    documents.extend(self._process_grade_levels(subject_data, subject, source))
            
            # Handle direct subject data structure
            elif isinstance(data, dict) and "topics" in data:
                for topic in data["topics"]:
                    # Create document for each topic
                    content = f"{topic.get('name', '')}\n{topic.get('description', '')}"
                    
                    doc = {
                        "content": content,
                        "metadata": {
                            "subject": subject,
                            "topic": topic.get('name', ''),
                            "source": source,
                            "exam_type": data.get('exam_type', 'YKS')
                        }
                    }
                    
                    # Add subtopics if available
                    if "subtopics" in topic:
                        for subtopic in topic["subtopics"]:
                            subdoc = {
                                "content": f"{subtopic.get('name', '')}\n{subtopic.get('details', '')}",
                                "metadata": {
                                    "subject": subject,
                                    "topic": topic.get('name', ''),
                                    "subtopic": subtopic.get('name', ''),
                                    "source": source,
                                    "exam_type": data.get('exam_type', 'YKS')
                                }
                            }
                            documents.append(subdoc)
                    
                    documents.append(doc)
            
            # Fallback - treat as general document
            else:
                content = json.dumps(data, ensure_ascii=False, indent=2)[:2000]  # Limit size
                doc = {
                    "content": content,
                    "metadata": {
                        "subject": subject,
                        "source": source,
                        "exam_type": "YKS",
                        "type": "curriculum_data"
                    }
                }
                documents.append(doc)
                
        except Exception as e:
            logger.error(f"Error processing YKS curriculum for {subject}: {e}")
            
        return documents
    
    def _find_subject_key(self, yks_data: Dict, subject: str) -> Optional[str]:
        """Find the correct subject key in YKS data"""
        subject_lower = subject.lower()
        
        # Map subject names to JSON keys
        subject_mapping = {
            'matematik': 'matematik',
            'fizik': 'fizik',
            'kimya': 'kimya', 
            'biyoloji': 'biyoloji',
            'tarih': 'tarih',
            'cografya': 'cografya',
            'cografya': 'cografya',
            'felsefe': 'felsefe',
            'din kulturu': 'din_kulturu',
            'turk dili ve edebiyati': 'turk_dili_ve_edebiyati',
            'turk dili ve edebiyati': 'turk_dili_ve_edebiyati',
            'inkilap ve ataturkculuk': 'inkilap_ve_ataturkculuk',
            'inkilap ve ataturkculuk': 'inkilap_ve_ataturkculuk'
        }
        
        # Try direct mapping first
        if subject_lower in subject_mapping:
            mapped_key = subject_mapping[subject_lower]
            if mapped_key in yks_data:
                return mapped_key
        
        # Try direct match
        if subject_lower in yks_data:
            return subject_lower
            
        # Fuzzy matching
        for key in yks_data.keys():
            if subject_lower in key.lower() or key.lower() in subject_lower:
                return key
                
        return None
    
    def _process_grade_levels(self, subject_data: Dict, subject: str, source: str) -> List[Dict]:
        """Process grade level structure (9, 10, 11, 12)"""
        documents = []
        
        for grade, grade_data in subject_data.items():
            if isinstance(grade_data, dict) and 'alt' in grade_data:
                docs = self._process_curriculum_level(
                    grade_data['alt'], subject, f"Sinif {grade}", source
                )
                documents.extend(docs)
                
        return documents
    
    def _process_curriculum_level(self, level_data: Dict, subject: str, grade: str, source: str, parent_path: str = "") -> List[Dict]:
        """Recursively process curriculum levels"""
        documents = []
        
        for key, item_data in level_data.items():
            if isinstance(item_data, dict):
                current_path = f"{parent_path}.{key}" if parent_path else key
                
                # Build content from all available information
                content_parts = []
                
                if 'baslik' in item_data:
                    content_parts.append(f"Baslik: {item_data['baslik']}")
                
                if 'terimler_ve_kavramlar' in item_data:
                    content_parts.append(f"Terimler ve Kavramlar: {item_data['terimler_ve_kavramlar']}")
                
                if 'sembol_ve_gosterimler' in item_data:
                    content_parts.append(f"Semboller: {item_data['sembol_ve_gosterimler']}")
                
                # Process explanations (aciklama)
                if 'aciklama' in item_data:
                    explanations = self._extract_explanations(item_data['aciklama'])
                    if explanations:
                        content_parts.append(f"Aciklama: {explanations}")
                
                content = "\n".join(content_parts)
                
                if content.strip():  # Only add if there's content
                    doc = {
                        "content": content,
                        "metadata": {
                            "subject": subject,
                            "grade": grade,
                            "code": key,
                            "title": item_data.get('baslik', ''),
                            "path": current_path,
                            "source": source,
                            "exam_type": "YKS",
                            "type": "curriculum_topic"
                        }
                    }
                    documents.append(doc)
                
                # Process sub-levels recursively
                if 'alt' in item_data:
                    sub_docs = self._process_curriculum_level(
                        item_data['alt'], subject, grade, source, current_path
                    )
                    documents.extend(sub_docs)
                    
        return documents
    
    def _extract_explanations(self, aciklama_data: Any) -> str:
        """Extract explanations from aciklama field"""
        explanations = []
        
        if isinstance(aciklama_data, dict):
            for key, value in aciklama_data.items():
                if isinstance(value, str):
                    explanations.append(f"({key}) {value}")
                    
        elif isinstance(aciklama_data, str):
            explanations.append(aciklama_data)
            
        elif isinstance(aciklama_data, list):
            for item in aciklama_data:
                if isinstance(item, str):
                    explanations.append(item)
                    
        return " ".join(explanations)
    
    async def initialize(self) -> bool:
        """
        Initialize the RAG system
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Test ChromaDB connection
            test_doc = {
                "content": "Test document for initialization",
                "metadata": {"test": True}
            }
            await self.add_documents([test_doc], collection_name="test")
            logger.info("RAG system initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            return False

# Global RAG system instance
rag_system = UnifiedRAGSystem()