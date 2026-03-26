"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useYouTubeAnalysis } from "@/lib/hooks/useApi";
import { Loader2, Youtube, Play, ExternalLink, Clock } from "lucide-react";

export default function YouTubeAnalysisPage() {
  const [videoUrl, setVideoUrl] = useState("");
  const [customPrompt, setCustomPrompt] = useState("");

  const { analyzeVideo, loading, error, data } = useYouTubeAnalysis();

  const isValidYouTubeUrl = (url: string) => {
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/|m\.youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})/;
    return youtubeRegex.test(url);
  };

  const extractVideoId = (url: string) => {
    const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/|m\.youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})/);
    return match ? match[1] : null;
  };

  const getVideoThumbnail = (url: string) => {
    const videoId = extractVideoId(url);
    return videoId ? `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg` : null;
  };

  const handleAnalyze = async () => {
    if (!videoUrl.trim()) {
      alert("Lütfen YouTube video URL'si girin");
      return;
    }

    if (!isValidYouTubeUrl(videoUrl)) {
      alert("Geçerli bir YouTube URL'si girin (örn: https://www.youtube.com/watch?v=...)");
      return;
    }

    await analyzeVideo(videoUrl, {
      custom_prompt: customPrompt.trim() || undefined,
    });
  };

  const videoId = extractVideoId(videoUrl);
  const thumbnail = getVideoThumbnail(videoUrl);

  return (
    <div className="container-x py-8">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Youtube className="w-8 h-8 text-red-600" />
          <h1 className="text-3xl font-bold text-gray-900">YouTube Video Analizi</h1>
        </div>
        <p className="text-gray-600">
          YouTube videolarını analiz edin, özet çıkarın ve ders notları oluşturun
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Video Analizi</h2>
          
          <div className="space-y-4">
            {/* Video URL */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                YouTube Video URL
              </label>
              <input
                type="url"
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {videoUrl && !isValidYouTubeUrl(videoUrl) && (
                <div className="text-red-600 text-xs mt-1">
                  Geçersiz YouTube URL formatı
                </div>
              )}
            </div>

            {/* Video Preview */}
            {videoUrl && isValidYouTubeUrl(videoUrl) && thumbnail && (
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <div className="relative">
                  <img 
                    src={thumbnail} 
                    alt="Video önizlemesi"
                    className="w-full h-48 object-cover"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.src = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
                    }}
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center">
                    <Play className="w-12 h-12 text-white" />
                  </div>
                </div>
                <div className="p-3 bg-gray-50">
                  <div className="flex items-center justify-between text-xs text-gray-600">
                    <span>Video ID: {videoId}</span>
                    <a 
                      href={videoUrl} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-blue-600 hover:text-blue-800"
                    >
                      <ExternalLink className="w-3 h-3" />
                      YouTube'da Aç
                    </a>
                  </div>
                </div>
              </div>
            )}


            {/* Custom Prompt */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Özel Talimat (Opsiyonel)
              </label>
              <textarea
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder="Analize yönelik özel talimatlarınız..."
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
              />
              <div className="text-xs text-gray-500 mt-1">
                Örn: "Bu matematik dersindeki formüllere odaklan" veya "Sadece tarihsel olayları listele"
              </div>
            </div>

            <Button
              onClick={handleAnalyze}
              disabled={loading || !videoUrl.trim() || !isValidYouTubeUrl(videoUrl)}
              className="w-full"
            >
              {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Videoyu Analiz Et
            </Button>

            {/* Info Box */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <div className="text-xs text-blue-800">
                <strong>💡 İpucu:</strong> En iyi sonuç için eğitimsel videolar seçin. 
                Video süresi ne kadar uzun olursa analiz o kadar detaylı olur.
              </div>
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
              <Loader2 className="w-8 h-8 animate-spin text-red-600" />
              <span className="ml-2 text-gray-600">Video analiz ediliyor...</span>
            </div>
          )}

          {data && !loading && (
            <div className="space-y-6">
              {data.success && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4">
                  <strong>✅ Başarılı!</strong> Video analizi tamamlandı.
                </div>
              )}

              {/* Educational Analysis */}
              {(data.educational_analysis || data.analysis) && (
                <div className="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="bg-gradient-to-r from-purple-500 to-purple-600 text-white text-sm font-semibold px-3 py-1.5 rounded-full shadow-sm">
                      🎓 Eğitimsel Analiz
                    </span>
                  </div>
                  
                  <div className="prose max-w-none">
                    <div className="whitespace-pre-wrap text-gray-800 text-base leading-relaxed">
                      {data.educational_analysis || data.analysis}
                    </div>
                  </div>
                </div>
              )}

              {/* Video Info */}
              {data.video_info && (
                <div className="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="bg-gradient-to-r from-purple-500 to-purple-600 text-white text-sm font-semibold px-3 py-1.5 rounded-full shadow-sm">
                      ℹ️ Video Bilgileri
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    {data.video_info.title && (
                      <div className="md:col-span-2">
                        <span className="font-medium">Başlık:</span> {data.video_info.title}
                      </div>
                    )}
                    {data.video_info.duration && (
                      <div className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        <span className="font-medium">Süre:</span> {data.video_info.duration}
                      </div>
                    )}
                    {data.video_info.channel && (
                      <div>
                        <span className="font-medium">Kanal:</span> {data.video_info.channel}
                      </div>
                    )}
                    {data.video_info.views && (
                      <div>
                        <span className="font-medium">Görüntülenme:</span> {data.video_info.views}
                      </div>
                    )}
                    {data.video_info.publish_date && (
                      <div>
                        <span className="font-medium">Yayın Tarihi:</span> {data.video_info.publish_date}
                      </div>
                    )}
                    {data.video_info.description && (
                      <div className="md:col-span-2 mt-2">
                        <span className="font-medium">Açıklama:</span>
                        <div className="mt-1 text-gray-600 text-xs max-h-20 overflow-y-auto">
                          {data.video_info.description}
                        </div>
                      </div>
                    )}
                    {data.video_info.tags && data.video_info.tags.length > 0 && (
                      <div className="md:col-span-2 mt-2">
                        <span className="font-medium">Etiketler:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {data.video_info.tags.map((tag: string, index: number) => (
                            <span key={index} className="bg-gray-100 text-gray-700 px-2 py-1 rounded-full text-xs">
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Transcript */}
              {data.transcript && (
                <div className="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="bg-gradient-to-r from-gray-500 to-gray-600 text-white text-sm font-semibold px-3 py-1.5 rounded-full shadow-sm">
                      📝 Transkript
                    </span>
                  </div>
                  
                  <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                    <div className="whitespace-pre-wrap text-gray-800 text-sm leading-relaxed font-mono">
                      {data.transcript}
                    </div>
                  </div>
                </div>
              )}


              {/* Metadata */}
              <div className="mt-6 pt-4 border-t border-gray-200 text-xs text-gray-500">
                <div className="flex gap-4">
                  {videoId && <span>🎬 Video ID: {videoId}</span>}
                  {data.agent_used && <span>🤖 {data.agent_used}</span>}
                  {data.processing_time && <span>⏱️ İşlem Süresi: {data.processing_time}s</span>}
                  {data.model_used && <span>🧠 Model: {data.model_used}</span>}
                </div>
              </div>
            </div>
          )}

          {!data && !loading && !error && (
            <div className="flex items-center justify-center py-8 text-gray-500">
              <div className="text-center">
                <Youtube className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                <p>Analiz sonuçları burada görünecek</p>
                <p className="text-sm mt-1">Önce geçerli bir YouTube URL'si girin</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}