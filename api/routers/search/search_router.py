"""
Search router for handling search endpoints
Includes: /search
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
import logging
import uuid

# Import models
from ...models.request_models import SearchRequest
from ...models.response_models import SearchResponse

# Import core modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from core.rag_system import rag_system

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["search"],
    responses={404: {"description": "Not found"}}
)

# Search Endpoint
@router.post("/search", response_model=SearchResponse)
async def search_content(request: SearchRequest):
    """Search through knowledge base"""
    try:
        # Perform search
        results = await rag_system.search(
            query=request.query,
            collection_names=request.collection_names,
            n_results=request.n_results,
            filter_metadata=request.filters
        )
        
        # Convert to SearchResult models
        search_results = []
        for result in results:
            search_result = SearchResult(
                result_id=result.get("id", str(uuid.uuid4())),
                content=result["content"],
                title=result.get("metadata", {}).get("title", "Untitled"),
                subject=None,  # Will be inferred from metadata
                topic=result.get("metadata", {}).get("topic"),
                relevance_score=result.get("score", 0.0),
                source_type=result.get("collection", "unknown"),
                metadata=result.get("metadata", {})
            )
            search_results.append(search_result)
        
        return SearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results),
            search_time=0.1,  # Placeholder
            filters_applied=request.filters or {},
            suggestions=[]
        )
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))