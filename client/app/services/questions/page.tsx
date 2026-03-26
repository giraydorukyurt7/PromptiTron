"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useQuestionGeneration } from "@/lib/hooks/useApi";
import { Loader2, CircleQuestionMark, CheckCircle } from "lucide-react";

const SUBJECTS = [
  { value: "matematik", label: "Matematik" },
  { value: "fizik", label: "Fizik" },
  { value: "kimya", label: "Kimya" },
  { value: "biyoloji", label: "Biyoloji" },
  { value: "turk_dili_ve_edebiyati", label: "Türk Dili ve Edebiyatı" },
  { value: "tarih", label: "Tarih" },
  { value: "cografya", label: "Coğrafya" },
  { value: "felsefe", label: "Felsefe" },
  { value: "din_kulturu", label: "Din Kültürü" },
  { value: "inkilap_ve_ataturkculuk", label: "İnkılap ve Atatürkçülük" },
];

const DIFFICULTIES = [
  { value: "easy", label: "Kolay" },
  { value: "medium", label: "Orta" },
  { value: "hard", label: "Zor" },
];

const QUESTION_TYPES = [
  { value: "multiple_choice", label: "Çoktan Seçmeli" },
  { value: "true_false", label: "Doğru-Yanlış" },
  { value: "fill_blank", label: "Boşluk Doldurma" },
  { value: "short_answer", label: "Kısa Cevap" },
  { value: "essay", label: "Kompozisyon" },
];

const EXAM_TYPES = [
  { value: "tyt", label: "TYT" },
  { value: "ayt", label: "AYT" },
  { value: "yks", label: "YKS" },
];

export default function QuestionsPage() {
  const [subject, setSubject] = useState("");
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState<"easy" | "medium" | "hard">("medium");
  const [questionType, setQuestionType] = useState<"multiple_choice" | "true_false" | "fill_blank" | "short_answer" | "essay">("multiple_choice");
  const [examType, setExamType] = useState<"tyt" | "ayt" | "yks">("tyt");
  const [count, setCount] = useState(5);

  const { generateQuestions, loading, error, data } = useQuestionGeneration();

  const handleGenerate = async () => {
    if (!subject || !topic) {
      alert("Lütfen ders ve konu seçiniz");
      return;
    }

    await generateQuestions(subject, topic, {
      difficulty,
      question_type: questionType,
      count,
      exam_type: examType,
    });
  };

  return (
    <div className="container-x py-8">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <CircleQuestionMark className="w-8 h-8 text-green-600" />
          <h1 className="text-3xl font-bold text-gray-900">Soru Oluştur</h1>
        </div>
        <p className="text-gray-600">
          YKS için özelleştirilmiş sorular oluşturun
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Soru Parametreleri</h2>
          
          <div className="space-y-4">
            {/* Subject */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ders
              </label>
              <select
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Ders seçiniz</option>
                {SUBJECTS.map((subj) => (
                  <option key={subj.value} value={subj.value}>
                    {subj.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Topic */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Konu
              </label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="Örn: Fonksiyonlar, Elektrik, Osmanlı Devleti..."
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

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
                {DIFFICULTIES.map((diff) => (
                  <option key={diff.value} value={diff.value}>
                    {diff.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Question Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Soru Tipi
              </label>
              <select
                value={questionType}
                onChange={(e) => setQuestionType(e.target.value as "multiple_choice" | "true_false" | "fill_blank" | "short_answer" | "essay")}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {QUESTION_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Exam Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sınav Tipi
              </label>
              <select
                value={examType}
                onChange={(e) => setExamType(e.target.value as "tyt" | "ayt" | "yks" )}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {EXAM_TYPES.map((exam) => (
                  <option key={exam.value} value={exam.value}>
                    {exam.label}
                  </option>
                ))}
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
              disabled={loading || !subject || !topic}
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
              {typeof error === 'string' ? error : JSON.stringify(error)}
            </div>
          )}

          {loading && (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
              <span className="ml-2 text-gray-600">Sorular oluşturuluyor...</span>
            </div>
          )}

          {data && !loading && (
            <div className="space-y-4">
              {/* Success Info */}
              {data.success && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4">
                  <strong>Başarılı!</strong> {data.count || 0} soru oluşturuldu.
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
                  })()}
                </div>
              )}

              {/* Metadata */}
              {data.subject && (
                <div className="mt-6 text-xs text-gray-500 space-y-1">
                  <div>Ders: {data.subject}</div>
                  <div>Konu: {data.topic}</div>
                  <div>Kullanılan Sistem: {data.agent_used || "AI Question Generator"}</div>
                </div>
              )}
            </div>
          )}

          {!data && !loading && !error && (
            <div className="flex items-center justify-center py-8 text-gray-500">
              Sorular burada görünecek
            </div>
          )}
        </div>
      </div>
    </div>
  );
}