import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.models.schemas import CrawledMetadata
from bs4 import BeautifulSoup

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "SitePulse AI"
    assert data["status"] == "online"


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "ollama_connected" in data
    assert "active_model" in data


def test_chat_endpoint_fallback():
    response = client.post(
        "/api/v1/chat",
        json={"message": "How do I configure CSP headers?", "url": "https://example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "Content-Security-Policy" in data["reply"]


@pytest.mark.asyncio
async def test_quick_scan_mocked_crawler():
    fake_metadata = CrawledMetadata(
        url="https://test.site",
        final_url="https://test.site",
        status_code=200,
        load_time_ms=210.0,
        page_size_bytes=15000,
        content_type="text/html",
        is_https=True,
        title="Test Site Title",
        title_length=15,
        meta_description="A good test site description with plenty of characters to pass the test.",
        meta_description_length=76,
        has_viewport=True,
        has_charset=True,
        html_lang="en",
        headings_count={"h1": 1},
        h1_headings=["Test Site Title"],
        images_total=1,
        images_missing_alt=0,
        security_headers={
            "content-security-policy": "default-src 'self'",
            "strict-transport-security": "max-age=31536000",
        },
    )
    fake_soup = BeautifulSoup("<html lang='en'><head><title>Test Site Title</title></head><body><h1>Test</h1></body></html>", "html.parser")

    with patch("app.services.crawler.WebsiteCrawler.fetch_page", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = (fake_metadata, fake_soup, "<html>...</html>")

        response = client.post(
            "/api/v1/quick-scan",
            json={"url": "https://test.site"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["url"] == "https://test.site"
        assert "overall_score" in data
        assert "category_scores" in data
        assert "issues" in data
        assert data["ai_analysis"] is None  # Quick scan excludes AI
