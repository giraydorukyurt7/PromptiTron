# modules/mindmap.py

import google.generativeai as genai
from modules.utils import get_timestamp
from pathlib import Path

genai.configure(api_key="GEMINI_API_KEYIN")  # 🔐

model = genai.GenerativeModel("gemini-pro")

def generate_mindmap(text, save=True):
    prompt = f"""
Aşağıdaki transkripti analiz ederek bir akıl haritası (mindmap) formatında ana konu başlıklarını ve alt kavramları hiyerarşik olarak listele.

Format:
- [Ana Başlık]
  - Alt Kavram 1
  - Alt Kavram 2
    - Alt Detay

Metin:
{text[:7000]}
"""
    response = model.generate_content(prompt)
    result = response.text

    if save:
        path = Path("Outputs/reports") / f"mindmap_{get_timestamp()}.txt"
        path.write_text(result, encoding="utf-8")

    return result