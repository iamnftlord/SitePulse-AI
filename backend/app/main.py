import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("sitepulse.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("=" * 60)
    logger.info(f" Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f" Environment: {settings.ENVIRONMENT} | Debug: {settings.DEBUG}")
    logger.info(f" Ollama URL: {settings.OLLAMA_BASE_URL} (Model: {settings.OLLAMA_MODEL})")
    logger.info(f" Docs available at: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info("=" * 60)
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "SitePulse AI - An intelligent developer tool & assistant that crawls websites, "
        "identifies technical defects across SEO, Security, Performance, and Accessibility, "
        "and generates prioritized AI-powered remediation plans using Ollama & open-weight LLMs."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router)
from app.api.routes import analyze_website
app.add_api_route("/api/audit", analyze_website, methods=["POST"], include_in_schema=False)


@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint providing service overview and documentation links."""
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "Website Intelligence & Technical Problem Analyzer Assistant",
        "documentation": "/docs",
        "health_check": f"{settings.API_V1_PREFIX}/health",
        "status": "online",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
