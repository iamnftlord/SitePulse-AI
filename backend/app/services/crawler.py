import asyncio
import logging
import time
from typing import Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import httpx

from app.core.config import settings
from app.core.security import SSRFValidationError, validate_target_url
from app.models.schemas import CrawledMetadata
from app.services.tech_detector import TechDetector

logger = logging.getLogger("sitepulse.crawler")

MAX_REDIRECTS = 5


class WebsiteCrawler:
    """Asynchronous, SSRF-hardened crawler for extracting web assets, DOM elements, and network metrics."""

    def __init__(self, timeout: float = settings.CRAWLER_TIMEOUT_SECONDS):
        self.timeout = timeout
        self.headers = {
            "User-Agent": settings.CRAWLER_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    async def fetch_page(self, url: str) -> Tuple[CrawledMetadata, BeautifulSoup, str]:
        """Crawls the target URL safely with SSRF protection and extracts comprehensive technical metadata."""
        # 1. SSRF check on initial URL
        validated_url = await validate_target_url(url, allow_private=settings.ALLOW_PRIVATE_IPS)
        start_time = time.perf_counter()

        current_url = validated_url
        redirect_count = 0
        final_response: Optional[httpx.Response] = None

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=False,  # Manually inspect every redirect hop against SSRF
            verify=False,
            headers=self.headers,
        ) as client:
            while redirect_count <= MAX_REDIRECTS:
                try:
                    response = await client.get(current_url)
                except httpx.TimeoutException as exc:
                    raise ValueError(f"Connection timed out while fetching {current_url} (limit: {self.timeout}s)") from exc
                except httpx.RequestError as exc:
                    raise ValueError(f"Network error while connecting to {current_url}: {str(exc)}") from exc

                # Check if this is a redirect
                if response.is_redirect and "location" in response.headers:
                    redirect_count += 1
                    if redirect_count > MAX_REDIRECTS:
                        raise ValueError(f"Exceeded maximum allowed redirects ({MAX_REDIRECTS}).")

                    location = response.headers["location"]
                    next_url = urljoin(current_url, location)

                    # Validate the redirect target against SSRF (e.g. stops attacker redirecting to 169.254.169.254)
                    current_url = await validate_target_url(next_url, allow_private=settings.ALLOW_PRIVATE_IPS)
                    continue

                final_response = response
                break

            if not final_response:
                raise ValueError(f"Failed to obtain a valid HTTP response from {url}")

            # Enforce max page payload size
            content_length_header = final_response.headers.get("content-length")
            if content_length_header and content_length_header.isdigit():
                if int(content_length_header) > settings.MAX_PAGE_SIZE_BYTES:
                    raise ValueError(
                        f"Page payload exceeds maximum allowable size ({settings.MAX_PAGE_SIZE_BYTES // (1024 * 1024)} MB)."
                    )

            if len(final_response.content) > settings.MAX_PAGE_SIZE_BYTES:
                raise ValueError(
                    f"Page payload exceeds maximum allowable size ({settings.MAX_PAGE_SIZE_BYTES // (1024 * 1024)} MB)."
                )

            load_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            content_type = final_response.headers.get("content-type", "")
            final_url = str(final_response.url)
            is_https = final_url.startswith("https://")
            status_code = final_response.status_code

            # Raw HTML and DOM parser
            html_text = final_response.text or ""
            soup = BeautifulSoup(html_text, "html.parser")

            # Extract basic tags
            title_tag = soup.find("title")
            title = title_tag.get_text().strip() if title_tag else None
            title_length = len(title) if title else 0

            meta_desc_tag = soup.find("meta", attrs={"name": lambda x: x and x.lower() == "description"})
            meta_description = meta_desc_tag.get("content", "").strip() if meta_desc_tag else None
            meta_description_length = len(meta_description) if meta_description else 0

            canonical_tag = soup.find(
                "link", rel=lambda x: x and "canonical" in [item.lower() for item in (x if isinstance(x, list) else [x])]
            )
            canonical_url = canonical_tag.get("href", "").strip() if canonical_tag else None

            # Viewport & Charset
            viewport_tag = soup.find("meta", attrs={"name": lambda x: x and x.lower() == "viewport"})
            has_viewport = viewport_tag is not None

            charset_tag = soup.find("meta", attrs={"charset": True}) or soup.find(
                "meta", attrs={"http-equiv": lambda x: x and x.lower() == "content-type"}
            )
            has_charset = charset_tag is not None

            html_tag = soup.find("html")
            html_lang = html_tag.get("lang") if html_tag and html_tag.get("lang") else None

            # Headings
            headings_count: Dict[str, int] = {}
            for level in range(1, 7):
                tag_name = f"h{level}"
                headings_count[tag_name] = len(soup.find_all(tag_name))

            h1_headings = [h.get_text().strip() for h in soup.find_all("h1") if h.get_text().strip()]

            # Images
            all_images = soup.find_all("img")
            images_total = len(all_images)
            images_missing_alt = sum(1 for img in all_images if not img.get("alt") or not img.get("alt").strip())

            # Links
            parsed_final_url = urlparse(final_url)
            base_domain = parsed_final_url.netloc.lower()

            all_anchors = soup.find_all("a", href=True)
            links_internal = 0
            links_external = 0

            for a in all_anchors:
                href = a.get("href", "").strip()
                if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                    continue
                full_link = urljoin(final_url, href)
                link_domain = urlparse(full_link).netloc.lower()
                if link_domain == base_domain:
                    links_internal += 1
                else:
                    links_external += 1

            # Social Tags (Open Graph & Twitter)
            og_title = soup.find("meta", property=lambda x: x and x.lower() == "og:title")
            og_image = soup.find("meta", property=lambda x: x and x.lower() == "og:image")
            has_open_graph = bool(og_title or og_image)

            twitter_card = soup.find("meta", attrs={"name": lambda x: x and x.lower() == "twitter:card"})
            has_twitter_card = twitter_card is not None

            # Extract security headers
            sec_headers_keys = [
                "content-security-policy",
                "strict-transport-security",
                "x-frame-options",
                "x-content-type-options",
                "referrer-policy",
                "permissions-policy",
            ]
            security_headers = {
                k: final_response.headers.get(k)
                for k in sec_headers_keys
            }

            # Check robots.txt and sitemap.xml in background
            has_robots_txt, has_sitemap = await self._check_robots_and_sitemap(client, final_url)

            # Detect technologies
            technologies = TechDetector.detect(soup, dict(final_response.headers), html_text)

            metadata = CrawledMetadata(
                url=url,
                final_url=final_url,
                status_code=status_code,
                load_time_ms=load_time_ms,
                page_size_bytes=len(final_response.content),
                content_type=content_type,
                is_https=is_https,
                title=title,
                title_length=title_length,
                meta_description=meta_description,
                meta_description_length=meta_description_length,
                canonical_url=canonical_url,
                has_viewport=has_viewport,
                has_charset=has_charset,
                html_lang=html_lang,
                headings_count=headings_count,
                h1_headings=h1_headings,
                images_total=images_total,
                images_missing_alt=images_missing_alt,
                links_internal=links_internal,
                links_external=links_external,
                has_open_graph=has_open_graph,
                has_twitter_card=has_twitter_card,
                has_robots_txt=has_robots_txt,
                has_sitemap=has_sitemap,
                security_headers=security_headers,
                technologies=technologies,
            )

            return metadata, soup, html_text

    async def _check_robots_and_sitemap(
        self, client: httpx.AsyncClient, base_url: str
    ) -> Tuple[Optional[bool], Optional[bool]]:
        """Quickly probes for the presence of /robots.txt and /sitemap.xml."""
        parsed = urlparse(base_url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = urljoin(origin, "/robots.txt")
        sitemap_url = urljoin(origin, "/sitemap.xml")

        async def probe(u: str) -> bool:
            try:
                res = await client.head(u, timeout=3.0)
                if res.status_code == 200:
                    return True
                if res.status_code in (405, 403):
                    get_res = await client.get(u, timeout=3.0)
                    return get_res.status_code == 200
                return False
            except Exception:
                return False

        try:
            robots_res, sitemap_res = await asyncio.gather(
                probe(robots_url),
                probe(sitemap_url),
                return_exceptions=True
            )
            return (
                bool(robots_res) if not isinstance(robots_res, Exception) else False,
                bool(sitemap_res) if not isinstance(sitemap_res, Exception) else False,
            )
        except Exception:
            return False, False
