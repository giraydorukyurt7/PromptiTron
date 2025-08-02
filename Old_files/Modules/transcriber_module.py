# Modules/transcriber.py

from faster_whisper import WhisperModel
from pathlib import Path
from datetime import datetime
import os

model = None  # Lazy-load

def transcribe_audio(audio_path, model_size="base", device="cuda", save=True):
    """
    MP3 dosyasını transkribe eder (faster-whisper ile).

    Args:
        audio_path (str or Path): Ses dosyasının yolu
        model_size (str): Whisper modeli (tiny, base, small...)
        device (str): "cuda" (GPU) veya "cpu"
        save (bool): Transcript dosyası kaydedilsin mi?

    Returns:
        transcript (str): Dönüştürülmüş metin
    """
    global model
    if model is None:
        print("🎙️ Whisper modeli yükleniyor...")
        model = WhisperModel(model_size, device=device, compute_type="float16")

    print(f"🧠 Transkripsiyon başlıyor: {audio_path}")
    segments, _ = model.transcribe(str(audio_path))

    transcript = " ".join([seg.text for seg in segments])

    if save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_dir = Path("Outputs/transcripts")
        save_dir.mkdir(parents=True, exist_ok=True)
        out_path = save_dir / f"transcript_{timestamp}.txt"
        out_path.write_text(transcript, encoding="utf-8")
        print(f"✅ Transkript kaydedildi: {out_path}")

    return transcript