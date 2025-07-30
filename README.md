# PromptiTron
PromptiTron



## 🧠 Git Branch ve Merge Stratejisi - PromptiTron Projesi

### 📂 Branch Yapısı

Proje geliştirme sürecinde anlaşılır, düzenli ve yönetilebilir bir Git yapısı kullanmak adına aşağıdaki **özellik bazlı** ama geliştirici ismini de içeren hibrit strateji uygulanacaktır:

```
main
  └── dev
        ├── feature/youtube-parser-giray
        ├── feature/chrome-extension-fatih
        └── feature/deb-support-acar
```

#### Açıklamalar:

* `main`: Kararlı, yayına hazır sürümleri içerir.
* `dev`: Geliştirme tamamlanmış, test edilmekte olan kodlar burada toplanır.
* `feature/...`: Yeni bir özellik geliştirme süreci burada yapılır. `feature/özellik-isim-gelistirici` formatı kullanılır.
* `fix/...` (Opsiyonel): Hataların düzeltildiği özel branch'lerdir.

---

### 🔄 Merge Akışı

1. Her geliştirici yeni bir özellik için `feature/` branch'i oluşturur.
2. Geliştirme tamamlandığında `Pull Request (PR)` açılır ve bu PR **`dev` branch'ine** yönlendirilir.
3. PR en az 1 ekip üyesi tarafından gözden geçirilir (code review).
4. Onaylanan PR, `dev` branch'ine merge edilir.
5. `dev` branch'inde entegre testler gerçekleştirilir.
6. Kararlı hale geldiğinde `dev` → `main` branch'ine merge yapılır.
7. Her ana sürüm `main` branch'inden oluşturulur ve sürüm numarası (`v1.0.0` vb.) ile tag'lenir.

---

### ✅ Ek Kurallar

* Her PR başlığı açıklayıcı olmalı. Örn: `feat: Add YouTube transcript parser`
* Commit mesajları kısa ve anlaşılır olmalı. Örn: `fix: correct time sync issue`
* Geliştirme sürecinde PR'lar küçük parçalara bölünmeli, büyük değişiklikler tek commit'e sıkıştırılmamalıdır.

---

Bu yapı ile hem paralel geliştirme kolaylaşır hem de hata yapıldığında geri dönmek çok daha basit olur. Git GUI araçları (Sourcetree, GitKraken) ile bu yapı rahatça takip edilebilir.

> 🧩 Not: Bu belgeyi `GIT_STRATEGY.md` adıyla projenin kök dizinine eklemeniz önerilir.