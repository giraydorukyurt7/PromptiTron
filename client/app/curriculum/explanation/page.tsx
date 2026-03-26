"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { useTopicExplanation } from "@/lib/hooks/useApi";
import { Loader2, BookOpen, ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function TopicExplanationPage() {
  const [selectedTopics, setSelectedTopics] = useState<any[]>([]);
  const [explanationLevel, setExplanationLevel] = useState<"basic" | "comprehensive" | "advanced">("comprehensive");
  const [includeExamples, setIncludeExamples] = useState(true);
  const [includeFormulas, setIncludeFormulas] = useState(true);

  const { explainTopics, loading, error, data } = useTopicExplanation();

  useEffect(() => {
    const savedTopics = sessionStorage.getItem('selectedCurriculumTopics');
    if (savedTopics) {
      setSelectedTopics(JSON.parse(savedTopics));
    }
  }, []);

  const handleGenerate = async () => {
    if (selectedTopics.length === 0) {
      alert("Seçilen konular bulunamadı. Lütfen YKS kazanımlar sayfasından konuları seçin.");
      return;
    }

    await explainTopics(selectedTopics, {
      explanation_level: explanationLevel,
      include_examples: includeExamples,
      include_formulas: includeFormulas,
    });
  };

  return (
    <div className="container-x py-8">
      {/* Header */}
      <div className="mb-8">
        <Link href="/yks" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800 mb-4">
          <ArrowLeft className="w-4 h-4" />
          YKS Kazanımlarına Dön
        </Link>
        
        <div className="flex items-center gap-3 mb-4">
          <BookOpen className="w-8 h-8 text-orange-600" />
          <h1 className="text-3xl font-bold text-gray-900">Konu Anlatımı</h1>
        </div>
        <p className="text-gray-600">
          Seçtiğiniz müfredat konularının detaylı anlatımını alın
        </p>
      </div>

      {/* Selected Topics Display */}
      {selectedTopics.length > 0 && (
        <div className="mb-8 bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Seçilen Konular ({selectedTopics.length})</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-40 overflow-y-auto">
            {selectedTopics.map((topic, index) => (
              <div key={index} className="bg-orange-50 p-3 rounded-lg">
                <div className="font-medium text-orange-900">{topic.title}</div>
                <div className="text-sm text-orange-700">
                  {topic.ders} • {topic.sinif}. Sınıf
                  {topic.konu && ` • ${topic.konu}`}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Parameters */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Anlatım Parametreleri</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Anlatım Seviyesi
              </label>
              <select
                value={explanationLevel}
                onChange={(e) => setExplanationLevel(e.target.value as any)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="basic">Temel</option>
                <option value="comprehensive">Kapsamlı</option>
                <option value="advanced">İleri Düzey</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">
                {explanationLevel === "basic" && "Temel kavramlar ve tanımlar"}
                {explanationLevel === "comprehensive" && "Detaylı açıklamalar ve örnekler"}
                {explanationLevel === "advanced" && "İleri düzey analiz ve derinlemesine inceleme"}
              </p>
            </div>

            <div className="space-y-3">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="includeExamples"
                  checked={includeExamples}
                  onChange={(e) => setIncludeExamples(e.target.checked)}
                  className="mr-2"
                />
                <label htmlFor="includeExamples" className="text-sm font-medium text-gray-700">
                  Örnekler ve Uygulamalar Dahil Et
                </label>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="includeFormulas"
                  checked={includeFormulas}
                  onChange={(e) => setIncludeFormulas(e.target.checked)}
                  className="mr-2"
                />
                <label htmlFor="includeFormulas" className="text-sm font-medium text-gray-700">
                  Formüller ve Matematiksel İfadeler Dahil Et
                </label>
              </div>
            </div>

            <Button
              onClick={handleGenerate}
              disabled={loading || selectedTopics.length === 0}
              className="w-full"
            >
              {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Konu Anlatımını Başlat
            </Button>
          </div>

          {/* Explanation Level Info */}
          <div className="mt-6 p-4 bg-orange-50 rounded-lg">
            <h3 className="text-sm font-semibold mb-2">Anlatım Seviyeleri</h3>
            <div className="text-xs text-gray-600 space-y-1">
              <div><strong>Temel:</strong> Hızlı kavram tanımları</div>
              <div><strong>Kapsamlı:</strong> Detaylı açıklamalar ve örnekler</div>
              <div><strong>İleri Düzey:</strong> Derinlemesine analiz ve bağlantılar</div>
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Konu Anlatımı</h2>
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              <strong>Hata:</strong> {typeof error === 'string' ? error : JSON.stringify(error)}
            </div>
          )}

          {loading && (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-orange-600" />
              <span className="ml-2 text-gray-600">Detaylı konu anlatımı hazırlanıyor...</span>
            </div>
          )}

          {data && !loading && (
            <div className="space-y-6">
              {data.success && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                  <strong>✅ Başarılı!</strong> {data.topics_count} konu için {data.explanation_level} seviyesinde anlatım oluşturuldu.
                </div>
              )}

              {/* Explanation Display */}
              {data.explanation && (
                <div className="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="bg-gradient-to-r from-orange-500 to-orange-600 text-white text-sm font-semibold px-3 py-1.5 rounded-full shadow-sm">
                      📚 Konu Anlatımı
                    </span>
                    <span className="bg-gray-100 text-gray-600 text-xs font-medium px-2.5 py-1 rounded-md">
                      {data.explanation_level || "Kapsamlı"} Seviye
                    </span>
                  </div>
                  
                  <div className="prose max-w-none">
                    <div className="whitespace-pre-wrap text-gray-800 text-base leading-relaxed">
                      {data.explanation}
                    </div>
                  </div>
                  
                  {/* Metadata */}
                  <div className="mt-6 pt-4 border-t border-gray-200">
                    <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                      {data.subjects && data.subjects.length > 0 && (
                        <div>
                          <strong>Kapsanan Dersler:</strong> {data.subjects.join(", ")}
                        </div>
                      )}
                      {data.topics_count && (
                        <div>
                          <strong>Konu Sayısı:</strong> {data.topics_count}
                        </div>
                      )}
                      {data.include_examples && (
                        <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                          📝 Örnekler Dahil
                        </span>
                      )}
                      {data.include_formulas && (
                        <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                          🧮 Formüller Dahil
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              )}

              <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                {data.subjects && data.subjects.length > 0 && (
                  <div>
                    <strong>Dersler:</strong> {data.subjects.join(", ")}
                  </div>
                )}
                {data.grade_levels && data.grade_levels.length > 0 && (
                  <div>
                    <strong>Sınıflar:</strong> {data.grade_levels.join(", ")}
                  </div>
                )}
              </div>

              <div className="flex flex-wrap gap-2 text-xs">
                {data.include_examples && (
                  <span className="bg-green-100 text-green-800 px-2 py-1 rounded">
                    ✓ Örnekler Dahil
                  </span>
                )}
                {data.include_formulas && (
                  <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    ✓ Formüller Dahil
                  </span>
                )}
              </div>
            </div>
          )}

          {!data && !loading && !error && selectedTopics.length === 0 && (
            <div className="flex items-center justify-center py-8 text-gray-500">
              <div className="text-center">
                <p>Seçilen konular bulunamadı.</p>
                <Link href="/yks" className="text-blue-600 hover:text-blue-800 text-sm">
                  YKS Kazanımlar sayfasından konuları seçin
                </Link>
              </div>
            </div>
          )}

          {!data && !loading && !error && selectedTopics.length > 0 && (
            <div className="flex items-center justify-center py-8 text-gray-500">
              Konu anlatımı burada görünecek
            </div>
          )}
        </div>
      </div>
    </div>
  );
}