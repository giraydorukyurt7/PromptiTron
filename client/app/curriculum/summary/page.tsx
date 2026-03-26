"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { useCurriculumSummary } from "@/lib/hooks/useApi";
import { Loader2, FileText, ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function CurriculumSummaryPage() {
  const [selectedTopics, setSelectedTopics] = useState<any[]>([]);
  const [summaryStyle, setSummaryStyle] = useState<"detailed" | "brief" | "bullet_points">("detailed");
  const [includeExamples, setIncludeExamples] = useState(true);

  const { summarizeTopics, loading, error, data } = useCurriculumSummary();

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

    await summarizeTopics(selectedTopics, {
      summary_style: summaryStyle,
      include_examples: includeExamples,
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
          <FileText className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">Konu Özeti</h1>
        </div>
        <p className="text-gray-600">
          Seçtiğiniz müfredat konularının kapsamlı özetini oluşturun
        </p>
      </div>

      {/* Selected Topics Display */}
      {selectedTopics.length > 0 && (
        <div className="mb-8 bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Seçilen Konular ({selectedTopics.length})</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-40 overflow-y-auto">
            {selectedTopics.map((topic, index) => (
              <div key={index} className="bg-blue-50 p-3 rounded-lg">
                <div className="font-medium text-blue-900">{topic.title}</div>
                <div className="text-sm text-blue-700">
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
          <h2 className="text-lg font-semibold mb-4">Özet Parametreleri</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Özet Stili
              </label>
              <select
                value={summaryStyle}
                onChange={(e) => setSummaryStyle(e.target.value as any)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="detailed">Detaylı</option>
                <option value="brief">Kısa</option>
                <option value="bullet_points">Madde Madde</option>
              </select>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="includeExamples"
                checked={includeExamples}
                onChange={(e) => setIncludeExamples(e.target.checked)}
                className="mr-2"
              />
              <label htmlFor="includeExamples" className="text-sm font-medium text-gray-700">
                Örnekler Dahil Et
              </label>
            </div>

            <Button
              onClick={handleGenerate}
              disabled={loading || selectedTopics.length === 0}
              className="w-full"
            >
              {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Özet Oluştur
            </Button>
          </div>
        </div>

        {/* Results */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Konu Özeti</h2>
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              <strong>Hata:</strong> {typeof error === 'string' ? error : JSON.stringify(error)}
            </div>
          )}

          {loading && (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
              <span className="ml-2 text-gray-600">Konu özeti hazırlanıyor...</span>
            </div>
          )}

          {data && !loading && (
            <div className="space-y-6">
              {data.success && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                  <strong>✅ Başarılı!</strong> {data.topics_count} konu için {data.summary_style} özet oluşturuldu.
                </div>
              )}

              {/* Summary Display */}
              {data.summary && (
                <div className="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="bg-gradient-to-r from-green-500 to-green-600 text-white text-sm font-semibold px-3 py-1.5 rounded-full shadow-sm">
                      📝 Özet
                    </span>
                    <span className="bg-gray-100 text-gray-600 text-xs font-medium px-2.5 py-1 rounded-md">
                      {data.summary_style || "Detaylı"} Özet
                    </span>
                  </div>
                  
                  <div className="prose max-w-none">
                    <div className="whitespace-pre-wrap text-gray-800 text-base leading-relaxed">
                      {data.summary}
                    </div>
                  </div>
                  
                  {/* Metadata */}
                  {data.topics_count && (
                    <div className="mt-4 pt-4 border-t border-gray-200 text-xs text-gray-500">
                      <div className="flex gap-4">
                        <span>📚 {data.topics_count} konu özetlendi</span>
                        {data.subjects && <span>📋 Dersler: {data.subjects.join(", ")}</span>}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {data.subjects && data.subjects.length > 0 && (
                <div className="text-sm text-gray-600">
                  <strong>Kapsanan Dersler:</strong> {data.subjects.join(", ")}
                </div>
              )}
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
              Özet burada görünecek
            </div>
          )}
        </div>
      </div>
    </div>
  );
}