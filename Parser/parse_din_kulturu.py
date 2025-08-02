import fitz
import re
import json

pdf_path = "lectures/din_kulturu.pdf"
output_path = "kazanimlar_din_kulturu.json"

# === Regex desenleri ===
grade_re = re.compile(r"^(\d{1,2})\. SINIF", re.IGNORECASE)
unit_re = re.compile(r"^(\d+\.\d+)\.\s+(.*)", re.IGNORECASE)
objective_re = re.compile(r"^(\d+\.\d+\.\d+)\.\s+(.*)")
subpoint_re = re.compile(r"([a-eç])\)", re.IGNORECASE)
keyword_re = re.compile(r"Anahtar Kavramlar", re.IGNORECASE)

# === PDF'ten satır satır oku ===
print("📄 PDF okunuyor...")
doc = fitz.open(pdf_path)
lines = []
for page in doc:
    blocks = page.get_text("dict")["blocks"]
    for b in blocks:
        for l in b.get("lines", []):
            text = " ".join([span["text"] for span in l["spans"]]).strip()
            if text:
                lines.append(text)
print(f"✅ Toplam {len(lines)} satır okundu.\n")

# === Veri yapısı başlat
data = {"yks": {"din_kulturu": {}}}
current_grade = None
current_unit = None
current_unit_title = None

i = 0
while i < len(lines):
    line = lines[i]

    # Sınıf
    match = grade_re.match(line)
    if match:
        current_grade = match.group(1)
        data["yks"]["din_kulturu"].setdefault(current_grade, {"alt": {}})
        print(f"🎓 Sınıf: {current_grade}")
        i += 1
        continue

    # Ünite başlığı
    match = unit_re.match(line)
    if match:
        current_unit, current_unit_title = match.groups()
        data["yks"]["din_kulturu"][current_grade]["alt"].setdefault(current_unit, {
            "baslik": current_unit_title.strip(),
            "anahtar_kavramlar": "",
            "alt": {}
        })
        print(f"📘 Ünite: {current_unit} → {current_unit_title.strip()}")
        i += 1
        continue

    # Anahtar kavramlar
    if keyword_re.match(line) and current_unit:
        kavramlar = []
        i += 1
        while i < len(lines) and not lines[i].startswith("●") and not re.match(r"^\d", lines[i]):
            kavramlar.append(lines[i].strip("●•").strip())
            i += 1
        joined = " ".join(kavramlar).strip()
        data["yks"]["din_kulturu"][current_grade]["alt"][current_unit]["anahtar_kavramlar"] = joined
        print(f"🔑 Anahtar kavramlar: {joined}")
        continue

    # Kazanım
    match = objective_re.match(line)
    if match and current_unit:
        kazanım_kodu, kazanım_baslik = match.groups()
        j = i + 1
        aciklama_lines = []

        # Açıklamaları topla
        while j < len(lines):
            next_line = lines[j]
            if objective_re.match(next_line) or unit_re.match(next_line) or grade_re.match(next_line) or keyword_re.match(next_line):
                break
            aciklama_lines.append(next_line.strip("•●").strip())
            j += 1

        full_text = " ".join(aciklama_lines).strip()
        subparts = list(re.finditer(r"([a-eç])\)\s", full_text))
        aciklama_dict = {}

        if subparts:
            for idx, sm in enumerate(subparts):
                label = sm.group(1)
                start = sm.end()
                end = subparts[idx + 1].start() if idx + 1 < len(subparts) else len(full_text)
                aciklama_dict[label] = full_text[start:end].strip()
        elif full_text:
            aciklama_dict = {"a": full_text}

        data["yks"]["din_kulturu"][current_grade]["alt"][current_unit]["alt"][kazanım_kodu] = {
            "baslik": kazanım_baslik.strip(),
            "aciklama": aciklama_dict
        }
        print(f"✅ Kazanım: {kazanım_kodu} → {kazanım_baslik.strip()}")
        i = j
        continue

    i += 1

# === JSON çıktısı
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n📁 JSON dosyasına yazıldı: {output_path}")