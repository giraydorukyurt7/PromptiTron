import fitz
import re
import json

pdf_path = "lectures/tarih.pdf"
output_path = "kazanimlar_tarih.json"

# === Regex desenleri ===
grade_re = re.compile(r"^TARİH DERSİ \((\d{1,2})\. SINIF\)", re.IGNORECASE)
unit_re = re.compile(r"^(\d+)\.\s*ÜNİTE[:：]?\s*(.*)", re.IGNORECASE)
objective_re = re.compile(r"^(\d+\.\d+\.\d+)\.\s+(.*)")
subpoint_re = re.compile(r"([a-eç])\)\s")

# === PDF oku
print("📄 PDF okunuyor...")
doc = fitz.open(pdf_path)
lines = []
for page in doc:
    blocks = page.get_text("dict")["blocks"]
    for b in blocks:
        for l in b.get("lines", []):
            line_text = " ".join([span["text"] for span in l["spans"]]).strip()
            if line_text:
                lines.append(line_text)
print(f"✅ Toplam {len(lines)} satır alındı.\n")

# === Veri yapısı
data = {"yks": {"tarih": {}}}
current_grade = None
current_unit_code = None

i = 0
while i < len(lines):
    line = lines[i]

    # SINIF algıla
    match = grade_re.match(line)
    if match:
        current_grade = match.group(1)
        data["yks"]["tarih"].setdefault(current_grade, {"alt": {}})
        current_unit_code = None
        print(f"\n🎓 Sınıf: {current_grade}")
        i += 1
        continue

    # ÜNİTE algıla
    match = unit_re.match(line)
    if match:
        unit_number, unit_title = match.groups()
        current_unit_code = f"{current_grade}.{unit_number}"
        data["yks"]["tarih"][current_grade]["alt"].setdefault(current_unit_code, {
            "baslik": unit_title.strip(),
            "alt": {}
        })
        print(f"📘 Ünite: {current_unit_code} → {unit_title.strip()}")
        i += 1
        continue

    # KAZANIM algıla
    match = objective_re.match(line)
    if match and current_unit_code:
        kazanım_kodu, kazanım_baslik = match.groups()

        # Açıklamayı birleştir
        j = i + 1
        raw = []
        while j < len(lines):
            next_line = lines[j]

            if grade_re.match(next_line) or unit_re.match(next_line) or objective_re.match(next_line):
                break
            raw.append(next_line)
            j += 1

        full_text = " ".join(raw).strip()
        subparts = list(subpoint_re.finditer(full_text))
        aciklamalar = {}

        if subparts:
            for idx, smatch in enumerate(subparts):
                label = smatch.group(1)
                start = smatch.end()
                end = subparts[idx + 1].start() if idx + 1 < len(subparts) else len(full_text)
                aciklamalar[label] = full_text[start:end].strip()
        elif full_text:
            aciklamalar = {"a": full_text}

        data["yks"]["tarih"][current_grade]["alt"][current_unit_code]["alt"][kazanım_kodu] = {
            "baslik": kazanım_baslik.strip(),
            "aciklama": aciklamalar
        }
        print(f"✅ Kazanım: {kazanım_kodu} → {kazanım_baslik.strip()}")
        i = j
        continue

    i += 1

# === JSON'a yaz
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n📁 JSON dosyasına yazıldı: {output_path}")