import fitz  # PyMuPDF
import re
import json
from collections import defaultdict

# PDF dosyasını aç
pdf_path = r"lectures\biyoloji.pdf"
output_path = r"kazanimlar_biyoloji.json"

# === PDF'ten metni oku (bold kontrolü için dict modunda) ===
doc = fitz.open(pdf_path)
lines = []
for page in doc:
    blocks = page.get_text("dict")["blocks"]
    for b in blocks:
        for l in b.get("lines", []):
            line_text = " ".join([span["text"] for span in l["spans"]])
            font_flags = [span["flags"] for span in l["spans"]]
            is_bold = any(flag & 2 for flag in font_flags)  # bold = 2
            lines.append((line_text.strip(), is_bold))

# === Regex desenleri ===
grade_section_re = re.compile(r"^(\d{1,2})\. SINIF ÜNİTE, KONU, KAZANIM VE AÇIKLAMALARI", re.IGNORECASE)
unit_re = re.compile(r"^(\d+\.\d+)\.\s+(.*)")
topic_re = re.compile(r"^(\d+\.\d+\.\d+)\.\s+(.*)")
objective_re = re.compile(r"^(\d+\.\d+\.\d+\.\d+)\.?\s+(.*)")
keyword_header_re = re.compile(r"^Anahtar\s*Kavramlar", re.IGNORECASE)
subpoint_re = re.compile(r"([a-eç])\.\s")

# === Ağaç yapısı ===
data = {"yks": {"biyoloji": {}}}
current_grade = None
current_unit = None
current_topic = None

i = 0
while i < len(lines):
    line, is_bold = lines[i]

    # SINIF başlığı
    match = grade_section_re.match(line)
    if match:
        current_grade = match.group(1)
        if current_grade not in data["yks"]["biyoloji"]:
            data["yks"]["biyoloji"][current_grade] = {"alt": {}}
        i += 1
        continue

    # Ünite (örnek: 9.1)
    match = unit_re.match(line)
    if match:
        unit_code, baslik = match.groups()
        inferred_grade = unit_code.split('.')[0]
        if inferred_grade != current_grade:
            current_grade = inferred_grade
            if current_grade not in data["yks"]["biyoloji"]:
                data["yks"]["biyoloji"][current_grade] = {"alt": {}}
        current_unit = unit_code
        data["yks"]["biyoloji"][current_grade]["alt"][current_unit] = {
            "baslik": baslik.strip(),
            "alt": {}
        }
        i += 1
        continue

    # Konu (örnek: 9.1.1)
    match = topic_re.match(line)
    if match:
        if current_grade is None or current_unit is None:
            i += 1
            continue
        current_topic, baslik = match.groups()
        data["yks"]["biyoloji"][current_grade]["alt"][current_unit]["alt"][current_topic] = {
            "baslik": baslik.strip(),
            "anahtar_kavramlar": "",
            "alt": {}
        }

        # Anahtar kavramlar varsa
        j = i + 1
        if j < len(lines) and keyword_header_re.match(lines[j][0]):
            j += 1
            keywords = []
            while j < len(lines):
                kw_line, _ = lines[j]
                if not kw_line or re.match(r"^\d", kw_line):
                    break
                keywords.append(kw_line)
                j += 1
            data["yks"]["biyoloji"][current_grade]["alt"][current_unit]["alt"][current_topic]["anahtar_kavramlar"] = " ".join(keywords).strip()
        i += 1
        continue

    # Kazanım (örnek: 9.1.1.1)
    match = objective_re.match(line)
    if match:
        if current_grade is None or current_unit is None or current_topic is None:
            i += 1
            continue
        kazanım_kodu, kazanım_baslik = match.groups()

        # devam eden satır varsa başlığa ekle
        j = i + 1
        while j < len(lines):
            next_line, next_bold = lines[j]
            if next_line.startswith(("a.", "b.", "c.", "ç.", "d.", "e.")) or not next_bold:
                break
            if not re.match(r"^\d", next_line):
                kazanım_baslik += " " + next_line
            j += 1

        # Açıklamaları al
        aciklama_raw = []
        while j < len(lines):
            acik_line, _ = lines[j]
            if re.match(r"^\d", acik_line):  # yeni başlık
                break
            aciklama_raw.append(acik_line)
            j += 1

        aciklama_str = " ".join(aciklama_raw).strip()
        subparts = list(subpoint_re.finditer(aciklama_str))

        aciklamalar = {}
        if subparts:
            for idx, match in enumerate(subparts):
                label = match.group(1)
                start = match.end()
                end = subparts[idx + 1].start() if idx + 1 < len(subparts) else len(aciklama_str)
                aciklamalar[label] = aciklama_str[start:end].strip()
        elif aciklama_str:
            aciklamalar = {"a": aciklama_str}
        else:
            aciklamalar = {}

        data["yks"]["biyoloji"][current_grade]["alt"][current_unit]["alt"][current_topic]["alt"][kazanım_kodu] = {
            "baslik": kazanım_baslik.strip(),
            "aciklama": aciklamalar
        }

        i = j
        continue

    i += 1

# === JSON olarak kaydet ===
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(output_path)
