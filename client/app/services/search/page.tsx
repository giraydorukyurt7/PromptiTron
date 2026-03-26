"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useSearch } from "@/lib/hooks/useApi";
import { Loader2, Search as SearchIcon } from "lucide-react";

const COLLECTIONS = [
  { value: "curriculum", label: "Müfredat" },
  { value: "documents", label: "Dokümanlar" },
  { value: "conversations", label: "Konuşmalar" },
  { value: "questions", label: "Sorular" },
];

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [selectedCollections, setSelectedCollections] = useState<string[]>([]);
  const [nResults, setNResults] = useState(10);

  const { search, loading, error, data } = useSearch();

  const handleCollectionChange = (collection: string, checked: boolean) => {
    if (checked) {
      setSelectedCollections(prev => [...prev, collection]);
    } else {
      setSelectedCollections(prev => prev.filter(c => c !== collection));
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) {
      alert("Lütfen bir arama terimi giriniz");
      return;
    }

    await search(query.trim(), {
      collection_names: selectedCollections.length > 0 ? selectedCollections : undefined,
      n_results: nResults,
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  return (
    <div className="container-x py-8">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <SearchIcon className="w-8 h-8 text-yellow-600" />
          <h1 className="text-3xl font-bold text-gray-900">Bilgi Ara</h1>
        </div>
        <p className="text-gray-600">
          Müfredat ve konu bilgilerinde arama yapın
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Search Form */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Arama Parametreleri</h2>
          
          <div className="space-y-4">
            {/* Query */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Arama Terimi
              </label>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Örn: fonksiyonlar, elektrik, osmanlı devleti..."
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Collections */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Arama Kapsamı
              </label>
              <div className="space-y-2">
                {COLLECTIONS.map((collection) => (
                  <label key={collection.value} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={selectedCollections.includes(collection.value)}
                      onChange={(e) => handleCollectionChange(collection.value, e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm">{collection.label}</span>
                  </label>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Hiç seçilmezse tüm koleksiyonlarda arar
              </p>
            </div>

            {/* Number of Results */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sonuç Sayısı
              </label>
              <input
                type="number"
                min="1"
                max="50"
                value={nResults}
                onChange={(e) => setNResults(parseInt(e.target.value) || 1)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <Button
              onClick={handleSearch}
              disabled={loading || !query.trim()}
              className="w-full"
            >
              {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              <SearchIcon className="w-4 h-4 mr-2" />
              Ara
            </Button>
          </div>
        </div>

        {/* Results */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Arama Sonuçları</h2>
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              {typeof error === 'string' ? error : JSON.stringify(error)}
            </div>
          )}

          {loading && (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
              <span className="ml-2 text-gray-600">Aranıyor...</span>
            </div>
          )}

          {data && !loading && (
            <div className="space-y-4">
              {/* Search Info */}
              <div className="text-sm text-gray-500 mb-4">
                <strong>{data.total_results || 0}</strong> sonuç bulundu
                {data.search_time && ` (${data.search_time.toFixed(3)} saniye)`}
              </div>

              {/* Results */}
              {data.results && data.results.length > 0 ? (
                <div className="space-y-4">
                  {data.results.map((result: any, index: number) => (
                    <div key={result.result_id || index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="font-medium text-gray-900">
                          {result.title || "Başlıksız"}
                        </h3>
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                          {result.source_type}
                        </span>
                      </div>
                      
                      {result.subject && (
                        <div className="text-xs text-blue-600 mb-2">
                          {result.subject}
                          {result.topic && ` • ${result.topic}`}
                        </div>
                      )}
                      
                      <div className="text-sm text-gray-700 mb-3">
                        {result.content.length > 300 
                          ? `${result.content.substring(0, 300)}...`
                          : result.content}
                      </div>
                      
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>Relevans: {(result.relevance_score * 100).toFixed(1)}%</span>
                        {result.metadata && Object.keys(result.metadata).length > 0 && (
                          <span>Metadata: {Object.keys(result.metadata).length} özellik</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  Sonuç bulunamadı
                </div>
              )}

              {/* Suggestions */}
              {data.suggestions && data.suggestions.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-sm font-semibold mb-2">Öneriler:</h3>
                  <div className="flex flex-wrap gap-2">
                    {data.suggestions.map((suggestion: string, index: number) => (
                      <button
                        key={index}
                        onClick={() => setQuery(suggestion)}
                        className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {!data && !loading && !error && (
            <div className="flex items-center justify-center py-8 text-gray-500">
              Arama sonuçları burada görünecek
            </div>
          )}
        </div>
      </div>
    </div>
  );
}