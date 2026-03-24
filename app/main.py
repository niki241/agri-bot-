import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routes.webhook import router as webhook_router
from app.routes.advisory import router as advisory_router
from app.routes.admin import router as admin_router
from app.services.ollama_client import check_ollama_health

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("🌾 Kisan Mitra starting up...")

    # Initialize database tables
    await init_db()
    logger.info("✅ Database tables initialized")

    # Check Ollama
    ollama_ok = await check_ollama_health()
    if ollama_ok:
        logger.info("✅ Ollama is available")
    else:
        logger.warning("⚠️ Ollama is NOT reachable — will use fallback responses")

    yield

    logger.info("🌾 Kisan Mitra shutting down...")


app = FastAPI(
    title="Kisan Mitra — Agri Advisory Bot",
    description="WhatsApp-first AI crop advisory for Indian farmers in Telugu & Hindi",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(webhook_router)
app.include_router(advisory_router)
app.include_router(admin_router)


@app.get("/health")
async def health_check():
    ollama_ok = await check_ollama_health()
    return {
        "status": "healthy",
        "service": "kisan-mitra",
        "ollama": "connected" if ollama_ok else "disconnected",
    }
