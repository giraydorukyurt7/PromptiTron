# agents/langgraph_graph.py

from agents.crewai_agents import *
from modules.transcriber import transcribe_audio
from modules.downloader import download_youtube_audio

# Basit görev akışı senaryosu
def run_learning_pipeline(url: str):
    print("🎥 1. Ses indiriliyor...")
    audio_path = download_youtube_audio(url)

    print("🧠 2. Transkript alınıyor...")
    transcript = transcribe_audio(audio_path, save=False)

    print("📝 3. Özet oluşturuluyor...")
    summary_agent = SummaryAgent("summary")
    summary = summary_agent.run({"text": transcript})

    print("📆 4. Çalışma planı oluşturuluyor...")
    plan_agent = StudyPlanAgent("plan")
    plan = plan_agent.run({"text": transcript})

    print("🎯 5. Quiz hazırlanıyor...")
    quiz_agent = QuizAgent("quiz")
    quiz = quiz_agent.run({"text": transcript})

    return {
        "transcript": transcript,
        "summary": summary,
        "plan": plan,
        "quiz": quiz
    }