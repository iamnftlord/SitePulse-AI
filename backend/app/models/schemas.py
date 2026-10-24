from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator


class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class CategoryType(str, Enum):
    SEO = "seo"
    SECURITY = "security"
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"
    TECHNOLOGY = "technology"


class AuditIssue(BaseModel):
    """Specific technical issue or warning detected on the site."""

    id: str = Field(..., description="Unique issue identifier, e.g., sec-missing-hsts")
    title: str = Field(..., description="Brief headline of the issue")
    category: CategoryType = Field(..., description="Category this issue belongs to")
    severity: SeverityLevel = Field(..., description="Issue severity level")
    description: str = Field(..., description="Detailed explanation of what was found")
    impact: str = Field(..., description="Impact on SEO, security, or user experience")
    recommendation: str = Field(..., description="How to remediate the issue")
    code_snippet: Optional[str] = Field(None, description="Suggested code fix or configuration snippet")
    element: Optional[str] = Field(None, description="HTML selector or header key involved")
    docs_url: Optional[str] = Field(None, description="Documentation or specification reference")


class CategoryScore(BaseModel):
    """Summary score and health metrics for a specific audit category."""

    category: CategoryType
    score: int = Field(..., ge=0, le=100, description="Health score from 0 to 100")
    grade: str = Field(..., description="Letter grade (A+, A, B, C, D, F)")
    passed_checks: int = Field(..., ge=0)
    total_checks: int = Field(..., ge=0)
    issues_count: int = Field(..., ge=0)


class DetectedTechnology(BaseModel):
    """Framework, library, server or CMS detected on the target site."""

    name: str
    category: str
    version: Optional[str] = None
    icon: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class CrawledMetadata(BaseModel):
    """Raw and processed technical attributes collected during crawl."""

    url: str
    final_url: str
    status_code: int
    load_time_ms: float
    page_size_bytes: int
    content_type: str
    is_https: bool
    title: Optional[str] = None
    title_length: int = 0
    meta_description: Optional[str] = None
    meta_description_length: int = 0
    canonical_url: Optional[str] = None
    has_viewport: bool = False
    has_charset: bool = False
    html_lang: Optional[str] = None
    headings_count: Dict[str, int] = Field(default_factory=dict)
    h1_headings: List[str] = Field(default_factory=list)
    images_total: int = 0
    images_missing_alt: int = 0
    links_internal: int = 0
    links_external: int = 0
    has_open_graph: bool = False
    has_twitter_card: bool = False
    has_robots_txt: Optional[bool] = None
    has_sitemap: Optional[bool] = None
    security_headers: Dict[str, Optional[str]] = Field(default_factory=dict)
    technologies: List[DetectedTechnology] = Field(default_factory=list)


class AIActionPlanItem(BaseModel):
    """An actionable, prioritized fix step recommended by AI."""

    priority_rank: int
    action: str
    category: CategoryType
    effort: str = Field(..., description="e.g. Quick Win (< 15 mins), Medium (1-3 hrs), Major")
    expected_impact: str
    code_example: Optional[str] = None


class AIAnalysisReport(BaseModel):
    """AI synthesized recommendations and strategic insights."""

    model_used: str
    executive_summary: str
    strengths: List[str]
    critical_weaknesses: List[str]
    action_plan: List[AIActionPlanItem]
    custom_advice: Optional[str] = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_fallback: bool = False


class AnalyzeRequest(BaseModel):
    """Request payload to initiate a website intelligence scan."""

    url: str = Field(..., description="Full URL to analyze (e.g. https://example.com)")
    include_ai: bool = Field(default=True, description="Whether to generate Ollama AI recommendations")
    model: Optional[str] = Field(default=None, description="Ollama model override, e.g. gemma4")
    custom_prompt: Optional[str] = Field(default=None, description="Optional custom instructions for AI advisor")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        clean = v.strip()
        if not clean.startswith(("http://", "https://")):
            clean = f"https://{clean}"
        return clean


class AnalyzeResponse(BaseModel):
    """Complete intelligence report for a scanned website."""

    url: str
    overall_score: int = Field(..., ge=0, le=100)
    overall_grade: str
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    duration_seconds: float
    metadata: CrawledMetadata
    category_scores: Dict[str, CategoryScore]
    issues: List[AuditIssue]
    ai_analysis: Optional[AIAnalysisReport] = None


class ChatRequest(BaseModel):
    """Follow-up questions regarding audit findings."""

    message: str
    url: Optional[str] = None
    context_issues: Optional[List[AuditIssue]] = None
    model: Optional[str] = None


class ChatResponse(BaseModel):
    """Interactive response from SitePulse AI assistant."""

    reply: str
    model_used: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HealthResponse(BaseModel):
    """System health and Ollama readiness check."""

    status: str
    version: str
    ollama_connected: bool
    ollama_url: str
    active_model: str
    available_models: List[str]
