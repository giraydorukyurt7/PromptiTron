"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { useCurriculumQuestions } from "@/lib/hooks/useApi";
import { Loader2, CircleQuestionMark, ArrowLeft, CheckCircle } from "lucide-react";
import Link from "next/link";


export default function CurriculumQuestionsPage() {
  const [selectedTopics, setSelectedTopics] = useState<any[]>([]);
  const [difficulty, setDifficulty] = useState<"easy" | "medium" | "hard">("medium");
  const [questionType, setQuestionType] = useState<"multiple_choice" | "true_false" | "fill_blank" | "short_answer" | "essay">("multiple_choice");
  const [count, setCount] = useState(5);
  const [examType, setExamType] = useState<"tyt" | "ayt" | "yks">("tyt");

  const { generateQuestions, loading, error, data } = useCurriculumQuestions();

  useEffect(() => {
    // Session storage'dan seçilen konuları al
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

    await generateQuestions(selectedTopics, {
      difficulty,
      question_type: questionType,
      count,
      exam_type: examType,
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
          <CircleQuestionMark className="w-8 h-8 text-green-600" />
          <h1 className="text-3xl font-bold text-gray-900">Müfredat Tabanlı Soru Oluştur</h1>
        </div>
        <p className="text-gray-600">
          Seçtiğiniz müfredat konularına dayalı sorular oluşturun
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
          <h2 className="text-lg font-semibold mb-4">Soru Parametreleri</h2>
          
          <div className="space-y-4">
            {/* Difficulty */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Zorluk Seviyesi
              </label>
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value as "easy" | "medium" | "hard")}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="easy">Kolay</option>
                <option value="medium">Orta</option>
                <option value="hard">Zor</option>
              </select>
            </div>

            {/* Question Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Soru Tipi
              </label>
              <select
                value={questionType}
                onChange={(e) => setQuestionType(e.target.value as any)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="multiple_choice">Çoktan Seçmeli</option>
                <option value="true_false">Doğru-Yanlış</option>
                <option value="fill_blank">Boşluk Doldurma</option>
                <option value="short_answer">Kısa Cevap</option>
                <option value="essay">Kompozisyon</option>
              </select>
            </div>

            {/* Exam Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sınav Tipi
              </label>
              <select
                value={examType}
                onChange={(e) => setExamType(e.target.value as any)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="tyt">TYT</option>
                <option value="ayt">AYT</option>
                <option value="yks">YKS</option>
              </select>
            </div>

            {/* Count */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Soru Sayısı
              </label>
              <input
                type="number"
                min="1"
                max="20"
                value={count}
                onChange={(e) => setCount(parseInt(e.target.value) || 1)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <Button
              onClick={handleGenerate}
              disabled={loading || selectedTopics.length === 0}
              className="w-full"
            >
              {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Sorular Oluştur
            </Button>
          </div>
        </div>

        {/* Results */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Oluşturulan Sorular</h2>
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              <strong>Hata:</strong> {typeof error === 'string' ? error : JSON.stringify(error)}
            </div>
          )}

          {loading && (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
              <span className="ml-2 text-gray-600">Müfredat tabanlı sorular oluşturuluyor...</span>
            </div>
          )}

          {data && !loading && (
            <div className="space-y-6">
              {data.success && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                  <strong>✅ Başarılı!</strong> {data.count || selectedTopics.length} konuya dayalı {data.count || count} soru oluşturuldu.
                </div>
              )}

              {/* Questions Display */}
              {data.questions && (
                <div className="space-y-6">
                  {(() => {
                    // Parse questions if it's a string
                    let questions = data.questions;
                    if (typeof questions === 'string') {
                      try {
                        // First try direct JSON parse
                        questions = JSON.parse(questions);
                      } catch (e) {
                        try {
                          // Try to extract JSON from the response
                          const jsonMatch = questions.match(/\[[\s\S]*\]|\{[\s\S]*\}/);
                          if (jsonMatch) {
                            questions = JSON.parse(jsonMatch[0]);
                          } else {
                            // Try to parse each line as separate JSON
                            const lines = questions.split('\n').filter(line => line.trim());
                            const parsedQuestions = [];
                            
                            for (const line of lines) {
                              try {
                                const parsed = JSON.parse(line);
                                parsedQuestions.push(parsed);
                              } catch (lineError) {
                                // Skip unparseable lines
                              }
                            }
                            
                            if (parsedQuestions.length > 0) {
                              questions = parsedQuestions;
                            } else {
                              // If no JSON found, create a single question object
                              questions = [{ question_text: questions }];
                            }
                          }
                        } catch (e2) {
                          // If parsing fails, treat as single question
                          questions = [{ question_text: questions }];
                        }
                      }
                    }

                    // Ensure questions is an array
                    if (!Array.isArray(questions)) {
                      questions = [questions];
                    }

                    // Store all answers to show at the end
                    const allAnswers: { questionNumber: number; answer: string; explanation?: string }[] = [];

                    return (
                      <>
                        {/* Questions */}
                        {questions.map((question: any, index: number) => {
                          const questionNumber = index + 1;
                          
                          // Extract question data
                          const questionText = question.question_text || question.soru_metni || question.soru || question.question || question;
                          let options = question.options || question.secenekler || question.şıklar || question.siklar || [];
                          const correctAnswer = question.correct_answer || question.dogru_cevap || question.cevap || "";
                          const explanation = question.explanation || question.aciklama || question.açıklama || "";

                          // Handle options if it's an object (like {A: "...", B: "..."})
                          if (typeof options === 'object' && !Array.isArray(options)) {
                            options = Object.entries(options).map(([letter, text]) => ({
                              option_letter: letter,
                              option_text: text
                            }));
                          }

                          // Store answer for later
                          if (correctAnswer) {
                            allAnswers.push({
                              questionNumber,
                              answer: correctAnswer,
                              explanation
                            });
                          }

                          return (
                            <div key={index} className="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                              {/* Question Number Badge */}
                              <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                  <span className="bg-gradient-to-r from-blue-500 to-blue-600 text-white text-sm font-semibold px-3 py-1.5 rounded-full shadow-sm">
                                    Soru {questionNumber}
                                  </span>
                                  <span className="bg-gray-100 text-gray-600 text-xs font-medium px-2.5 py-1 rounded-md">
                                    {questionType === "multiple_choice" && "Çoktan Seçmeli"}
                                    {questionType === "true_false" && "Doğru/Yanlış"}
                                    {questionType === "fill_blank" && "Boşluk Doldurma"}
                                    {questionType === "short_answer" && "Kısa Cevap"}
                                    {questionType === "essay" && "Kompozisyon"}
                                  </span>
                                </div>
                                <span className="text-xs text-gray-400 font-medium">
                                  {difficulty === "easy" && "Kolay"}
                                  {difficulty === "medium" && "Orta"}
                                  {difficulty === "hard" && "Zor"}
                                </span>
                              </div>

                              {/* Question Text */}
                              <div className="mb-5">
                                <p className="text-gray-800 text-base leading-relaxed font-medium">
                                  {typeof questionText === 'string' ? questionText : JSON.stringify(questionText)}
                                </p>
                              </div>

                              {/* Options for Multiple Choice */}
                              {options.length > 0 && (
                                <div className="space-y-2 mb-4">
                                  {options.map((option: any, optIndex: number) => {
                                    let optionLetter;
                                    let optionText;
                                    
                                    if (typeof option === 'string') {
                                      optionLetter = String.fromCharCode(65 + optIndex);
                                      optionText = option;
                                    } else if (option.option_letter) {
                                      optionLetter = option.option_letter;
                                      optionText = option.option_text || option.text || "";
                                    } else {
                                      optionLetter = String.fromCharCode(65 + optIndex);
                                      optionText = option.option_text || option.text || option.secenek || JSON.stringify(option);
                                    }

                                    return (
                                      <div key={optIndex} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                                        <span className="font-medium text-gray-700 min-w-[28px]">
                                          {optionLetter})
                                        </span>
                                        <span className="text-gray-700 text-sm leading-relaxed">
                                          {optionText}
                                        </span>
                                      </div>
                                    );
                                  })}
                                </div>
                              )}

                              {/* Question Type Specific UI */}
                              {questionType === "true_false" && (
                                <div className="space-y-2 mb-4">
                                  <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                                    <span className="font-medium text-gray-700">A)</span>
                                    <span className="text-gray-700 text-sm">Doğru</span>
                                  </div>
                                  <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                                    <span className="font-medium text-gray-700">B)</span>
                                    <span className="text-gray-700 text-sm">Yanlış</span>
                                  </div>
                                </div>
                              )}

                              {questionType === "fill_blank" && (
                                <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                                  <p className="text-sm text-yellow-800">
                                    Boşlukları uygun kelimelerle doldurunuz.
                                  </p>
                                </div>
                              )}

                              {(questionType === "short_answer" || questionType === "essay") && (
                                <div className="mb-4">
                                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 min-h-[100px] bg-gray-50">
                                    <p className="text-sm text-gray-500 italic">
                                      {questionType === "short_answer" ? "Kısa cevap alanı" : "Kompozisyon yazma alanı"}
                                    </p>
                                  </div>
                                </div>
                              )}
                            </div>
                          );
                        })}

                        {/* Answer Key Section */}
                        {allAnswers.length > 0 && (
                          <div className="mt-8 bg-blue-50 border-2 border-blue-200 rounded-lg p-6">
                            <h3 className="text-lg font-semibold text-blue-900 mb-4 flex items-center gap-2">
                              <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm">
                                ✓
                              </span>
                              Cevap Anahtarı
                            </h3>
                            <div className="space-y-3">
                              {allAnswers.map((answer, index) => (
                                <div key={index} className="bg-white rounded-lg p-4 border border-blue-100">
                                  <div className="flex items-start gap-3">
                                    <span className="font-medium text-blue-800 min-w-[80px]">
                                      Soru {answer.questionNumber}:
                                    </span>
                                    <div className="flex-1">
                                      <span className="font-semibold text-gray-800">
                                        {answer.answer}
                                      </span>
                                      {answer.explanation && (
                                        <p className="text-sm text-gray-600 mt-2">
                                          <strong>Açıklama:</strong> {answer.explanation}
                                        </p>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </>
                    );
                  })()
                  }
                </div>
              )}

              {data.agent_used && (
                <div className="text-xs text-gray-500 text-center py-2 border-t">
                  Kullanılan Sistem: {data.agent_used}
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
              Sorular burada görünecek
            </div>
          )}
        </div>
      </div>
    </div>
  );
}