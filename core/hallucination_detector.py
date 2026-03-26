"""
Hallucination Detection and Content Validation System
Uses multiple AI techniques to detect and prevent hallucinations in educational content
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import statistics

from core.gemini_client import gemini_client
from core.rag_system import rag_system

logger = logging.getLogger(__name__)

class HallucinationDetector:
    """Advanced hallucination detection system"""
    
    def __init__(self):
        self.fact_check_prompts = {
            "general": """Bu içeriği fact-check yap ve doğruluğunu değerlendir:

İçerik: {content}

Değerlendirme kriterleri:
1. Faktüel doğruluk (bilinen gerçeklerle uyum)
2. Bilimsel doğruluk
3. Matematiksel doğruluk
4. Tarihsel doğruluk
5. Mantıksal tutarlılık
6. Kaynak güvenilirliği

Her bir iddia için:
- Doğru/Yanlış/Belirsiz olarak işaretle
- Güven skoru (0-100)
- Gerekçe
- Kaynakla doğrulama önerisi

JSON formatında yanıt ver.""",

            "educational": """Bu eğitim içeriğini YKS müfredatı perspektifinden doğrula:

İçerik: {content}

Kontrol edilecek noktalar:
1. Müfredata uygunluk
2. Seviye uygunluğu
3. Kavramsal doğruluk
4. Formül ve hesaplama doğruluğu
5. Tanım doğruluğu
6. Örneklerin uygunluğu
7. Yaygın yanılgılara neden olup olmadığı

Potansiyel sorun alanlarını işaretle ve düzeltme önerileri sun.""",

            "mathematical": """Bu matematik içeriğini doğrula:

İçerik: {content}

Kontrol noktaları:
1. Formül doğruluğu
2. Hesaplama adımları
3. Matematiksel gösterim
4. Teorik açıklamalar
5. Örnek çözümler
6. Sonuçların mantıklılığı

