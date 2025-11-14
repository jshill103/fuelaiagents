# app/services/sources_service.py

from typing import Optional, List, Dict, Any
import psycopg2


def _get_db_conn():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="asa",
        user="postgres",
        password="postgres",
    )


def create_source(
    platform: str,
    handle: str,
    is_competitor: bool = False,
    fetch_schedule: str = "daily",
) -> str:
    """
    Insert a new row into the sources table, or return the existing id
    if a row with the same (platform, handle) already exists.
    """
    conn = _get_db_conn()
    cur = conn.cursor()

    # Check if it already exists
    cur.execute(
        """
        select id
        from sources
        where platform = %s and handle = %s
        """,
        (platform, handle),
    )
    row = cur.fetchone()
    if row:
        source_id = row[0]
        cur.close()
        conn.close()
        return str(source_id)

    # Insert new
    cur.execute(
        """
        insert into sources (platform, handle, is_competitor, fetch_schedule)
        values (%s, %s, %s, %s)
        returning id
        """,
        (platform, handle, is_competitor, fetch_schedule),
    )
    source_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return str(source_id)


def list_sources() -> List[Dict[str, Any]]:
    """
    Simple helper to list all sources (for debugging / UI later).
    """
    conn = _get_db_conn()
    cur = conn.cursor()
    cur.execute(
        """
        select id, platform, handle, is_competitor, fetch_schedule
        from sources
        order by platform, handle
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "id": str(r[0]),
            "platform": r[1],
            "handle": r[2],
            "is_competitor": r[3],
            "fetch_schedule": r[4],
        }
        for r in rows
    ]