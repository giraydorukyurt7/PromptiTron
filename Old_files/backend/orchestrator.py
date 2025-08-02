from modules.transcriber import transcribe_audio
from modules.downloader import download_youtube_audio
from modules.summarizer import summarize_text
from modules.worldcloud_module import generate_wordcloud
from modules.studyplanner import create_study_plan
from modules.quizgenerator import generate_quiz
from modules.mindmap import generate_mindmap
from modules.concept_extractor import extract_concepts
from modules.pdfgenerator import generate_pdf_report
from agents.rag_agent import build_vector_store, search_similar
from agents.langgraph_graph import run_learning_pipeline

def run_agent_task(task_name, input_data):
    """
    Görev adına göre uygun modülü çalıştırır.
    """
    if task_name == "download":
        return download_youtube_audio(input_data["url"])

    elif task_name == "transcribe":
        return transcribe_audio(input_data["audio_path"])

    elif task_name == "summarize":
        return summarize_text(input_data["text"])

    elif task_name == "worldcloud":
        return generate_wordcloud(input_data["text"])

    elif task_name == "studyplan":
        return create_study_plan(input_data["text"])

    elif task_name == "mindmap":
        return generate_mindmap(input_data["text"])

    elif task_name == "quiz":
        return generate_quiz(input_data["text"])

    elif task_name == "concepts":
        return extract_concepts(input_data["text"])

    elif task_name == "export_pdf":
        return generate_pdf_report(input_data["sections"])

    elif task_name == "build_vector_store":
        return build_vector_store(input_data["text"]) or "✅ Vektör deposu oluşturuldu."

    elif task_name == "search_similar":
        return search_similar(input_data["query"], input_data.get("top_k", 5))

    elif task_name == "full_pipeline":
        return run_learning_pipeline(input_data["url"])

    else:
        return f"❌ Desteklenmeyen görev: {task_name}"