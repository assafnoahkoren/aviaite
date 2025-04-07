import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Union
from pathlib import Path
import os
import sys
from dotenv import load_dotenv

# Add the server directory to Python path for direct script execution
server_dir = Path(__file__).resolve().parent.parent
if str(server_dir) not in sys.path:
    sys.path.append(str(server_dir))

class EmbeddingManager:
    """Manager class for generating and processing embeddings."""
    
    def __init__(self, model_name: str = 'BAAI/bge-large-en-v1.5', embedding_dim: int = 1536):
        """
        Initialize the EmbeddingManager.
        
        Args:
            model_name (str): Name of the sentence-transformers model to use
            embedding_dim (int): Target dimension for embeddings (padding if necessary)
        """
        self.model = SentenceTransformer(model_name)
        self.original_dim = self.model.get_sentence_embedding_dimension()
        self.embedding_dim = embedding_dim
        
        if self.original_dim > self.embedding_dim:
            raise ValueError(f"Model dimension ({self.original_dim}) cannot be larger than target dimension ({self.embedding_dim})")
            
        print(f"Initialized EmbeddingManager with model {model_name}")
        print(f"Original dimension: {self.original_dim}, Target dimension: {self.embedding_dim}")
    
    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """
        Normalize a vector to unit length.
        
        Args:
            vector (np.ndarray): Vector to normalize
            
        Returns:
            np.ndarray: Normalized vector
        """
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm
    
    def _pad_embedding(self, embedding: np.ndarray) -> np.ndarray:
        """
        Pad an embedding to the target dimension.
        
        Args:
            embedding (np.ndarray): Original embedding
            
        Returns:
            np.ndarray: Padded embedding
        """
        if len(embedding) == self.embedding_dim:
            return self._normalize_vector(embedding)
            
        # Normalize original embedding
        normalized = self._normalize_vector(embedding)
        
        # Pad with zeros
        padded = np.pad(normalized, (0, self.embedding_dim - len(normalized)), 'constant')
        
        # Normalize again to ensure unit length
        return self._normalize_vector(padded)
    
    def generate_embedding(self, text: Union[str, List[str]], show_progress: bool = False) -> Union[np.ndarray, List[np.ndarray]]:
        """
        Generate embeddings for one or more texts.
        
        Args:
            text (Union[str, List[str]]): Text or list of texts to embed
            show_progress (bool): Whether to show progress bar for batch processing
            
        Returns:
            Union[np.ndarray, List[np.ndarray]]: Single embedding or list of embeddings
        """
        # Generate embeddings
        embeddings = self.model.encode(text, show_progress_bar=show_progress)
        
        # Handle single text case
        if isinstance(text, str):
            return self._pad_embedding(embeddings)
        
        # Handle multiple texts
        return [self._pad_embedding(emb) for emb in embeddings]
    
    def embeddings_to_list(self, embeddings: Union[np.ndarray, List[np.ndarray]]) -> Union[List[float], List[List[float]]]:
        """
        Convert numpy array embeddings to lists for database storage.
        
        Args:
            embeddings (Union[np.ndarray, List[np.ndarray]]): Embeddings to convert
            
        Returns:
            Union[List[float], List[List[float]]]: Embeddings as lists
        """
        if isinstance(embeddings, np.ndarray) and embeddings.ndim == 1:
            return embeddings.tolist()
        return [emb.tolist() for emb in embeddings]

# Example usage
if __name__ == "__main__":
    # Test the embedding manager
    manager = EmbeddingManager()
    
    # Test single text
    text = "This is a test sentence."
    embedding = manager.generate_embedding(text)
    print(f"\nSingle text embedding shape: {embedding.shape}")
    print(f"Is normalized: {abs(np.linalg.norm(embedding) - 1.0) < 1e-6}")
    
    # Test multiple texts
    texts = ["First sentence.", "Second sentence.", "Third sentence."]
    embeddings = manager.generate_embedding(texts, show_progress=True)
    print(f"\nMultiple text embeddings count: {len(embeddings)}")
    print(f"Each embedding shape: {embeddings[0].shape}")
    print(f"All normalized: {all(abs(np.linalg.norm(emb) - 1.0) < 1e-6 for emb in embeddings)}") 