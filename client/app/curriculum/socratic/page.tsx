"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { useCurriculumSocratic } from "@/lib/hooks/useApi";
import { Loader2, Brain, ArrowLeft, Send, HelpCircle } from "lucide-react";
import Link from "next/link";

export default function SocraticAIPage() {
  const [selectedTopics, setSelectedTopics] = useState<any[]>([]);
  const [messages, setMessages] = useState<{role: 'user' | 'assistant', content: string}[]>([]);
  const [currentMessage, setCurrentMessage] = useState("");
  const [sessionStarted, setSessionStarted] = useState(false);
  const [learningGoal, setLearningGoal] = useState("");

  const { startSocraticDialogue, loading, error, data } = useCurriculumSocratic();

  useEffect(() => {
    const savedTopics = sessionStorage.getItem('selectedCurriculumTopics');
    if (savedTopics) {
      setSelectedTopics(JSON.parse(savedTopics));
    }
  }, []);

  useEffect(() => {
    if (data && data.response) {
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    }
  }, [data]);

  const handleStartSession = async () => {
    if (selectedTopics.length === 0) {
      alert("Seçilen konular bulunamadı. Lütfen YKS kazanımlar sayfasından konuları seçin.");
      return;
    }

    const initialPrompt = `Sokratik öğretim metoduyla öğrenmek istiyorum. Hedefim: ${learningGoal || 'Konuları derinlemesine anlamak'}. Seçtiğim konular: ${selectedTopics.map(t => t.title).join(", ")}. Lütfen sorular sorarak öğrenmeme yardım et.`;
    
    setMessages([{ role: 'user', content: initialPrompt }]);
    setSessionStarted(true);
    
    await startSocraticDialogue(initialPrompt, selectedTopics, {
      topic: 'Socratic Learning',
      context: { socratic_mode: true }
    });
  };

  const handleSendMessage = async () => {
    if (!currentMessage.trim() || !sessionStarted) return;

    const userMessage = { role: 'user' as const, content: currentMessage };
    setMessages(prev => [...prev, userMessage]);
    
    const conversationContext = messages.map(m => ({
      role: m.role,
      content: m.content
    }));

    await startSocraticDialogue(currentMessage, selectedTopics, {
      topic: 'Socratic Learning',
      context: { conversation: conversationContext, socratic_mode: true }
    });

    setCurrentMessage("");
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
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
          <Brain className="w-8 h-8 text-purple-600" />
          <h1 className="text-3xl font-bold text-gray-900">Sokratik AI</h1>
        </div>
        <p className="text-gray-600">
          Sokratik öğretim metoduyla konuları keşfedin - AI sorular sorar, siz cevap vererek öğrenirsiniz
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

      <div className="bg-white rounded-lg border border-gray-200 p-6">
        {!sessionStarted ? (
          <div className="space-y-6">
            <div className="text-center">
              <Brain className="w-16 h-16 text-purple-400 mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-4">Sokratik Öğrenme Seansı</h2>
              <p className="text-gray-600 mb-6">
                Sokratik metodla öğrenmeye hazır mısınız? AI sorular soracak, 
                sizden cevaplar isteyecek ve böylece konuları kendi kendinize keşfedeceksiniz.
              </p>
            </div>

            {/* Learning Goal Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Öğrenme Hedefiniz (İsteğe Bağlı)
              </label>
              <textarea
                value={learningGoal}
                onChange={(e) => setLearningGoal(e.target.value)}
                placeholder="Bu konularda neyi öğrenmek istiyorsunuz? Örn: Temel kavramları anlamak, problem çözme becerim geliştirmek..."
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                rows={3}
              />
            </div>

            {/* Socratic Method Info */}
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="flex items-start gap-3">
                <HelpCircle className="w-5 h-5 text-purple-600 mt-0.5" />
                <div>
                  <h3 className="font-medium text-purple-900 mb-2">Sokratik Yöntem Nedir?</h3>
                  <div className="text-sm text-purple-700 space-y-1">
                    <p>• AI size doğrudan cevap vermez, bunun yerine düşündürücü sorular sorar</p>
                    <p>• Kendi çıkarımlarınızı yapmanızı ve sonuçlara kendiniz ulaşmanızı sağlar</p>
                    <p>• Derinlemesine anlama ve kritik düşünme becerilerinizi geliştirir</p>
                    <p>• Bilgiyi ezberlemek yerine, kavramanızı hedefler</p>
                  </div>
                </div>
              </div>
            </div>

            <Button
              onClick={handleStartSession}
              disabled={loading || selectedTopics.length === 0}
              className="w-full bg-purple-600 hover:bg-purple-700"
            >
              {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Sokratik Seansı Başlat
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Messages */}
            <div className="h-96 overflow-y-auto border rounded-lg p-4 bg-gray-50 space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-purple-600 text-white'
                        : 'bg-white text-gray-800 border border-purple-200'
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{message.content}</div>
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-white text-gray-800 border border-purple-200 px-4 py-2 rounded-lg">
                    <Loader2 className="w-4 h-4 animate-spin" />
                  </div>
                </div>
              )}
            </div>

            {/* Message Input */}
            <div className="flex gap-2">
              <textarea
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Düşüncelerinizi ve cevaplarınızı yazın... (Enter ile gönder)"
                className="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                rows={2}
                disabled={loading}
              />
              <Button
                onClick={handleSendMessage}
                disabled={loading || !currentMessage.trim()}
                className="px-4 bg-purple-600 hover:bg-purple-700"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                <strong>Hata:</strong> {typeof error === 'string' ? error : JSON.stringify(error)}
              </div>
            )}

            {/* Socratic Tips */}
            <div className="bg-purple-50 p-3 rounded-lg">
              <div className="text-xs text-purple-700">
                <strong>İpucu:</strong> AI'nın sorularını dikkatlice düşünün. Emin olmadığınız konularda "Bilmiyorum" demeniz normal - 
                bu öğrenme sürecinin bir parçası!
              </div>
            </div>
          </div>
        )}

        {!sessionStarted && selectedTopics.length === 0 && (
          <div className="flex items-center justify-center py-8 text-gray-500">
            <div className="text-center">
              <p>Seçilen konular bulunamadı.</p>
              <Link href="/yks" className="text-blue-600 hover:text-blue-800 text-sm">
                YKS Kazanımlar sayfasından konuları seçin
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}