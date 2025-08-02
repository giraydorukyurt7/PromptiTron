import fitz
import re
import json

pdf_path = "lectures/kimya.pdf"
output_path = "kazanimlar_kimya.json"

# === Regex desenleri ===
grade_re = re.compile(r"^(\d{1,2})\. SINIF.*KAZANIM", re.IGNORECASE)
unit_re = re.compile(r"^(\d+\.\d+)\.\s+(.*)")
topic_re = re.compile(r"^(\d+\.\d+\.\d+)\.\s+(.*)")
objective_re = re.compile(r"^(\d+\.\d+\.\d+\.\d+)\.?\s+(.*)")
keyword_re = re.compile(r"^Anahtar\s*kavramlar[:：]?\s*(.*)", re.IGNORECASE)
subpoint_re = re.compile(r"([a-eç])\.\s")

# === PDF'ten satır oku
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
print(f"✅ {len(lines)} satır alındı.\n")

# === Veri yapısı
data = {"yks": {"kimya": {}}}
current_grade = None
current_unit = None
current_topic = None

i = 0
while i < len(lines):
    line = lines[i]

    # SINIF algıla
    match = grade_re.match(line)
    if match:
        current_grade = match.group(1)
        data["yks"]["kimya"].setdefault(current_grade, {"alt": {}})
        current_unit = None
        current_topic = None
        print(f"\n🎓 Sınıf: {current_grade}")
        i += 1
        continue

    # ÜNİTE algıla
    match = unit_re.match(line)
    if match:
        current_unit, unit_title = match.groups()
        if current_grade is not None:
            data["yks"]["kimya"][current_grade]["alt"].setdefault(current_unit, {
                "baslik": unit_title.strip(),
                "anahtar_kavramlar": "",
                "alt": {}
            })
            current_topic = None
            print(f"📘 Ünite: {current_unit} → {unit_title.strip()}")

            # Anahtar kavramlar kontrolü
            j = i + 1
            while j < len(lines):
                kw_line = lines[j]
                kw_match = keyword_re.match(kw_line)
                if kw_match:
                    keywords = kw_match.group(1).strip()
                    k = j + 1
                    while k < len(lines) and not re.match(r"^\d", lines[k]):
                        keywords += " " + lines[k].strip()
                        k += 1
                    data["yks"]["kimya"][current_grade]["alt"][current_unit]["anahtar_kavramlar"] = keywords
                    print(f"🔑 Anahtar kavramlar: {keywords}")
                    break
                if unit_re.match(kw_line) or topic_re.match(kw_line) or objective_re.match(kw_line):
                    break
                j += 1
        i += 1
        continue

    # KONU algıla
    match = topic_re.match(line)
    if match and current_unit:
        current_topic, topic_title = match.groups()
        data["yks"]["kimya"][current_grade]["alt"][current_unit]["alt"].setdefault(current_topic, {
            "baslik": topic_title.strip(),
            "alt": {}
        })
        print(f"📗 Konu: {current_topic} → {topic_title.strip()}")
        i += 1
        continue

    # KAZANIM algıla
    match = objective_re.match(line)
    if match and current_topic:
        kazanım_kodu, kazanım_baslik = match.groups()

        # Açıklamayı birleştir
        j = i + 1
        raw = []
        while j < len(lines):
            next_line = lines[j]

            grade_match = grade_re.match(next_line)
            if grade_match:
                current_grade = grade_match.group(1)
                data["yks"]["kimya"].setdefault(current_grade, {"alt": {}})
                current_unit = None
                current_topic = None
                print(f"\n🎓 (Geç açıklamada algılandı) Yeni sınıf: {current_grade}")
                break

            if unit_re.match(next_line) or topic_re.match(next_line) or objective_re.match(next_line):
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

        if current_grade is None or current_unit is None or current_topic is None:
            print(f"⚠️ Kazanım atlandı (eksik bağlam): {kazanım_kodu} → {kazanım_baslik.strip()}")
            i = j
            continue

        data["yks"]["kimya"][current_grade]["alt"][current_unit]["alt"][current_topic]["alt"][kazanım_kodu] = {
            "baslik": kazanım_baslik.strip(),
            "aciklama": aciklamalar
        }
        print(f"✅ Kazanım: {kazanım_kodu} → {kazanım_baslik.strip()}")
        i = j
        continue

    i += 1

# === JSON çıktısı
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n📁 JSON dosyasına yazıldı: {output_path}")
