# Modules/downloader.py

import os
import yt_dlp
from datetime import datetime
from pathlib import Path

def download_youtube_audio(url, output_dir="Outputs/audio"):
    """
    YouTube videosundan sesi indirir (mp3 formatında).

    Args:
        url (str): YouTube video URL'si
        output_dir (str): Ses dosyasının kaydedileceği klasör

    Returns:
        Path: İndirilen dosyanın tam yolu
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(output_dir) / f"audio_{timestamp}.%(ext)s"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(output_path),
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    print(f"⬇️ YouTube ses indiriliyor: {url}")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    final_path = str(output_path).replace("%(ext)s", "mp3")
    print(f"✅ İndirme tamamlandı: {final_path}")
    return Path(final_path)