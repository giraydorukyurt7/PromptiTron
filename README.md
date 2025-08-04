# Promptitron Unified AI System

Bu proje, YKS (Yükseköğretim Kurumları Sınavı) öğrencileri için kapsamlı bir yapay zeka eğitim sistemidir. Google Gemini 2.5, RAG (Retrieval-Augmented Generation), LangChain ve uzman yönlendirme sistemlerini birleştirerek kişiselleştirilmiş öğrenme deneyimi sunar.

## 🚀 Özellikler

### 🤖 AI Sistemi
- **Google Gemini 2.5 Entegrasyonu**: Pro, Flash ve Flash-Lite modeller
- **Çoklu Uzman Sistemi**: Matematik, Fizik, Kimya, Biyoloji uzmanları
- **LangGraph İş Akışları**: Karmaşık görevler için yapılandırılmış süreçler
- **Fonksiyon Çağırma**: Yapılandırılmış çıktılar ve araç kullanımı

### 📚 RAG (Retrieval-Augmented Generation)
- **Hibrit Arama**: Semantik + anahtar kelime araması
- **Çoklu Koleksiyon**: Müfredat, sohbetler, belgeler
- **Kişiselleştirme**: Öğrenci profiline göre uyarlanan sonuçlar
- **Akıllı Yeniden Sıralama**: LLM tabanlı sonuç optimizasyonu

### 💬 Konuşma Belleği
- **Uzun Dönem Hafıza**: Otomatik özet ve bağlam yönetimi
- **Öğrenci Profilleri**: Öğrenme stili, güçlü/zayıf yönler takibi
- **Performans Analizi**: İlerleme izleme ve öneriler

### 📖 Eğitim İçerikleri
- **Soru Üretimi**: YKS formatında çoktan seçmeli sorular
- **Çalışma Planları**: Kişiselleştirilmiş haftalık/günlük programlar
- **Kavram Açıklamaları**: Sokratik yöntemle öğretim
- **Performans Raporları**: Detaylı analiz ve öneriler

## 🏗️ Sistem Mimarisi

```
promptitron_unified/
├── core/                    # Temel AI modülleri
│   ├── gemini_client.py    # Birleşik Gemini istemcisi
│   ├── rag_system.py       # Gelişmiş RAG sistemi
│   ├── agents.py           # LangGraph agent sistemi
│   ├── chains.py           # LangChain zincir tanımları
│   └── conversation_memory.py # Konuşma bellek sistemi
├── api/                     # FastAPI endpoint'leri
│   └── main_api.py         # Ana API uygulaması
├── models/                  # Pydantic veri modelleri
│   └── structured_models.py # Yapılandırılmış çıktı modelleri
├── data/                    # Veri dosyaları
│   └── jsonn/              # YKS müfredat verileri
├── config.py               # Sistem konfigürasyonu
├── main.py                 # Ana giriş noktası
└── requirements.txt        # Python bağımlılıkları
```

## 🛠️ Kurulum

### 1. Proje Klonlama
```bash
git clone <repository-url>
cd promptitron_unified
```

### 2. Sanal Environment Oluşturma
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Bağımlılıkları Yükleme
```bash
pip install -r requirements.txt
```

### 4. Environment Değişkenleri
`.env.example` dosyasını `.env` olarak kopyalayın ve gerekli API anahtarlarını ekleyin:
```bash
cp .env.example .env
```

`.env` dosyasında şu değerleri güncelleyin:
```env
GOOGLE_API_KEY=your_google_api_key_here
SECRET_KEY=your_secret_key_here
```

### 5. Çalıştırma
```bash
python main.py
```

API dokümantasyonu: http://localhost:8000/docs

## 📝 API Kullanımı

### Chat Endpoint
```python
import requests

response = requests.post("http://localhost:8000/chat", json={
    "message": "Matematik derivatif konusunu açıkla",
    "student_id": "student_123",
    "use_memory": True
})

print(response.json())
```

### Soru Üretimi
```python
response = requests.post("http://localhost:8000/generate/questions", json={
    "subject": "matematik",
    "topic": "türev",
    "difficulty": "medium",
    "count": 3
})

print(response.json())
```

### Çalışma Planı
```python
response = requests.post("http://localhost:8000/generate/study-plan", json={
    "student_profile": {
        "student_id": "student_123",
        "target_exam": "YKS",
        "weak_subjects": ["fizik"],
        "strong_subjects": ["matematik"],
        "daily_hours": 6
    },
    "duration_weeks": 12
})

print(response.json())
```

## 🔧 Konfigürasyon

### Gemini Modelleri
- **Pro**: Karmaşık mantık gerektiren görevler
- **Flash**: Genel amaçlı, hızlı yanıtlar
- **Flash-Lite**: Basit görevler, düşük maliyet

### RAG Ayarları
- **Semantic Weight**: 0.7 (Semantik arama ağırlığı)
- **Keyword Weight**: 0.3 (Anahtar kelime ağırlığı)
- **Reranking**: LLM tabanlı sonuç iyileştirme

### Güvenlik
- Otomatik içerik filtresi
- Rate limiting
- API anahtarı koruması

## 🧪 Test Etme

```bash
# Unit testler
pytest tests/

# API testleri
python -m pytest tests/test_api.py

# Integration testleri
python -m pytest tests/test_integration.py
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Sistem İstatistikleri
```bash
curl http://localhost:8000/stats
```

## 🔄 Güncellemeler

### Müfredat Verilerini Güncelleme
1. JSON dosyalarını `data/jsonn/` klasörüne ekleyin
2. Sistemi yeniden başlatın
3. Veriler otomatik olarak RAG sistemine yüklenecek

### Yeni Uzman Ekleme
1. `core/agents.py` dosyasında yeni uzman tanımı ekleyin
2. Uzmanlık alanı anahtar kelimelerini belirleyin
3. Sistem otomatik olarak yeni uzmanı kullanacak

## 🚨 Sorun Giderme

### Yaygın Hatalar

1. **Google API Anahtarı Hatası**
   - `.env` dosyasında `GOOGLE_API_KEY` değerini kontrol edin
   - API anahtarınızın aktif olduğundan emin olun

2. **ChromaDB Hatası**
   - `chroma_db` klasörünü silin ve sistemi yeniden başlatın
   - Disk alanınızı kontrol edin

3. **Memory Hatası**
   - Büyük dosyalar için batch boyutunu küçültün
   - `MAX_OUTPUT_TOKENS` değerini azaltın

### Loglama
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit yapın (`git commit -m 'Add some AmazingFeature'`)
4. Push yapın (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 📞 İletişim

- **Email**: support@promptitron.ai
- **GitHub Issues**: Teknik sorular için
- **Documentation**: Detaylı dokümantasyon için `/docs` endpoint'ini ziyaret edin

---

**Not**: Bu sistem eğitim amaçlıdır ve gerçek sınav sonuçlarını garanti etmez. Profesyonel eğitim danışmanlığı almanızı öneririz.