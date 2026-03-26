"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useContentAnalysis } from "@/lib/hooks/useApi";
import { Loader2, FileText, Lightbulb } from "lucide-react";

const ANALYSIS_TYPES = [
  { value: "general", label: "Genel Analiz" },
  { value: "educational", label: "Eğitimsel Analiz" },
  { value: "summary", label: "Özet Çıkarma" },
  { value: "key_points", label: "Ana Noktalar" },
  { value: "questions", label: "Soru Üretme" },
  { value: "critique", label: "Eleştirel Analiz" },
];

export default function ContentAnalysisPage() {
  const [content, setContent] = useState("");
  const [analysisType, setAnalysisType] = useState("general");
  const [includeSuggestions, setIncludeSuggestions] = useState(true);

  const { analyzeContent, loading, error, data } = useContentAnalysis();

  const handleAnalyze = async () => {
    if (!content.trim()) {
      alert("Lütfen analiz edilecek içeriği girin");
      return;
    }

    await analyzeContent(content, {
      analysis_type: analysisType,
      include_suggestions: includeSuggestions,
    });
  };

  return (
    <div className="container-x py-8">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <FileText className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">İçerik Analizi</h1>
        </div>
        <p className="text-gray-600">
          Metin içeriğini analiz edin ve değerli bilgiler çıkarın
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Analiz Parametreleri</h2>
          
          <div className="space-y-4">
            {/* Content Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Analiz Edilecek İçerik
              </label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Analiz etmek istediğiniz metni buraya yapıştırın..."
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[200px] resize-vertical"
                rows={8}
              />
              <div className="text-xs text-gray-500 mt-1">
                Karakter sayısı: {content.length}
              </div>
            </div>

            {/* Analysis Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Analiz Tipi
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

            {/* Include Suggestions */}
            <div>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={includeSuggestions}
                  onChange={(e) => setIncludeSuggestions(e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Öneriler ve geliştirme fırsatları dahil et</span>
              </label>
            </div>

            <Button
              onClick={handleAnalyze}
              disabled={loading || !content.trim()}
              className="w-full"
            >
              {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              İçeriği Analiz Et
            </Button>
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
              <span className="ml-2 text-gray-600">İçerik analiz ediliyor...</span>
            </div>
          )}

          {data && !loading && (
            <div className="space-y-6">
              {data.success && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4">
                  <strong>✅ Başarılı!</strong> İçerik analizi tamamlandı.
                </div>
              )}

              {/* Analysis Results */}
              {data.analysis && (
                <div className="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="bg-gradient-to-r from-blue-500 to-blue-600 text-white text-sm font-semibold px-3 py-1.5 rounded-full shadow-sm">
                      📊 Analiz Raporu
                    </span>
                    <span className="bg-gray-100 text-gray-600 text-xs font-medium px-2.5 py-1 rounded-md">
                      {ANALYSIS_TYPES.find(t => t.value === analysisType)?.label}
                    </span>
                  </div>
                  
                  <div className="prose max-w-none">
                    <div className="whitespace-pre-wrap text-gray-800 text-base leading-relaxed">
                      {data.analysis}
                    </div>
                  </div>
                </div>
              )}

              {/* Suggestions */}
              {data.suggestions && includeSuggestions && (
                <div className="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="bg-gradient-to-r from-yellow-500 to-yellow-600 text-white text-sm font-semibold px-3 py-1.5 rounded-full shadow-sm">
                      💡 Öneriler
                    </span>
                  </div>
                  
                  <div className="prose max-w-none">
                    <div className="whitespace-pre-wrap text-gray-800 text-base leading-relaxed">
                      {data.suggestions}
                    </div>
                  </div>
                </div>
              )}

              {/* Metadata */}
              <div className="mt-6 pt-4 border-t border-gray-200 text-xs text-gray-500">
                <div className="flex gap-4">
                  <span>📝 Karakter: {content.length}</span>
                  <span>🔍 Analiz Tipi: {ANALYSIS_TYPES.find(t => t.value === analysisType)?.label}</span>
                  {data.agent_used && <span>🤖 Sistem: {data.agent_used}</span>}
                </div>
              </div>
            </div>
          )}

          {!data && !loading && !error && (
            <div className="flex items-center justify-center py-8 text-gray-500">
              <div className="text-center">
                <Lightbulb className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                <p>Analiz sonuçları burada görünecek</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}