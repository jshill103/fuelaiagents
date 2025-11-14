# app/main.py

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.routes.health import router as health_router
from app.routes.discovery import router as discovery_router
from app.routes.sources import router as sources_router
from app.routes.dashboard import router as dashboard_router
from app.routes.scheduled import router as scheduled_router

app = FastAPI(title="FuelAI Agents", version="1.0.0")

app.include_router(health_router)
app.include_router(discovery_router)
app.include_router(sources_router)
app.include_router(dashboard_router)
app.include_router(scheduled_router)


@app.get("/")
def root():
    """Redirect to dashboard."""
    return RedirectResponse(url="/dashboard")