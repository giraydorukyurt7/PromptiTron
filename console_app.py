import os
import sys
import asyncio
import logging
import colorama
from rich.console import Console
from rich.logging import RichHandler
from console_app_modules.core_manager import ConsoleManager

# Windows compatibility
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

console = Console(force_terminal=True, width=120, color_system="windows" if sys.platform.startswith('win') else "truecolor")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)

# Initialize colorama
colorama.init()

def main():
    try:
        manager = ConsoleManager(console)
        asyncio.run(manager.run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        logger.exception("Unhandled exception")

if __name__ == "__main__":
    main()

#
#
#import os
#import sys
#import json
#import asyncio
#import requests
#import time
#import re
#from datetime import datetime
#from pathlib import Path
#from typing import Dict, Any, List, Optional
#import logging
#from rich.console import Console
#from rich.logging import RichHandler
#from rich.table import Table
#from rich.progress import Progress, SpinnerColumn, TextColumn
#from rich.markdown import Markdown
#from rich.prompt import Prompt, Confirm
#from rich.syntax import Syntax
#from rich.panel import Panel
#from rich.text import Text
#import colorama
#
## Add project root to path
#project_root = Path(__file__).parent
#sys.path.insert(0, str(project_root))
#
#from core.gemini_client import gemini_client
#from core.rag_system import rag_system
#from core.agents import agent_system
#from core.conversation_memory import conversation_memory
#from core.document_understanding import document_understanding
#from core.hierarchical_menu import hierarchical_menu
#from models.structured_models import *
#from config import settings
#
## Startup initialization flag
#_system_initialized = False
#
#
## API base URL
#API_BASE_URL = "http://localhost:8000"
#
#