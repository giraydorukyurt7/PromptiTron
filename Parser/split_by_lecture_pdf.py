import fitz  # PyMuPDF
import os

# İçindekiler kısmından belirlenen sayfa aralıkları
# format: "ders_adi": (başlangıç_sayfa, bitiş_sayfa)
DERS_SAYFALARI = {
    "turk_dili_ve_edebiyati": (4, 50),
    "din_kulturu": (51, 74),
    "tarih": (75, 96),
    "inkilap_ve_ataturkculuk": (97, 104),
    "cografya": (105, 116),
    "matematik": (117, 147),
    "fizik": (148, 175),
    "kimya": (176, 199),
    "biyoloji": (200, 219),
    "felsefe": (220, 231),
    "mantik": (232, 239),
    "sosyoloji": (240, 250),
    "psikoloji": (251, 263),
    "ingilizce": (264, 309),
    "almanca": (310, 341),
    "fransizca": (342, 373),
    "arapca": (374, 506),
    "rusca": (507, 586)
}

def split_pdf_by_ders(pdf_path, output_folder="lectures"):
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)

    for ders, (start, end) in DERS_SAYFALARI.items():
        print(f"📚 İşleniyor: {ders} ({start}–{end})")
        new_doc = fitz.open()
        for i in range(start - 1, end):  # PyMuPDF 0-index'li
            new_doc.insert_pdf(doc, from_page=i, to_page=i)
        output_path = os.path.join(output_folder, f"{ders}.pdf")
        new_doc.save(output_path)
        new_doc.close()
        print(f"✅ Kaydedildi: {output_path}")

    print("\n🎉 PDF bölme işlemi tamamlandı.")

if __name__ == "__main__":
    pdf_path = "yks_kazanimlar.pdf"
    split_pdf_by_ders(pdf_path)
