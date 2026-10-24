import logging
import time
from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.core.security import SSRFValidationError
from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    ChatRequest,
    ChatResponse,
    HealthResponse,
)
from app.services.ai_advisor import ai_advisor
from app.services.auditor import Auditor
from app.services.crawler import WebsiteCrawler

logger = logging.getLogger(__name__)

router = APIRouter(prefix=settings.API_V1_PREFIX)


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Returns system status, active version, and Ollama engine connectivity."""
    ollama_info = await ai_advisor.check_health()
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        ollama_connected=ollama_info["connected"],
        ollama_url=settings.OLLAMA_BASE_URL,
        active_model=ollama_info["active_model"],
        available_models=ollama_info["available_models"],
    )


@router.get("/models", tags=["AI Engine"])
async def list_models():
    """Lists available open-weight models detected in local Ollama service."""
    ollama_info = await ai_advisor.check_health()
    return {
        "connected": ollama_info["connected"],
        "active_model": ollama_info["active_model"],
        "available_models": ollama_info["available_models"],
    }


@router.post("/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
@router.post("/audit", response_model=AnalyzeResponse, tags=["Analysis"])
async def analyze_website(request: AnalyzeRequest):
    """
    Performs full website analysis:
    1. Asynchronous crawl & metadata extraction
    2. Technology detection (CMS, frameworks, servers)
    3. Multi-domain audit (SEO, Security, Performance, Accessibility)
    4. Deterministic score calculation & letter grading
    5. Ollama open-weight AI synthesis with prioritized action plan
    """
    start_time = time.perf_counter()
    crawler = WebsiteCrawler()

    try:
        metadata, soup, html_text = await crawler.fetch_page(request.url)
    except SSRFValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Security Policy Violation: {str(exc)}",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Crawling failed: {str(exc)}",
        )
    except Exception as exc:
        logger.error(f"Unexpected crawler error for {request.url}: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while inspecting the target website: {str(exc)}",
        )

    # Deterministic technical audit
    issues, category_scores, overall_score, overall_grade = Auditor.audit(
        metadata=metadata,
        soup=soup,
        html_text=html_text,
    )

    # AI Synthesis
    ai_report = None
    if request.include_ai:
        try:
            ai_report = await ai_advisor.generate_report(
                metadata=metadata,
                issues=issues,
                category_scores=category_scores,
                model=request.model,
                custom_prompt=request.custom_prompt,
            )
        except Exception as exc:
            logger.warning(f"AI recommendation generation failed: {exc}")

    duration = round(time.perf_counter() - start_time, 2)

    return AnalyzeResponse(
        url=request.url,
        overall_score=overall_score,
        overall_grade=overall_grade,
        duration_seconds=duration,
        metadata=metadata,
        category_scores=category_scores,
        issues=issues,
        ai_analysis=ai_report,
    )


@router.post("/quick-scan", response_model=AnalyzeResponse, tags=["Analysis"])
async def quick_scan(request: AnalyzeRequest):
    """Rapid technical scan omitting LLM synthesis for sub-second responses."""
    request.include_ai = False
    return await analyze_website(request)


@router.post("/chat", response_model=ChatResponse, tags=["AI Assistant"])
async def chat_assistant(request: ChatRequest):
    """Interactive follow-up questions with the SitePulse AI assistant."""
    reply = await ai_advisor.chat(
        message=request.message,
        url=request.url,
        context_issues=request.context_issues,
        model=request.model,
    )
    return ChatResponse(
        reply=reply,
        model_used=request.model or settings.OLLAMA_MODEL,
    )
