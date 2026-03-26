#!/usr/bin/env python3
"""
Promptitron Worker Service
Handles background document processing, RAG updates, and maintenance tasks
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from core.rag_system import rag_system
from core.document_understanding import DocumentAnalyzer
from rich.console import Console

console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptitronWorker:
    def __init__(self):
        self.document_analyzer = DocumentAnalyzer()
        self.running = True
        
    async def start(self):
        """Start the worker service"""
        console.print("[cyan]🔧 Promptitron Worker Service Started[/cyan]")
        
        try:
            # Initialize systems
            await self._initialize_systems()
            
            # Start main worker loop
            await self._worker_loop()
            
        except KeyboardInterrupt:
            console.print("[yellow]⚠️  Worker service stopped by user[/yellow]")
        except Exception as e:
            logger.error(f"Worker service error: {e}")
            console.print(f"[red]❌ Worker service error: {e}[/red]")
        finally:
            await self._cleanup()
    
    async def _initialize_systems(self):
        """Initialize worker systems"""
        console.print("[cyan]📚 Initializing RAG system...[/cyan]")
        # RAG system will auto-initialize when needed
        
        console.print("[cyan]📄 Document analyzer ready[/cyan]")
    
    async def _worker_loop(self):
        """Main worker processing loop"""
        while self.running:
            try:
                # Check for new documents to process
                await self._process_pending_documents()
                
                # Maintain RAG system health
                await self._maintain_rag_system()
                
                # Sleep between cycles
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Worker loop error: {e}")
                await asyncio.sleep(60)  # Longer sleep on error
    
    async def _process_pending_documents(self):
        """Process any pending documents"""
        uploads_dir = Path("uploads")
        if not uploads_dir.exists():
            return
            
        # Process new files
        for file_path in uploads_dir.glob("**/*"):
            if file_path.is_file() and not file_path.name.startswith('.processed_'):
                try:
                    console.print(f"[cyan]📄 Processing: {file_path.name}[/cyan]")
                    
                    # Analyze document
                    if file_path.suffix.lower() == '.pdf':
                        result = await self.document_analyzer.analyze_pdf(str(file_path))
                    elif file_path.suffix.lower() in ['.docx', '.doc']:
                        result = await self.document_analyzer.analyze_document(str(file_path))
                    else:
                        continue
                    
                    # Add to RAG system if analysis successful
                    if result and result.get('success'):
                        await self._add_to_rag(result, file_path)
                    
                    # Mark as processed
                    processed_path = file_path.parent / f".processed_{file_path.name}"
                    file_path.rename(processed_path)
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
    
    async def _add_to_rag(self, analysis_result: dict, file_path: Path):
        """Add processed document to RAG system"""
        try:
            # Extract text content
            content = analysis_result.get('extracted_text', '')
            if not content:
                return
            
            # Prepare metadata
            metadata = {
                'filename': file_path.name,
                'file_type': file_path.suffix,
                'processed_at': analysis_result.get('timestamp'),
                'source': 'worker_processor'
            }
            
            # Add to RAG
            await rag_system.add_documents([content], [metadata])
            console.print(f"[green]✅ Added {file_path.name} to RAG system[/green]")
            
        except Exception as e:
            logger.error(f"Error adding to RAG: {e}")
    
    async def _maintain_rag_system(self):
        """Perform RAG system maintenance"""
        try:
            # Check RAG system health
            stats = await rag_system.get_collection_stats()
            
            if stats:
                total_docs = sum(stat.get('count', 0) for stat in stats.values())
                if total_docs > 0:
                    console.print(f"[dim]📊 RAG System: {total_docs} documents across {len(stats)} collections[/dim]")
            
        except Exception as e:
            logger.debug(f"RAG maintenance check: {e}")
    
    async def _cleanup(self):
        """Cleanup worker resources"""
        console.print("[cyan]🧹 Cleaning up worker resources...[/cyan]")
        self.running = False

async def main():
    """Main worker entry point"""
    worker = PromptitronWorker()
    await worker.start()

if __name__ == "__main__":
    asyncio.run(main())