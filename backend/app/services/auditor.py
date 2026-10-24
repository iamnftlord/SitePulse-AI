from typing import Dict, List, Tuple
from bs4 import BeautifulSoup

from app.models.schemas import (
    AuditIssue,
    CategoryScore,
    CategoryType,
    CrawledMetadata,
    SeverityLevel,
)


class Auditor:
    """Performs deterministic technical auditing and score calculations."""

    @classmethod
    def audit(cls, metadata: CrawledMetadata, soup: BeautifulSoup, html_text: str) -> Tuple[List[AuditIssue], Dict[str, CategoryScore], int, str]:
        issues: List[AuditIssue] = []

        # 1. SEO Checks
        seo_passed = 0
        seo_total = 7

        # Title
        if not metadata.title:
            issues.append(AuditIssue(
                id="seo-missing-title",
                title="Missing <title> Tag",
                category=CategoryType.SEO,
                severity=SeverityLevel.CRITICAL,
                description="The page lacks a <title> element in the HTML <head>.",
                impact="Search engines cannot determine the page topic and will likely not rank it effectively.",
                recommendation="Add a descriptive <title> tag between 30 and 60 characters.",
                code_snippet="<title>Primary Keyword - Brand Name</title>",
                element="<title>",
                docs_url="https://developers.google.com/search/docs/appearance/title-link",
            ))
        elif metadata.title_length < 20:
            issues.append(AuditIssue(
                id="seo-short-title",
                title="Title Tag is Too Short",
                category=CategoryType.SEO,
                severity=SeverityLevel.LOW,
                description=f"The title tag is only {metadata.title_length} characters.",
                impact="Short titles under-utilize search snippet space and miss valuable keywords.",
                recommendation="Expand the title tag to 30-60 characters.",
                element="<title>",
            ))
        elif metadata.title_length > 65:
            issues.append(AuditIssue(
                id="seo-long-title",
                title="Title Tag is Too Long",
                category=CategoryType.SEO,
                severity=SeverityLevel.LOW,
                description=f"The title tag is {metadata.title_length} characters, exceeding the 60-character limit.",
                impact="Google and search engines will truncate the title in search result pages.",
                recommendation="Shorten the title to under 60 characters to prevent truncation.",
                element="<title>",
            ))
        else:
            seo_passed += 1

        # Meta Description
        if not metadata.meta_description:
            issues.append(AuditIssue(
                id="seo-missing-description",
                title="Missing Meta Description",
                category=CategoryType.SEO,
                severity=SeverityLevel.HIGH,
                description="No <meta name='description'> tag was found.",
                impact="Search engines generate automatic snippets which often perform poorly for click-through rate (CTR).",
                recommendation="Add a concise, compelling meta description between 120 and 160 characters.",
                code_snippet='<meta name="description" content="Engaging summary of this page with key highlights and a clear call to action.">',
                element='<meta name="description">',
                docs_url="https://developers.google.com/search/docs/appearance/snippet",
            ))
        elif metadata.meta_description_length < 70 or metadata.meta_description_length > 165:
            issues.append(AuditIssue(
                id="seo-suboptimal-description-length",
                title="Meta Description Length Suboptimal",
                category=CategoryType.SEO,
                severity=SeverityLevel.LOW,
                description=f"Meta description is {metadata.meta_description_length} characters (recommended: 120-160).",
                impact="Descriptions that are too short may be replaced by search engines; descriptions that are too long get clipped.",
                recommendation="Aim for 120-160 characters for optimal desktop and mobile visibility.",
                element='<meta name="description">',
            ))
        else:
            seo_passed += 1

        # H1 Heading
        h1_count = metadata.headings_count.get("h1", 0)
        if h1_count == 0:
            issues.append(AuditIssue(
                id="seo-missing-h1",
                title="Missing Primary <h1> Heading",
                category=CategoryType.SEO,
                severity=SeverityLevel.HIGH,
                description="No <h1> tag was found on the page.",
                impact="Search engines and screen readers rely on the <h1> to identify the page's core subject.",
                recommendation="Add exactly one clear <h1> tag representing the page topic.",
                code_snippet="<h1>Your Primary Value Proposition</h1>",
                element="<h1>",
            ))
        elif h1_count > 1:
            issues.append(AuditIssue(
                id="seo-multiple-h1",
                title=f"Multiple <h1> Headings Detected ({h1_count})",
                category=CategoryType.SEO,
                severity=SeverityLevel.MEDIUM,
                description=f"Found {h1_count} <h1> headings on the page.",
                impact="Having multiple <h1> elements dilutes topic authority and confuses document hierarchy.",
                recommendation="Consolidate into a single <h1> heading and demote subheadings to <h2> or <h3>.",
                element="<h1>",
            ))
        else:
            seo_passed += 1

        # Canonical Link
        if not metadata.canonical_url:
            issues.append(AuditIssue(
                id="seo-missing-canonical",
                title="Missing Canonical URL Tag",
                category=CategoryType.SEO,
                severity=SeverityLevel.MEDIUM,
                description="No <link rel='canonical'> element was found in the HTML head.",
                impact="Risk of duplicate content penalties when the page is reachable via different query params, protocols, or trailing slashes.",
                recommendation="Specify the preferred URL for this page using a canonical tag.",
                code_snippet=f'<link rel="canonical" href="{metadata.final_url}" />',
                element='<link rel="canonical">',
            ))
        else:
            seo_passed += 1

        # Social Meta / Open Graph
        if not metadata.has_open_graph:
            issues.append(AuditIssue(
                id="seo-missing-open-graph",
                title="Missing Open Graph Meta Tags",
                category=CategoryType.SEO,
                severity=SeverityLevel.MEDIUM,
                description="No Open Graph (og:title, og:image) tags found.",
                impact="Links shared on Slack, LinkedIn, Facebook, and Discord will display without rich preview cards or thumbnails.",
                recommendation="Add Open Graph protocol tags for rich social sharing previews.",
                code_snippet='<meta property="og:title" content="Page Title" />\n<meta property="og:description" content="Description" />\n<meta property="og:image" content="https://example.com/preview.jpg" />',
                element='<meta property="og:*">',
            ))
        else:
            seo_passed += 1

        # robots.txt
        if metadata.has_robots_txt is False:
            issues.append(AuditIssue(
                id="seo-missing-robots-txt",
                title="Robots.txt Not Detected",
                category=CategoryType.SEO,
                severity=SeverityLevel.LOW,
                description="Could not access /robots.txt on the domain.",
                impact="Search engine crawlers have no indexing instructions or crawl budget directives.",
                recommendation="Deploy a standard /robots.txt file at the domain root.",
                code_snippet="User-agent: *\nAllow: /\nSitemap: https://example.com/sitemap.xml",
                element="/robots.txt",
            ))
        else:
            seo_passed += 1

        # sitemap.xml
        if metadata.has_sitemap is False:
            issues.append(AuditIssue(
                id="seo-missing-sitemap",
                title="XML Sitemap Not Found at Standard Location",
                category=CategoryType.SEO,
                severity=SeverityLevel.LOW,
                description="Could not find /sitemap.xml at the standard root path.",
                impact="New or nested pages may take longer for search engine bots to discover and index.",
                recommendation="Generate an XML sitemap and reference it in /robots.txt.",
                element="/sitemap.xml",
            ))
        else:
            seo_passed += 1

        # 2. Security Checks
        sec_passed = 0
        sec_total = 7

        if not metadata.is_https:
            issues.append(AuditIssue(
                id="sec-no-https",
                title="Site Does Not Use HTTPS",
                category=CategoryType.SECURITY,
                severity=SeverityLevel.CRITICAL,
                description="The connection is serving content over insecure plain HTTP.",
                impact="All transmitted data (passwords, cookies, form inputs) can be intercepted via Man-in-the-Middle attacks. Browsers display 'Not Secure' warning.",
                recommendation="Obtain an SSL/TLS certificate (e.g. Let's Encrypt) and force HTTP to HTTPS redirects.",
                docs_url="https://letsencrypt.org/",
            ))
        else:
            sec_passed += 1

        sec_headers = metadata.security_headers

        # HSTS
        if not sec_headers.get("strict-transport-security"):
            issues.append(AuditIssue(
                id="sec-missing-hsts",
                title="Missing Strict-Transport-Security (HSTS)",
                category=CategoryType.SECURITY,
                severity=SeverityLevel.HIGH,
                description="HTTP Strict Transport Security header is not configured.",
                impact="Vulnerable to SSL-stripping attacks on the initial HTTP request.",
                recommendation="Add Strict-Transport-Security header with at least 1-year duration and includeSubDomains.",
                code_snippet="Strict-Transport-Security: max-age=31536000; includeSubDomains; preload",
                element="Header: Strict-Transport-Security",
            ))
        else:
            sec_passed += 1

        # Content-Security-Policy
        if not sec_headers.get("content-security-policy"):
            issues.append(AuditIssue(
                id="sec-missing-csp",
                title="Missing Content-Security-Policy (CSP)",
                category=CategoryType.SECURITY,
                severity=SeverityLevel.HIGH,
                description="No Content-Security-Policy header is served.",
                impact="Leaves the site susceptible to Cross-Site Scripting (XSS), data injection, and rogue script execution.",
                recommendation="Define a restrictive Content-Security-Policy header.",
                code_snippet="Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https:; img-src 'self' data: https:;",
                element="Header: Content-Security-Policy",
            ))
        else:
            sec_passed += 1

        # X-Frame-Options
        if not sec_headers.get("x-frame-options"):
            issues.append(AuditIssue(
                id="sec-missing-x-frame-options",
                title="Missing X-Frame-Options (Clickjacking Protection)",
                category=CategoryType.SECURITY,
                severity=SeverityLevel.MEDIUM,
                description="No X-Frame-Options or frame-ancestors CSP directive found.",
                impact="The page can be embedded inside an invisible <iframe> on malicious third-party websites to trick users into unintentional clicks (Clickjacking).",
                recommendation="Set X-Frame-Options to DENY or SAMEORIGIN.",
                code_snippet="X-Frame-Options: SAMEORIGIN",
                element="Header: X-Frame-Options",
            ))
        else:
            sec_passed += 1

        # X-Content-Type-Options
        if not sec_headers.get("x-content-type-options"):
            issues.append(AuditIssue(
                id="sec-missing-nosniff",
                title="Missing X-Content-Type-Options",
                category=CategoryType.SECURITY,
                severity=SeverityLevel.MEDIUM,
                description="The X-Content-Type-Options: nosniff header is absent.",
                impact="Browsers may attempt MIME-sniffing on untyped assets, potentially executing malicious scripts masked as images or text.",
                recommendation="Add X-Content-Type-Options header with value 'nosniff'.",
                code_snippet="X-Content-Type-Options: nosniff",
                element="Header: X-Content-Type-Options",
            ))
        else:
            sec_passed += 1

        # Referrer-Policy
        if not sec_headers.get("referrer-policy"):
            issues.append(AuditIssue(
                id="sec-missing-referrer-policy",
                title="Missing Referrer-Policy Header",
                category=CategoryType.SECURITY,
                severity=SeverityLevel.LOW,
                description="Referrer-Policy header is not explicitly set.",
                impact="Sensitive path and parameter information in URLs could leak to external analytics or linked third-party sites.",
                recommendation="Set Referrer-Policy to strict-origin-when-cross-origin or no-referrer.",
                code_snippet="Referrer-Policy: strict-origin-when-cross-origin",
                element="Header: Referrer-Policy",
            ))
        else:
            sec_passed += 1

        # Permissions-Policy
        if not sec_headers.get("permissions-policy"):
            issues.append(AuditIssue(
                id="sec-missing-permissions-policy",
                title="Missing Permissions-Policy",
                category=CategoryType.SECURITY,
                severity=SeverityLevel.LOW,
                description="Permissions-Policy (formerly Feature-Policy) is not defined.",
                impact="Browsers allow camera, microphone, geolocation APIs without explicit restriction.",
                recommendation="Configure Permissions-Policy to disable unnecessary browser features.",
                code_snippet="Permissions-Policy: camera=(), microphone=(), geolocation=()",
                element="Header: Permissions-Policy",
            ))
        else:
            sec_passed += 1

        # 3. Performance Checks
        perf_passed = 0
        perf_total = 4

        # Response Time / TTFB
        if metadata.load_time_ms > 2000:
            issues.append(AuditIssue(
                id="perf-critical-response-time",
                title="Critical Server Response Latency",
                category=CategoryType.PERFORMANCE,
                severity=SeverityLevel.CRITICAL,
                description=f"Server response time was {metadata.load_time_ms}ms (> 2000ms threshold).",
                impact="Severe negative impact on user bounce rate and Core Web Vitals (TTFB / LCP). Search engines deprioritize slow pages.",
                recommendation="Enable server-side caching (Redis, Varnish), optimize backend database queries, or use edge CDN routing.",
            ))
        elif metadata.load_time_ms > 800:
            issues.append(AuditIssue(
                id="perf-slow-response-time",
                title="High Server Response Time",
                category=CategoryType.PERFORMANCE,
                severity=SeverityLevel.MEDIUM,
                description=f"Server response time was {metadata.load_time_ms}ms (recommended: < 600ms).",
                impact="Delays page rendering and increases First Contentful Paint.",
                recommendation="Investigate server bottlenecks, enable HTTP/2 or HTTP/3, and leverage edge caching.",
            ))
        else:
            perf_passed += 1

        # Page Size
        size_kb = round(metadata.page_size_bytes / 1024, 1)
        if metadata.page_size_bytes > 2 * 1024 * 1024:
            issues.append(AuditIssue(
                id="perf-huge-html-payload",
                title="Massive HTML Payload Size",
                category=CategoryType.PERFORMANCE,
                severity=SeverityLevel.HIGH,
                description=f"Initial HTML document payload is {size_kb} KB (> 2MB).",
                impact="Slows initial DOM parsing and consumes high mobile bandwidth.",
                recommendation="Minify HTML, inline fewer large base64 data URIs or scripts, and paginate long lists.",
            ))
        elif metadata.page_size_bytes > 500 * 1024:
            issues.append(AuditIssue(
                id="perf-heavy-page-size",
                title="Heavy HTML Document Size",
                category=CategoryType.PERFORMANCE,
                severity=SeverityLevel.LOW,
                description=f"Initial HTML payload is {size_kb} KB (recommended: < 300 KB).",
                impact="May delay DOM construction and first render on mobile devices.",
                recommendation="Remove extraneous inline styles/scripts and verify Gzip/Brotli compression is active.",
            ))
        else:
            perf_passed += 1

        # Image lazy loading check
        unoptimized_imgs = soup.find_all("img", attrs={"loading": lambda x: x != "lazy"})
        if len(unoptimized_imgs) > 5:
            issues.append(AuditIssue(
                id="perf-missing-lazy-loading",
                title="Images Missing loading='lazy'",
                category=CategoryType.PERFORMANCE,
                severity=SeverityLevel.LOW,
                description=f"Found {len(unoptimized_imgs)} images without native lazy loading.",
                impact="Browser loads all off-screen images eagerly, blocking bandwidth needed for critical above-the-fold assets.",
                recommendation="Add loading='lazy' and explicit width/height attributes to below-the-fold images.",
                code_snippet='<img src="photo.webp" alt="Description" loading="lazy" width="600" height="400">',
            ))
        else:
            perf_passed += 1

        # Total image count sanity check
        if metadata.images_total > 30:
            issues.append(AuditIssue(
                id="perf-high-image-count",
                title=f"High Image Count on Single Page ({metadata.images_total})",
                category=CategoryType.PERFORMANCE,
                severity=SeverityLevel.LOW,
                description=f"Page references {metadata.images_total} individual images.",
                impact="Excessive network requests increase connection overhead and memory usage.",
                recommendation="Use CSS sprites or modern responsive picture formats (WebP / AVIF) and lazy load aggressively.",
            ))
        else:
            perf_passed += 1

        # 4. Accessibility & UX Checks
        a11y_passed = 0
        a11y_total = 4

        # Viewport Meta
        if not metadata.has_viewport:
            issues.append(AuditIssue(
                id="a11y-missing-viewport",
                title="Missing Mobile Viewport Meta Tag",
                category=CategoryType.ACCESSIBILITY,
                severity=SeverityLevel.CRITICAL,
                description="No <meta name='viewport'> tag detected.",
                impact="Mobile devices will render the desktop version with tiny, unreadable text, failing Google's Mobile-Friendly guidelines.",
                recommendation="Add standard responsive viewport meta tag in <head>.",
                code_snippet='<meta name="viewport" content="width=device-width, initial-scale=1.0">',
                element='<meta name="viewport">',
            ))
        else:
            a11y_passed += 1

        # HTML Lang
        if not metadata.html_lang:
            issues.append(AuditIssue(
                id="a11y-missing-lang",
                title="Missing HTML <html> lang Attribute",
                category=CategoryType.ACCESSIBILITY,
                severity=SeverityLevel.HIGH,
                description="The <html> element does not specify a 'lang' attribute.",
                impact="Screen readers cannot determine the correct pronunciation rules and automated translators cannot determine source language.",
                recommendation="Add the primary language code to the <html> tag.",
                code_snippet='<html lang="en">',
                element="<html lang>",
                docs_url="https://www.w3.org/WAI/tutorials/page-structure/language/",
            ))
        else:
            a11y_passed += 1

        # Image Alt Attributes
        if metadata.images_total > 0 and metadata.images_missing_alt > 0:
            missing_ratio = metadata.images_missing_alt / metadata.images_total
            sev = SeverityLevel.HIGH if missing_ratio > 0.3 else SeverityLevel.MEDIUM
            issues.append(AuditIssue(
                id="a11y-missing-alt-tags",
                title=f"{metadata.images_missing_alt} Image(s) Missing 'alt' Attribute",
                category=CategoryType.ACCESSIBILITY,
                severity=sev,
                description=f"{metadata.images_missing_alt} out of {metadata.images_total} images have missing or empty alt attributes.",
                impact="Visually impaired users relying on screen readers receive no context for images; also impairs image SEO.",
                recommendation="Provide meaningful descriptive alt text for content images or alt='' for purely decorative graphics.",
                code_snippet='<img src="team.jpg" alt="SitePulse AI core engineering team at Hacktoberfest" />',
                element="<img alt>",
            ))
        else:
            a11y_passed += 1

        # Charset
        if not metadata.has_charset:
            issues.append(AuditIssue(
                id="a11y-missing-charset",
                title="Missing Charset Declaration",
                category=CategoryType.ACCESSIBILITY,
                severity=SeverityLevel.MEDIUM,
                description="No <meta charset='utf-8'> tag found.",
                impact="May result in mojibake or broken character encoding for special symbols and international characters.",
                recommendation="Add <meta charset='utf-8'> as the first child of <head>.",
                code_snippet='<meta charset="utf-8">',
                element='<meta charset="utf-8">',
            ))
        else:
            a11y_passed += 1

        # Calculate Scores
        def calc_score(passed: int, total: int, count_issues: int) -> Tuple[int, str]:
            if total == 0:
                return 100, "A+"
            raw = round((passed / total) * 100)
            # Penalize for critical issues
            score = max(0, min(100, raw))
            if score >= 95:
                grade = "A+"
            elif score >= 85:
                grade = "A"
            elif score >= 70:
                grade = "B"
            elif score >= 55:
                grade = "C"
            elif score >= 40:
                grade = "D"
            else:
                grade = "F"
            return score, grade

        seo_score, seo_grade = calc_score(seo_passed, seo_total, len([i for i in issues if i.category == CategoryType.SEO]))
        sec_score, sec_grade = calc_score(sec_passed, sec_total, len([i for i in issues if i.category == CategoryType.SECURITY]))
        perf_score, perf_grade = calc_score(perf_passed, perf_total, len([i for i in issues if i.category == CategoryType.PERFORMANCE]))
        a11y_score, a11y_grade = calc_score(a11y_passed, a11y_total, len([i for i in issues if i.category == CategoryType.ACCESSIBILITY]))

        category_scores: Dict[str, CategoryScore] = {
            CategoryType.SEO.value: CategoryScore(
                category=CategoryType.SEO,
                score=seo_score,
                grade=seo_grade,
                passed_checks=seo_passed,
                total_checks=seo_total,
                issues_count=len([i for i in issues if i.category == CategoryType.SEO]),
            ),
            CategoryType.SECURITY.value: CategoryScore(
                category=CategoryType.SECURITY,
                score=sec_score,
                grade=sec_grade,
                passed_checks=sec_passed,
                total_checks=sec_total,
                issues_count=len([i for i in issues if i.category == CategoryType.SECURITY]),
            ),
            CategoryType.PERFORMANCE.value: CategoryScore(
                category=CategoryType.PERFORMANCE,
                score=perf_score,
                grade=perf_grade,
                passed_checks=perf_passed,
                total_checks=perf_total,
                issues_count=len([i for i in issues if i.category == CategoryType.PERFORMANCE]),
            ),
            CategoryType.ACCESSIBILITY.value: CategoryScore(
                category=CategoryType.ACCESSIBILITY,
                score=a11y_score,
                grade=a11y_grade,
                passed_checks=a11y_passed,
                total_checks=a11y_total,
                issues_count=len([i for i in issues if i.category == CategoryType.ACCESSIBILITY]),
            ),
        }

        # Overall weighted score
        overall_score = round(
            (seo_score * 0.30) + (sec_score * 0.30) + (perf_score * 0.20) + (a11y_score * 0.20)
        )
        _, overall_grade = calc_score(overall_score, 100, len(issues))

        return issues, category_scores, overall_score, overall_grade
