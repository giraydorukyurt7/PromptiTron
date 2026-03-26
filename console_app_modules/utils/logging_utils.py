import json
from datetime import datetime

class LoggingUtils:
    def log_http_request(self, method: str, url: str, status_code: int, response_time: float, error: str = None):
        """HTTP isteklerini konsola logla"""
        if hasattr(self, 'console'):
            if error:
                self.console.print(f"[red][X] {method} {url} - ERROR: {error}[/red]")
            elif status_code >= 200 and status_code < 300:
                self.console.print(f"[green][OK] {method} {url} - {status_code} ({response_time:.2f}s)[/green]")
            elif status_code >= 400 and status_code < 500:
                self.console.print(f"[yellow][!] {method} {url} - {status_code} ({response_time:.2f}s)[/yellow]")
            else:
                self.console.print(f"[red][ERR] {method} {url} - {status_code} ({response_time:.2f}s)[/red]")
 
    def log_langgraph_activity(self, activity: str, data: dict = None, node: str = None, state: dict = None):
        """LangGraph aktivitelerini detaylı olarak logla"""
        if hasattr(self, 'console'):
            timestamp = datetime.now().strftime("%H:%M:%S")
            msg = f"[blue][LG] [{timestamp}] LangGraph: {activity}"
            if node:
                msg += f" (Node: {node})"
            msg += "[/blue]"
            self.console.print(msg)
            
            if data:
                self.console.print(f"[dim]  Data: {json.dumps(data, indent=2, ensure_ascii=False)}[/dim]")
            if state:
                self.console.print(f"[dim]  State: {json.dumps(state, indent=2, ensure_ascii=False)}[/dim]")
    
    def log_langchain_activity(self, activity: str, data: dict = None, chain_type: str = None, tokens: int = None):
        """LangChain aktivitelerini detaylı olarak logla"""
        if hasattr(self, 'console'):
            timestamp = datetime.now().strftime("%H:%M:%S")
            msg = f"[magenta][LC] [{timestamp}] LangChain: {activity}"
            if chain_type:
                msg += f" (Chain: {chain_type})"
            if tokens:
                msg += f" (Tokens: {tokens})"
            msg += "[/magenta]"
            self.console.print(msg)
            
            if data:
                self.console.print(f"[dim]  Input: {json.dumps(data, indent=2, ensure_ascii=False)}[/dim]")
    
    def log_crewai_activity(self, activity: str, agent: str = None, task: str = None, status: str = None, result: str = None):
        """CrewAI aktivitelerini detaylı olarak logla"""
        if hasattr(self, 'console'):
            timestamp = datetime.now().strftime("%H:%M:%S")
            msg = f"[cyan][AI] [{timestamp}] CrewAI: {activity}"
            if agent:
                msg += f" - Agent: {agent}"
            if task:
                msg += f" - Task: {task}"
            if status:
                msg += f" - Status: {status}"
            msg += "[/cyan]"
            self.console.print(msg)
            
            if result:
                self.console.print(f"[dim]  Result: {result[:100]}{'...' if len(result) > 100 else ''}[/dim]")
    
    def log_mcp_activity(self, activity: str, tool: str = None, params: dict = None, result: str = None, duration: float = None):
        """MCP aktivitelerini detaylı olarak logla"""
        if hasattr(self, 'console'):
            timestamp = datetime.now().strftime("%H:%M:%S")
            msg = f"[yellow][MCP] [{timestamp}] MCP: {activity}"
            if tool:
                msg += f" - Tool: {tool}"
            if duration:
                msg += f" ({duration:.2f}s)"
            msg += "[/yellow]"
            self.console.print(msg)
            
            if params:
                self.console.print(f"[dim]  Params: {json.dumps(params, indent=2, ensure_ascii=False)}[/dim]")
            if result:
                self.console.print(f"[dim]  Result: {result[:150]}{'...' if len(result) > 150 else ''}[/dim]")
    
    def log_rag_activity(self, activity: str, query: str = None, results_count: int = None, collection: str = None):
        """RAG aktivitelerini logla"""
        if hasattr(self, 'console'):
            timestamp = datetime.now().strftime("%H:%M:%S")
            msg = f"[green][RAG] [{timestamp}] RAG: {activity}"
            if collection:
                msg += f" (Collection: {collection})"
            if results_count is not None:
                msg += f" - Found {results_count} results"
            msg += "[/green]"
            self.console.print(msg)
            
            if query:
                self.console.print(f"[dim]  Query: {query}[/dim]")
    
    def log_gemini_activity(self, activity: str, model: str = None, tokens_used: int = None, response_time: float = None):
        """Gemini aktivitelerini logla"""
        if hasattr(self, 'console'):
            timestamp = datetime.now().strftime("%H:%M:%S")
            msg = f"[purple][BRAIN] [{timestamp}] Gemini: {activity}"
            if model:
                msg += f" (Model: {model})"
            if tokens_used:
                msg += f" - Tokens: {tokens_used}"
            if response_time:
                msg += f" ({response_time:.2f}s)"
            msg += "[/purple]"
            self.console.print(msg)