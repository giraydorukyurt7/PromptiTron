# modules/studyplanner.py

import google.generativeai as genai
from modules.utils import get_timestamp
from pathlib import Path

genai.configure(api_key="GEMINI_API_KEYIN")

model = genai.GenerativeModel("gemini-pro")

def create_study_plan(text, save=True):
    prompt = f"""
Aşağıdaki eğitim metnine göre 3 günlük sade bir çalışma planı oluştur. Her gün için özet, yapılacaklar ve dikkat edilmesi gereken konuları belirt.

Metin:
{text[:7000]}
"""
    response = model.generate_content(prompt)
    result = response.text

    if save:
        path = Path("Outputs/reports") / f"studyplan_{get_timestamp()}.txt"
        path.write_text(result, encoding="utf-8")

    return result