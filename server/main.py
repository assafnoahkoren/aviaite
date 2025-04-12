import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any
from src.semantic_search import SemanticSearchClient
from anthropic import Anthropic
import json
from dotenv import load_dotenv
from src.ask_your_pdf_client import AskYourPdfClient

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
load_dotenv()
print(f"Anthropic API Key: {os.getenv('ANTHROPIC_API_KEY')}")
anthropic_client = Anthropic(
    api_key=os.getenv('ANTHROPIC_API_KEY')
)

# Initialize AskYourPdf client
ask_your_pdf_client = AskYourPdfClient()

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
    analysis: Dict[str, Any]

class KnowledgeBaseQuery(BaseModel):
    """Model for knowledge base queries"""
    query: str
    temperature: float = 0.7
    language: str = "ENGLISH"
    length: str = "SHORT"

@app.post("/api/search", response_model=SearchResponse)
async def semantic_search(search_request: SearchQuery):
    """
    Perform semantic search on the document chunks and analyze results using Claude.
    
    Args:
        search_request (SearchQuery): The search request containing the query and parameters
        
    Returns:
        SearchResponse: The search results with metadata and Claude's analysis
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

        # Prepare context for Claude
        context = "\n\n".join([
            f"Document {r.chunk_id} (similarity: {r.similarity:.2f}):\n{r.chunk_text}"
            for r in search_results
        ])
        
        # Get analysis from Claude
        message = anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0.2,
            messages=[{
                "role": "user",
                "content": f"""Based on the following search results for the query "{search_request.query}",
                formart the answer like this:
                {{
                    "answer": string,
                }}
                provide a concise (4 lines maximum, 2 lines is ideal) analysis and summary of the relevant information (PLEASE GIVEN BACK THE ANSWER WITHOUT ANY OTHER TEXT) :

                {context}"""
            }]
        )
        
        # Extract the text content from Claude's response
        try:
            analysis_json = json.loads(message.content[0].text) if message.content else {"answer": "No analysis available", "chunk_ids": []}
        except json.JSONDecodeError:
            analysis_text = "Error parsing analysis response"
        
        return SearchResponse(
            results=search_results,
            total_results=len(search_results),
            query=search_request.query,
            analysis=analysis_json
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error performing semantic search: {str(e)}"
        )

@app.post("/api/ask")
async def ask_knowledge_base(query: KnowledgeBaseQuery):
    """
    Query the knowledge base.
    
    Args:
        query (KnowledgeBaseQuery): The query containing the question and parameters
        
    Returns:
        str: The complete response from the knowledge base
    """
    try:
        response = ask_your_pdf_client.ask_knowledge_base(
            query=query.query,
            temperature=0.7,
            language="ENGLISH",
            length="SHORT"
        )
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error querying knowledge base: {str(e)}"
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

    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 