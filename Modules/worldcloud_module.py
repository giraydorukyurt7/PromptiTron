import os
from pathlib import Path
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import nltk
import datetime

# Stopwords yükle (ilk kullanımda indir)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
from nltk.corpus import stopwords

def generate_wordcloud(language="turkish"):
    # 📁 Yol çözümleme - Script'in bulunduğu yerden Proje köküne çıkar
    project_root = Path(__file__).resolve().parent.parent
    transcripts_dir = project_root / "Transcripts"
    output_dir = project_root / "Wordclouds"

    print(f"📁 Transkript klasörü: {transcripts_dir}")

    if not transcripts_dir.exists():
        print("❌ Hata: Transkript klasörü bulunamadı.")
        return

    txt_files = list(transcripts_dir.glob("*.txt"))
    print(f"📄 Bulunan .txt dosyası sayısı: {len(txt_files)}")

    if len(txt_files) == 0:
        print("❌ Hata: Hiç .txt dosyası bulunamadı.")
        return

    all_text = ""

    for file in txt_files:
        print(f"📂 İşleniyor: {file.name}")
        try:
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().strip()
                print(f"🔎 Okunan karakter: {len(content)}")
                if content:
                    print(f"🧾 İlk 100 karakter: {content[:100]}")
                    all_text += content + " "
                else:
                    print(f"⚠️ Uyarı: {file.name} boş veya sadece boşluk içeriyor.")
        except Exception as e:
            print(f"❌ Hata: {file.name} okunamadı: {e}")

    final_length = len(all_text.strip())
    print(f"\n🧮 Toplam birleştirilmiş metin uzunluğu: {final_length} karakter")

    if final_length == 0:
        print("❌ Hiçbir dosyada anlamlı içerik bulunamadı. Kelime bulutu oluşturulamadı.")
        return

    try:
        stop_words = set(stopwords.words(language))
        print(f"🛑 Stopword sayısı ({language}): {len(stop_words)}")
    except:
        print(f"⚠️ '{language}' dili için stopwords bulunamadı. Varsayılan set kullanılacak.")
        stop_words = STOPWORDS

    # Wordcloud klasörünü oluştur
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = output_dir / f"wordcloud_{timestamp}.png"

    print("🌥️ Word cloud oluşturuluyor...")
    try:
        wordcloud = WordCloud(
            width=1600,
            height=800,
            background_color="white",
            stopwords=stop_words,
            collocations=False
        ).generate(all_text)

        print(f"💾 Kaydediliyor: {save_path}")
        plt.figure(figsize=(20, 10))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()

        print("✅ Word cloud başarıyla oluşturuldu.")
    except Exception as e:
        print(f"❌ Word cloud oluşturulurken hata: {e}")

# 🧪 Örnek kullanım
if __name__ == "__main__":
    generate_wordcloud()