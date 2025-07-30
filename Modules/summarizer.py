# Modules/summarizer.py

import google.generativeai as genai
from pathlib import Path
from Modules.utils import get_timestamp

# 🔐 API anahtarını buraya yaz (veya .env ile al)
genai.configure(api_key="GEMINI_API_KEYIN")

model = genai.GenerativeModel("gemini-pro")

def summarize_text(text, save=True):
    """
    Transkripti özetler ve soru üretir.

    Args:
        text (str): Transkript metni
        save (bool): Özet ve sorular dosyaya yazılsın mı?

    Returns:
        str: Özet ve sorular
    """
    prompt = f"""
Aşağıda bir ders transkripti yer alıyor. Bu metni özetle ve içeriğe dayalı 3 tane çoktan seçmeli soru üret. Her soru için doğru cevabı belirt.

TRANSKRİPT:
{text[:7000]}
"""
    print("📚 Gemini ile özetleme başlıyor...")
    response = model.generate_content(prompt)
    result = response.text

    if save:
        out_dir = Path("Outputs/reports")
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"summary_{get_timestamp()}.txt"
        path.write_text(result, encoding="utf-8")
        print(f"✅ Özet & sorular kaydedildi: {path}")

    return result