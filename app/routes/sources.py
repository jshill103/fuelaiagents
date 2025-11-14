# app/routes/sources.py

from typing import Dict, Any, List
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.sources_service import create_source, list_sources

router = APIRouter(prefix="/sources", tags=["sources"])


class SourceCreateRequest(BaseModel):
    platform: str
    handle: str
    is_competitor: bool = False
    fetch_schedule: str = "daily"


@router.post("", response_model=Dict[str, Any])
def create_source_route(body: SourceCreateRequest):
    """
    Approve/add a source (e.g. from the discovery suggestions).
    """
    source_id = create_source(
        platform=body.platform,
        handle=body.handle,
        is_competitor=body.is_competitor,
        fetch_schedule=body.fetch_schedule,
    )
    return {
        "id": source_id,
        "platform": body.platform,
        "handle": body.handle,
        "is_competitor": body.is_competitor,
        "fetch_schedule": body.fetch_schedule,
    }


@router.get("", response_model=List[Dict[str, Any]])
def list_sources_route():
    return list_sources()


@router.delete("/{source_id}")
def delete_source_route(source_id: str):
    """
    Delete a source and all its associated posts.
    """
    import psycopg2
    
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="asa",
        user="postgres",
        password="postgres",
    )
    cur = conn.cursor()
    
    # Check if source exists
    cur.execute("SELECT handle FROM sources WHERE id = %s", (source_id,))
    row = cur.fetchone()
    
    if not row:
        cur.close()
        conn.close()
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Source not found")
    
    handle = row[0]
    
    # Delete source (cascade will delete posts)
    cur.execute("DELETE FROM sources WHERE id = %s", (source_id,))
    conn.commit()
    
    cur.close()
    conn.close()
    
    return {"success": True, "deleted_handle": handle}