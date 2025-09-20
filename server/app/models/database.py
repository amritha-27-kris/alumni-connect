import pymysql
import os
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DATABASE_HOST', 'localhost'),
    'user': os.environ.get('DATABASE_USER', 'root'),
    'password': os.environ.get('DATABASE_PASSWORD', ''),
    'database': os.environ.get('DATABASE_NAME', 'alumni_connect'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    'autocommit': True
}

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    connection = None
    try:
        connection = pymysql.connect(**DB_CONFIG)
        yield connection
    except Exception as e:
        if connection:
            connection.rollback()
        raise e
    finally:
        if connection:
            connection.close()

def execute_query(query, params=None, fetch_one=False, fetch_all=True):
    """Execute a database query and return results"""
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith('SELECT'):
                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
            else:
                connection.commit()
                return cursor.lastrowid if query.strip().upper().startswith('INSERT') else cursor.rowcount

def execute_many(query, params_list):
    """Execute a query with multiple parameter sets"""
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.executemany(query, params_list)
            connection.commit()
            return cursor.rowcount