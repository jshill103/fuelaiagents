# app/main.py

from fastapi import FastAPI

from app.routes.health import router as health_router
from app.routes.discovery import router as discovery_router
from app.routes.sources import router as sources_router

app = FastAPI()

app.include_router(health_router)
app.include_router(discovery_router)
app.include_router(sources_router)