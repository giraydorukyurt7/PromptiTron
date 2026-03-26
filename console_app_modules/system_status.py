from rich.panel import Panel
from rich.table import Table

class SystemStatus:
    async def show_system_status(self):
        """Sistem durumunu detaylı olarak göster"""
        self.console.print(Panel("[bold blue]System Status[/bold blue]"))
        
        # Log system check
        self.log_mcp_activity("System Health Check", tool="HealthMonitor")
        
        # API Health Check
        result = await self.call_api("/health", "GET")
        
        table = Table(title="Component Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details")
        
        # API Status
        if result.get("status") == "healthy":
            table.add_row("API Server", "[OK] Online", f"Version: {result.get('version', 'Unknown')}")
            self.log_mcp_activity("Health Check", tool="APIServer", result="Healthy")
        else:
            table.add_row("API Server", "[ERR] Offline", "Connection failed")
            self.log_mcp_activity("Health Check", tool="APIServer", result="Failed")
        
        # Check components with detailed logging
        services = result.get("services", {})
        for service_name, service_status in services.items():
            if service_status == "healthy":
                table.add_row(service_name, "[green][OK] Healthy[/green]", "Operational")
                self.log_mcp_activity("Service Check", tool=service_name, result="Healthy")
            else:
                table.add_row(service_name, "[red][ERR] Error[/red]", str(service_status))
                self.log_mcp_activity("Service Check", tool=service_name, result=f"Error: {service_status}")
        
        self.console.print(table)
        
        # Get additional stats
        stats_result = await self.call_api("/stats", "GET")
        if stats_result:
            self.console.print("\n[bold]System Statistics:[/bold]")
            self.console.print(f"Total Conversations: {stats_result.get('total_conversations', 0)}")
            self.console.print(f"Total Students: {stats_result.get('total_students', 0)}")
            self.console.print(f"System Uptime: {stats_result.get('uptime', 'Unknown')}")
            
            self.log_rag_activity(
                "Statistics Retrieved",
                results_count=stats_result.get('total_conversations', 0)
            )