Hatalar varsa detaylı açıklama ve düzeltme öner."""
        }
        
        self.confidence_thresholds = {
            "high": 0.9,
            "medium": 0.7,
            "low": 0.5
        }
        
        self.validation_techniques = [
            "cross_reference",
            "logical_consistency",
            "source_validation", 
            "peer_review",
            "computational_check"
        ]
    
    async def detect_hallucination(
        self, 
        content: str, 
        context: Optional[Dict[str, Any]] = None,
        check_type: str = "general"
    ) -> Dict[str, Any]:
        """Main hallucination detection function"""
        try:
            results = {}
            
            # 1. Initial content analysis
            results["content_analysis"] = await self._analyze_content_structure(content)
            
            # 2. Fact checking with AI
            results["fact_check"] = await self._ai_fact_check(content, check_type)
            
            # 3. Cross-reference with RAG
            results["cross_reference"] = await self._cross_reference_rag(content, context)
            
            # 4. Logical consistency check
            results["logical_consistency"] = await self._check_logical_consistency(content)
            
            # 5. Source validation (if sources mentioned)
            results["source_validation"] = await self._validate_sources(content)
            
            # 6. Mathematical validation (if applicable)
            if self._contains_math(content):
                results["mathematical_validation"] = await self._validate_mathematical_content(content)
            
            # 7. Confidence scoring
            overall_confidence = self._calculate_confidence_score(results)
            
            # 8. Generate final assessment
            assessment = self._generate_assessment(results, overall_confidence)
            
            return {
                "success": True,
                "overall_confidence": overall_confidence,
                "assessment": assessment,
                "detailed_results": results,
                "recommendations": self._generate_recommendations(results),
                "risk_level": self._assess_risk_level(overall_confidence),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Hallucination detection error: {e}")
            return {
                "success": False,
                "error": str(e),
                "risk_level": "unknown"
            }
    
    async def _analyze_content_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure for inconsistencies"""
        try:
            analysis = {
                "word_count": len(content.split()),
                "sentence_count": len(re.findall(r'[.!?]+', content)),
                "paragraph_count": len(content.split('\n\n')),
                "claim_count": len(re.findall(r'\b(is|are|was|were|will|can|cannot|must)\b', content.lower())),
                "specificity_indicators": len(re.findall(r'\b(\d+|\d+\.\d+|exactly|precisely|specifically)\b', content.lower())),
                "uncertainty_indicators": len(re.findall(r'\b(maybe|perhaps|possibly|might|could|probably)\b', content.lower())),
                "superlative_usage": len(re.findall(r'\b(best|worst|most|least|always|never|all|none)\b', content.lower()))
            }
            
            # Calculate structural consistency score
            if analysis["sentence_count"] > 0:
                analysis["avg_sentence_length"] = analysis["word_count"] / analysis["sentence_count"]
                analysis["claim_density"] = analysis["claim_count"] / analysis["sentence_count"]
                analysis["specificity_ratio"] = analysis["specificity_indicators"] / analysis["sentence_count"]
                analysis["uncertainty_ratio"] = analysis["uncertainty_indicators"] / analysis["sentence_count"]
            
            return analysis
            
        except Exception as e:
            logger.error(f"Content structure analysis error: {e}")
            return {}
    
    async def _ai_fact_check(self, content: str, check_type: str) -> Dict[str, Any]:
        """AI-powered fact checking"""
        try:
            prompt = self.fact_check_prompts.get(check_type, self.fact_check_prompts["general"])
            formatted_prompt = prompt.format(content=content)
            
            response = await gemini_client.generate_content(
                prompt=formatted_prompt,
                system_instruction="Sen fact-checking uzmanısın. Eğitim içeriklerinin doğruluğunu titizlikle kontrol ediyorsun."
            )
            
            if not response.get("success", True):
                return {"error": "Fact check failed"}
            
            # Try to parse JSON response
            fact_check_text = response.get("text", "")
            
            try:
                fact_check_data = json.loads(fact_check_text)
            except json.JSONDecodeError:
                # Fallback: analyze text response
                fact_check_data = self._parse_fact_check_text(fact_check_text)
            
            return {
                "success": True,
                "analysis": fact_check_data,
                "raw_response": fact_check_text
            }
            
        except Exception as e:
            logger.error(f"AI fact check error: {e}")
            return {"error": str(e)}
    
    async def _cross_reference_rag(self, content: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Cross-reference content with RAG knowledge base"""
        try:
            # Extract key claims from content
            claims = await self._extract_claims(content)
            
            reference_results = []
            
            for claim in claims[:5]:  # Limit to top 5 claims
                # Search RAG for related information
                search_results = await rag_system.search(
                    query=claim,
                    n_results=3,
                    collection_names=["curriculum", "documents"]
                )
                
                # Analyze consistency
                consistency_score = await self._analyze_consistency(claim, search_results)
                
                reference_results.append({
                    "claim": claim,
                    "references_found": len(search_results),
                    "consistency_score": consistency_score,
                    "supporting_evidence": search_results[:2]  # Top 2 supporting documents
                })
            
            overall_consistency = statistics.mean([r["consistency_score"] for r in reference_results]) if reference_results else 0.5
            
            return {
                "overall_consistency": overall_consistency,
                "claim_analysis": reference_results,
                "total_claims_checked": len(reference_results)
            }
            
        except Exception as e:
            logger.error(f"Cross-reference error: {e}")
            return {"error": str(e)}
    
    async def _check_logical_consistency(self, content: str) -> Dict[str, Any]:
        """Check logical consistency of content"""
        try:
            consistency_prompt = f"""Bu içeriğin mantıksal tutarlılığını analiz et:

İçerik: {content}

Kontrol noktaları:
1. İfadeler arası çelişki var mı?
2. Mantık zinciri doğru mu?
3. Sebep-sonuç ilişkileri mantıklı mı?
4. Örnekler iddialarla uyumlu mu?
5. Sonuçlar öncüllerden mantıklı şekilde çıkıyor mu?

0-100 arası tutarlılık skoru ver ve gerekçelendirme yap."""
            
            response = await gemini_client.generate_content(
                prompt=consistency_prompt,
                system_instruction="Mantık ve tutarlılık analizi uzmanısın."
            )
            
            consistency_text = response.get("text", "")
            
            # Extract score
            score_match = re.search(r'(\d+)\s*/\s*100', consistency_text)
            consistency_score = int(score_match.group(1)) / 100 if score_match else 0.5
            
            return {
                "consistency_score": consistency_score,
                "analysis": consistency_text,
                "issues_found": self._extract_consistency_issues(consistency_text)
            }
            
        except Exception as e:
            logger.error(f"Logical consistency check error: {e}")
            return {"error": str(e)}
    
    async def _validate_sources(self, content: str) -> Dict[str, Any]:
        """Validate mentioned sources and references"""
        try:
            # Find potential source mentions
            source_patterns = [
                r'kaynak[:\s]*([^\n]+)',
                r'referans[:\s]*([^\n]+)',
                r'çalışma[:\s]*([^\n]+)',
                r'araştırma[:\s]*([^\n]+)',
                r'\((19|20)\d{2}\)',  # Year references
                r'[A-Z][a-z]+ et al\.',  # Academic citations
            ]
            
            sources_found = []
            for pattern in source_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                sources_found.extend(matches)
            
            if not sources_found:
                return {
                    "sources_mentioned": 0,
                    "validation_possible": False,
                    "note": "No specific sources mentioned"
                }
            
            # For now, just check if sources look legitimate
            legitimate_count = 0
            for source in sources_found:
                if self._looks_legitimate_source(str(source)):
                    legitimate_count += 1
            
            return {
                "sources_mentioned": len(sources_found),
                "legitimate_sources": legitimate_count,
                "legitimacy_ratio": legitimate_count / len(sources_found) if sources_found else 0,
                "sources": sources_found[:5]  # Top 5 sources
            }
            
        except Exception as e:
            logger.error(f"Source validation error: {e}")
            return {"error": str(e)}
    
    async def _validate_mathematical_content(self, content: str) -> Dict[str, Any]:
        """Validate mathematical content"""
        try:
            math_validation_prompt = f"""Bu matematik içeriğini doğrula:

İçerik: {content}

Kontrol et:
1. Formüller doğru mu?
2. Hesaplamalar doğru mu?
3. Matematiksel gösterimler uygun mu?
4. Örnek çözümler doğru mu?
5. Sonuçlar mantıklı mı?

Hatalar varsa belirt ve düzeltme öner."""
            
            response = await gemini_client.generate_content(
                prompt=math_validation_prompt,
                system_instruction="Matematik doğrulama uzmanısın. Formülleri ve hesaplamaları titizlikle kontrol ediyorsun."
            )
            
            validation_text = response.get("text", "")
            
            # Extract mathematical elements
            formulas = re.findall(r'[a-zA-Z]\s*=\s*[^,\n]+', content)
            equations = re.findall(r'\d+\s*[+\-*/]\s*\d+\s*=\s*\d+', content)
            
            return {
                "formulas_found": len(formulas),
                "equations_found": len(equations),
                "validation_analysis": validation_text,
                "mathematical_elements": {
                    "formulas": formulas[:3],
                    "equations": equations[:3]
                }
            }
            
        except Exception as e:
            logger.error(f"Mathematical validation error: {e}")
            return {"error": str(e)}
    
    def _contains_math(self, content: str) -> bool:
        """Check if content contains mathematical elements"""
        math_indicators = [
            r'[a-zA-Z]\s*=\s*[^,\n]+',  # Formulas
            r'\d+\s*[+\-*/]\s*\d+',     # Simple equations
            r'\\[a-zA-Z]+\{',           # LaTeX
            r'\b(formül|denklem|hesap|integral|türev|limit)\b'  # Math keywords
        ]
        
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in math_indicators)
    
    async def _extract_claims(self, content: str) -> List[str]:
        """Extract factual claims from content"""
        try:
            claim_extraction_prompt = f"""Bu metinden önemli faktüel iddiaları çıkar:

Metin: {content}

Her bir iddiayı ayrı satırda listele. Sadece doğrulanabilir, objektif iddiaları dahil et."""
            
            response = await gemini_client.generate_content(
                prompt=claim_extraction_prompt,
                system_instruction="İddiaları objektif şekilde ayır ve listele."
            )
            
            claims_text = response.get("text", "")
            claims = [claim.strip() for claim in claims_text.split('\n') if claim.strip() and not claim.strip().startswith('-')]
            
            return claims[:10]  # Limit to 10 claims
            
        except Exception as e:
            logger.error(f"Claim extraction error: {e}")
            return []
    
    async def _analyze_consistency(self, claim: str, search_results: List[Dict]) -> float:
        """Analyze consistency between claim and search results"""
        try:
            if not search_results:
                return 0.5  # Neutral when no references
            
            # Simple consistency check based on content similarity
            # In a production system, this would be more sophisticated
            
            reference_content = " ".join([result.get("content", "") for result in search_results[:3]])
            
            consistency_prompt = f"""Bu iddia ile referans içerik arasındaki tutarlılığı değerlendir:

İddia: {claim}

Referans içerik: {reference_content}

0-1 arası tutarlılık skoru ver (0: tamamen çelişkili, 1: tamamen tutarlı)."""
            
            response = await gemini_client.generate_content(
                prompt=consistency_prompt,
                system_instruction="Tutarlılık analizi yap."
            )
            
            # Extract score
            score_text = response.get("text", "0.5")
            score_match = re.search(r'0\.\d+|1\.0|0|1', score_text)
            
            if score_match:
                return float(score_match.group())
            return 0.5
            
        except Exception as e:
            logger.error(f"Consistency analysis error: {e}")
            return 0.5
    
    def _parse_fact_check_text(self, text: str) -> Dict[str, Any]:
        """Parse fact check text when JSON parsing fails"""
        # Simple text parsing fallback
        doğru_count = len(re.findall(r'\bdoğru\b', text.lower()))
        yanlış_count = len(re.findall(r'\byanlış\b', text.lower()))
        belirsiz_count = len(re.findall(r'\bbelirsiz\b', text.lower()))
        
        total = doğru_count + yanlış_count + belirsiz_count
        
        if total > 0:
            accuracy_score = doğru_count / total
        else:
            accuracy_score = 0.5
        
        return {
            "accuracy_score": accuracy_score,
            "correct_claims": doğru_count,
            "incorrect_claims": yanlış_count,
            "uncertain_claims": belirsiz_count,
            "analysis_text": text
        }
    
    def _extract_consistency_issues(self, text: str) -> List[str]:
        """Extract consistency issues from analysis text"""
        issues = []
        
        issue_indicators = [
            "çelişki", "tutarsızlık", "mantıksız", "uyumsuz", "hata"
        ]
        
        sentences = text.split('.')
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in issue_indicators):
                issues.append(sentence.strip())
        
        return issues[:5]  # Top 5 issues
    
    def _looks_legitimate_source(self, source: str) -> bool:
        """Check if a source looks legitimate"""
        # Simple heuristics for source legitimacy
        legitimate_indicators = [
            r'\d{4}',  # Contains year
            r'\.org|\.edu|\.gov',  # Educational/government domains
            r'journal|research|study',  # Academic terms
            r'[A-Z][a-z]+ [A-Z][a-z]+',  # Author names
        ]
        
        return any(re.search(pattern, source, re.IGNORECASE) for pattern in legitimate_indicators)
    
    def _calculate_confidence_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall confidence score"""
        try:
            scores = []
            weights = {}
            
            # Fact check score
            if "fact_check" in results and "analysis" in results["fact_check"]:
                fact_score = results["fact_check"]["analysis"].get("accuracy_score", 0.5)
                scores.append(fact_score)
                weights[len(scores) - 1] = 0.3
            
            # Cross-reference score
            if "cross_reference" in results:
                cross_score = results["cross_reference"].get("overall_consistency", 0.5)
                scores.append(cross_score)
                weights[len(scores) - 1] = 0.25
            
            # Logical consistency score
            if "logical_consistency" in results:
                logic_score = results["logical_consistency"].get("consistency_score", 0.5)
                scores.append(logic_score)
                weights[len(scores) - 1] = 0.25
            
            # Source validation score
            if "source_validation" in results:
                source_score = results["source_validation"].get("legitimacy_ratio", 0.5)
                scores.append(source_score)
                weights[len(scores) - 1] = 0.1
            
            # Mathematical validation score
            if "mathematical_validation" in results:
                # For now, assume math validation passes if no errors mentioned
                math_text = results["mathematical_validation"].get("validation_analysis", "")
                math_score = 0.8 if "hata" not in math_text.lower() else 0.3
                scores.append(math_score)
                weights[len(scores) - 1] = 0.1
            
            if not scores:
                return 0.5
            
            # Calculate weighted average
            if weights:
                weighted_sum = sum(scores[i] * weights.get(i, 1) for i in range(len(scores)))
                total_weight = sum(weights.values())
                return round(weighted_sum / total_weight, 3)
            else:
                return round(statistics.mean(scores), 3)
                
        except Exception as e:
            logger.error(f"Confidence calculation error: {e}")
            return 0.5
    
    def _generate_assessment(self, results: Dict[str, Any], confidence: float) -> str:
        """Generate overall assessment"""
        if confidence >= self.confidence_thresholds["high"]:
            return "İçerik yüksek güvenilirlikte. Halüsinasyon riski düşük."
        elif confidence >= self.confidence_thresholds["medium"]:
            return "İçerik orta güvenilirlikte. Bazı noktalar doğrulanmalı."
        elif confidence >= self.confidence_thresholds["low"]:
            return "İçerik düşük güvenilirlikte. Ciddi doğrulama gerekiyor."
        else:
            return "İçerik çok düşük güvenilirlikte. Halüsinasyon riski yüksek."
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Fact check recommendations
        if "fact_check" in results:
            fact_data = results["fact_check"].get("analysis", {})
            if fact_data.get("incorrect_claims", 0) > 0:
                recommendations.append("Yanlış bilgiler tespit edildi. İddialar doğrulanmalı.")
            if fact_data.get("uncertain_claims", 0) > 0:
                recommendations.append("Belirsiz iddialar var. Ek kaynak araştırması yapılmalı.")
        
        # Consistency recommendations
        if "logical_consistency" in results:
            issues = results["logical_consistency"].get("issues_found", [])
            if issues:
                recommendations.append("Mantıksal tutarsızlıklar düzeltilmeli.")
        
        # Source recommendations
        if "source_validation" in results:
            legitimacy = results["source_validation"].get("legitimacy_ratio", 1)
            if legitimacy < 0.5:
                recommendations.append("Daha güvenilir kaynaklar kullanılmalı.")
        
        # Mathematical recommendations
        if "mathematical_validation" in results:
            math_text = results["mathematical_validation"].get("validation_analysis", "")
            if "hata" in math_text.lower():
                recommendations.append("Matematik hesaplamaları kontrol edilmeli.")
        
        if not recommendations:
            recommendations.append("İçerik genel olarak güvenilir görünüyor.")
        
        return recommendations
    
    def _assess_risk_level(self, confidence: float) -> str:
        """Assess hallucination risk level"""
        if confidence >= self.confidence_thresholds["high"]:
            return "low"
        elif confidence >= self.confidence_thresholds["medium"]:
            return "medium"
        elif confidence >= self.confidence_thresholds["low"]:
            return "high"
        else:
            return "critical"

# Global hallucination detector
hallucination_detector = HallucinationDetector()