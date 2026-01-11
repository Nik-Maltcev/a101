"""FastAPI application entry point."""

import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.jobs import router as jobs_router
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Set log level for our app modules
logging.getLogger("app").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Defect Classifier",
    description="Сервис для автоматической обработки Excel-файлов с комментариями о дефектах",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(jobs_router)

# Mount static files
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")


@app.get("/")
async def root():
    """Root endpoint - serve the web UI."""
    return FileResponse(settings.STATIC_DIR / "index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    logger.info("Application starting up...")
    logger.info(f"LLM API URL: {settings.LLM_API_URL}")
    logger.info(f"LLM Model: {settings.LLM_MODEL}")
    logger.info(f"API Key configured: {'Yes' if settings.LLM_API_KEY else 'No'}")
