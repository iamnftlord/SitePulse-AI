from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    PROJECT_NAME: str = "SitePulse AI"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Host & Port
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma4"
    OLLAMA_REQUEST_TIMEOUT: float = 60.0

    # Crawler Configuration
    CRAWLER_TIMEOUT_SECONDS: float = 15.0
    CRAWLER_USER_AGENT: str = "SitePulseAI-Auditor/1.0 (+https://github.com/SitePulseAI/sitepulse)"
    MAX_PAGE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10MB limit

    # Security & Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 30
    ALLOW_PRIVATE_IPS: bool = False

    # CORS Configuration
    CORS_ORIGINS: Union[List[str], str] = ["*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
