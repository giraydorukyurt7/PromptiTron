"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { useCurriculumSocratic } from "@/lib/hooks/useApi";
import { Loader2, MessageCircle, ArrowLeft, Send } from "lucide-react";
import Link from "next/link";

export default function CurriculumAIChatPage() {
  const [selectedTopics, setSelectedTopics] = useState<any[]>([]);
  const [messages, setMessages] = useState<{role: 'user' | 'assistant', content: string}[]>([]);
  const [currentMessage, setCurrentMessage] = useState("");
  const [conversationStarted, setConversationStarted] = useState(false);

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

  const handleStartConversation = async () => {
    if (selectedTopics.length === 0) {
      alert("Seçilen konular bulunamadı. Lütfen YKS kazanımlar sayfasından konuları seçin.");
      return;
    }

    const initialMessage = `Merhaba! Seçtiğim müfredat konuları hakkında AI ile sohbet etmek istiyorum. Konularım: ${selectedTopics.map(t => t.title).join(", ")}`;
    
    setMessages([{ role: 'user', content: initialMessage }]);
    setConversationStarted(true);
    
    await startSocraticDialogue(initialMessage, selectedTopics, {
      topic: 'AI Chat',
      context: {}
    });
  };

  const handleSendMessage = async () => {
    if (!currentMessage.trim() || !conversationStarted) return;

    const userMessage = { role: 'user' as const, content: currentMessage };
    setMessages(prev => [...prev, userMessage]);
    
    const conversationContext = messages.map(m => ({
      role: m.role,
      content: m.content
    }));

    await startSocraticDialogue(currentMessage, selectedTopics, {
      topic: 'AI Chat',
      context: { conversation: conversationContext }
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
          <MessageCircle className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">AI ile Devam Et</h1>
        </div>
        <p className="text-gray-600">
          Seçtiğiniz müfredat konuları hakkında AI ile interaktif sohbet edin
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

      <div className="bg-white rounded-lg border border-gray-200 p-6">
        {!conversationStarted ? (
          <div className="text-center py-8">
            <MessageCircle className="w-16 h-16 text-blue-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-4">AI Sohbetini Başlat</h2>
            <p className="text-gray-600 mb-6">
              Seçtiğiniz konular hakkında AI ile etkileşimli bir sohbet başlatın. 
              Sorularınızı sorun, konuları derinlemesine inceleyin.
            </p>
            <Button
              onClick={handleStartConversation}
              disabled={loading || selectedTopics.length === 0}
              className="px-8 py-3"
            >
              {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Sohbeti Başlat
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
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-gray-800 border'
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{message.content}</div>
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-white text-gray-800 border px-4 py-2 rounded-lg">
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
                placeholder="Mesajınızı yazın... (Enter ile gönder)"
                className="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                rows={2}
                disabled={loading}
              />
              <Button
                onClick={handleSendMessage}
                disabled={loading || !currentMessage.trim()}
                className="px-4"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                <strong>Hata:</strong> {typeof error === 'string' ? error : JSON.stringify(error)}
              </div>
            )}
          </div>
        )}

        {!conversationStarted && selectedTopics.length === 0 && (
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