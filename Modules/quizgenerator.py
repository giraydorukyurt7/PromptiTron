# modules/quizgenerator.py

import google.generativeai as genai
from modules.utils import get_timestamp
from pathlib import Path

genai.configure(api_key="GEMINI_API_KEYIN")

model = genai.GenerativeModel("gemini-pro")

def generate_quiz(text, save=True):
    prompt = f"""
Aşağıdaki ders içeriğini analiz ederek 5 tane orta ve zor seviyede çoktan seçmeli soru üret. Her soru için 4 seçenek ve doğru cevabı ver.

Metin:
{text[:7000]}
"""
    response = model.generate_content(prompt)
    result = response.text

    if save:
        path = Path("Outputs/reports") / f"quiz_{get_timestamp()}.txt"
        path.write_text(result, encoding="utf-8")

    return result