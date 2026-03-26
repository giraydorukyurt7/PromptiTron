from datetime import datetime
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

class ExportManager:
    async def export_conversation(self):
        """Konuşma geçmişini dışa aktar"""
        self.console.print(Panel("[bold yellow]Export Conversation[/bold yellow]"))
        
        # Check if there's any conversation history
        if not self.conversation_history:
            self.console.print("[yellow]⚠️ Henüz hiç konuşma yapılmamış.[/yellow]")
            self.console.print("[dim]Önce AI Assistant modunda soru sorun, sonra export yapın.[/dim]")
            return
        
        self.console.print(f"[green]📄 {len(self.conversation_history)} konuşma bulundu.[/green]")
        
        # User-friendly format selection
        format_choices = {
            "1. Markdown (.md)": "markdown",
            "2. JSON (.json)": "json", 
            "3. Text (.txt)": "txt"
        }
        
        self.console.print("\n[bold cyan]Export Formatları:[/bold cyan]")
        for choice in format_choices.keys():
            self.console.print(f"  {choice}")
            
        format_display = Prompt.ask("\nFormat seçin", choices=list(format_choices.keys()), default="1. Markdown (.md)")
        format_choice = format_choices[format_display]
        
        self.log_mcp_activity(
            "Export Started",
            tool="DataExporter",
            params={"format": format_choice}
        )
        
        # Create export data
        export_data = {
            "session_id": self.session_id,
            "export_time": datetime.now().isoformat(),
            "conversation_count": len(self.conversation_history),
            "history": self.conversation_history
        }
        
        filename = f"conversation_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_choice}"
        
        if format_choice == "json":
            import json
            content = json.dumps(export_data, indent=2, ensure_ascii=False)
        elif format_choice == "markdown":
            content = f"# 🎓 Promptitron Konuşma Geçmişi\n\n"
            content += f"**📅 Export Zamanı:** {export_data['export_time']}\n"
            content += f"**🆔 Session ID:** {export_data['session_id']}\n"
            content += f"**💬 Toplam Konuşma:** {export_data['conversation_count']}\n\n"
            content += "---\n\n"
            
            for i, item in enumerate(self.conversation_history, 1):
                timestamp = item.get('timestamp', 'Unknown')
                content += f"## 💬 Konuşma {i}\n\n"
                content += f"**⏰ Zaman:** {timestamp}\n"
                content += f"**🔧 Sistem:** {item.get('system_used', 'Unknown')}\n"
                if item.get('processing_time'):
                    content += f"**⚡ İşlem Süresi:** {item['processing_time']:.2f}s\n"
                content += "\n"
                content += f"**👤 Kullanıcı:**\n{item.get('user', '')}\n\n"
                content += f"**🤖 Asistan:**\n{item.get('assistant', '')}\n\n"
                content += "---\n\n"
        else:  # txt
            content = f"PROMPTITRON KONUŞMA GEÇMİŞİ\n"
            content += "=" * 50 + "\n"
            content += f"Export Zamanı: {export_data['export_time']}\n"
            content += f"Session ID: {export_data['session_id']}\n"
            content += f"Toplam Konuşma: {export_data['conversation_count']}\n"
            content += "=" * 50 + "\n\n"
            
            for i, item in enumerate(self.conversation_history, 1):
                timestamp = item.get('timestamp', 'Unknown')
                content += f"KONUŞMA {i}\n"
                content += f"Zaman: {timestamp}\n"
                content += f"Sistem: {item.get('system_used', 'Unknown')}\n"
                if item.get('processing_time'):
                    content += f"İşlem Süresi: {item['processing_time']:.2f}s\n"
                content += f"\nKullanıcı: {item.get('user', '')}\n"
                content += f"Asistan: {item.get('assistant', '')}\n\n"
                content += "-" * 30 + "\n\n"
        
        # Save file
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Get file size for better feedback
            import os
            file_size = os.path.getsize(filename)
            file_size_kb = file_size / 1024
            
            self.console.print(f"[green]✅ Export başarılı![/green]")
            self.console.print(f"[dim]📁 Dosya: {filename}[/dim]")
            self.console.print(f"[dim]📏 Boyut: {file_size_kb:.1f} KB[/dim]")
            self.console.print(f"[dim]💬 {len(self.conversation_history)} konuşma export edildi[/dim]")
            
            self.log_mcp_activity(
                "Export Completed",
                tool="DataExporter",
                result=f"Saved to {filename} ({file_size_kb:.1f} KB)"
            )
        except Exception as e:
            self.console.print(f"[red]Export failed: {e}[/red]")
            self.log_mcp_activity(
                "Export Failed",
                tool="DataExporter",
                result=str(e)
            )