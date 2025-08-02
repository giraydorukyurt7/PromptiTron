import fitz  # PyMuPDF
import re
import json

# === Dosya yolları ===
pdf_path = "lectures/felsefe.pdf"
output_path = "kazanimlar_felsefe.json"

# === Regex desenleri ===
class_header_re = re.compile(r"^.*?(\d{1,2})\. Sınıf Konu", re.IGNORECASE)
unit_header_re = re.compile(r"^ÜNİTE\s*(\d+):\s*(.*)", re.IGNORECASE)
gain_re = re.compile(r"^(\d{1,2}\.\d+\.\d+)\.?\s+(.*)")
subpoint_re = re.compile(r"([a-eç])\)\s")

# === PDF satırlarını oku
print("📄 PDF okunuyor...")
doc = fitz.open(pdf_path)
lines = []
for page_number, page in enumerate(doc):
    blocks = page.get_text("dict")["blocks"]
    for b in blocks:
        for l in b.get("lines", []):
            line_text = " ".join([span["text"] for span in l["spans"]]).strip()
            lines.append(line_text)
print(f"✅ Toplam {len(lines)} satır alındı PDF'ten.\n")

# === Veri yapısı
data = {"yks": {"felsefe": {}}}
current_grade = None
current_unit_title = None
total_kazanims = 0

# === Satırları tara
i = 0
while i < len(lines):
    line = lines[i].strip()

    # Sınıf başlığı yakala
    match = class_header_re.match(line)
    if match:
        current_grade = match.group(1)
        data["yks"]["felsefe"].setdefault(current_grade, {})
        current_unit_title = None
        print(f"\n🎓 Sınıf: {current_grade}. sınıf")
        i += 1
        continue

    # Ünite başlığı yakala
    match = unit_header_re.match(line)
    if match:
        if current_grade is not None:
            _, unit_title = match.groups()
            current_unit_title = unit_title.strip()
            data["yks"]["felsefe"][current_grade].setdefault(current_unit_title, {})
            print(f"📘 Ünite bulundu: {current_unit_title}")
        else:
            print(f"⚠️ Sınıf başlığı tanımlanmadan ünite bulundu: '{line}'")
        i += 1
        continue

    # Kazanım yakala
    match = gain_re.match(line)
    if match:
        if current_grade is None or current_unit_title is None:
            print(f"⚠️ Kazanım atlandı: sınıf veya ünite tanımlı değil → '{line}'")
            i += 1
            continue

        code, title = match.groups()
        kazanım_aciklamalar = {}

        # Açıklamaları topla
        j = i + 1
        raw = []
        while j < len(lines):
            next_line = lines[j].strip()
            if gain_re.match(next_line) or class_header_re.match(next_line) or unit_header_re.match(next_line):
                break
            raw.append(next_line)
            j += 1

        full_text = " ".join(raw).strip()
        subparts = list(subpoint_re.finditer(full_text))

        if subparts:
            for idx, smatch in enumerate(subparts):
                label = smatch.group(1)
                start = smatch.end()
                end = subparts[idx + 1].start() if idx + 1 < len(subparts) else len(full_text)
                kazanım_aciklamalar[label] = full_text[start:end].strip()
        elif full_text:
            kazanım_aciklamalar = {"a": full_text}

        data["yks"]["felsefe"][current_grade][current_unit_title][code] = {
            "baslik": title.strip(),
            "aciklama": kazanım_aciklamalar
        }

        print(f"✅ Kazanım eklendi: {code} → {title.strip()}")
        total_kazanims += 1
        i = j
        continue

    i += 1

# === JSON'a yaz
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n📦 Toplam {total_kazanims} kazanım JSON dosyasına kaydedildi.")
print(f"📁 Çıktı dosyası: {output_path}")