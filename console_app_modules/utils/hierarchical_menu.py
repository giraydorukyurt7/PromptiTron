from rich.prompt import Prompt

class HierarchicalMenu:
    def show_subject_selection(self):
        """Ders seçimi"""
        # ... (Orijinal kod)
        pass

    def show_grade_selection(self, subject_name: str, subject_code: str):
        """Sınıf seçimi"""
        # ... (Orijinal kod)
        pass

    # ... (Diğer menü fonksiyonları)
    def display_menu(self):
        """Ana menüyü göster"""
        table = Table(title="🎓 Promptitron Console Menu", show_header=False)
        table.add_column("Seçenek", style="cyan", width=12)
        table.add_column("Açıklama", style="white")
        
        table.add_row("1", "🤖 AI Asistan Modu - Ders soruları sorun ve açıklama alın")
        table.add_row("2", "❓ Soru Oluştur - Tüm derslerden test soruları üretin")
        table.add_row("3", "📅 Çalışma Planı - Kişiselleştirilmiş YKS hazırlık planı")
        table.add_row("4", "🔍 Bilgi Ara - Müfredat ve konu bilgilerinde arama")
        table.add_row("5", "📊 İçerik Analizi - Metin zorluk analizi")
        table.add_row("6", "📄 Doküman Analizi - PDF, Word analizi + soru çıkarma")
        table.add_row("7", "🌐 Web Sitesi Analizi - URL'den eğitim içeriği analizi")
        table.add_row("8", "📺 YouTube Video Analizi - Video transkript + analiz")
        table.add_row("9", "📚 Müfredat Göster - Ders müfredatlarını inceleyin")
        table.add_row("10", "📤 Geçmiş Dışa Aktar - Konuşma geçmişinizi kaydedin")
        table.add_row("11", "⚙️ Sistem Durumu - API ve servis durumları")
        table.add_row("12", "🛠️ Ayarlar - Konfigürasyon seçenekleri")
        table.add_row("0", "🚪 Çıkış - Uygulamadan çıkın")
        
        console.print(table)

# Singleton instance
hierarchical_menu = HierarchicalMenu()