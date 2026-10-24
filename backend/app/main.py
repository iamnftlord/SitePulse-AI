import logging
import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router, analyze_website
from app.core.config import settings
from app.core.rate_limiter import RateLimitMiddleware
from app.core.security import SSRFValidationError

# Configure structured logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("sitepulse.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle management."""
    logger.info("=" * 60)
    logger.info(f" Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f" Environment: {settings.ENVIRONMENT} | Debug: {settings.DEBUG}")
    logger.info(f" Rate Limiting: {'Enabled (' + str(settings.RATE_LIMIT_PER_MINUTE) + '/min)' if settings.RATE_LIMIT_ENABLED else 'Disabled'}")
    logger.info(f" SSRF Private IPs: {'Allowed (Dev Mode)' if settings.ALLOW_PRIVATE_IPS else 'Blocked (Production Mode)'}")
    logger.info(f" Ollama URL: {settings.OLLAMA_BASE_URL} (Model: {settings.OLLAMA_MODEL})")
    logger.info(f" Docs available at: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info("=" * 60)
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME} gracefully...")


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

# 1. Tracing & Performance Middleware
@app.middleware("http")
async def request_tracing_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    start_time = time.perf_counter()

    response: Response = await call_next(request)

    process_time = round((time.perf_counter() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = str(process_time)
    return response


# 2. Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware)

# 3. CORS Middleware
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time-Ms", "Retry-After"],
)

# Global Exception Handlers
@app.exception_handler(SSRFValidationError)
async def ssrf_exception_handler(request: Request, exc: SSRFValidationError):
    logger.warning(f"SSRF violation blocked from {request.client.host if request.client else 'unknown'}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "SecurityValidationError",
            "detail": f"Target URL failed security verification: {str(exc)}",
            "type": "ssrf_violation",
        },
    )


# Register API Routes
app.include_router(router)
app.add_api_route("/api/audit", analyze_website, methods=["POST"], include_in_schema=False)


# Health and Liveness Probes
@app.get("/healthz", tags=["System"])
async def liveness_probe():
    """Lightweight Kubernetes/Docker container liveness probe."""
    return {"status": "ok", "timestamp": time.time()}


@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint providing service overview and documentation links."""
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "Website Intelligence & Technical Problem Analyzer Assistant",
        "documentation": "/docs",
        "health_check": f"{settings.API_V1_PREFIX}/health",
        "liveness": "/healthz",
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
