import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the server directory to Python path so we can import the postgres client
server_dir = Path(__file__).resolve().parents[2]
sys.path.append(str(server_dir))

# Load environment variables from .env file
load_dotenv(server_dir / '.env')

from src.postgres_client import PostgresClient

def main():
	pass

if __name__ == "__main__":
    main()
