import asyncio
import sys
import os
from rich.console import Console
from console_app_modules.core_manager import ConsoleManager

# Windows compatibility
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

async def test_console():
    """Test console app initialization"""
    console = Console(force_terminal=True, width=120, color_system="windows" if sys.platform.startswith('win') else "truecolor")
    
    try:
        # Create ConsoleManager instance
        manager = ConsoleManager(console)
        console.print("[green]OK: ConsoleManager created successfully[/green]")
        
        # Test session ID generation
        session_id = manager.generate_session_id()
        console.print(f"[green]OK: Session ID generated: {session_id}[/green]")
        
        # Test display_menu method
        console.print("[yellow]Testing display_menu method:[/yellow]")
        manager.display_menu()
        console.print("[green]OK: Menu displayed successfully[/green]")
        
        # Test system initialization
        console.print("[yellow]Testing system initialization:[/yellow]")
        await manager.initialize_systems()
        console.print("[green]OK: Systems initialized successfully[/green]")
        
        console.print("\n[bold green]All tests passed! Console app is working.[/bold green]")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        import traceback
        console.print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_console())