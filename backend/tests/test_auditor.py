from bs4 import BeautifulSoup
from app.models.schemas import CategoryType, CrawledMetadata, SeverityLevel
from app.services.auditor import Auditor


def test_auditor_flags_missing_title_and_description():
    metadata = CrawledMetadata(
        url="http://example.com",
        final_url="http://example.com",
        status_code=200,
        load_time_ms=150.0,
        page_size_bytes=5000,
        content_type="text/html",
        is_https=False,
        title=None,
        meta_description=None,
        headings_count={"h1": 0},
        images_total=2,
        images_missing_alt=2,
        security_headers={},
    )
    html = "<html><body><img src='1.png'><img src='2.png'></body></html>"
    soup = BeautifulSoup(html, "html.parser")

    issues, category_scores, overall_score, overall_grade = Auditor.audit(metadata, soup, html)

    issue_ids = [i.id for i in issues]
    assert "seo-missing-title" in issue_ids
    assert "seo-missing-description" in issue_ids
    assert "seo-missing-h1" in issue_ids
    assert "sec-no-https" in issue_ids
    assert "sec-missing-hsts" in issue_ids
    assert "sec-missing-csp" in issue_ids
    assert "a11y-missing-alt-tags" in issue_ids
    assert "a11y-missing-viewport" in issue_ids
    assert "a11y-missing-lang" in issue_ids

    assert overall_score < 50
    assert overall_grade in ["D", "F"]


def test_auditor_good_site_high_score():
    metadata = CrawledMetadata(
        url="https://perfect-site.org",
        final_url="https://perfect-site.org",
        status_code=200,
        load_time_ms=180.0,
        page_size_bytes=24000,
        content_type="text/html",
        is_https=True,
        title="SitePulse AI - Next Gen Website Intelligence & Audit",
        title_length=51,
        meta_description="Analyze your website and receive actionable, AI-powered developer recommendations across SEO, Security, Performance, and A11y.",
        meta_description_length=134,
        canonical_url="https://perfect-site.org",
        has_viewport=True,
        has_charset=True,
        html_lang="en",
        headings_count={"h1": 1, "h2": 3},
        h1_headings=["Next Gen Website Intelligence"],
        images_total=4,
        images_missing_alt=0,
        links_internal=10,
        links_external=2,
        has_open_graph=True,
        has_twitter_card=True,
        has_robots_txt=True,
        has_sitemap=True,
        security_headers={
            "content-security-policy": "default-src 'self'",
            "strict-transport-security": "max-age=31536000",
            "x-frame-options": "SAMEORIGIN",
            "x-content-type-options": "nosniff",
            "referrer-policy": "strict-origin-when-cross-origin",
            "permissions-policy": "camera=()",
        },
    )
    html = '<html lang="en"><head><title>Test</title><meta name="viewport" content="width=device-width"></head><body><h1>Heading</h1><img src="pic.jpg" alt="Description" loading="lazy"></body></html>'
    soup = BeautifulSoup(html, "html.parser")

    issues, category_scores, overall_score, overall_grade = Auditor.audit(metadata, soup, html)

    assert len(issues) == 0
    assert overall_score >= 95
    assert overall_grade in ["A+", "A"]
    assert category_scores["security"].score == 100
    assert category_scores["seo"].score == 100
