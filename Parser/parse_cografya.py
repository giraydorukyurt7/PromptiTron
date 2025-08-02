import fitz  # PyMuPDF
import re
import json

# === Dosya yolları ===
pdf_path = "lectures/cografya.pdf"
output_path = "kazanimlar_cografya.json"

# === Regex desenleri ===
class_header_re = re.compile(r"^(\d{1,2})\. SINIF COĞRAFYA DERSİ ÖĞRETİM PROGRAMI", re.IGNORECASE)
gain_re = re.compile(r"^(\d{1,2}\.\d+\.\d+)\.\s+(.*)")
subpoint_re = re.compile(r"([a-eç])\)\s")

# === Tema eşleştirmesi ===
tema_haritasi = {
    "1": "Doğal Sistemler",
    "2": "Beşerî Sistemler",
    "3": "Küresel Ortam: Bölgeler ve Ülkeler",
    "4": "Çevre ve Toplum"
}

# === PDF satırlarını oku
doc = fitz.open(pdf_path)
lines = []
for page in doc:
    blocks = page.get_text("dict")["blocks"]
    for b in blocks:
        for l in b.get("lines", []):
            line_text = " ".join([span["text"] for span in l["spans"]]).strip()
            is_red = any(abs(span["color"] - 16711680) < 100 for span in l["spans"])  # kırmızı RGB
            lines.append((line_text, is_red))

# === Veri yapısı
data = {"yks": {"cografya": {}}}
current_grade = None

# === Ana döngü
i = 0
while i < len(lines):
    line, is_red = lines[i]

    # Sınıf başlığı kontrolü
    match = class_header_re.match(line)
    if match:
        current_grade = match.group(1)
        data["yks"]["cografya"].setdefault(current_grade, {})
        i += 1
        continue

    # Kazanım kontrolü
    match = gain_re.match(line)
    if match:
        if current_grade is None:
            i += 1
            continue

        code, title = match.groups()
        kazanım_baslik = title.strip()
        kazanım_aciklamalar = {}

        # Tema kodunu al
        tema_kodu = code.split(".")[1]
        tema_adi = tema_haritasi.get(tema_kodu, "Bilinmeyen Tema")
        data["yks"]["cografya"][current_grade].setdefault(tema_adi, {})

        # Açıklamaları topla
        j = i + 1
        raw = []
        while j < len(lines):
            sub_line, _ = lines[j]
            if class_header_re.match(sub_line) or gain_re.match(sub_line):
                break
            raw.append(sub_line)
            j += 1

        full_text = " ".join(raw).strip()
        subparts = list(subpoint_re.finditer(full_text))

        if subparts:
            for idx, match in enumerate(subparts):
                label = match.group(1)
                start = match.end()
                end = subparts[idx + 1].start() if idx + 1 < len(subparts) else len(full_text)
                kazanım_aciklamalar[label] = full_text[start:end].strip()
        elif full_text:
            kazanım_aciklamalar = {"a": full_text}

        # Kazanımı yerleştir
        data["yks"]["cografya"][current_grade][tema_adi][code] = {
            "baslik": kazanım_baslik,
            "aciklama": kazanım_aciklamalar,
            "ozel_program": is_red
        }

        i = j
        continue

    i += 1

# === JSON'a yaz
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ Kazanımlar başarıyla kaydedildi: {output_path}")