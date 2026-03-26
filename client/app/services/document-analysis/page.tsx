"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { useDocumentAnalysis } from "@/lib/hooks/useApi";
import { Loader2, Upload, FileText, CheckCircle, AlertCircle } from "lucide-react";

const ANALYSIS_TYPES = [
  { value: "general", label: "Genel Analiz" },
  { value: "educational", label: "Eğitimsel Analiz" },
  { value: "summary", label: "Özet Çıkarma" },
  { value: "key_points", label: "Ana Noktalar" },
  { value: "questions", label: "Soru Üretme" },
  { value: "structure", label: "Yapı Analizi" },
];

const SUPPORTED_FORMATS = [
  "PDF (.pdf)",
  "Word (.doc, .docx)", 
  "Text (.txt)",
  "Markdown (.md)",
  "RTF (.rtf)"
];

export default function DocumentAnalysisPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [description, setDescription] = useState("");
  const [analysisType, setAnalysisType] = useState("general");
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { uploadDocument, loading, error, data } = useDocumentAnalysis();

  const handleFileSelect = (file: File) => {
    // Check file size (max 100MB)
    if (file.size > 100 * 1024 * 1024) {
      alert("Dosya boyutu 100MB'dan büyük olamaz");
      return;
    }

    // Check file type
    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain',
      'text/markdown',
      'application/rtf'
    ];

    if (!allowedTypes.includes(file.type)) {
      alert("Desteklenmeyen dosya formatı. Lütfen PDF, Word, Text veya Markdown dosyası seçin.");
      return;
    }

    setSelectedFile(file);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      alert("Lütfen analiz edilecek dosyayı seçin");
      return;
    }

    await uploadDocument(selectedFile, description, analysisType);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="container-x py-8">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <FileText className="w-8 h-8 text-green-600" />
          <h1 className="text-3xl font-bold text-gray-900">Döküman Analizi</h1>
        </div>
        <p className="text-gray-600">
          PDF, Word, Text dosyalarını yükleyin ve kapsamlı analiz edin
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Döküman Yükleme</h2>
          
          <div className="space-y-4">
            {/* File Upload Area */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Dosya Seçin
              </label>
              
              <div
                className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                  dragActive
                    ? "border-blue-400 bg-blue-50"
                    : "border-gray-300 hover:border-gray-400"
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                {selectedFile ? (
                  <div className="space-y-2">
                    <CheckCircle className="w-8 h-8 text-green-600 mx-auto" />
                    <div className="text-sm font-medium text-gray-900">
                      {selectedFile.name}
                    </div>
                    <div className="text-xs text-gray-500">
                      {formatFileSize(selectedFile.size)}
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setSelectedFile(null);
                        if (fileInputRef.current) {
                          fileInputRef.current.value = "";
                        }
                      }}
                    >
                      Farklı Dosya Seç
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <Upload className="w-8 h-8 text-gray-400 mx-auto" />
                    <div className="text-sm text-gray-600">
                      Dosyayı buraya sürükleyip bırakın veya
                    </div>
                    <Button
                      variant="outline"
                      onClick={() => fileInputRef.current?.click()}
                    >
                      Dosya Seç
                    </Button>
                  </div>
                )}
              </div>

              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept=".pdf,.doc,.docx,.txt,.md,.rtf"
                onChange={handleFileInput}
              />

              {/* Supported formats info */}
              <div className="mt-2 text-xs text-gray-500">
                <strong>Desteklenen formatlar:</strong> {SUPPORTED_FORMATS.join(", ")}
                <br />
                <strong>Maksimum dosya boyutu:</strong> 100MB
              </div>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Açıklama (Opsiyonel)
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Dökümanla ilgili kısa açıklama..."
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
              />
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

            <Button
              onClick={handleAnalyze}
              disabled={loading || !selectedFile}
              className="w-full"
            >
              {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Dökümanı Analiz Et
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
              <Loader2 className="w-8 h-8 animate-spin text-green-600" />
              <span className="ml-2 text-gray-600">Döküman analiz ediliyor...</span>
            </div>
          )}

          {data && !loading && (
            <div className="space-y-6">
              {data.success && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4">
                  <strong>✅ Başarılı!</strong> Döküman analizi tamamlandı.
                </div>
              )}

              {/* Analysis Results */}
              {data.analysis && (
                <div className="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="bg-gradient-to-r from-green-500 to-green-600 text-white text-sm font-semibold px-3 py-1.5 rounded-full shadow-sm">
                      📄 Döküman Analizi
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

              {/* Document Info */}
              {data.document_info && (
                <div className="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="bg-gradient-to-r from-blue-500 to-blue-600 text-white text-sm font-semibold px-3 py-1.5 rounded-full shadow-sm">
                      ℹ️ Döküman Bilgileri
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    {data.document_info.pages && (
                      <div>
                        <span className="font-medium">Sayfa Sayısı:</span> {data.document_info.pages}
                      </div>
                    )}
                    {data.document_info.word_count && (
                      <div>
                        <span className="font-medium">Kelime Sayısı:</span> {data.document_info.word_count}
                      </div>
                    )}
                    {data.document_info.file_size && (
                      <div>
                        <span className="font-medium">Dosya Boyutu:</span> {data.document_info.file_size}
                      </div>
                    )}
                    {data.document_info.format && (
                      <div>
                        <span className="font-medium">Format:</span> {data.document_info.format}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Metadata */}
              <div className="mt-6 pt-4 border-t border-gray-200 text-xs text-gray-500">
                <div className="flex gap-4">
                  {selectedFile && <span>📁 {selectedFile.name}</span>}
                  <span>🔍 {ANALYSIS_TYPES.find(t => t.value === analysisType)?.label}</span>
                  {data.agent_used && <span>🤖 {data.agent_used}</span>}
                </div>
              </div>
            </div>
          )}

          {!data && !loading && !error && (
            <div className="flex items-center justify-center py-8 text-gray-500">
              <div className="text-center">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                <p>Analiz sonuçları burada görünecek</p>
                <p className="text-sm mt-1">Önce bir dosya seçin</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}