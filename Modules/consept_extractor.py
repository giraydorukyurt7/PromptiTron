# modules/concept_extractor.py

import google.generativeai as genai
from modules.utils import get_timestamp
from pathlib import Path

genai.configure(api_key="GEMINI_API_KEYIN")

model = genai.GenerativeModel("gemini-pro")

def extract_concepts(text, save=True):
    prompt = f"""
Aşağıdaki eğitim metnini analiz ederek içinde geçen önemli teknik terimleri, tanımları ve kavramları listele.

Format:
- Kavram: Açıklama
- Kavram: Açıklama

Metin:
{text[:7000]}
"""
    response = model.generate_content(prompt)
    result = response.text

    if save:
        path = Path("Outputs/reports") / f"concepts_{get_timestamp()}.txt"
        path.write_text(result, encoding="utf-8")

    return result