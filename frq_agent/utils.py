import sqlite3
from typing import List, Tuple, Any
from contextlib import contextmanager

@contextmanager
def database_connection(db_path: str):
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()

def execute_query(db_path: str, query: str, params: tuple = ()) -> List[Tuple[Any, ...]]:
    """Execute SQL query and return results.
    
    Args:
        db_path: Path to SQLite database
        query: SQL query string
        params: Query parameters (optional)
        
    Returns:
        List of query results as tuples
    """
    with database_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()