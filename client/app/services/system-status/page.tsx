"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { useSystemStats } from "@/lib/hooks/useApi";
import { apiClient } from "@/lib/api/client";
import { Loader2, Settings, CheckCircle, XCircle, AlertCircle } from "lucide-react";

export default function SystemStatusPage() {
  const [healthStatus, setHealthStatus] = useState<any>(null);
  const [healthLoading, setHealthLoading] = useState(false);
  const [healthError, setHealthError] = useState<string | null>(null);

  const { loadStats, loadCollectionsInfo, loading, error, data } = useSystemStats();

  const checkHealth = async () => {
    setHealthLoading(true);
    setHealthError(null);
    try {
      const result = await apiClient.healthCheck();
      if (result.success) {
        setHealthStatus(result.data);
      } else {
        setHealthError(result.error || "Health check failed");
      }
    } catch (err) {
      setHealthError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setHealthLoading(false);
    }
  };

  const loadSystemStats = async () => {
    await loadStats();
  };

  const loadCollections = async () => {
    await loadCollectionsInfo();
  };

  useEffect(() => {
    checkHealth();
    loadSystemStats();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case "healthy":
      case "loaded":
      case "idle":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "loading":
        return <Loader2 className="w-5 h-5 text-yellow-500 animate-spin" />;
      case "not_loaded":
      case "error":
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  return (
    <div className="container-x py-8">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Settings className="w-8 h-8 text-gray-600" />
          <h1 className="text-3xl font-bold text-gray-900">Sistem Durumu</h1>
        </div>
        <p className="text-gray-600">
          API ve servislerin durumunu kontrol edin
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Health Status */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">API Sağlık Durumu</h2>
            <Button onClick={checkHealth} disabled={healthLoading} size="sm">
              {healthLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Yenile
            </Button>
          </div>

          {healthError && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              {typeof healthError === 'string' ? healthError : JSON.stringify(healthError)}
            </div>
          )}

          {healthStatus && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">API Durumu</span>
                <div className="flex items-center gap-2">
                  {getStatusIcon(healthStatus.status)}
                  <span className="text-sm capitalize">{healthStatus.status}</span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Versiyon</span>
                <span className="text-sm">{healthStatus.version}</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Son Güncelleme</span>
                <span className="text-sm">{new Date(healthStatus.timestamp).toLocaleString()}</span>
              </div>

              {healthStatus.services && (
                <div className="mt-4">
                  <h3 className="text-sm font-semibold mb-2">Servisler</h3>
                  <div className="space-y-2">
                    {Object.entries(healthStatus.services).map(([service, status]) => (
                      <div key={service} className="flex items-center justify-between">
                        <span className="text-sm">{service}</span>
                        <div className="flex items-center gap-2">
                          {getStatusIcon(status as string)}
                          <span className="text-sm capitalize">{status as string}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* System Statistics */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Sistem İstatistikleri</h2>
            <Button onClick={loadSystemStats} disabled={loading} size="sm">
              {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Yenile
            </Button>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              {typeof error === 'string' ? error : JSON.stringify(error)}
            </div>
          )}

          {data && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Toplam Konuşma</span>
                <span className="text-sm">{data.total_conversations || 0}</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Toplam Öğrenci</span>
                <span className="text-sm">{data.total_students || 0}</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Toplam Özet</span>
                <span className="text-sm">{data.total_summaries || 0}</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Sistem Sağlığı</span>
                <div className="flex items-center gap-2">
                  {getStatusIcon(data.system_health)}
                  <span className="text-sm">{data.system_health}</span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Çalışma Süresi</span>
                <span className="text-sm">{data.uptime}</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Versiyon</span>
                <span className="text-sm">{data.version}</span>
              </div>
            </div>
          )}
        </div>

        {/* Collections Info */}
        <div className="bg-white rounded-lg border border-gray-200 p-6 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Koleksiyon Bilgileri</h2>
            <Button onClick={loadCollections} disabled={loading} size="sm">
              {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Koleksiyonları Yükle
            </Button>
          </div>

          {data && data.collections && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {Object.entries(data.collections).map(([collection, count]) => (
                  <div key={collection} className="bg-gray-50 rounded-lg p-4">
                    <div className="text-sm font-medium text-gray-700 mb-1 capitalize">
                      {collection}
                    </div>
                    <div className="text-2xl font-bold text-gray-900">
                      {typeof count === 'number' ? count.toLocaleString() : count}
                    </div>
                  </div>
                ))}
              </div>

              {data.sync_status && (
                <div className="mt-6">
                  <h3 className="text-sm font-semibold mb-3">Senkronizasyon Durumu</h3>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <span className="text-sm font-medium">RAG Müfredat Dokümanları:</span>
                        <span className="ml-2">{data.sync_status.rag_curriculum_docs}</span>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Müfredat Yükleyici Konuları:</span>
                        <span className="ml-2">{data.sync_status.curriculum_loader_topics}</span>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Fark:</span>
                        <span className="ml-2">{data.sync_status.difference}</span>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Senkronize:</span>
                        <div className="flex items-center gap-2 ml-2">
                          {data.sync_status.synced ? (
                            <CheckCircle className="w-4 h-4 text-green-500" />
                          ) : (
                            <XCircle className="w-4 h-4 text-red-500" />
                          )}
                          <span>{data.sync_status.synced ? "Evet" : "Hayır"}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}