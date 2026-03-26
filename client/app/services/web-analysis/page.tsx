"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useWebAnalysis } from "@/lib/hooks/useApi";
import { Loader2, Globe } from "lucide-react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const ANALYSIS_TYPES = [
  { value: "educational", label: "Eğitim İçeriği Analizi" },
  { value: "yks_compliance", label: "YKS Uyumluluk Analizi" },
  { value: "curriculum_mapping", label: "Müfredat Eşleştirme" },
  { value: "comprehensive", label: "Kapsamlı Analiz" },
  { value: "custom", label: "Özel Analiz" },
];

export default function WebAnalysisPage() {
  const [url, setUrl] = useState("");
  const [analysisType, setAnalysisType] = useState("educational");
  const [customPrompt, setCustomPrompt] = useState("");

  const { analyzeWebsite, loading, error, data } = useWebAnalysis();

  const handleAnalyze = async () => {
    if (!url.trim()) {
      alert("Lütfen bir URL giriniz");
      return;
    }

    // Basic URL validation
    try {
      new URL(url);
    } catch {
      alert("Lütfen geçerli bir URL giriniz (http:// veya https:// ile başlamalı)");
      return;
    }

    const options: any = { analysis_type: analysisType };
    if (analysisType === "custom" && customPrompt.trim()) {
      options.custom_prompt = customPrompt.trim();
    }

    await analyzeWebsite(url.trim(), options);
  };

  return (
    <div className="container-x py-8">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Globe className="w-8 h-8 text-cyan-600" />
          <h1 className="text-3xl font-bold text-gray-900">Web Sitesi Analizi</h1>
        </div>
        <p className="text-gray-600">
          Web sitelerini eğitim değeri açısından analiz edin
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Analiz Parametreleri</h2>
          
          <div className="space-y-4">
            {/* URL */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Web Sitesi URL'si
              </label>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com"
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                Analiz edilecek web sitesinin tam URL'sini giriniz
              </p>
            </div>

            {/* Analysis Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Analiz Türü
              </label>
              <select
                value={analysisType}
                onChange={(e) => setAnalysisType(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {ANALYSIS_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Custom Prompt */}
            {analysisType === "custom" && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Özel Analiz Talimatı
                </label>
                <textarea
                  value={customPrompt}
                  onChange={(e) => setCustomPrompt(e.target.value)}
                  placeholder="Web sitesini nasıl analiz etmek istediğinizi açıklayın..."
                  rows={4}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  AI'ya web sitesini nasıl analiz etmesi gerektiğini söyleyin
                </p>
              </div>
            )}

            <Button
              onClick={handleAnalyze}
              disabled={loading || !url.trim()}
              className="w-full"
            >
              {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Web Sitesini Analiz Et
            </Button>
          </div>

          {/* Analysis Type Descriptions */}
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-sm font-semibold mb-2">Analiz Türleri</h3>
            <div className="text-xs text-gray-600 space-y-1">
              <div><strong>Eğitim İçeriği:</strong> Genel eğitim değeri analizi</div>
              <div><strong>YKS Uyumluluk:</strong> YKS müfredatına uygunluk kontrolü</div>
              <div><strong>Müfredat Eşleştirme:</strong> Hangi konularla eşleştiğini bulur</div>
              <div><strong>Kapsamlı:</strong> Tüm analiz türlerini birleştirir</div>
              <div><strong>Özel:</strong> Kendi talimatınızla analiz</div>
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Analiz Sonuçları</h2>
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              <strong>Hata:</strong> {typeof error === 'string' ? error : JSON.stringify(error)}
            </div>
          )}

          {loading && (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
              <span className="ml-2 text-gray-600">Web sitesi analiz ediliyor...</span>
            </div>
          )}

          {data && !loading && (
            <div className="space-y-4">
              {/* Success Message */}
              {data.success && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-4">
                  <strong>✅ Başarılı!</strong> Web sitesi analizi tamamlandı.
                </div>
              )}

              <Accordion type="single" collapsible defaultValue="url-info" className="space-y-2">
                {/* URL Info */}
                {data.url && (
                  <AccordionItem value="url-info" className="bg-white border border-gray-200 rounded-lg">
                    <AccordionTrigger className="px-4 hover:no-underline">
                      <span className="font-medium text-gray-900 flex items-center gap-2">
                        🌐 Analiz Edilen URL
                      </span>
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pb-4">
                      <p className="text-sm text-blue-600 break-all bg-blue-50 p-2 rounded">{data.url}</p>
                    </AccordionContent>
                  </AccordionItem>
                )}

                {/* YKS Curriculum Check */}
                {data.curriculum_check && (
                  <AccordionItem value="curriculum-check" className="bg-white border-2 border-blue-200 rounded-lg">
                    <AccordionTrigger className="px-4 hover:no-underline">
                      <span className="text-lg font-semibold text-blue-900 flex items-center gap-2">
                        📊 YKS Müfredat Uygunluk Kontrolü
                      </span>
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pb-4">
                      {data.curriculum_check.yks_relevant ? (
                        <div className="space-y-3">
                          <div className="flex items-center gap-2">
                            <span className="text-green-600 text-lg">✅</span>
                            <span className="text-green-700 font-medium">İçerik YKS müfredatına uygun</span>
                          </div>
                          
                          {data.curriculum_check.subjects && (
                            <div>
                              <span className="font-medium text-gray-700">🎯 İlgili Dersler:</span>
                              <div className="flex flex-wrap gap-2 mt-2">
                                {data.curriculum_check.subjects.map((subject: string, index: number) => (
                                  <span key={index} className="bg-cyan-100 text-cyan-800 px-2 py-1 rounded-md text-sm font-medium">
                                    {subject}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          {data.curriculum_check.confidence_score && (
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-gray-700">🎖️ Güven Skoru:</span>
                              <span className="text-blue-700 font-semibold">
                                {data.curriculum_check.confidence_score.toFixed(2)}/1.0
                              </span>
                            </div>
                          )}
                          
                          {data.curriculum_check.education_level && (
                            <div className="text-sm text-gray-600">
                              <span className="font-medium">Eğitim Seviyesi:</span> {data.curriculum_check.education_level}
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="space-y-3">
                          <div className="flex items-center gap-2">
                            <span className="text-red-600 text-lg">❌</span>
                            <span className="text-red-700 font-medium">İçerik YKS müfredat dışı</span>
                          </div>
                          
                          {data.curriculum_check.reason && (
                            <div className="text-yellow-700 bg-yellow-50 p-3 rounded">
                              <span className="font-medium">⚠️ Sebep:</span> {data.curriculum_check.reason}
                            </div>
                          )}
                          
                          <p className="text-sm text-gray-600">
                            Bu web sitesi YKS dersleriyle ilgili eğitim içeriği içermiyor.
                          </p>
                        </div>
                      )}
                    </AccordionContent>
                  </AccordionItem>
                )}

                {/* Content Information */}
                {data.content_info && (
                  <AccordionItem value="content-info" className="bg-white border border-gray-200 rounded-lg">
                    <AccordionTrigger className="px-4 hover:no-underline">
                      <span className="font-medium text-gray-900 flex items-center gap-2">
                        📄 İçerik Bilgileri
                      </span>
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pb-4">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div className="bg-blue-50 p-3 rounded">
                          <span className="font-medium">📝 Kelime Sayısı:</span>
                          <span className="ml-2">{data.content_info.word_count || 0}</span>
                        </div>
                        <div className="bg-green-50 p-3 rounded">
                          <span className="font-medium">🖼️ Görsel Sayısı:</span>
                          <span className="ml-2">{data.content_info.images_count || 0}</span>
                        </div>
                        <div className="bg-purple-50 p-3 rounded">
                          <span className="font-medium">🔗 Link Sayısı:</span>
                          <span className="ml-2">{data.content_info.links_count || 0}</span>
                        </div>
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                )}

                {/* Structured Data Analysis */}
                {data.structured_data && (
                  <AccordionItem value="structured-data" className="bg-white border border-gray-200 rounded-lg">
                    <AccordionTrigger className="px-4 hover:no-underline">
                      <span className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                        📊 Yapılandırılmış Veri Analizi
                      </span>
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pb-4">
                      <div className="space-y-4">
                        {data.structured_data.subject && (
                          <div>
                            <span className="font-medium text-blue-700">📚 Ana Ders:</span>
                            <span className="ml-2">{data.structured_data.subject}</span>
                          </div>
                        )}
                        
                        {data.structured_data.topics && data.structured_data.topics.length > 0 && (
                          <div>
                            <span className="font-medium text-blue-700">📋 Konular ({data.structured_data.topics.length} adet):</span>
                            <div className="flex flex-wrap gap-1 mt-2">
                              {data.structured_data.topics.map((topic: string, index: number) => (
                                <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                                  {topic}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {data.structured_data.difficulty_level && (
                          <div>
                            <span className="font-medium text-blue-700">⚡ Zorluk Seviyesi:</span>
                            <span className="ml-2">{data.structured_data.difficulty_level}</span>
                          </div>
                        )}
                        
                        {data.structured_data.education_level && (
                          <div>
                            <span className="font-medium text-blue-700">🎓 Eğitim Seviyesi:</span>
                            <span className="ml-2">{data.structured_data.education_level}</span>
                          </div>
                        )}
                        
                        {data.structured_data.key_concepts && data.structured_data.key_concepts.length > 0 && (
                          <div>
                            <span className="font-medium text-blue-700">🧠 Anahtar Kavramlar ({data.structured_data.key_concepts.length} adet):</span>
                            <ul className="list-disc list-inside mt-2 ml-4 space-y-1">
                              {data.structured_data.key_concepts.map((concept: string, index: number) => (
                                <li key={index} className="text-sm">{concept}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        
                        {data.structured_data.learning_objectives && data.structured_data.learning_objectives.length > 0 && (
                          <div>
                            <span className="font-medium text-blue-700">🎯 Öğrenme Hedefleri ({data.structured_data.learning_objectives.length} adet):</span>
                            <ol className="list-decimal list-inside mt-2 ml-4 space-y-1">
                              {data.structured_data.learning_objectives.map((objective: string, index: number) => (
                                <li key={index} className="text-sm">{objective}</li>
                              ))}
                            </ol>
                          </div>
                        )}
                        
                        {data.structured_data.formulas && data.structured_data.formulas.length > 0 && (
                          <div>
                            <span className="font-medium text-blue-700">📐 Formüller ({data.structured_data.formulas.length} adet):</span>
                            <ol className="list-decimal list-inside mt-2 ml-4 space-y-1">
                              {data.structured_data.formulas.map((formula: string, index: number) => (
                                <li key={index} className="text-sm font-mono bg-gray-100 p-1 rounded">{formula}</li>
                              ))}
                            </ol>
                          </div>
                        )}
                        
                        {data.structured_data.exam_relevance && (
                          <div>
                            <span className="font-medium text-blue-700">🎯 Sınav Uygunluğu:</span>
                            <span className="ml-2">{data.structured_data.exam_relevance}</span>
                          </div>
                        )}
                        
                        {data.structured_data.estimated_study_time && (
                          <div>
                            <span className="font-medium text-blue-700">⏱️ Tahmini Çalışma Süresi:</span>
                            <span className="ml-2">{data.structured_data.estimated_study_time} dakika</span>
                          </div>
                        )}
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                )}

                {/* Educational Analysis */}
                {data.educational_analysis && (
                  <AccordionItem value="educational-analysis" className="bg-white border border-gray-200 rounded-lg">
                    <AccordionTrigger className="px-4 hover:no-underline">
                      <span className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                        🎓 Detaylı Eğitim Analizi
                      </span>
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pb-4">
                      <div className="prose prose-sm max-w-none">
                        <div className="whitespace-pre-wrap text-gray-700 bg-gray-50 p-4 rounded-lg">
                          {data.educational_analysis}
                        </div>
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                )}

                {/* Generated Questions */}
                {data.generated_questions && data.generated_questions.length > 0 && (
                  <AccordionItem value="generated-questions" className="bg-white border border-gray-200 rounded-lg">
                    <AccordionTrigger className="px-4 hover:no-underline">
                      <span className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                        ❓ Üretilen Sorular: {data.generated_questions.length} adet
                      </span>
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pb-4">
                      <div className="space-y-4">
                        {data.generated_questions.map((question: any, index: number) => (
                          <div key={index} className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                            <div className="font-medium text-yellow-800 mb-2">Soru {index + 1}:</div>
                            <div className="text-gray-700 text-sm">
                              {question.content || JSON.stringify(question)}
                            </div>
                          </div>
                        ))}
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                )}

                {/* Study Materials */}
                {data.study_materials && (
                  <AccordionItem value="study-materials" className="bg-white border border-gray-200 rounded-lg">
                    <AccordionTrigger className="px-4 hover:no-underline">
                      <span className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                        📚 Çalışma Materyalleri
                      </span>
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pb-4">
                      {data.study_materials.summary && (
                        <div className="mb-4">
                          <h4 className="font-medium text-green-700 mb-2 flex items-center gap-2">
                            📝 İçerik Özeti:
                          </h4>
                          <div className="text-gray-700 bg-green-50 p-4 rounded-lg">
                            {data.study_materials.summary}
                          </div>
                        </div>
                      )}
                      
                      {data.study_materials.key_points && data.study_materials.key_points.length > 0 && (
                        <div className="mb-4">
                          <h4 className="font-medium text-green-700 mb-2 flex items-center gap-2">
                            🔑 Önemli Noktalar ({data.study_materials.key_points.length} adet):
                          </h4>
                          <ol className="list-decimal list-inside space-y-1 ml-4">
                            {data.study_materials.key_points.map((point: string, index: number) => (
                              <li key={index} className="text-sm text-gray-700">{point}</li>
                            ))}
                          </ol>
                        </div>
                      )}
                      
                      {data.study_materials.concept_map && (
                        <div>
                          <h4 className="font-medium text-green-700 mb-2 flex items-center gap-2">
                            🗺️ Kavram Haritası:
                          </h4>
                          <div className="text-gray-700 bg-green-50 p-4 rounded-lg font-mono text-sm">
                            {data.study_materials.concept_map}
                          </div>
                        </div>
                      )}
                    </AccordionContent>
                  </AccordionItem>
                )}
              </Accordion>

              {/* Processing Time */}
              {data.processing_time && (
                <div className="text-xs text-gray-500 text-center py-4 border-t mt-4">
                  ⏱️ İşlem süresi: {data.processing_time.toFixed(2)} saniye
                </div>
              )}
            </div>
          )}

          {!data && !loading && !error && (
            <div className="flex items-center justify-center py-8 text-gray-500">
              Analiz sonuçları burada görünecek
            </div>
          )}
        </div>
      </div>
    </div>
  );
}