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
import pickle
import os

logger = logging.getLogger(__name__)

class UnifiedRAGSystem:
    def __init__(self):
        """Initialize unified RAG system with enhanced features"""
        # Vectorstore cache paths
        self.vectorstore_cache_dir = os.path.join(settings.CHROMA_PERSIST_DIR, "cache")
        self.embedding_cache_path = os.path.join(self.vectorstore_cache_dir, "embedding_cache.pkl")
        self.collections_cache_path = os.path.join(self.vectorstore_cache_dir, "collections_cache.pkl")
        
        # Create cache directory if not exists
        os.makedirs(self.vectorstore_cache_dir, exist_ok=True)
        
        # Initialize ChromaDB with multiple collections
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Load or create collections
        self.collections = self._load_or_create_collections()
        
        # Load or initialize embedding cache
        self._embedding_cache = self._load_embedding_cache()
        
        # Search configuration
        self.default_search_config = {
            "semantic_weight": 0.7,
            "keyword_weight": 0.3,
            "rerank": True,
            "use_mmr": True,
            "mmr_lambda": 0.7
        }
        
        logger.info("Unified RAG system initialized successfully")
        
        # Ensure all required collections exist
        self._ensure_all_collections()
    
    def _ensure_all_collections(self):
        """Ensure all required collections exist"""
        required_collections = {
            "curriculum": "yks_curriculum",
            "conversations": "conversations", 
            "documents": "uploaded_documents",
            "questions": "generated_questions",
            "web_content": "web_content",
            "youtube_content": "youtube_content"
        }
        
        for key, actual_name in required_collections.items():
            if key not in self.collections:
                logger.info(f"Creating missing collection: {key} ({actual_name})")
                collection = self._get_or_create_collection(actual_name)
                self.collections[key] = collection
    
    def _load_or_create_collections(self) -> Dict[str, chromadb.Collection]:
        """Load cached collections or create new ones"""
        try:
            # Try to load from cache first
            if os.path.exists(self.collections_cache_path):
                logger.info("Loading collections from cache...")
                collections = {}
                collection_names = ["yks_curriculum", "conversations", "uploaded_documents", "generated_questions", "web_content", "youtube_content"]
                
                for name in collection_names:
                    try:
                        collection = self.client.get_collection(name)
                        # Map collection names to simplified keys
                        key = name.replace("yks_", "")
                        if name == "web_content":
                            key = "web_content"
                        elif name == "youtube_content":  
                            key = "youtube_content"
                        collections[key] = collection
                        logger.info(f"Loaded collection '{name}' from cache")
                    except:
                        # Create if not found
                        collection = self.client.create_collection(
                            name=name,
                            metadata={"hnsw:space": "cosine"}
                        )
                        key = name.replace("yks_", "")
                        if name == "web_content":
                            key = "web_content"
                        elif name == "youtube_content":  
                            key = "youtube_content"
                        collections[key] = collection
                        logger.info(f"Created new collection '{name}'")
                
                return collections
            else:
                # Create fresh collections
                logger.info("Creating fresh collections...")
                collections = {
                    "curriculum": self._get_or_create_collection("yks_curriculum"),
                    "conversations": self._get_or_create_collection("conversations"),
                    "documents": self._get_or_create_collection("uploaded_documents"),
                    "questions": self._get_or_create_collection("generated_questions"),
                    "web_content": self._get_or_create_collection("web_content"),
                    "youtube_content": self._get_or_create_collection("youtube_content")
                }
                
                # Save cache marker
                self._save_collections_cache()
                return collections
                
        except Exception as e:
            logger.error(f"Error loading collections: {e}")
            # Fallback to creating fresh collections
            return {
                "curriculum": self._get_or_create_collection("yks_curriculum"),
                "conversations": self._get_or_create_collection("conversations"),
                "documents": self._get_or_create_collection("uploaded_documents"),
                "questions": self._get_or_create_collection("generated_questions"),
                "web_content": self._get_or_create_collection("web_content"),
                "youtube_content": self._get_or_create_collection("youtube_content")
            }

    def _get_or_create_collection(self, name: str) -> chromadb.Collection:
        """Get or create a ChromaDB collection"""
        try:
            # First try to get existing collection
            try:
                collection = self.client.get_collection(name)
                logger.info(f"Found existing collection: {name}")
                return collection
            except Exception:
                # Collection doesn't exist, create it
                logger.info(f"Creating new collection: {name}")
                return self.client.create_collection(
                    name=name,
                    metadata={"hnsw:space": "cosine"}
                )
        except Exception as e:
            logger.error(f"Error creating collection {name}: {e}")
            raise
    
    def _load_embedding_cache(self) -> Dict[str, List[float]]:
        """Load embedding cache from disk"""
        try:
            if os.path.exists(self.embedding_cache_path):
                with open(self.embedding_cache_path, 'rb') as f:
                    cache = pickle.load(f)
                    logger.info(f"Loaded {len(cache)} embeddings from cache")
                    return cache
        except Exception as e:
            logger.warning(f"Could not load embedding cache: {e}")
        
        return {}
    
    def _save_embedding_cache(self):
        """Save embedding cache to disk"""
        try:
            with open(self.embedding_cache_path, 'wb') as f:
                pickle.dump(self._embedding_cache, f)
                logger.info(f"Saved {len(self._embedding_cache)} embeddings to cache")
        except Exception as e:
            logger.error(f"Error saving embedding cache: {e}")
            
    def _save_collections_cache(self):
        """Save collections cache marker"""
        try:
            with open(self.collections_cache_path, 'w') as f:
                json.dump({"cached": True, "timestamp": datetime.now().isoformat()}, f)
        except Exception as e:
            logger.error(f"Error saving collections cache: {e}")
    
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
                logger.warning(f"Collection {collection_name} not found, creating it...")
                # Create the collection dynamically
                collection = self._get_or_create_collection(collection_name)
                self.collections[collection_name] = collection
                logger.info(f"Created collection {collection_name}")
                
                if not collection:
                    logger.error(f"Failed to create collection {collection_name}")
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
                collections = {}
                for name in collection_names:
                    if name in self.collections:
                        collections[name] = self.collections[name]
                    else:
                        logger.warning(f"Collection {name} not found, creating it...")
                        collection = self._get_or_create_collection(name)
                        if collection:
                            self.collections[name] = collection
                            collections[name] = collection
                            logger.info(f"Created collection {name}")
                        else:
                            logger.error(f"Failed to create collection {name}")
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
            prompt = f"""Aşağıdaki bağlam bilgilerini kullanarak soruyu cevapla:

Bağlam:
{context}

Soru: {question}

Lütfen bağlam bilgilerini kullanarak detaylı ve doğru bir cevap ver."""
            
            response = await gemini_client.generate_content(
                prompt=prompt,
                system_instruction="Sen YKS uzmanı bir eğitmensin. Verilen bağlam bilgilerini kullanarak soruları doğru ve detaylı cevapla."
            )
            
            return response["text"]
            
        except Exception as e:
            logger.error(f"Error generating answer with context: {str(e)}")
            return "Üzgünüm, sorunuzu cevaplayamadım."
    
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
                # Periodically save cache (every 10 new embeddings)
                if len(self._embedding_cache) % 10 == 0:
                    self._save_embedding_cache()
            
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
            
            prompt = f"""Aşağıdaki sorguya en uygun sonuçları sırala:

Sorgu: {query}

Adaylar:
{chr(10).join(candidates)}

En uygun sıralama (sadece numaraları virgülle ayırarak yaz):"""
            
            response = await gemini_client.generate_content(
                prompt=prompt,
                system_instruction="Sen bir arama sonucu sıralama uzmanısın.",
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
            logger.info("Reloading curriculum data - clearing existing collection")
            
            # Clear existing curriculum collection
            await self.clear_collection("curriculum")
            
            # Load fresh data
            return await self.load_curriculum_data(json_dir)
            
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
        """Load YKS curriculum data using unified curriculum loader with caching"""
        try:
            # Check if curriculum is already loaded (unless force reload)
            if not force_reload:
                curriculum_collection = self.collections.get("curriculum")
                if curriculum_collection and curriculum_collection.count() > 0:
                    logger.info(f"Curriculum already loaded ({curriculum_collection.count()} documents). Use force_reload=True to reload.")
                    return True
            
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
                    content_parts.append(f"Başlık: {topic['title']}")
                    
                # Add content if available
                if topic.get('content'):
                    content_parts.append(f"İçerik: {topic['content']}")
                    
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
                # Clear existing if force reload
                if force_reload:
                    await self.clear_collection("curriculum")
                
                success = await self.add_documents(documents, collection_name="curriculum")
                
                # Save cache after loading
                self._save_embedding_cache()
                self._save_collections_cache()
                
                logger.info(f"Loaded {len(documents)} curriculum documents from curriculum_loader")
                logger.info(f"Total topics processed: {len(curriculum_loader.flat_topics)}")
                return success
            
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
            'coğrafya': 'cografya',
            'cografya': 'cografya',
            'felsefe': 'felsefe',
            'din kulturu': 'din_kulturu',
            'türk dili ve edebiyatı': 'turk_dili_ve_edebiyati',
            'turk dili ve edebiyati': 'turk_dili_ve_edebiyati',
            'inkılap ve atatürkçülük': 'inkilap_ve_ataturkculuk',
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
                    grade_data['alt'], subject, f"Sınıf {grade}", source
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
                    content_parts.append(f"Başlık: {item_data['baslik']}")
                
                if 'terimler_ve_kavramlar' in item_data:
                    content_parts.append(f"Terimler ve Kavramlar: {item_data['terimler_ve_kavramlar']}")
                
                if 'sembol_ve_gosterimler' in item_data:
                    content_parts.append(f"Semboller: {item_data['sembol_ve_gosterimler']}")
                
                # Process explanations (aciklama)
                if 'aciklama' in item_data:
                    explanations = self._extract_explanations(item_data['aciklama'])
                    if explanations:
                        content_parts.append(f"Açıklama: {explanations}")
                
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

    async def search_curriculum_topics(
        self,
        selected_topics: List[Dict[str, Any]],
        query: Optional[str] = None,
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for curriculum content based on selected topics"""
        try:
            # Build search filters from selected topics
            search_filters = []
            subjects = set()
            grades = set()
            
            for topic_data in selected_topics:
                if topic_data.get("ders"):
                    subjects.add(topic_data["ders"])
                if topic_data.get("sinif"):
                    grades.add(topic_data["sinif"])
            
            # Create comprehensive search query
            if query:
                search_query = query
            else:
                # Build query from selected topics
                topic_titles = [topic.get("title", "") for topic in selected_topics if topic.get("title")]
                search_query = " ".join(topic_titles[:5])  # Limit to avoid too long queries
            
            # Perform search with curriculum focus
            results = await self.search(
                query=search_query,
                collection_names=["curriculum"],
                n_results=n_results,
                filter_metadata=None  # Will filter manually
            )
            
            # Filter results based on selected topics
            filtered_results = []
            for result in results:
                metadata = result.get("metadata", {})
                
                # Check if result matches selected topics
                matches_topic = False
                
                # Check subject match
                if subjects and metadata.get("subject") in subjects:
                    matches_topic = True
                
                # Check grade match
                if grades and metadata.get("grade") in grades:
                    matches_topic = True
                
                # Check title/content match
                for topic_data in selected_topics:
                    if topic_data.get("title"):
                        title = topic_data["title"].lower()
                        content = result.get("content", "").lower()
                        if title in content or any(word in content for word in title.split()):
                            matches_topic = True
                            break
                
                if matches_topic:
                    filtered_results.append(result)
            
            logger.info(f"Curriculum search returned {len(filtered_results)} filtered results from {len(results)} total")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error searching curriculum topics: {str(e)}")
            return []
    
    async def get_related_curriculum_content(
        self,
        selected_topics: List[Dict[str, Any]],
        relation_type: str = "similar"  # similar, prerequisite, advanced
    ) -> List[Dict[str, Any]]:
        """Get related curriculum content based on selected topics"""
        try:
            # Extract key information from selected topics
            subjects = []
            grades = []
            concepts = []
            
            for topic_data in selected_topics:
                if topic_data.get("ders"):
                    subjects.append(topic_data["ders"])
                if topic_data.get("sinif"):
                    grades.append(topic_data["sinif"])
                if topic_data.get("title"):
                    concepts.append(topic_data["title"])
            
            # Build relation-based search queries
            related_results = []
            
            if relation_type == "similar":
                # Find similar topics in same subject/grade
                for subject in set(subjects):
                    for grade in set(grades):
                        similar_query = f"{subject} {grade}. sınıf"
                        results = await self.search(
                            query=similar_query,
                            collection_names=["curriculum"],
                            n_results=5,
                            filter_metadata={"subject": subject, "grade": grade}
                        )
                        related_results.extend(results)
                        
            elif relation_type == "prerequisite":
                # Find prerequisite topics (lower grades, foundational concepts)
                for subject in set(subjects):
                    for grade in set(grades):
                        try:
                            prev_grade = str(int(grade) - 1) if grade.isdigit() else grade
                            prereq_query = f"{subject} {prev_grade}. sınıf temel"
                            results = await self.search(
                                query=prereq_query,
                                collection_names=["curriculum"],
                                n_results=3,
                                filter_metadata={"subject": subject, "grade": prev_grade}
                            )
                            related_results.extend(results)
                        except ValueError:
                            continue
                            
            elif relation_type == "advanced":
                # Find advanced topics (higher grades, complex concepts)
                for subject in set(subjects):
                    for grade in set(grades):
                        try:
                            next_grade = str(int(grade) + 1) if grade.isdigit() else grade
                            advanced_query = f"{subject} {next_grade}. sınıf ileri"
                            results = await self.search(
                                query=advanced_query,
                                collection_names=["curriculum"],
                                n_results=3,
                                filter_metadata={"subject": subject, "grade": next_grade}
                            )
                            related_results.extend(results)
                        except ValueError:
                            continue
            
            # Remove duplicates and limit results
            seen_ids = set()
            unique_results = []
            for result in related_results:
                result_id = result.get("id")
                if result_id not in seen_ids:
                    seen_ids.add(result_id)
                    unique_results.append(result)
                    
                if len(unique_results) >= 15:  # Limit total results
                    break
            
            logger.info(f"Found {len(unique_results)} related curriculum topics ({relation_type})")
            return unique_results
            
        except Exception as e:
            logger.error(f"Error getting related curriculum content: {str(e)}")
            return []
    
    async def analyze_curriculum_coverage(
        self,
        selected_topics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze curriculum coverage and gaps for selected topics"""
        try:
            # Extract subjects and grades
            subjects = {}
            all_grades = set()
            
            for topic_data in selected_topics:
                subject = topic_data.get("ders", "Unknown")
                grade = topic_data.get("sinif", "Unknown")
                
                if subject not in subjects:
                    subjects[subject] = {"grades": set(), "topics": []}
                
                subjects[subject]["grades"].add(grade)
                subjects[subject]["topics"].append(topic_data.get("title", ""))
                all_grades.add(grade)
            
            # Analyze coverage for each subject
            coverage_analysis = {}
            
            for subject, data in subjects.items():
                # Get all available topics for this subject
                all_topics_query = f"{subject} müfredat konular"
                all_available = await self.search(
                    query=all_topics_query,
                    collection_names=["curriculum"],
                    n_results=50,
                    filter_metadata={"subject": subject}
                )
                
                # Calculate coverage metrics
                total_available = len(all_available)
                selected_count = len(data["topics"])
                coverage_percentage = (selected_count / total_available * 100) if total_available > 0 else 0
                
                # Find missing important topics
                available_titles = {result.get("metadata", {}).get("title", "").lower() 
                                 for result in all_available}
                selected_titles = {title.lower() for title in data["topics"] if title}
                missing_topics = available_titles - selected_titles
                
                coverage_analysis[subject] = {
                    "total_available_topics": total_available,
                    "selected_topics_count": selected_count,
                    "coverage_percentage": round(coverage_percentage, 2),
                    "grades_covered": list(data["grades"]),
                    "missing_topics_sample": list(missing_topics)[:10],  # Sample of missing topics
                    "coverage_status": "High" if coverage_percentage > 70 else "Medium" if coverage_percentage > 40 else "Low"
                }
            
            # Overall analysis
            total_selected = len(selected_topics)
            subjects_count = len(subjects)
            
            analysis_result = {
                "overall_metrics": {
                    "total_selected_topics": total_selected,
                    "subjects_covered": subjects_count,
                    "grades_covered": list(all_grades),
                    "avg_coverage_per_subject": round(sum(s["coverage_percentage"] for s in coverage_analysis.values()) / subjects_count, 2) if subjects_count > 0 else 0
                },
                "subject_analysis": coverage_analysis,
                "recommendations": []
            }
            
            # Generate recommendations
            for subject, analysis in coverage_analysis.items():
                if analysis["coverage_percentage"] < 50:
                    analysis_result["recommendations"].append(
                        f"{subject} dersinde daha fazla konu seçimi yaparak kapsamı artırabilirsiniz"
                    )
                
                if len(analysis["grades_covered"]) < 2:
                    analysis_result["recommendations"].append(
                        f"{subject} dersinde farklı sınıf seviyelerinden konular eklemeyi düşünün"
                    )
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing curriculum coverage: {str(e)}")
            return {"error": "Coverage analysis failed"}
    
    async def generate_curriculum_context(
        self,
        selected_topics: List[Dict[str, Any]],
        context_type: str = "comprehensive"  # comprehensive, focused, related
    ) -> str:
        """Generate rich context from selected curriculum topics for AI processing"""
        try:
            # Search for detailed content related to selected topics
            curriculum_results = await self.search_curriculum_topics(selected_topics)
            
            # Get related content if requested
            related_content = []
            if context_type in ["comprehensive", "related"]:
                related_content = await self.get_related_curriculum_content(selected_topics, "similar")
            
            # Build comprehensive context
            context_parts = []
            
            # Add selected topics context
            context_parts.append("=== SEÇİLEN MÜFREDAT KONULARI ===")
            for topic_data in selected_topics:
                topic_context = []
                if topic_data.get("ders"):
                    topic_context.append(f"Ders: {topic_data['ders']}")
                if topic_data.get("sinif"):
                    topic_context.append(f"Sınıf: {topic_data['sinif']}")
                if topic_data.get("title"):
                    topic_context.append(f"Konu: {topic_data['title']}")
                if topic_data.get("aciklama"):
                    topic_context.append(f"Açıklama: {topic_data['aciklama']}")
                
                context_parts.append(" | ".join(topic_context))
            
            # Add detailed curriculum content
            if curriculum_results:
                context_parts.append("\n=== DETAYLI MÜFREDAT İÇERİĞİ ===")
                for i, result in enumerate(curriculum_results[:10]):  # Limit to prevent too long context
                    content = result.get("content", "")
                    metadata = result.get("metadata", {})
                    
                    source_info = []
                    if metadata.get("subject"):
                        source_info.append(f"Ders: {metadata['subject']}")
                    if metadata.get("grade"):
                        source_info.append(f"Sınıf: {metadata['grade']}")
                    if metadata.get("title"):
                        source_info.append(f"Başlık: {metadata['title']}")
                    
                    context_parts.append(f"[{i+1}] {' | '.join(source_info)}\n{content[:500]}...")
            
            # Add related content for comprehensive context
            if related_content and context_type == "comprehensive":
                context_parts.append("\n=== İLGİLİ KONULAR ===")
                for i, result in enumerate(related_content[:5]):  # Limit related content
                    content = result.get("content", "")
                    metadata = result.get("metadata", {})
                    title = metadata.get("title", f"İlgili Konu {i+1}")
                    
                    context_parts.append(f"[İlgili] {title}: {content[:300]}...")
            
            # Join all parts
            full_context = "\n\n".join(context_parts)
            
            logger.info(f"Generated curriculum context: {len(full_context)} characters, {len(selected_topics)} topics")
            return full_context
            
        except Exception as e:
            logger.error(f"Error generating curriculum context: {str(e)}")
            return "Müfredat bağlamı oluşturulamadı."

# Global RAG system instance
rag_system = UnifiedRAGSystem()