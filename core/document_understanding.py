    
    def __init__(self):
        self.supported_formats = {
            'text': ['.txt', '.md', '.rtf'],
            'document': ['.pdf', '.docx', '.doc'],
            'image': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'],
            'code': ['.py', '.js', '.html', '.css', '.json', '.xml']
        }
        
        self.extraction_prompts = {
            'general': """Bu belgeyi analiz et ve asagidaki bilgileri cikar:
1. Ana konu ve icerik ozeti
2. Onemli kavramlar ve terimler
3. Egitim seviyesi (ilkokul, ortaokul, lise, universite)
4. Mufredat uyumu (varsa hangi YKS dersi/konusu)
5. Ogrenme hedefleri
6. Zorluk seviyesi
7. Onemli formuller, tanimlar veya kurallar
8. Pratik ornekler ve uygulamalar""",
            
            'educational': """Bu egitim materyalini YKS perspektifinden analiz et:
1. Hangi YKS dersine ait (Matematik, Fizik, Kimya, Biyoloji, vb.)
2. Hangi uniteler ve konular kapsaniyor
3. Mufredat kazanimlari ile uyum
4. Soru tipleri ve cozum yontemleri
5. Kavram yanilgilari ve dikkat edilecek noktalar
6. On kosul bilgiler
7. Ilgili konularla baglantilar
8. Ogrenci icin onerilen calisma stratejisi""",
            
            'question_analysis': """Bu soru/test materyalini analiz et:
1. Soru turu (coktan secmeli, acik uclu, vb.)
2. Zorluk seviyesi ve YKS uyumu
3. Olculmek istenen kazanimlar
4. Cozum stratejileri ve adimlari
5. Yaygin hatalar ve dikkat edilecek noktalar
6. Benzer soru turleri icin ipuclari
7. Zaman yonetimi onerileri
8. Ilgili konu basliklari
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return {"error": "File not found"}
            
            # Extract content based on file type
            content_data = await self._extract_content(file_path)
            
            if content_data.get("error"):
                return content_data
            
            # Analyze content with Gemini
            analysis_result = await self._analyze_content(
                content_data, analysis_type, custom_prompt
            )
            
            # Add to RAG system if successful
            if analysis_result.get("success"):
                await self._add_to_rag(file_path, content_data, analysis_result)
            
            return {
                "success": True,
                "file_info": {
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "type": content_data.get("type"),
                    "format": content_data.get("format")
                },
                "content": content_data.get("content", "")[:500] + "..." if len(content_data.get("content", "")) > 500 else content_data.get("content", ""),
                "analysis": analysis_result.get("analysis"),
                "structured_data": analysis_result.get("structured_data"),
                "educational_metadata": analysis_result.get("educational_metadata")
            }
            
        except Exception as e:
            logger.error(f"Document processing error: {e}")
            return {"error": str(e)}
    
    async def _extract_content(self, file_path: Path) -> Dict[str, Any]:
        pass
        try:
            file_extension = file_path.suffix.lower()
            mime_type = mimetypes.guess_type(str(file_path))[0]
            
            # Text files
            if file_extension in self.supported_formats['text']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                return {
                    "type": "text",
                    "format": file_extension,
                    "content": content,
                    "mime_type": mime_type
                }
            
            # PDF files
            elif file_extension == '.pdf':
                return await self._extract_pdf_content(file_path)
            
            # Word documents
            elif file_extension in ['.docx', '.doc']:
                return await self._extract_docx_content(file_path)
            
            # Images
            elif file_extension in self.supported_formats['image']:
                return await self._extract_image_content(file_path)
            
            # Code files
            elif file_extension in self.supported_formats['code']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                return {
                    "type": "code",
                    "format": file_extension,
                    "content": content,
                    "mime_type": mime_type
                }
            
            else:
                return {"error": f"Unsupported file format: {file_extension}"}
                
        except Exception as e:
            logger.error(f"Content extraction error: {e}")
            return {"error": str(e)}
    
    async def _extract_pdf_content(self, file_path: Path) -> Dict[str, Any]:
        pass
        try:
            import pdfplumber
            
            content = ""
            tables = []
            images = []
            
            with pdfplumber.open(file_path) as pdf:
                # Extract text
                for page in pdf.pages:
                    if page.extract_text():
                        content += page.extract_text() + "\n"
                    
                    # Extract tables
                    for table in page.extract_tables():
                        if table:
                            tables.append(table)
                
                # Get basic info
                info = pdf.metadata or {}
            
            return {
                "type": "document",
                "format": ".pdf",
                "content": content,
                "tables": tables,
                "pages": len(pdf.pages),
                "metadata": info
            }
            
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return {"error": f"PDF processing failed: {str(e)}"}
    
    async def _extract_docx_content(self, file_path: Path) -> Dict[str, Any]:
        pass
        try:
            doc = docx.Document(file_path)
            
            content = ""
            tables = []
            
            # Extract paragraphs
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    content += paragraph.text + "\n"
            
            # Extract tables
            for table in doc.tables:
                table_data = []
                for row in table.rows:
                    row_data = [cell.text for cell in row.cells]
                    table_data.append(row_data)
                tables.append(table_data)
            
            return {
                "type": "document",
                "format": ".docx",
                "content": content,
                "tables": tables,
                "sections": len(doc.sections)
            }
            
        except Exception as e:
            logger.error(f"DOCX extraction error: {e}")
            return {"error": f"DOCX processing failed: {str(e)}"}
    
    async def _extract_image_content(self, file_path: Path) -> Dict[str, Any]:
        pass
        try:
            # Load image
            image = PIL.Image.open(file_path)
            
            # Convert to base64 for API
            import io
            buffer = io.BytesIO()
            image.save(buffer, format=image.format or 'PNG')
            image_data = base64.b64encode(buffer.getvalue()).decode()
            
            # Use Gemini vision to extract text and understand content
            vision_prompt = """Bu goruntuyu analiz et ve asagidaki bilgileri cikar:
1. Goruntude bulunan metin (varsa)
2. Gorsel icerik aciklamasi
3. Egitim amacli kullanim potansiyeli
4. Hangi derslerde kullanilabilir
5. Gorsel ogelerin aciklamasi (diyagram, grafik, sekil vb.)
6. Onemli bilgiler ve kavramlar
        try:
            content = content_data.get("content", "")
            
            if not content.strip():
                return {"error": "No content to analyze"}
            
            # Select analysis prompt
            if custom_prompt:
                analysis_prompt = custom_prompt
            else:
                analysis_prompt = self.extraction_prompts.get(analysis_type, self.extraction_prompts["general"])
            
            # Combine prompt with content
            full_prompt = f"{analysis_prompt}\n\nBelge Icerigi:\n{content}"
            
            # Analyze with Gemini
            response = await gemini_client.generate_content(
                prompt=full_prompt,
                system_instruction="Sen uzman bir egitim analisti ve YKS konularinda uzmansin. Belgeleri egitim perspektifinden analiz ediyorsun."
            )
            
            if not response.get("success", True):
                return {"error": "Analysis failed"}
            
            analysis_text = response.get("text", "")
            
            # Extract structured data
            structured_data = await self._extract_structured_info(analysis_text, content)
            
            # Generate educational metadata
            educational_metadata = await self._generate_educational_metadata(content, structured_data)
            
            return {
                "success": True,
                "analysis": analysis_text,
                "structured_data": structured_data,
                "educational_metadata": educational_metadata
            }
            
        except Exception as e:
            logger.error(f"Content analysis error: {e}")
            return {"error": str(e)}
    
    async def _extract_structured_info(self, analysis_text: str, content: str) -> Dict[str, Any]:
        pass
        try:
            # Use Gemini to extract structured data
            structured_prompt = f"""
            Analiz metninden yapilandirilmis bilgi cikar:
            
            Analiz: {analysis_text}
            
            JSON formatinda su bilgileri cikar:
            {{
                "subject": "ana ders (Matematik, Fizik, Kimya, Biyoloji, vb.)",
                "topics": ["konu1", "konu2", ...],
                "difficulty_level": "kolay/orta/zor",
                "education_level": "lise/universite/vb.",
                "key_concepts": ["kavram1", "kavram2", ...],
                "formulas": ["formul1", "formul2", ...],
                "learning_objectives": ["hedef1", "hedef2", ...],
                "exam_relevance": "YKS/TYT/AYT uygunlugu",
                "estimated_study_time": "tahmini calisma suresi dakika cinsinden"
            }}
            response = await gemini_client.generate_content(
                prompt=structured_prompt,
                system_instruction="JSON formatinda yanit ver. Gecerli JSON formatini koru."
            )
            
            try:
                import json
                structured_data = json.loads(response.get("text", "{}"))
                return structured_data
            except json.JSONDecodeError:
                # Fallback to manual parsing
                return {
                    "subject": "Genel",
                    "topics": [],
                    "difficulty_level": "orta",
                    "education_level": "lise",
                    "key_concepts": [],
                    "formulas": [],
                    "learning_objectives": [],
                    "exam_relevance": "YKS",
                    "estimated_study_time": 30
                }
                
        except Exception as e:
            logger.error(f"Structured info extraction error: {e}")
            return {}
    
    async def _generate_educational_metadata(self, content: str, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
        try:
            return {
                "content_length": len(content),
                "reading_time_minutes": max(1, len(content.split()) // 200),  # ~200 words per minute
                "complexity_score": self._calculate_complexity_score(content),
                "curriculum_alignment": structured_data.get("exam_relevance", ""),
                "prerequisite_topics": [],  # Could be enhanced with AI
                "related_topics": structured_data.get("topics", []),
                "study_recommendations": self._generate_study_recommendations(structured_data),
                "assessment_suggestions": self._generate_assessment_suggestions(structured_data)
            }
            
        except Exception as e:
            logger.error(f"Educational metadata generation error: {e}")
            return {}
    
    def _calculate_complexity_score(self, content: str) -> float:
        pass
        try:
            words = content.split()
            
            # Factors affecting complexity
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
            sentence_count = content.count('.') + content.count('!') + content.count('?')
            avg_sentence_length = len(words) / sentence_count if sentence_count > 0 else 0
            
            # Technical terms indicators
            technical_indicators = ['formul', 'denklem', 'teoremi', 'kanunu', 'ilkesi', 'integral', 'turev']
            technical_score = sum(1 for indicator in technical_indicators if indicator in content.lower())
            
            # Normalize scores
            word_score = min(avg_word_length / 10, 1)
            sentence_score = min(avg_sentence_length / 20, 1)
            tech_score = min(technical_score / 5, 1)
            
            # Weighted complexity score
            complexity = (word_score * 0.3 + sentence_score * 0.4 + tech_score * 0.3)
            return round(complexity, 2)
            
        except Exception:
            return 0.5  # Default medium complexity
    
    def _generate_study_recommendations(self, structured_data: Dict[str, Any]) -> List[str]:
        pass
        recommendations = []
        
        difficulty = structured_data.get("difficulty_level", "orta")
        subject = structured_data.get("subject", "")
        
        if difficulty == "zor":
            recommendations.extend([
                "Bu konuyu kucuk parcalara bolerek calis",
                "On kosul konulari tekrar et",
                "Bol ornek coz ve pratik yap"
            ])
        elif difficulty == "kolay":
            recommendations.extend([
                "Hizli gecis yapabilirsin",
                "Ana kavramlari pekistir",
                "Ileri seviye sorulara odaklan"
            ])
        else:
            recommendations.extend([
                "Duzenli tekrar yap",
                "Kavramlari anlamaya odaklan",
                "Benzer ornekleri incele"
            ])
        
        if "matematik" in subject.lower():
            recommendations.append("Formulleri ezberlemek yerine anlamaya odaklan")
        elif "fizik" in subject.lower():
            recommendations.append("Gunluk yasam ornekleri ile iliskilendir")
        
        return recommendations
    
    def _generate_assessment_suggestions(self, structured_data: Dict[str, Any]) -> List[str]:
        pass
        suggestions = []
        
        topics = structured_data.get("topics", [])
        subject = structured_data.get("subject", "")
        
        if topics:
            suggestions.append(f"Bu konulardan soru coz: {', '.join(topics[:3])}")
        
        if structured_data.get("exam_relevance"):
            suggestions.append(f"{structured_data['exam_relevance']} formatinda sorular coz")
        
        suggestions.extend([
            "Konu testi coz",
            "Zamanli deneme yap",
            "Hata analizi yap"
        ])
        
        return suggestions
    
    async def _add_to_rag(self, file_path: Path, content_data: Dict[str, Any], analysis_result: Dict[str, Any]):
        pass
        try:
            document = {
                "content": content_data.get("content", ""),
                "metadata": {
                    "filename": file_path.name,
                    "file_type": content_data.get("type"),
                    "subject": analysis_result.get("structured_data", {}).get("subject", ""),
                    "topics": analysis_result.get("structured_data", {}).get("topics", []),
                    "difficulty": analysis_result.get("structured_data", {}).get("difficulty_level", ""),
                    "education_level": analysis_result.get("structured_data", {}).get("education_level", ""),
                    "upload_date": datetime.now().isoformat(),
                    "analysis": analysis_result.get("analysis", "")
                }
            }
            
            await rag_system.add_documents([document], collection_name="documents")
            logger.info(f"Added document {file_path.name} to RAG system")
            
        except Exception as e:
            logger.error(f"Error adding document to RAG: {e}")

# Global document understanding system
document_understanding = DocumentUnderstandingSystem()