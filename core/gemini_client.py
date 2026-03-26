"""
Unified Google Gemini AI Client with comprehensive features
Combines functionality from both basic and enhanced clients
"""

import google.generativeai as genai
from google.generativeai import types as genai_types
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from google.generativeai import protos
import instructor
from typing import Dict, Any, List, Optional, Union, Type, TypeVar
from pathlib import Path
import logging
import asyncio
import base64
import mimetypes
from pydantic import BaseModel, ValidationError
import PIL.Image
from tenacity import retry, stop_after_attempt, wait_exponential
from config import settings
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()

T = TypeVar('T', bound=BaseModel)

class UnifiedGeminiClient:
    def __init__(self):
        """Initialize unified Gemini client with all features"""
        # Configure API key
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        # Initialize different models
        self.models = {
            "pro": genai.GenerativeModel(settings.GEMINI_PRO_MODEL),
            "flash": genai.GenerativeModel(settings.GEMINI_FLASH_MODEL),
            "flash_lite": genai.GenerativeModel(settings.GEMINI_FLASH_LITE_MODEL),
            "thinking": genai.GenerativeModel(settings.GEMINI_THINKING_MODEL)
        }
        
        # Initialize instructor clients for structured output
        self.instructor_clients = {
            model_name: instructor.from_gemini(
                client=model,
                mode=instructor.Mode.GEMINI_JSON
            )
            for model_name, model in self.models.items()
        }
        
        # Default model
        self.default_model = "flash"
        
        # Safety settings
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        
        # Generation config
        self.generation_config = genai_types.GenerationConfig(
            temperature=settings.TEMPERATURE,
            top_p=settings.TOP_P,
            top_k=settings.TOP_K,
            max_output_tokens=settings.MAX_OUTPUT_TOKENS,
        )
        
        # Function registry for function calling
        self._function_registry = {}
        
        # Initialize hallucination detector (lazy loading to avoid circular import)
        self._hallucination_detector = None
        
        # Initialize RAG system (lazy loading to avoid circular import) 
        self._rag_system = None
        
        logger.info("Unified Gemini client initialized successfully")
    
    async def generate_content_with_video(
        self,
        prompt: str,
        video_url: str,
        system_instruction: Optional[str] = None,
        model_name: str = "gemini-2.5-flash",
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Generate content with YouTube video URL support"""
        try:
            import google.generativeai as genai
            
            # Configure the model with system instruction
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_instruction,
                safety_settings=self.safety_settings
            )
            
            logger.info(f"LangChain: Generating content with {model_name} and video URL")
            
            # For YouTube URLs, Gemini supports direct URL input in content
            content_parts = [prompt, video_url]
            
            # Generate response
            response = await asyncio.to_thread(
                model.generate_content,
                content_parts,
                generation_config=self.generation_config
            )
            
            # Handle different finish reasons for video content
            if response and hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                finish_reason = getattr(candidate, 'finish_reason', None)
                
                if finish_reason == 2:  # MAX_TOKENS
                    try:
                        partial_text = ""
                        if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                            for part in candidate.content.parts:
                                if hasattr(part, 'text'):
                                    partial_text += part.text
                        
                        sanitized_text = self._sanitize_text(partial_text)
                        return {
                            "text": sanitized_text,  # Uyarı mesajı kaldırıldı
                            "success": True,
                            "truncated": True  # Sadece flag olarak işaretle
                        }
                    except:
                        return {
                            "text": "[HATA: Video analizi tamamlanamadı - token limiti aşıldı]",
                            "success": False,
                            "error": "Video analysis failed due to token limit"
                        }
                
                elif finish_reason == 3:  # SAFETY
                    return {
                        "text": "[HATA: Video içeriği güvenlik filtreleri tarafından engellendi]",
                        "success": False,
                        "error": "Video content blocked by safety filters"
                    }
            
            # Try to get normal response
            if response and hasattr(response, 'text'):
                # Fix encoding issues for Turkish content
                sanitized_text = self._sanitize_text(response.text)
                return {
                    "text": sanitized_text,
                    "success": True
                }
            else:
                return {
                    "text": "[HATA: Video analizi yanıtı oluşturulamadı]",
                    "success": False,
                    "error": "No response generated from video analysis"
                }
                
        except Exception as e:
            logger.error(f"Video content generation error: {e}")
            return {
                "text": "",
                "success": False,
                "error": str(e)
            }
    
    def _sanitize_text(self, text: str) -> str:
        """Sanitize text for proper UTF-8 encoding"""
        if not isinstance(text, str):
            text = str(text)
        
        try:
            # Ensure proper UTF-8 encoding
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='replace')
            
            # Fix common Turkish character encoding issues
            replacements = {
                'Ä±': 'ı', 'Ä°': 'İ', 'Ã§': 'ç', 'Ã–': 'Ö', 
                'Ã¼': 'ü', 'ÄŸ': 'ğ', 'Åž': 'ş', 'Ã¤': 'ä',
                'Ã©': 'é', 'Ã¡': 'á', 'Ã³': 'ó', 'Ãº': 'ú',
                'â€œ': '"', 'â€': '"', 'â€™': "'", 'â€"': '-',
                'Ã¢': 'â', 'Ã®': 'î', 'Ã´': 'ô', 'Ã»': 'û'
            }
            
            for wrong, correct in replacements.items():
                text = text.replace(wrong, correct)
            
            # Ensure final UTF-8 compatibility
            text = text.encode('utf-8', errors='replace').decode('utf-8')
            
            return text
            
        except Exception as e:
            logger.warning(f"Text sanitization error: {e}")
            return str(text)
    
    @property
    def hallucination_detector(self):
        """Lazy load hallucination detector to avoid circular import"""
        if self._hallucination_detector is None:
            from core.hallucination_detector import hallucination_detector
            self._hallucination_detector = hallucination_detector
        return self._hallucination_detector
    
    @property
    def rag_system(self):
        """Lazy load RAG system to avoid circular import"""
        if self._rag_system is None:
            from core.rag_system import rag_system
            self._rag_system = rag_system
        return self._rag_system
    
    async def generate_content_with_rag(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model_name: Optional[str] = None,
        use_rag: bool = True,
        rag_collections: Optional[List[str]] = None,
        rag_results: int = 5,
        validation_level: str = "medium",
        validation_type: str = "educational",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate content with RAG context, hallucination detection, and ranking
        
        Args:
            prompt: User prompt
            system_instruction: System instructions
            model_name: Model to use
            use_rag: Whether to use RAG for context
            rag_collections: Collections to search (default: all)
            rag_results: Number of RAG results to retrieve
            validation_level: Validation strictness
            validation_type: Type of validation
            **kwargs: Additional generation parameters
        
        Returns:
            Enhanced response with RAG context, validation, and ranking
        """
        try:
            enhanced_prompt = prompt
            rag_context = []
            
            # Retrieve RAG context if enabled
            if use_rag:
                try:
                    search_results = await self.rag_system.search(
                        query=prompt,
                        collection_names=rag_collections,
                        n_results=rag_results
                    )
                    
                    if search_results:
                        # Format context from RAG results
                        context_parts = []
                        for i, result in enumerate(search_results[:rag_results], 1):
                            content = result.get("content", "")[:500]  # Limit context length
                            source = result.get("metadata", {}).get("source", "Bilinmeyen")
                            context_parts.append(f"[Kaynak {i}: {source}]\n{content}")
                        
                        rag_context = search_results
                        context_text = "\n\n".join(context_parts)
                        
                        # Enhance prompt with RAG context
                        enhanced_prompt = f"""Aşağıdaki bağlam bilgilerini kullanarak soruyu cevapla:

Bağlam Bilgileri:
{context_text}

Soru: {prompt}

Lütfen bağlam bilgilerini kullanarak doğru ve detaylı bir cevap ver. Bağlamda olmayan bilgiler hakkında spekülasyon yapma."""
                        
                        logger.info(f"RAG context added: {len(search_results)} documents")
                    
                except Exception as e:
                    logger.warning(f"RAG search failed, continuing without context: {e}")
            
            # Generate content with enhanced prompt
            response = await self.generate_content(
                prompt=enhanced_prompt,
                system_instruction=system_instruction,
                model_name=model_name,
                **kwargs
            )
            
            # Add RAG information to response
            response["rag_used"] = use_rag
            response["rag_context"] = rag_context
            response["rag_results_count"] = len(rag_context)
            
            # Validate content if successful
            if response.get("success", True) and response.get("text") and validation_level != "none":
                validation_result = await self.hallucination_detector.detect_hallucination(
                    content=response["text"],
                    context={
                        "prompt": prompt,
                        "system_instruction": system_instruction,
                        "rag_context": rag_context[:3]  # Include top 3 RAG results for validation
                    },
                    check_type=validation_type
                )
                
                # Add validation to response
                response["validation"] = validation_result
                response["confidence_score"] = validation_result.get("overall_confidence", 0.5)
                response["risk_level"] = validation_result.get("risk_level", "unknown")
                response["validated"] = True
                
                # Add ranking based on confidence and RAG relevance
                rag_score = min(len(rag_context) / rag_results, 1.0) if rag_context else 0
                confidence_score = validation_result.get("overall_confidence", 0.5)
                response["ranking_score"] = (confidence_score * 0.7 + rag_score * 0.3)
                
                # Add warnings for low confidence
                if confidence_score < 0.6:
                    response["warning"] = "Düşük güvenilirlik: İçerik doğrulanmalı"
                elif rag_score < 0.5 and use_rag:
                    response["warning"] = "Sınırlı bağlam: Daha fazla kaynak gerekebilir"
                
                logger.info(f"Enhanced response: confidence={confidence_score:.3f}, rag_score={rag_score:.3f}, ranking={response['ranking_score']:.3f}")
            else:
                response["validated"] = False
                response["ranking_score"] = 0.3  # Low score for unvalidated content
            
            return response
            
        except Exception as e:
            logger.error(f"Error in RAG-enhanced generation: {e}")
            # Fallback to basic generation
            return await self.generate_content(
                prompt=prompt,
                system_instruction=system_instruction,
                model_name=model_name,
                **kwargs
            )
    
    async def generate_content_with_validation(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model_name: Optional[str] = None,
        validation_level: str = "medium",  # none, low, medium, high
        validation_type: str = "educational",  # general, educational, mathematical
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate content with automatic hallucination detection
        
        Args:
            prompt: The user prompt
            system_instruction: System instructions
            model_name: Model to use
            validation_level: Validation strictness (none, low, medium, high)
            validation_type: Type of validation (general, educational, mathematical)
            **kwargs: Additional arguments for generate_content
        
        Returns:
            Response with validation results included
        """
        try:
            # Generate content normally
            response = await self.generate_content(
                prompt=prompt,
                system_instruction=system_instruction,
                model_name=model_name,
                **kwargs
            )
            
            # Skip validation if disabled
            if validation_level == "none":
                return response
            
            # Validate content
            if response.get("success", True) and response.get("text"):
                validation_result = await self.hallucination_detector.detect_hallucination(
                    content=response["text"],
                    context={"prompt": prompt, "system_instruction": system_instruction},
                    check_type=validation_type
                )
                
                # Add validation to response
                response["validation"] = validation_result
                response["confidence_score"] = validation_result.get("overall_confidence", 0.5)
                response["risk_level"] = validation_result.get("risk_level", "unknown")
                response["validated"] = True
                
                # Add warnings for low confidence
                if validation_result.get("overall_confidence", 0.5) < 0.6:
                    response["warning"] = "Düşük güvenilirlik: İçerik doğrulanmalı"
                
                logger.info(f"Content validated: confidence={response['confidence_score']:.3f}, risk={response['risk_level']}")
            else:
                response["validated"] = False
                response["validation_error"] = "Could not validate empty or failed response"
            
            return response
            
        except Exception as e:
            logger.error(f"Error in content generation with validation: {e}")
            # Return unvalidated response on validation error
            response = await self.generate_content(
                prompt=prompt,
                system_instruction=system_instruction,
                model_name=model_name,
                **kwargs
            )
            response["validated"] = False
            response["validation_error"] = str(e)
            return response
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model_name: Optional[str] = None,
        use_thinking: bool = False,
        images: Optional[List[Union[str, Path, PIL.Image.Image]]] = None,
        documents: Optional[List[Union[str, Path]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[genai_types.Tool]] = None,
        tool_config: Optional[protos.ToolConfig] = None,
        stream: bool = False
    ):
        """
        Generate content using Gemini with full feature support
        
        Args:
            prompt: The user prompt
            system_instruction: System instructions for the model
            model_name: Model to use (pro, flash, flash_lite)
            use_thinking: Use thinking model for complex reasoning
            images: List of images to include
            documents: List of documents to include
            temperature: Override default temperature
            max_tokens: Override default max tokens
            tools: Function calling tools
            tool_config: Function calling configuration
            stream: Enable streaming response
        
        Returns:
            Response dictionary with text and metadata
        """
        try:
            # Sanitize input texts to ensure proper UTF-8 encoding
            prompt = self._sanitize_text(prompt)
            if system_instruction:
                system_instruction = self._sanitize_text(system_instruction)
            
            # Log LangChain activity
            console.print(f"[magenta]LangChain: Generating content with Gemini {model_name or self.default_model}[/magenta]")
            
            # Select model
            if use_thinking:
                model_name = "thinking"
            model_name = model_name or self.default_model
            model = self.models.get(model_name, self.models[self.default_model])
            
            # Configure model with system instruction
            if system_instruction:
                model = genai.GenerativeModel(
                    model_name=model._model_name,
                    system_instruction=system_instruction
                )
            
            # Prepare content parts
            content_parts = [prompt]
            
            # Add images if provided
            if images:
                for image in images:
                    if isinstance(image, str) and Path(image).exists():
                        img = PIL.Image.open(image)
                        content_parts.append(img)
                    elif isinstance(image, Path) and image.exists():
                        img = PIL.Image.open(image)
                        content_parts.append(img)
                    elif isinstance(image, PIL.Image.Image):
                        content_parts.append(image)
            
            # Add documents if provided
            if documents:
                for doc in documents:
                    doc_path = Path(doc) if isinstance(doc, str) else doc
                    if doc_path.exists():
                        mime_type = mimetypes.guess_type(str(doc_path))[0]
                        with open(doc_path, 'rb') as f:
                            doc_data = f.read()
                            if mime_type and mime_type.startswith('text'):
                                content_parts.append(doc_data.decode('utf-8', errors='ignore'))
                            else:
                                # For binary files, use blob
                                blob = {
                                    "mime_type": mime_type or "application/octet-stream",
                                    "data": base64.b64encode(doc_data).decode()
                                }
                                content_parts.append(blob)
            
            # Update generation config if needed
            gen_config = self.generation_config
            if temperature is not None or max_tokens is not None:
                gen_config = genai_types.GenerationConfig(
                    temperature=temperature or self.generation_config.temperature,
                    top_p=self.generation_config.top_p,
                    top_k=self.generation_config.top_k,
                    max_output_tokens=max_tokens or self.generation_config.max_output_tokens,
                )
            
            # Generate response
            if stream:
                return self._generate_streaming(
                    model, content_parts, gen_config, tools, tool_config, model_name
                )
            else:
                response = model.generate_content(
                    content_parts,
                    generation_config=gen_config,
                    safety_settings=self.safety_settings,
                    tools=tools,
                    tool_config=tool_config
                )
                
                # Handle different finish reasons
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    finish_reason = getattr(candidate, 'finish_reason', None)
                    
                    if finish_reason == 2:  # MAX_TOKENS
                        # Try to get partial content
                        try:
                            partial_text = ""
                            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                                for part in candidate.content.parts:
                                    if hasattr(part, 'text'):
                                        partial_text += part.text
                            
                            return {
                                "text": partial_text,  # Uyarı mesajı kaldırıldı
                                "model": model_name,
                                "success": True,
                                "truncated": True,  # Sadece flag olarak işaretle
                                "warning": "Response truncated due to max tokens",
                                "finish_reason": finish_reason,
                                "usage": response.usage_metadata if hasattr(response, 'usage_metadata') else None
                            }
                        except:
                            return {
                                "text": "[HATA: Yanıt oluşturulamadı - token limiti aşıldı]",
                                "model": model_name,
                                "success": False,
                                "error": "Max tokens exceeded, no partial content available"
                            }
                    
                    elif finish_reason == 3:  # SAFETY
                        return {
                            "text": "[HATA: İçerik güvenlik filtreleri tarafından engellendi]",
                            "model": model_name,
                            "success": False,
                            "error": "Content blocked by safety filters"
                        }
                
                # Normal successful response
                try:
                    return {
                        "text": response.text,
                        "model": model_name,
                        "success": True,
                        "usage": response.usage_metadata if hasattr(response, 'usage_metadata') else None,
                        "candidates": response.candidates if hasattr(response, 'candidates') else None
                    }
                except Exception as text_error:
                    return {
                        "text": "[HATA: Yanıt metni çıkarılamadı]",
                        "model": model_name,
                        "success": False,
                        "error": f"Failed to extract response text: {str(text_error)}"
                    }
                
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise
    
    async def _generate_streaming(
        self, 
        model, 
        content_parts, 
        gen_config, 
        tools, 
        tool_config, 
        model_name
    ):
        """Helper method for streaming content generation"""
        response = model.generate_content(
            content_parts,
            generation_config=gen_config,
            safety_settings=self.safety_settings,
            tools=tools,
            tool_config=tool_config,
            stream=True
        )
        
        # Collect streaming response
        full_text = ""
        for chunk in response:
            if chunk.text:
                full_text += chunk.text
                yield {"text": chunk.text, "streaming": True}
        
        yield {
            "text": full_text,
            "streaming": False,
            "model": model_name,
            "success": True,
            "usage": response.usage_metadata if hasattr(response, 'usage_metadata') else None
        }
    
    async def generate_structured_output(
        self,
        prompt: str,
        response_model: Type[T],
        system_instruction: Optional[str] = None,
        model_name: Optional[str] = None,
        max_retries: int = 3
    ) -> T:
        """
        Generate structured output using instructor
        
        Args:
            prompt: The user prompt
            response_model: Pydantic model for response structure
            system_instruction: System instructions
            model_name: Model to use
            max_retries: Maximum retry attempts
        
        Returns:
            Structured response as Pydantic model instance
        """
        try:
            model_name = model_name or self.default_model
            client = self.instructor_clients.get(model_name, self.instructor_clients[self.default_model])
            
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            
            response = await asyncio.to_thread(
                client.messages.create,
                messages=messages,
                response_model=response_model,
                max_retries=max_retries
            )
            
            return response
            
        except ValidationError as e:
            logger.error(f"Validation error in structured output: {str(e)}")
            raise
        except RuntimeError as e:
            if "cannot schedule new futures after shutdown" in str(e):
                logger.warning("Structured output generation skipped due to shutdown")
                raise
            else:
                logger.error(f"Runtime error in structured output: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Error generating structured output: {str(e)}")
            raise
    
    async def generate_embeddings(
        self,
        texts: Union[str, List[str]],
        task_type: Optional[str] = None,
        title: Optional[str] = None,
        output_dimensionality: Optional[int] = None
    ) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for text(s)
        
        Args:
            texts: Text or list of texts to embed
            task_type: Task type for embedding (RETRIEVAL_QUERY, RETRIEVAL_DOCUMENT, etc.)
            title: Optional title for document embedding
            output_dimensionality: Output dimension (128-3072)
        
        Returns:
            Embedding vector(s)
        """
        try:
            task_type = task_type or settings.EMBEDDING_TASK_TYPE
            output_dimensionality = output_dimensionality or settings.EMBEDDING_DIMENSIONS
            
            # Ensure texts is a list
            is_single = isinstance(texts, str)
            if is_single:
                texts = [texts]
            
            # Prepare task config
            task_config = {
                "task_type": task_type
            }
            if title:
                task_config["title"] = title
            
            # Generate embeddings
            result = await asyncio.to_thread(
                genai.embed_content,
                model=settings.GEMINI_EMBEDDING_MODEL,
                content=texts,
                task_type=task_type,
                title=title,
                output_dimensionality=output_dimensionality
            )
            
            # Extract embeddings properly
            if is_single:
                # Single text - return single embedding
                embedding = result['embedding']
                # Ensure it's a flat list of floats
                if isinstance(embedding, list) and len(embedding) > 0:
                    if isinstance(embedding[0], list):
                        return embedding[0]  # Flatten if nested
                    return embedding
                return embedding
            else:
                # Multiple texts - return list of embeddings
                embeddings = result['embedding']
                # Ensure each embedding is a flat list
                if isinstance(embeddings, list):
                    flattened = []
                    for emb in embeddings:
                        if isinstance(emb, list) and len(emb) > 0:
                            if isinstance(emb[0], list):
                                flattened.append(emb[0])  # Flatten if nested
                            else:
                                flattened.append(emb)
                        else:
                            flattened.append(emb)
                    return flattened
                return embeddings
            
        except RuntimeError as e:
            if "cannot schedule new futures after shutdown" in str(e):
                logger.warning("Embeddings generation skipped due to shutdown")
                # Re-raise the exception to stop processing during shutdown
                raise
            else:
                logger.error(f"Runtime error generating embeddings: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def register_function(self, func: callable, description: str, parameters: Dict[str, Any]):
        """Register a function for function calling"""
        self._function_registry[func.__name__] = {
            "function": func,
            "description": description,
            "parameters": parameters
        }
    
    async def execute_with_functions(
        self,
        prompt: str,
        available_functions: Optional[List[str]] = None,
        system_instruction: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute prompt with function calling capabilities
        
        Args:
            prompt: User prompt
            available_functions: List of function names to make available
            system_instruction: System instructions
            model_name: Model to use
        
        Returns:
            Response with function call results
        """
        try:
            # Get available functions
            if available_functions:
                functions = {name: self._function_registry[name] 
                           for name in available_functions 
                           if name in self._function_registry}
            else:
                functions = self._function_registry
            
            # Create tools from functions
            tools = []
            for name, func_info in functions.items():
                tool = genai_types.Tool(
                    function_declarations=[
                        protos.FunctionDeclaration(
                            name=name,
                            description=func_info["description"],
                            parameters=func_info["parameters"]
                        )
                    ]
                )
                tools.append(tool)
            
            # Configure tool usage
            tool_config = protos.ToolConfig(
                function_calling_config=protos.FunctionCallingConfig(
                    mode=protos.FunctionCallingConfig.Mode[settings.FUNCTION_CALLING_MODE]
                )
            )
            
            # Generate initial response
            response = await self.generate_content(
                prompt=prompt,
                system_instruction=system_instruction,
                model_name=model_name,
                tools=tools,
                tool_config=tool_config
            )
            
            # Handle function calls if any
            if response.get("candidates") and response["candidates"][0].content.parts:
                for part in response["candidates"][0].content.parts:
                    if hasattr(part, "function_call"):
                        func_call = part.function_call
                        func_name = func_call.name
                        func_args = dict(func_call.args)
                        
                        # Execute function
                        if func_name in functions:
                            func = functions[func_name]["function"]
                            result = await func(**func_args) if asyncio.iscoroutinefunction(func) else func(**func_args)
                            
                            # Return function result
                            return {
                                "text": response.get("text", ""),
                                "function_call": {
                                    "name": func_name,
                                    "args": func_args,
                                    "result": result
                                },
                                "model": response.get("model")
                            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error executing with functions: {str(e)}")
            raise
    
    async def analyze_image(
        self,
        image_path: Union[str, Path],
        prompt: str,
        system_instruction: Optional[str] = None,
        extract_text: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze image with optional text extraction
        
        Args:
            image_path: Path to image
            prompt: Analysis prompt
            system_instruction: System instructions
            extract_text: Whether to extract text from image
        
        Returns:
            Analysis results
        """
        try:
            if extract_text:
                prompt = f"First, extract any text visible in this image. Then, {prompt}"
            
            response = await self.generate_content(
                prompt=prompt,
                system_instruction=system_instruction,
                images=[image_path],
                model_name="flash"  # Flash is best for multi-modal
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            raise
    
    async def count_tokens(self, text: str, model_name: Optional[str] = None) -> int:
        """Count tokens in text"""
        try:
            model_name = model_name or self.default_model
            model = self.models.get(model_name, self.models[self.default_model])
            
            result = await asyncio.to_thread(model.count_tokens, text)
            return result.total_tokens
            
        except RuntimeError as e:
            if "cannot schedule new futures after shutdown" in str(e):
                logger.warning("Token counting skipped due to shutdown")
                return 0  # Return 0 tokens during shutdown
            else:
                logger.error(f"Runtime error counting tokens: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Error counting tokens: {str(e)}")
            raise
    
    async def initialize(self) -> bool:
        """
        Initialize the client and test connectivity
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            console.print("[magenta]🔶 LangChain: Initializing Gemini client...[/magenta]")
            # Test basic connectivity
            await self.count_tokens("test")
            logger.info("Gemini client initialized successfully")
            console.print("[green]✓ Gemini client initialized successfully[/green]")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            return False

# Global client instance
gemini_client = UnifiedGeminiClient()