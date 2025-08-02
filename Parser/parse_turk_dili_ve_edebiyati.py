import re
import json
from pdfminer.high_level import extract_text

pdf_path = "lectures/turk_dili_ve_edebiyati.pdf"
output_path = "kazanimlar_turk_dili_ve_edebiyati.json"

# Sadece 2-12. sayfaları oku (0-index: 1-11)
print(f"📂 PDF dosyası okunuyor (sayfa 2-12): {pdf_path}")
text = extract_text(pdf_path, page_numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
lines = text.splitlines()
print(f"✅ {len(lines)} satır okundu")

data = {"yks": {"turk_dili_ve_edebiyati": {}}}
current_section = None
current_subsection = None
last_kazanim = None
unmatched_lines = []
current_item_dict = {}  # Kazanım koduna göre açıklama maddelerini tutar

print("\n🔍 İçerik analiz ediliyor...")
for i, line in enumerate(lines):
    original_line = line
    line = line.strip()
    
    # Her 50 satırda bir durum bilgisi
    if i % 50 == 0:
        status_info = f"[S:{current_section or '-'} SS:{current_subsection.split('.')[-1] if current_subsection else '-'} K:{last_kazanim.split('.')[-1] if last_kazanim else '-'}]"
        print(f"{i+1:4}{status_info}: {line[:60]}{'...' if len(line)>60 else ''}")

    # Boş satırları atla
    if not line:
        continue

    # 1. BÖLÜM TESPİTİ (A), B), C))
    section_match = re.match(r"^([ABC])\)\s*(.+)", line)
    if section_match:
        sec_code, sec_title = section_match.groups()
        data["yks"]["turk_dili_ve_edebiyati"][sec_code] = {
            "baslik": sec_title.strip(),
            "alt": {}
        }
        current_section = sec_code
        current_subsection = None
        last_kazanim = None
        print(f"  🟢 YENİ BÖLÜM: {sec_code}) {sec_title.strip()}")
        continue

    # 2. ALT BAŞLIK TESPİTİ (1., 2., 3.)
    if current_section:
        subhead_match = re.match(r"^(\d+)\.\s*(.+)", line)
        if subhead_match:
            sub_num, sub_title = subhead_match.groups()
            sub_code = f"{current_section}.{sub_num}"
            
            # Eğer alt başlık henüz yoksa oluştur
            if sub_code not in data["yks"]["turk_dili_ve_edebiyati"][current_section]["alt"]:
                data["yks"]["turk_dili_ve_edebiyati"][current_section]["alt"][sub_code] = {
                    "baslik": sub_title.strip(),
                    "alt": {}
                }
            
            current_subsection = sub_code
            last_kazanim = None
            print(f"    🔸 ALT BAŞLIK: {sub_code} {sub_title.strip()}")
            continue

    # 3. KAZANIM TESPİTİ (A.1.1., B.2.3. vb)
    if current_section and current_subsection:
        kazanim_match = re.match(r"^([ABC])\.\s*(\d+)\.\s*(\d+)\.\s*(.+)", line)
        if not kazanim_match:
            # Alternatif format denemesi: A.1.1. (boşluksuz)
            kazanim_match = re.match(r"^([ABC])\.(\d+)\.(\d+)\.\s*(.+)", line)
        
        if kazanim_match:
            sec, sub_num, kaz_num, kaz_title = kazanim_match.groups()
            kazanim_code = f"{sec}.{sub_num}.{kaz_num}"
            
            # Mevcut alt başlık kontrolü
            expected_subsection = f"{sec}.{sub_num}"
            if current_subsection != expected_subsection:
                print(f"    ⚠️ UYUSMAYAN ALT BAŞLIK! Beklenen: {current_subsection}, Gelen: {expected_subsection}")
                current_subsection = expected_subsection
                
                # Eğer yoksa yeni alt başlık oluştur
                if current_subsection not in data["yks"]["turk_dili_ve_edebiyati"][sec]["alt"]:
                    print(f"    ⚠️ YENİ ALT BAŞLIK OLUŞTURULUYOR: {current_subsection}")
                    data["yks"]["turk_dili_ve_edebiyati"][sec]["alt"][current_subsection] = {
                        "baslik": f"OTOMATİK OLUŞTURULDU ({current_subsection})",
                        "alt": {}
                    }
            
            # Kazanımı ekle (açıklama artık sözlük olacak)
            data["yks"]["turk_dili_ve_edebiyati"][sec]["alt"][current_subsection]["alt"][kazanim_code] = {
                "baslik": kaz_title.strip(),
                "aciklama": {}
            }
            last_kazanim = kazanim_code
            # Bu kazanım için açıklama sözlüğü oluştur
            current_item_dict[last_kazanim] = {}
            print(f"      ✅ KAZANIM: {kazanim_code} {kaz_title.strip()}")
            continue

    # 4. AÇIKLAMA SATIRI (önceki kazanıma ekle)
    if last_kazanim and current_section and current_subsection:
        try:
            # Kazanımın açıklama sözlüğünü al
            sec, sub_num, kaz_num = last_kazanim.split('.')
            kaz_path = data["yks"]["turk_dili_ve_edebiyati"][sec]["alt"][f"{sec}.{sub_num}"]["alt"][last_kazanim]
            aciklama_dict = kaz_path["aciklama"]
            
            # Madde işareti kontrol et (a., b., c. vb)
            item_match = re.match(r"^([a-z])\.\s*(.*)", line)
            if item_match:
                item_letter = item_match.group(1)
                content = item_match.group(2).strip()
                
                # Maddeyi sözlüğe ekle
                aciklama_dict[item_letter] = content
                print(f"        📝 Madde {item_letter} eklendi: {content[:40]}{'...' if len(content)>40 else ''}")
            else:
                # Madde işareti yoksa, 'a' maddesi olarak ekle veya güncelle
                if 'a' not in aciklama_dict:
                    # İlk açıklama satırı
                    aciklama_dict['a'] = line
                    print(f"        📝 'a' maddesi oluşturuldu: {line[:40]}{'...' if len(line)>40 else ''}")
                else:
                    # Var olan 'a' maddesine ekle
                    aciklama_dict['a'] += " " + line
                    print(f"        📝 'a' maddesi genişletildi: +{len(line)} karakter")
                    
        except KeyError as e:
            print(f"        ❗ AÇIKLAMA HATASI: {last_kazanim} bulunamadı: {str(e)}")
            unmatched_lines.append(line)
    else:
        print(f"        ❗ EŞLEŞMEYEN SATIR: {line}")
        unmatched_lines.append(line)

# Rapor oluştur
print("\n📊 İŞLEM SONUÇLARI:")
print(f"- Toplam satır: {len(lines)}")
print(f"- İşlenmeyen satırlar: {len(unmatched_lines)}")
if unmatched_lines:
    print("  İşlenmeyen satır örnekleri:")
    for i, line in enumerate(unmatched_lines[:5]):
        print(f"  {i+1}. {line[:80]}{'...' if len(line)>80 else ''}")

# JSON'a yaz
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n✅ JSON dosyası kaydedildi: {output_path}")
print("⭐ İşlem tamamlandı")