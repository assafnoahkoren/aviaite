import numpy as np
from typing import List, Dict, Any
import json
import sys
from pathlib import Path

# Add the server directory to Python path for direct script execution
server_dir = Path(__file__).resolve().parent.parent
if str(server_dir) not in sys.path:
    sys.path.append(str(server_dir))

try:
    # Try relative import (when used as a module)
    from .postgres_client import PostgresClient
    from .embedding_manager import EmbeddingManager
except ImportError:
    # Fall back to absolute import (when run as a script)
    from src.postgres_client import PostgresClient
    from src.embedding_manager import EmbeddingManager

class SemanticSearchClient:
    """Client for performing semantic search on the database."""

    def __init__(self, model_name: str = 'BAAI/bge-large-en-v1.5', embedding_dim: int = 1536):
        """
        Initialize the SemanticSearchClient.

        Args:
            model_name (str): Name of the sentence-transformers model to use.
            embedding_dim (int): Target dimension for embeddings.
        """
        self.embedding_manager = EmbeddingManager(model_name, embedding_dim)
        
        self.postgres_client = PostgresClient()  # Assumes default connection settings from .env

    def search_similar(self, query_text: str, similarity_threshold: float = 0.5, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for chunks similar to the query text.

        Args:
            query_text (str): The text to search for.
            similarity_threshold (float): Minimum similarity score (cosine similarity) to include.
            max_results (int): Maximum number of results to return.

        Returns:
            List[Dict[str, Any]]: List of similar chunks found in the database.
        """
        print(f"Generating embedding for query: '{query_text[:50]}...'")
        query_embedding = self.embedding_manager.generate_embedding(query_text)
        
        # Convert numpy array to list for SQL query parameter
        query_embedding_list = self.embedding_manager.embeddings_to_list(query_embedding)

        sql_query = """
            SELECT * FROM search_similar_chunks(%s::vector, %s::float, %s::integer);
        """
        
        params = (query_embedding_list, similarity_threshold, max_results)
        
        print(f"Searching database with threshold={similarity_threshold}, max_results={max_results}")
        try:
            with self.postgres_client as db:
                results = db.execute_query(sql_query, params)
            print(f"Found {len(results)} similar chunks.")
            return results
        except Exception as e:
            print(f"❌ Error during database search: {e}")
            return []

# Example Usage (can be run directly for testing)
if __name__ == '__main__':
    # Make sure .env is loaded if running directly
    from dotenv import load_dotenv
    from pathlib import Path
    server_dir = Path(__file__).resolve().parents[1]  # Go up one level to server dir
    load_dotenv(server_dir / '.env')

    search_client = SemanticSearchClient()
    
    test_query = "What are the hours for the westbound tracks?"
    similar_chunks = search_client.search_similar(test_query, similarity_threshold=0.6, max_results=5)
    
    if similar_chunks:
        print("\n--- Top Similar Chunks ---")
        for i, chunk in enumerate(similar_chunks):
            print(f"\nResult {i+1} (Similarity: {chunk['similarity']:.4f}):")
            print(f"Chunk ID: {chunk['chunk_id']}")
            # Pretty print metadata
            pages = chunk['metadata']['pages']
            print(f"Pages: {pages}")
            print(f"Text: {chunk['chunk_text'][:300]}...")
    else:
        print("No similar chunks found.") 