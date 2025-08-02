import fitz
import re
import json

pdf_path = "lectures/matematik.pdf"
output_path = "kazanimlar_matematik.json"

# === Regex desenleri ===
grade_re = re.compile(r"^(\d{1,2})\.\s*SINIF", re.IGNORECASE)
unit_re = re.compile(r"^(\d+\.\d+)\.\s+(.*)")
topic_re = re.compile(r"^(\d+\.\d+\.\d+)\.\s+(.*)")
objective_re = re.compile(r"^(\d+\.\d+\.\d+\.\d+)\.?\s+(.*)")
term_re = re.compile(r"^Terimler ve Kavramlar[:：]?\s*(.*)", re.IGNORECASE)
symbol_re = re.compile(r"^Sembol(?:ler)? ve Gösterimler[:：]?\s*(.*)", re.IGNORECASE)
subpoint_re = re.compile(r"([a-eç])\)\s")

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
print(f"✅ Toplam {len(lines)} satır alındı PDF'ten.\n")

data = {"yks": {"matematik": {}}}
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
        data["yks"]["matematik"].setdefault(current_grade, {"alt": {}})
        current_unit = None
        current_topic = None
        print(f"\n🎓 Sınıf: {current_grade}")
        i += 1
        continue

    # ÜNİTE algıla
    match = unit_re.match(line)
    if match:
        current_unit, unit_title = match.groups()
        data["yks"]["matematik"][current_grade]["alt"].setdefault(current_unit, {
            "baslik": unit_title.strip(),
            "alt": {}
        })
        current_topic = None
        print(f"📘 Ünite: {current_unit} → {unit_title.strip()}")
        i += 1
        continue

    # KONU algıla
    match = topic_re.match(line)
    if match and current_unit:
        current_topic, topic_title = match.groups()
        data["yks"]["matematik"][current_grade]["alt"][current_unit]["alt"].setdefault(current_topic, {
            "baslik": topic_title.strip(),
            "terimler_ve_kavramlar": "",
            "sembol_ve_gosterimler": "",
            "alt": {}
        })
        print(f"📗 Konu: {current_topic} → {topic_title.strip()}")
        i += 1

        # Sonraki birkaç satırda "Terimler ve Kavramlar" ya da "Sembol ve Gösterimler" varsa al
        j = i
        while j < len(lines):
            term_match = term_re.match(lines[j])
            symbol_match = symbol_re.match(lines[j])
            if term_match and current_topic:
                data["yks"]["matematik"][current_grade]["alt"][current_unit]["alt"][current_topic]["terimler_ve_kavramlar"] = term_match.group(1).strip()
                print(f"📌 Terimler ve Kavramlar bulundu.")
            elif symbol_match and current_topic:
                data["yks"]["matematik"][current_grade]["alt"][current_unit]["alt"][current_topic]["sembol_ve_gosterimler"] = symbol_match.group(1).strip()
                print(f"🔣 Sembol ve Gösterimler bulundu.")
            elif re.match(r"^\d", lines[j]):
                break
            j += 1
        continue

    # KAZANIM algıla
    match = objective_re.match(line)
    if match and current_topic:
        kazanım_kodu, kazanım_baslik = match.groups()

        # Açıklamayı topla
        j = i + 1
        raw = []
        while j < len(lines):
            next_line = lines[j]
            if any([
                grade_re.match(next_line),
                unit_re.match(next_line),
                topic_re.match(next_line),
                objective_re.match(next_line)
            ]):
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

        data["yks"]["matematik"][current_grade]["alt"][current_unit]["alt"][current_topic]["alt"][kazanım_kodu] = {
            "baslik": kazanım_baslik.strip(),
            "aciklama": aciklamalar
        }
        print(f"✅ Kazanım: {kazanım_kodu} → {kazanım_baslik.strip()}")
        i = j
        continue

    i += 1

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n📁 JSON dosyasına yazıldı: {output_path}")