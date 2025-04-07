import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, List, Any

class PostgresClient:
    def __init__(self, 
                 host: str = os.getenv('POSTGRES_HOST', 'localhost'),
                 port: int = int(os.getenv('POSTGRES_PORT', '5432')),
                 database: str = os.getenv('POSTGRES_DB', 'postgres'),
                 user: str = os.getenv('POSTGRES_USER', 'postgres'),
                 password: str = os.getenv('POSTGRES_PASSWORD', '')):
        self.connection_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        self.conn = None
        self.cursor = None

    def connect(self) -> None:
        """Establish connection to the PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        except Exception as e:
            raise Exception(f"Error connecting to PostgreSQL database: {str(e)}")

    def disconnect(self) -> None:
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute a query and return the results.
        
        Args:
            query (str): SQL query to execute
            params (tuple, optional): Query parameters
            
        Returns:
            List[Dict[str, Any]]: Query results as a list of dictionaries
        """
        try:
            if not self.conn or self.conn.closed:
                self.connect()
            
            self.cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                return self.cursor.fetchall()
            else:
                self.conn.commit()
                return []
                
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            raise Exception(f"Error executing query: {str(e)}")

    def __enter__(self):
        """Context manager enter method."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit method."""
        self.disconnect()

# Example usage:
# with PostgresClient() as db:
#     results = db.execute_query("SELECT * FROM your_table WHERE column = %s", ('value',)) 