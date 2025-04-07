import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import argparse
import PyPDF2
import re
import json
from typing import List, Dict, Optional, Tuple, Any
import mimetypes
from dataclasses import dataclass
import numpy as np
from sentence_transformers import SentenceTransformer

# Add the server directory to Python path so we can import the postgres client
server_dir = Path(__file__).resolve().parents[2]
sys.path.append(str(server_dir))

# Load environment variables from .env file
load_dotenv(server_dir / '.env')

from src.postgres_client import PostgresClient

@dataclass
class ProcessedDocument:
    """Class to hold processed document data and metadata"""
    chunks: List[str]  # The actual text chunks
    chunks_metadata: List[Dict[str, any]]  # Metadata for each chunk
    chunks_embeddings: List[np.ndarray]  # Embeddings for each chunk
    metadata: Dict[str, any]  # Metadata about the document
    original_file: Path  # Path to original file

def get_file_from_path(file_path: str) -> Path:
    """
    Validate and return a Path object for the given file path.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        Path: Validated Path object
        
    Raises:
        SystemExit: If file does not exist
    """
    path = Path(file_path)
    if not path.exists():
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    
    print(f"Found file: {path.absolute()}")
    return path

def print_file_size(file: Path) -> None:
	"""
	Print the file size in human readable format.
	
	Args:
		file (Path): Path object of the file
	"""
	file_size = file.stat().st_size
	
	# Convert to human readable format
	def convert_size(size_bytes):
		for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
			if size_bytes < 1024.0:
				return f"{size_bytes:.2f} {unit}"
			size_bytes /= 1024.0
	
	print(f"File size: {convert_size(file_size)}")
        
def extract_text_from_pdf(file_path: Path) -> Tuple[str, List[Dict[str, any]]]:
    """
    Extract text from a PDF file and track page information.
    
    Args:
        file_path (Path): Path to the PDF file
        
    Returns:
        Tuple[str, List[Dict[str, any]]]: Tuple containing:
            - Extracted text
            - List of page information dictionaries
    """
    text = ""
    page_info = []
    current_position = 0
    
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    # Store page information
                    page_info.append({
                        'page_number': page_num,
                        'start_char': current_position,
                        'end_char': current_position + len(page_text),
                        'page_size': page.mediabox,
                        'page_text_length': len(page_text)
                    })
                    # Add page text to full text
                    text += page_text + "\n"
                    current_position = len(text)
    except Exception as e:
        print(f"❌ Error extracting text from PDF: {e}")
        raise
    
    return text, page_info

