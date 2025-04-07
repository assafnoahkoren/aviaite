import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import argparse
import PyPDF2
import re
from typing import List, Dict, Optional
import mimetypes
from dataclasses import dataclass

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
        
def extract_text_from_pdf(file_path: Path) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        file_path (Path): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"❌ Error extracting text from PDF: {e}")
        raise
    return text

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

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text (str): Text to split into chunks
        chunk_size (int): Maximum size of each chunk
        overlap (int): Number of characters to overlap between chunks
        
    Returns:
        List[str]: List of text chunks
    """
    chunks = []
    start = 0
    text_length = len(text)

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
        
        # Add the chunk to our list
        chunks.append(text[start:end].strip())
        
        # Move the start pointer, ensuring we don't go backwards
        start = min(end, start + chunk_size - overlap)
    
    return chunks

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
        text = extract_text_from_pdf(file_path)
    else:
        raise ValueError(f"Unsupported file type: {mime_type}")
    
    # Clean the text
    cleaned_text = clean_text(text)
    
    # Split into chunks
    chunks = chunk_text(cleaned_text, chunk_size, overlap)
    
    # Extract metadata
    metadata = extract_metadata(file_path)
    
    return ProcessedDocument(
        chunks=chunks,
        metadata=metadata,
        original_file=file_path
    )
        
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
        
        # TODO: Add embedding generation and database upload
        
    except Exception as e:
        print(f"❌ Error during preprocessing: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process and upload a file to PostgreSQL')
    parser.add_argument('--file_path', type=str, help='Path to the file to be processed and uploaded', default='C:/Users/asafk/Downloads/NAT DOC 007_Eff.20MAR2025.pdf')
    
    args = parser.parse_args()
    main(args.file_path)
