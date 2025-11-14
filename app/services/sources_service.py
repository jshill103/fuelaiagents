# app/services/sources_service.py

from typing import Optional, List, Dict, Any

from app.db.connection import get_db_cursor


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
    with get_db_cursor() as cur:
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
            return str(row[0])

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
        return str(source_id)


def list_sources() -> List[Dict[str, Any]]:
    """
    Simple helper to list all sources (for debugging / UI later).
    """
    with get_db_cursor() as cur:
        cur.execute(
            """
            select id, platform, handle, is_competitor, fetch_schedule
            from sources
            order by platform, handle
            """
        )
        rows = cur.fetchall()

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


def delete_source(source_id: str) -> Optional[str]:
    """
    Delete a source and all its associated posts (via cascade).
    
    Returns:
        The handle of the deleted source, or None if not found.
    """
    with get_db_cursor() as cur:
        # Check if source exists
        cur.execute("SELECT handle FROM sources WHERE id = %s", (source_id,))
        row = cur.fetchone()
        
        if not row:
            return None
        
        handle = row[0]
        
        # Delete source (cascade will delete posts)
        cur.execute("DELETE FROM sources WHERE id = %s", (source_id,))
        
        return handle