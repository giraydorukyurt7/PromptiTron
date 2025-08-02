# main.py

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from Modules.downloader import download_youtube_audio
from Modules.transcriber import transcribe_audio
from Modules.summarizer import summarize_text  # opsiyonel
import os

app = Flask(__name__, static_folder="frontend")
CORS(app)  # Gerekirse: CORS aç (çapraz istekler için)

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/transcribe", methods=["POST"])
def transcribe_route():
    try:
        data = request.get_json()
        url = data.get("url")

        if not url:
            return jsonify({"error": "URL eksik"}), 400

        print("🚀 Transkript işlemi başlıyor...")
        audio_path = download_youtube_audio(url)
        transcript = transcribe_audio(audio_path)

        # Opsiyonel özet
        try:
            summary = summarize_text(transcript)
        except Exception as e:
            summary = "⚠️ Özetleme başarısız: " + str(e)

        return jsonify({
            "transcript": transcript,
            "summary": summary
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Statik dosyaları (script.js, style.css) sunmak için
@app.route('/<path:path>')
def static_proxy(path):
    return app.send_static_file(path)


if __name__ == "__main__":
    app.run(debug=True, port=5000)