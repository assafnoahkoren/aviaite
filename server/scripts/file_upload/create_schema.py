import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
import sys

# Add the server directory to Python path so we can import the postgres client
server_dir = Path(__file__).resolve().parents[2]
sys.path.append(str(server_dir))

# Load environment variables from .env file
load_dotenv(server_dir / '.env')

def create_schema():
    """Create the database schema."""
    # Read the schema file
    schema_file = Path(__file__).parent / 'schema.sql'
    with open(schema_file, 'r') as f:
        schema_sql = f.read()
    
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_PORT', '5432')),
        database=os.getenv('POSTGRES_DB', 'aviaite'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'postgres')
    )
    
    # Create a cursor
    cur = conn.cursor()
    
    try:
        # Execute the schema SQL
        cur.execute(schema_sql)
        conn.commit()
        print("✅ Successfully created database schema")
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_schema() 