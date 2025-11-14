# app/db/connection.py
"""
Centralized database connection management with proper error handling.
"""

import os
import psycopg2
from contextlib import contextmanager
from typing import Generator


def get_db_config() -> dict:
    """Get database configuration from environment or defaults."""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", 5432)),
        "dbname": os.getenv("DB_NAME", "asa"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "postgres"),
    }


def get_db_connection():
    """
    Create a database connection with proper configuration.
    
    Raises:
        psycopg2.Error: If connection fails
    """
    config = get_db_config()
    return psycopg2.connect(**config)


@contextmanager
def get_db_cursor() -> Generator:
    """
    Context manager for database operations with automatic cleanup.
    
    Usage:
        with get_db_cursor() as cur:
            cur.execute("SELECT * FROM sources")
            results = cur.fetchall()
    
    Automatically commits on success and closes connection on exit.
    Rolls back on exception.
    """
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

