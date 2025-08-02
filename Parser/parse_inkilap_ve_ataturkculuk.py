import fitz
import re
import json

pdf_path = "lectures/inkilap_ve_ataturkculuk.pdf"
output_path = "kazanimlar_inkilap_ve_ataturkculuk.json"

# === Regex desenleri ===
unit_re = re.compile(r"^(\d+)\.\s*ÜNİTE[:：]?\s*(.*)", re.IGNORECASE)
objective_re = re.compile(r"^(\d+\.\d+)\.\s+(.*)")
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
data = {"yks": {"inkilap_ve_ataturkculuk": {"12": {"alt": {}}}}}
current_unit_number = None
current_unit_code = None

i = 0
while i < len(lines):
    line = lines[i]

    # ÜNİTE algıla
    match = unit_re.match(line)
    if match:
        current_unit_number, unit_title = match.groups()
        current_unit_code = f"12.{current_unit_number}"
        data["yks"]["inkilap_ve_ataturkculuk"]["12"]["alt"][current_unit_code] = {
            "baslik": unit_title.strip(),
            "alt": {}
        }
        print(f"📘 Ünite: {current_unit_code} → {unit_title.strip()}")
        i += 1
        continue

    # KAZANIM algıla
    match = objective_re.match(line)
    if match and current_unit_code:
        kazanım_kodu_raw, kazanım_baslik = match.groups()
        kazanım_kodu = f"12.{kazanım_kodu_raw}"

        # Açıklamaları tara
        j = i + 1
        raw = []
        while j < len(lines):
            next_line = lines[j]

            if unit_re.match(next_line) or objective_re.match(next_line):
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

        data["yks"]["inkilap_ve_ataturkculuk"]["12"]["alt"][current_unit_code]["alt"][kazanım_kodu] = {
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