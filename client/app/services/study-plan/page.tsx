"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useStudyPlan } from "@/lib/hooks/useApi";
import { Loader2, NotebookPen } from "lucide-react";

const EXAM_TYPES = [
  { value: "TYT", label: "TYT" },
  { value: "AYT", label: "AYT" },
  { value: "YKS", label: "YKS" },
  { value: "LGS", label: "LGS" },
];

const GRADE_LEVELS = [
  { value: "9", label: "9. Sınıf" },
  { value: "10", label: "10. Sınıf" },
  { value: "11", label: "11. Sınıf" },
  { value: "12", label: "12. Sınıf" },
  { value: "mezun", label: "Mezun" },
];

export default function StudyPlanPage() {
  const [studentProfile, setStudentProfile] = useState({
    name: "",
    grade: "",
    target_score: "",
    weak_subjects: [] as string[],
    strong_subjects: [] as string[],
    study_style: "",
    available_time: "",
  });
  const [targetExam, setTargetExam] = useState<"TYT" | "AYT" | "YKS" | "LGS">("TYT");
  const [durationWeeks, setDurationWeeks] = useState(12);
  const [dailyHours, setDailyHours] = useState(6);

  const { generateStudyPlan, loading, error, data } = useStudyPlan();

  const handleInputChange = (field: string, value: string) => {
    setStudentProfile(prev => ({ ...prev, [field]: value }));
  };

  const handleArrayInputChange = (field: "weak_subjects" | "strong_subjects", value: string) => {
    const subjects = value.split(",").map(s => s.trim()).filter(s => s);
    setStudentProfile(prev => ({ ...prev, [field]: subjects }));
  };

  const handleGenerate = async () => {
    if (!studentProfile.name || !studentProfile.grade) {
      alert("Lütfen en az isim ve sınıf bilgilerini giriniz");
      return;
    }

    await generateStudyPlan(studentProfile, {
      target_exam: targetExam,
      duration_weeks: durationWeeks,
      daily_hours: dailyHours,
    });
  };

  return (
    <div className="container-x py-8">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <NotebookPen className="w-8 h-8 text-purple-600" />
          <h1 className="text-3xl font-bold text-gray-900">Çalışma Planı Oluştur</h1>
        </div>
        <p className="text-gray-600">
          Kişiselleştirilmiş YKS hazırlık planınızı oluşturun
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Öğrenci Profili</h2>
          
          <div className="space-y-4">
            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                İsim
              </label>
              <input
                type="text"
                value={studentProfile.name}
                onChange={(e) => handleInputChange("name", e.target.value)}
                placeholder="Adınız ve soyadınız"
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Grade */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sınıf
              </label>
              <select
                value={studentProfile.grade}
                onChange={(e) => handleInputChange("grade", e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Sınıf seçiniz</option>
                {GRADE_LEVELS.map((grade) => (
                  <option key={grade.value} value={grade.value}>
                    {grade.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Target Score */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Hedef Puan (isteğe bağlı)
              </label>
              <input
                type="number"
                value={studentProfile.target_score}
                onChange={(e) => handleInputChange("target_score", e.target.value)}
                placeholder="Örn: 450"
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Weak Subjects */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Zayıf Olduğunuz Dersler (virgülle ayırın)
              </label>
              <input
                type="text"
                value={studentProfile.weak_subjects.join(", ")}
                onChange={(e) => handleArrayInputChange("weak_subjects", e.target.value)}
                placeholder="Örn: Matematik, Fizik, Kimya"
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Strong Subjects */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Güçlü Olduğunuz Dersler (virgülle ayırın)
              </label>
              <input
                type="text"
                value={studentProfile.strong_subjects.join(", ")}
                onChange={(e) => handleArrayInputChange("strong_subjects", e.target.value)}
                placeholder="Örn: Türkçe, Tarih, Coğrafya"
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Study Style */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Çalışma Tarzınız
              </label>
              <select
                value={studentProfile.study_style}
                onChange={(e) => handleInputChange("study_style", e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Seçiniz</option>
                <option value="visual">Görsel Öğrenme</option>
                <option value="auditory">İşitsel Öğrenme</option>
                <option value="kinesthetic">Kinestetik Öğrenme</option>
                <option value="mixed">Karma</option>
              </select>
            </div>

            <h3 className="text-md font-semibold mt-6 mb-4">Plan Parametreleri</h3>

            {/* Target Exam */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Hedef Sınav
              </label>
              <select
                value={targetExam}
                onChange={(e) => setTargetExam(e.target.value as "TYT" | "AYT" | "YKS" | "LGS")}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {EXAM_TYPES.map((exam) => (
                  <option key={exam.value} value={exam.value}>
                    {exam.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Duration */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Plan Süresi (Hafta)
              </label>
              <input
                type="number"
                min="1"
                max="52"
                value={durationWeeks}
                onChange={(e) => setDurationWeeks(parseInt(e.target.value) || 1)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Daily Hours */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Günlük Çalışma Saati
              </label>
              <input
                type="number"
                min="1"
                max="16"
                value={dailyHours}
                onChange={(e) => setDailyHours(parseInt(e.target.value) || 1)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <Button
              onClick={handleGenerate}
              disabled={loading || !studentProfile.name || !studentProfile.grade}
              className="w-full"
            >
              {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Çalışma Planı Oluştur
            </Button>
          </div>
        </div>

        {/* Results */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Oluşturulan Plan</h2>
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              {typeof error === 'string' ? error : JSON.stringify(error)}
            </div>
          )}

          {loading && (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
              <span className="ml-2 text-gray-600">Plan oluşturuluyor...</span>
            </div>
          )}

          {data && !loading && (
            <div className="prose prose-sm max-w-none">
              <div className="whitespace-pre-wrap text-gray-700">
                {typeof data.study_plan === 'string' ? data.study_plan : JSON.stringify(data, null, 2)}
              </div>
            </div>
          )}

          {!data && !loading && !error && (
            <div className="flex items-center justify-center py-8 text-gray-500">
              Çalışma planınız burada görünecek
            </div>
          )}
        </div>
      </div>
    </div>
  );
}