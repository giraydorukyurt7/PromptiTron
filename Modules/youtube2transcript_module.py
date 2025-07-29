import subprocess
import whisper
from datetime import datetime
from pathlib import Path
import yt_dlp
import os
import math
import numpy as np
import soundfile as sf
import io

# 📌 Ayarlanabilir split süresi (saniye cinsinden)
SPLIT_DURATION = 60

# 📁 Transkriptler bir üst dizine yazılacak
output_dir = Path(__file__).resolve().parent.parent / "Transcripts"

def get_youtube_info(url):
    print("🔍 YouTube bilgileri alınıyor...")
    ydl_opts = {
        'quiet': True,
        'format': 'bestaudio/best',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info['title']
        duration = info.get('duration', 0)

        print(f"📄 Başlık: {title}")
        print(f"⏱️ Süre: {duration} saniye")

        if 'url' in info:
            stream_url = info['url']
        elif 'requested_formats' in info and info['requested_formats'][0].get('url'):
            stream_url = info['requested_formats'][0]['url']
        else:
            raise ValueError("❌ Audio stream URL alınamadı.")
        
    print("✅ YouTube bilgileri başarıyla alındı.\n")
    return title, duration, stream_url

def split_and_transcribe_youtube(url, output_dir=output_dir):
    print("🎙️ Whisper modeli yükleniyor...")
    model = whisper.load_model("base")
    print("✅ Whisper modeli yüklendi.\n")

    title, duration, stream_url = get_youtube_info(url)

    safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_")).rstrip()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    os.makedirs(output_dir, exist_ok=True)
    num_parts = math.ceil(duration / SPLIT_DURATION)

    print(f"📦 Toplam parça sayısı: {num_parts}")
    print(f"💾 Çıktılar klasörü: {output_dir}\n")

    for i in range(num_parts):
        start_time = i * SPLIT_DURATION
        part_name = f"{safe_title}_{timestamp}_part{i+1}.txt"
        save_path = Path(output_dir) / part_name

        print(f"🚧 [{i+1}/{num_parts}] Parça hazırlanıyor: {start_time}s - {min(start_time + SPLIT_DURATION, duration)}s")

        command = [
            "ffmpeg", "-ss", str(start_time), "-t", str(SPLIT_DURATION),
            "-i", stream_url,
            "-f", "wav",
            "-ar", "16000",
            "-ac", "1",
            "-loglevel", "quiet",
            "pipe:1"
        ]

        print("📤 FFmpeg başlatılıyor...")
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        wav_bytes, _ = process.communicate()

        print("🎧 Ses buffer'a alındı, numpy'a çevriliyor...")
        audio_data, sr = sf.read(io.BytesIO(wav_bytes))
        audio_data = audio_data.astype(np.float32)  # 📌 dtype düzeltildi

        print("🧠 Whisper transkripsiyon başlıyor...")
        result = model.transcribe(audio_data, fp16=False)

        print(f"📄 Transkript kaydediliyor: {save_path.name}")
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(result["text"])

        print("✅ Parça başarıyla işlendi.\n")

    print("🎉 Tüm transkript parçaları oluşturuldu.")

if __name__ == "__main__":
    test_url = "https://www.youtube.com/watch?v=Qa8A0qjh27Y"
    print(f"🚀 YouTube transkript işlemi başlıyor: {test_url}\n")
    split_and_transcribe_youtube(test_url)