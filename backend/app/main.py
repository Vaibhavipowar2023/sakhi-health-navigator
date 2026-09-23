"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import router
from backend.app.db.engine import init_db


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Create indexes on startup, nothing special on shutdown."""
    init_db()
    yield


app = FastAPI(
    title="Sakhi Health Navigator",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
