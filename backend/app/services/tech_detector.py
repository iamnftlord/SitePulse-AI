import re
from typing import Dict, List
from bs4 import BeautifulSoup
from app.models.schemas import DetectedTechnology


class TechDetector:
    """Detects web frameworks, CMS, analytics, CDN, and server technologies."""

    @classmethod
    def detect(cls, soup: BeautifulSoup, headers: Dict[str, str], html_text: str) -> List[DetectedTechnology]:
        technologies: List[DetectedTechnology] = []
        lower_headers = {k.lower(): v.lower() for k, v in headers.items()}
        scripts = [s.get("src", "") for s in soup.find_all("script") if s.get("src")]
        links = [l.get("href", "") for l in soup.find_all("link") if l.get("href")]
        all_assets = " ".join(scripts + links).lower()

        # 1. Server & Cloud / CDN
        server = lower_headers.get("server", "")
        if "cloudflare" in server or "cf-ray" in lower_headers:
            technologies.append(DetectedTechnology(name="Cloudflare", category="CDN / Security", icon="cloudflare"))
        if "nginx" in server:
            version_match = re.search(r"nginx/([\d.]+)", server)
            technologies.append(DetectedTechnology(
                name="Nginx",
                category="Web Server",
                version=version_match.group(1) if version_match else None,
                icon="nginx"
            ))
        elif "apache" in server:
            version_match = re.search(r"apache/([\d.]+)", server)
            technologies.append(DetectedTechnology(
                name="Apache",
                category="Web Server",
                version=version_match.group(1) if version_match else None,
                icon="apache"
            ))
        elif "caddy" in server:
            technologies.append(DetectedTechnology(name="Caddy", category="Web Server", icon="caddy"))

        # 2. Backend & Platforms
        powered_by = lower_headers.get("x-powered-by", "")
        if "php" in powered_by:
            v_match = re.search(r"php/([\d.]+)", powered_by)
            technologies.append(DetectedTechnology(
                name="PHP",
                category="Programming Language",
                version=v_match.group(1) if v_match else None,
                icon="php"
            ))
        if "express" in powered_by:
            technologies.append(DetectedTechnology(name="Express.js", category="Backend Framework", icon="nodejs"))
        if "next.js" in powered_by or lower_headers.get("x-nextjs-cache") is not None:
            technologies.append(DetectedTechnology(name="Next.js", category="Frontend Framework", icon="nextjs"))

        # 3. Meta Generator
        meta_generator = soup.find("meta", attrs={"name": re.compile(r"^generator$", re.I)})
        gen_content = meta_generator.get("content", "").lower() if meta_generator else ""

        if "wordpress" in gen_content or "wp-content" in all_assets:
            v_match = re.search(r"wordpress\s*([\d.]+)", gen_content)
            technologies.append(DetectedTechnology(
                name="WordPress",
                category="CMS",
                version=v_match.group(1) if v_match else None,
                icon="wordpress"
            ))
        if "shopify" in gen_content or "cdn.shopify.com" in all_assets or "shopify" in lower_headers.get("x-shopid", ""):
            technologies.append(DetectedTechnology(name="Shopify", category="E-commerce", icon="shopify"))
        if "webflow" in gen_content or "data-wf-page" in html_text:
            technologies.append(DetectedTechnology(name="Webflow", category="Website Builder", icon="webflow"))
        if "wix" in gen_content or "wix.com" in all_assets:
            technologies.append(DetectedTechnology(name="Wix", category="Website Builder", icon="wix"))
        if "ghost" in gen_content:
            technologies.append(DetectedTechnology(name="Ghost", category="CMS", icon="ghost"))

        # 4. Frontend Libraries & Frameworks
        if soup.find(id="__next") or "/_next/static/" in all_assets:
            if not any(t.name == "Next.js" for t in technologies):
                technologies.append(DetectedTechnology(name="Next.js", category="Frontend Framework", icon="nextjs"))
            if not any(t.name == "React" for t in technologies):
                technologies.append(DetectedTechnology(name="React", category="JavaScript Library", icon="react"))

        if soup.find(id="__nuxt") or "/_nuxt/" in all_assets:
            technologies.append(DetectedTechnology(name="Nuxt.js", category="Frontend Framework", icon="nuxt"))
            technologies.append(DetectedTechnology(name="Vue.js", category="JavaScript Framework", icon="vue"))

        if soup.find(attrs={"data-reactroot": True}) or "react" in all_assets:
            if not any(t.name == "React" for t in technologies):
                technologies.append(DetectedTechnology(name="React", category="JavaScript Library", icon="react"))

        if soup.find(attrs={"ng-app": True}) or soup.find(attrs={"ng-version": True}) or "angular" in all_assets:
            technologies.append(DetectedTechnology(name="Angular", category="JavaScript Framework", icon="angular"))

        # 5. Styling Frameworks
        # Tailwind CSS detection (popular utility classes or style signatures)
        if (
            "tailwind" in all_assets
            or re.search(r'class="[^"]*(?:flex|grid|hidden|p-\d|m-\d|text-[a-z]+-\d+|bg-[a-z]+-\d+)[^"]*"', html_text)
        ):
            technologies.append(DetectedTechnology(name="Tailwind CSS", category="UI / CSS Framework", icon="tailwind"))

        if "bootstrap" in all_assets or soup.find("link", href=re.compile(r"bootstrap", re.I)):
            technologies.append(DetectedTechnology(name="Bootstrap", category="UI / CSS Framework", icon="bootstrap"))

        # 6. Analytics & Tag Managers
        if "google-analytics.com" in all_assets or "googletagmanager.com" in all_assets or "gtag" in html_text:
            technologies.append(DetectedTechnology(name="Google Analytics / Tag Manager", category="Analytics", icon="analytics"))

        # Deduplicate by name
        unique_tech: Dict[str, DetectedTechnology] = {}
        for t in technologies:
            if t.name not in unique_tech:
                unique_tech[t.name] = t

        return list(unique_tech.values())