def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text (str): Raw text to clean
        
    Returns:
        str: Cleaned text
    """
    # Replace multiple newlines with single newline
    text = re.sub(r'\n\s*\n', '\n', text)
    
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    
    return text.strip()

def get_page_info_for_chunk(start_char: int, end_char: int, page_info: List[Dict[str, any]]) -> Dict[str, any]:
    """
    Get page information for a specific chunk based on character positions.
    
    Args:
        start_char (int): Start character position of the chunk
        end_char (int): End character position of the chunk
        page_info (List[Dict[str, any]]): List of page information dictionaries
        
    Returns:
        Dict[str, any]: Dictionary containing page information for the chunk
    """
    chunk_pages = []
    chunk_page_ranges = []
    
    for page in page_info:
        page_start = page['start_char']
        page_end = page['end_char']
        
        # Check if chunk overlaps with this page
        if start_char < page_end and end_char > page_start:
            chunk_pages.append(page['page_number'])
            
            # Calculate the relative positions within the page
            chunk_start_in_page = max(0, start_char - page_start)
            chunk_end_in_page = min(page['page_text_length'], end_char - page_start)
            
            chunk_page_ranges.append({
                'page_number': page['page_number'],
                'start_in_page': chunk_start_in_page,
                'end_in_page': chunk_end_in_page,
                'page_text_length': page['page_text_length']
            })
    
    return {
        'pages': chunk_pages,
        'page_ranges': chunk_page_ranges,
        'spans_multiple_pages': len(chunk_pages) > 1
    }

def chunk_text(text: str, page_info: List[Dict[str, any]], chunk_size: int = 1000, overlap: int = 100) -> tuple[List[str], List[Dict[str, any]]]:
    """
    Split text into overlapping chunks and generate metadata for each chunk.
    
    Args:
        text (str): Text to split into chunks
        page_info (List[Dict[str, any]]): List of page information dictionaries
        chunk_size (int): Maximum size of each chunk
        overlap (int): Number of characters to overlap between chunks
        
    Returns:
        tuple[List[str], List[Dict[str, any]]]: Tuple containing:
            - List of text chunks
            - List of metadata dictionaries for each chunk
    """
    chunks = []
    chunks_metadata = []
    start = 0
    text_length = len(text)
    chunk_index = 0

    while start < text_length:
        # Find the end of the chunk
        end = start + chunk_size
        
        # If this is not the last chunk, try to break at a sentence boundary
        if end < text_length:
            # Look for sentence boundaries (., !, ?) within the overlap region
            overlap_start = end - overlap
            overlap_text = text[overlap_start:end]
            
            # Find the last sentence boundary in the overlap region
            matches = list(re.finditer(r'[.!?]\s', overlap_text))
            if matches:
                # Adjust end to the last sentence boundary found
                last_match = matches[-1]
                end = overlap_start + last_match.end()
        
        # Get the chunk text
        chunk_text = text[start:end].strip()
        
        # Get page information for this chunk
        page_info_for_chunk = get_page_info_for_chunk(start, end, page_info)
        
        # Create metadata for this chunk
        chunk_metadata = {
            'chunk_index': chunk_index,
            'start_char': start,
            'end_char': end,
            'chunk_size': len(chunk_text),
            'num_sentences': len(re.findall(r'[.!?]\s', chunk_text)) + 1,
            'num_words': len(chunk_text.split()),
            'is_first_chunk': chunk_index == 0,
            'is_last_chunk': end >= text_length,
            # Add page information
            'pages': page_info_for_chunk['pages'],
            'page_ranges': page_info_for_chunk['page_ranges'],
            'spans_multiple_pages': page_info_for_chunk['spans_multiple_pages']
        }
        
        # Add to our lists
        chunks.append(chunk_text)
        chunks_metadata.append(chunk_metadata)
        
        # Move the start pointer, ensuring we don't go backwards
        start = min(end, start + chunk_size - overlap)
        chunk_index += 1
    
    return chunks, chunks_metadata

def extract_metadata(file_path: Path) -> Dict[str, any]:
    """
    Extract metadata from the file.
    
    Args:
        file_path (Path): Path to the file
        
    Returns:
        Dict[str, any]: Dictionary containing metadata
    """
    metadata = {
        'filename': file_path.name,
        'file_size': file_path.stat().st_size,
        'file_type': mimetypes.guess_type(file_path)[0],
        'created_time': os.path.getctime(file_path),
        'modified_time': os.path.getmtime(file_path)
    }
    
    # If it's a PDF, extract PDF-specific metadata
    if metadata['file_type'] == 'application/pdf':
        try:
            with open(file_path, 'rb') as file:
                pdf = PyPDF2.PdfReader(file)
                if pdf.metadata:
                    metadata.update({
                        'title': pdf.metadata.get('/Title', ''),
                        'author': pdf.metadata.get('/Author', ''),
                        'subject': pdf.metadata.get('/Subject', ''),
                        'creator': pdf.metadata.get('/Creator', ''),
                        'page_count': len(pdf.pages)
                    })
        except Exception as e:
            print(f"Warning: Could not extract PDF metadata: {e}")
    
    return metadata

def generate_embeddings(chunks: List[str], model_name: str = 'BAAI/bge-large-en-v1.5') -> List[np.ndarray]:
    """
    Generate embeddings for text chunks using sentence-transformers.
    The BAAI/bge-large-en-v1.5 model produces 1024-dimensional embeddings,
    which we pad to 1536 dimensions to match OpenAI's format.
    
    Args:
        chunks (List[str]): List of text chunks to embed
        model_name (str): Name of the sentence-transformers model to use
        
    Returns:
        List[np.ndarray]: List of embeddings as numpy arrays with 1536 dimensions
    """
    model = SentenceTransformer(model_name)
    embeddings = model.encode(chunks, show_progress_bar=True)
    
    # Pad embeddings from 1024 to 1536 dimensions
    padded_embeddings = []
    for embedding in embeddings:
        # Normalize the original embedding
        normalized = embedding / np.linalg.norm(embedding)
        # Pad with zeros to reach 1536 dimensions
        padded = np.pad(normalized, (0, 1536 - len(normalized)), 'constant')
        # Normalize again to ensure unit length
        padded = padded / np.linalg.norm(padded)
        padded_embeddings.append(padded)
    
    return padded_embeddings

def preprocess_document(file_path: Path, chunk_size: int = 1000, overlap: int = 100) -> ProcessedDocument:
    """
    Preprocess a document for RAG.
    
    Args:
        file_path (Path): Path to the document
        chunk_size (int): Size of text chunks
        overlap (int): Overlap between chunks
        
    Returns:
        ProcessedDocument: Processed document with chunks and metadata
    """
    # Extract text based on file type
    mime_type = mimetypes.guess_type(file_path)[0]
    
    if mime_type == 'application/pdf':
        text, page_info = extract_text_from_pdf(file_path)
    else:
        raise ValueError(f"Unsupported file type: {mime_type}")
    
    # Clean the text
    cleaned_text = clean_text(text)
    
    # Split into chunks and get chunk metadata
    chunks, chunks_metadata = chunk_text(cleaned_text, page_info, chunk_size, overlap)
    
    # Generate embeddings for chunks
    print("Generating embeddings...")
    chunks_embeddings = generate_embeddings(chunks)
    print(f"Generated {len(chunks_embeddings)} embeddings of dimension {chunks_embeddings[0].shape[0]}")
    
    # Extract metadata
    metadata = extract_metadata(file_path)
    
    return ProcessedDocument(
        chunks=chunks,
        chunks_metadata=chunks_metadata,
        chunks_embeddings=chunks_embeddings,
        metadata=metadata,
        original_file=file_path
    )
        
def save_chunks_to_db(processed_doc: ProcessedDocument, postgres_client: PostgresClient) -> None:
    """
    Save chunks and their metadata to the database.
    
    Args:
        processed_doc (ProcessedDocument): Processed document containing chunks and metadata
        postgres_client (PostgresClient): PostgreSQL client instance
    """
    try:
        # Prepare values for insertion - convert metadata to JSON string and embeddings to list
        values = [
            (chunk, json.dumps(metadata), embedding.tolist()) 
            for chunk, metadata, embedding in zip(
                processed_doc.chunks, 
                processed_doc.chunks_metadata, 
                processed_doc.chunks_embeddings
            )
        ]
        
        # SQL query template
        insert_query = """
            INSERT INTO chunks (chunk_text, metadata, embedding)
            VALUES %s
        """
        
        # Template for execute_values - using positional parameters for 1536-dimensional vectors
        template = "(%s, %s::jsonb, %s::vector(1536))"
        
        postgres_client.execute_values(insert_query, values, template=template)
        print(f"✅ Successfully saved {len(values)} chunks to database")
    except Exception as e:
        print(f"❌ Error saving chunks to database: {e}")
        raise

def main(file_path: str):
    """
    Process and upload a file to PostgreSQL.
    
    Args:
        file_path (str): Path to the file to be processed and uploaded
    """
    file = get_file_from_path(file_path)
    print_file_size(file)
    
    try:
        # Preprocess the document
        processed_doc = preprocess_document(file)
        
        # Print some stats
        print(f"\nPreprocessing complete:")
        print(f"- Number of chunks: {len(processed_doc.chunks)}")
        print(f"- Average chunk size: {sum(len(c) for c in processed_doc.chunks) / len(processed_doc.chunks):.0f} characters")
        print(f"- Metadata extracted: {list(processed_doc.metadata.keys())}")
        print(f"- Chunk metadata includes: {list(processed_doc.chunks_metadata[0].keys())}")
        
        # Save chunks to database
        postgres_client = PostgresClient()
        save_chunks_to_db(processed_doc, postgres_client)
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process and upload a file to PostgreSQL')
    parser.add_argument('--file_path', type=str, help='Path to the file to be processed and uploaded', default='C:/Users/asafk/Downloads/NAT DOC 007_Eff.20MAR2025.pdf')
    
    args = parser.parse_args()
    main(args.file_path)
