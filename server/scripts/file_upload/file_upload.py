import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import argparse

# Add the server directory to Python path so we can import the postgres client
server_dir = Path(__file__).resolve().parents[2]
sys.path.append(str(server_dir))

# Load environment variables from .env file
load_dotenv(server_dir / '.env')

from src.postgres_client import PostgresClient

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

def main(file_path: str):
    """
    Process and upload a file to PostgreSQL.
    
    Args:
        file_path (str): Path to the file to be processed and uploaded
    """
    file = get_file_from_path(file_path)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process and upload a file to PostgreSQL')
    parser.add_argument('file_path', type=str, help='Path to the file to be processed and uploaded')
    
    args = parser.parse_args()
    main(args.file_path)
