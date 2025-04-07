import os
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from typing import Optional, Dict, List, Any, Sequence

class PostgresClient:
    def __init__(self, 
                 host: str = os.getenv('POSTGRES_HOST', 'localhost'),
                 port: int = int(os.getenv('POSTGRES_PORT', '5432')),
                 database: str = os.getenv('POSTGRES_DB', 'aviaite'),
                 user: str = os.getenv('POSTGRES_USER', 'postgres'),
                 password: str = os.getenv('POSTGRES_PASSWORD', 'postgres')):
        self.connection_params = {
            'host': 'ep-winter-darkness-a2mwfp0o-pooler.eu-central-1.aws.neon.tech',
            'port': '5432',
            'database': 'aviaite',
            'user': 'aviaite_owner',
            'password': 'npg_cYwGqZV4ku1C'
        }
        self.conn = None
        self.cursor = None

    def connect(self) -> None:
        """Establish connection to the PostgreSQL database."""
        try:
            # Print connection string (without password)
            safe_params = self.connection_params.copy()
            safe_params['password'] = '***' if safe_params['password'] else ''
            print(f"Connecting to PostgreSQL database: postgresql://{safe_params['user']}:{safe_params['password']}@{safe_params['host']}:{safe_params['port']}/{safe_params['database']}")
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

    def execute_values(self, query: str, values: Sequence[tuple], template: Optional[str] = None, page_size: int = 100) -> None:
        """
        Execute a query with multiple rows of values using psycopg2.extras.execute_values.
        
        Args:
            query (str): SQL query template with %s for the values clause
            values (Sequence[tuple]): Sequence of value tuples to insert
            template (str, optional): Optional template string for formatting values
            page_size (int): Number of rows to insert in each batch
        """
        try:
            if not self.conn or self.conn.closed:
                self.connect()
            
            execute_values(self.cursor, query, values, template, page_size)
            self.conn.commit()
                
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            raise Exception(f"Error executing values: {str(e)}")

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
#     # For bulk inserts:
#     db.execute_values("INSERT INTO table (col1, col2) VALUES %s", [(1, 'a'), (2, 'b')]) 