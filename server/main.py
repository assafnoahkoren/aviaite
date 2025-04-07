from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from src.semantic_search import SemanticSearchClient
import json

app = FastAPI(
    title="Aviaite API",
    description="API for aviation document search and analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize the semantic search client (reuse the same instance)
semantic_client = SemanticSearchClient()

class SearchQuery(BaseModel):
    """Model for semantic search requests"""
    query: str
    similarity_threshold: float = 0.5
    max_results: int = 5

class SearchResult(BaseModel):
    """Model for search results"""
    chunk_id: int
    chunk_text: str
    similarity: float
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    """Model for search response"""
    results: List[SearchResult]
    total_results: int
    query: str

@app.post("/api/search", response_model=SearchResponse)
async def semantic_search(search_request: SearchQuery):
    """
    Perform semantic search on the document chunks.
    
    Args:
        search_request (SearchQuery): The search request containing the query and parameters
        
    Returns:
        SearchResponse: The search results with metadata
    """
    try:
        # Perform the search
        results = semantic_client.search_similar(
            query_text=search_request.query,
            similarity_threshold=search_request.similarity_threshold,
            max_results=search_request.max_results
        )
        
        # Convert results to response model
        search_results = [
            SearchResult(
                chunk_id=result['chunk_id'],
                chunk_text=result['chunk_text'],
                similarity=result['similarity'],
                metadata=result['metadata']
            )
            for result in results
        ]
        
        return SearchResponse(
            results=search_results,
            total_results=len(search_results),
            query=search_request.query
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error performing semantic search: {str(e)}"
        )

@app.get("/")
async def root():
    """Root endpoint returning API information"""
    return {
        "name": "Aviaite API",
        "version": "1.0.0",
        "description": "API for aviation document search and analysis"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 