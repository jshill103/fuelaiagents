# app/routes/sources.py

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.sources_service import create_source, list_sources, delete_source

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
    result = delete_source(source_id)
    if not result:
        raise HTTPException(status_code=404, detail="Source not found")
    return {"success": True, "deleted_handle": result}