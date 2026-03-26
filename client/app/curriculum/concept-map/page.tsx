"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { useConceptMap } from "@/lib/hooks/useApi";
import { Loader2, Map, ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function ConceptMapPage() {
  const [selectedTopics, setSelectedTopics] = useState<any[]>([]);
  const [mapType, setMapType] = useState<"hierarchical" | "network" | "flowchart">("hierarchical");
  const [includeConnections, setIncludeConnections] = useState(true);

  const { generateConceptMap, loading, error, data } = useConceptMap();

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

    await generateConceptMap(selectedTopics, {
      map_type: mapType,
      include_connections: includeConnections,
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
          <Map className="w-8 h-8 text-purple-600" />
          <h1 className="text-3xl font-bold text-gray-900">Kavram Haritası</h1>
        </div>
        <p className="text-gray-600">
          Seçtiğiniz müfredat konularının mantık bağlantılarını görselleştirin
        </p>
      </div>

      {/* Selected Topics Display */}
      {selectedTopics.length > 0 && (
        <div className="mb-8 bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Seçilen Konular ({selectedTopics.length})</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-40 overflow-y-auto">
            {selectedTopics.map((topic, index) => (
              <div key={index} className="bg-purple-50 p-3 rounded-lg">
                <div className="font-medium text-purple-900">{topic.title}</div>
                <div className="text-sm text-purple-700">
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
          <h2 className="text-lg font-semibold mb-4">Harita Parametreleri</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Harita Tipi
              </label>
              <select
                value={mapType}
                onChange={(e) => setMapType(e.target.value as any)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="hierarchical">Hiyerarşik</option>
                <option value="network">Ağ Yapısı</option>
                <option value="flowchart">Akış Şeması</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">
                {mapType === "hierarchical" && "Konuları yukarıdan aşağıya düzenler"}
                {mapType === "network" && "Konuları birbirine bağlı ağ halinde gösterir"}
                {mapType === "flowchart" && "Konuları akış şeması olarak düzenler"}
              </p>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="includeConnections"
                checked={includeConnections}
                onChange={(e) => setIncludeConnections(e.target.checked)}
                className="mr-2"
              />
              <label htmlFor="includeConnections" className="text-sm font-medium text-gray-700">
                Konular Arası Bağlantıları Göster
              </label>
            </div>

            <Button
              onClick={handleGenerate}
              disabled={loading || selectedTopics.length === 0}
              className="w-full"
            >
              {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Kavram Haritası Oluştur
            </Button>
          </div>

          {/* Map Type Descriptions */}
          <div className="mt-6 p-4 bg-purple-50 rounded-lg">
            <h3 className="text-sm font-semibold mb-2">Harita Tipleri</h3>
            <div className="text-xs text-gray-600 space-y-1">
              <div><strong>Hiyerarşik:</strong> Ana kavramdan alt kavramlara doğru</div>
              <div><strong>Ağ Yapısı:</strong> Kavramları çok yönlü bağlantılarla</div>
              <div><strong>Akış Şeması:</strong> Süreç odaklı düzenleme</div>
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Kavram Haritası</h2>
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              <strong>Hata:</strong> {typeof error === 'string' ? error : JSON.stringify(error)}
            </div>
          )}

          {loading && (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
              <span className="ml-2 text-gray-600">Kavram haritası oluşturuluyor...</span>
            </div>
          )}

          {data && !loading && (
            <div className="space-y-6">
              {data.success && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                  <strong>✅ Başarılı!</strong> {data.topics_count} konu için {data.map_type} tipi kavram haritası oluşturuldu.
                </div>
              )}

              {/* Concept Map Display */}
              {data.concept_map && (
                <div className="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="bg-gradient-to-r from-purple-500 to-purple-600 text-white text-sm font-semibold px-3 py-1.5 rounded-full shadow-sm">
                      🗺️ Kavram Haritası
                    </span>
                    <span className="bg-gray-100 text-gray-600 text-xs font-medium px-2.5 py-1 rounded-md">
                      {data.map_type || "Hiyerarşik"} Tip
                    </span>
                  </div>
                  
                  <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <div className="whitespace-pre-wrap text-gray-800 text-base leading-relaxed font-mono text-sm overflow-auto max-h-[500px]">
                      {data.concept_map}
                    </div>
                  </div>
                  
                  {/* Metadata */}
                  {(data.main_concepts || data.connections_count) && (
                    <div className="mt-4 pt-4 border-t border-gray-200 text-xs text-gray-500">
                      <div className="flex gap-4">
                        {data.main_concepts && <span>💡 Ana Kavramlar: {data.main_concepts.length}</span>}
                        {data.connections_count && <span>🔗 Bağlantılar: {data.connections_count}</span>}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {data.main_concepts && data.main_concepts.length > 0 && (
                <div className="bg-purple-50 p-4 rounded-lg">
                  <h3 className="font-medium text-purple-900 mb-2">Ana Kavramlar:</h3>
                  <div className="flex flex-wrap gap-2">
                    {data.main_concepts.map((concept: string, index: number) => (
                      <span key={index} className="bg-purple-200 text-purple-800 px-2 py-1 rounded text-sm">
                        {concept}
                      </span>
                    ))}
                  </div>
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
              Kavram haritası burada görünecek
            </div>
          )}
        </div>
      </div>
    </div>
  );
}