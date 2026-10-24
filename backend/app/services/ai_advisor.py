import json
import logging
from typing import Any, Dict, List, Optional
import httpx

from app.core.config import settings
from app.models.schemas import (
    AIActionPlanItem,
    AIAnalysisReport,
    AuditIssue,
    CategoryType,
    CrawledMetadata,
    SeverityLevel,
)

logger = logging.getLogger(__name__)


class AIAdvisor:
    """Orchestrates Ollama open-weight LLM prompts and deterministic fallback synthesis."""

    def __init__(self, base_url: str = settings.OLLAMA_BASE_URL, default_model: str = settings.OLLAMA_MODEL):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.timeout = settings.OLLAMA_REQUEST_TIMEOUT

    async def check_health(self) -> Dict[str, Any]:
        """Checks if Ollama is running and retrieves list of installed models."""
        url = f"{self.base_url}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name", "") for m in data.get("models", [])]
                    return {
                        "connected": True,
                        "available_models": models,
                        "active_model": self.default_model,
                    }
        except Exception:
            pass

        return {
            "connected": False,
            "available_models": [],
            "active_model": self.default_model,
        }

    async def generate_report(
        self,
        metadata: CrawledMetadata,
        issues: List[AuditIssue],
        category_scores: Dict[str, Any],
        model: Optional[str] = None,
        custom_prompt: Optional[str] = None,
    ) -> AIAnalysisReport:
        """Generates structured strategic recommendations using Ollama or fallback."""
        selected_model = model or self.default_model
        health = await self.check_health()

        if health["connected"]:
            try:
                report = await self._call_ollama(
                    metadata=metadata,
                    issues=issues,
                    category_scores=category_scores,
                    model=selected_model,
                    custom_prompt=custom_prompt,
                )
                if report:
                    return report
            except Exception as exc:
                logger.warning(f"Ollama generation failed ({exc}). Falling back to internal heuristic engine.")

        # If Ollama is unavailable or returned invalid JSON, execute deterministic synthesis
        return self._generate_heuristic_report(metadata, issues, category_scores, selected_model)

    async def _call_ollama(
        self,
        metadata: CrawledMetadata,
        issues: List[AuditIssue],
        category_scores: Dict[str, Any],
        model: str,
        custom_prompt: Optional[str] = None,
    ) -> Optional[AIAnalysisReport]:
        """Invokes Ollama API requesting strict JSON output."""
        tech_list = ", ".join([f"{t.name} ({t.category})" for t in metadata.technologies]) or "None detected"
        issues_summary = [
            {
                "id": i.id,
                "title": i.title,
                "category": i.category.value,
                "severity": i.severity.value,
                "description": i.description,
            }
            for i in issues
        ]

        system_prompt = (
            "You are SitePulse AI, a world-class principal web architect, security engineer, and performance consultant.\n"
            "Analyze the provided technical audit findings for the website and generate an actionable, senior-level review.\n"
            "Respond ONLY with a valid JSON object matching this schema:\n"
            "{\n"
            '  "executive_summary": "High-level 2-3 sentence strategic summary of the site\'s technical posture.",\n'
            '  "strengths": ["List of 2-4 areas where the site performed well"],\n'
            '  "critical_weaknesses": ["List of 2-4 highest-risk technical defects"],\n'
            '  "action_plan": [\n'
            "    {\n"
            '      "priority_rank": 1,\n'
            '      "action": "Clear imperative action title",\n'
            '      "category": "seo" | "security" | "performance" | "accessibility",\n'
            '      "effort": "Quick Win (< 15 mins)" | "Medium (1-3 hours)" | "Major (> 1 day)",\n'
            '      "expected_impact": "Tangible benefit of implementing this fix",\n'
            '      "code_example": "Code snippet, Nginx config, or HTML tag to apply"\n'
            "    }\n"
            "  ],\n"
            '  "custom_advice": "Specific high-value architectural advice for this tech stack"\n'
            "}\n"
            "Do not include markdown backticks around JSON if possible, or format as standard json."
        )

        user_content = (
            f"Website: {metadata.final_url}\n"
            f"Technologies: {tech_list}\n"
            f"Page Load: {metadata.load_time_ms}ms, Page Size: {round(metadata.page_size_bytes/1024, 1)} KB\n"
            f"Detected Issues ({len(issues)} total):\n{json.dumps(issues_summary, indent=2)}\n"
        )
        if custom_prompt:
            user_content += f"\nAdditional User Instructions: {custom_prompt}\n"

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": f"{system_prompt}\n\nTask:\n{user_content}",
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.2,
            },
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                raw_response = resp.json().get("response", "{}")
                parsed_data = json.loads(raw_response)

                action_plan_items: List[AIActionPlanItem] = []
                for item in parsed_data.get("action_plan", []):
                    action_plan_items.append(
                        AIActionPlanItem(
                            priority_rank=item.get("priority_rank", 1),
                            action=item.get("action", "Remediate issue"),
                            category=CategoryType(item.get("category", "seo")),
                            effort=item.get("effort", "Medium (1-3 hours)"),
                            expected_impact=item.get("expected_impact", "Improves site quality"),
                            code_example=item.get("code_example"),
                        )
                    )

                return AIAnalysisReport(
                    model_used=model,
                    executive_summary=parsed_data.get("executive_summary", "Site analysis completed."),
                    strengths=parsed_data.get("strengths", []),
                    critical_weaknesses=parsed_data.get("critical_weaknesses", []),
                    action_plan=action_plan_items,
                    custom_advice=parsed_data.get("custom_advice"),
                    is_fallback=False,
                )

        return None

    def _generate_heuristic_report(
        self,
        metadata: CrawledMetadata,
        issues: List[AuditIssue],
        category_scores: Dict[str, Any],
        model: str,
    ) -> AIAnalysisReport:
        """Deterministic heuristic intelligence engine used when Ollama is offline or warming up."""
        critical_issues = [i for i in issues if i.severity == SeverityLevel.CRITICAL]
        high_issues = [i for i in issues if i.severity == SeverityLevel.HIGH]
        medium_issues = [i for i in issues if i.severity == SeverityLevel.MEDIUM]

        # Determine Strengths
        strengths: List[str] = []
        if metadata.is_https:
            strengths.append("HTTPS transport encryption is actively enforced.")
        if metadata.load_time_ms < 600:
            strengths.append(f"Fast initial server response time ({metadata.load_time_ms}ms).")
        if metadata.title and 20 <= metadata.title_length <= 65:
            strengths.append(f"Properly bounded <title> tag ({metadata.title_length} characters).")
        if metadata.has_viewport:
            strengths.append("Responsive mobile viewport tag is properly configured.")
        if metadata.technologies:
            tech_names = ", ".join([t.name for t in metadata.technologies[:3]])
            strengths.append(f"Identified modern stack components: {tech_names}.")
        if not strengths:
            strengths.append("Site is live, responsive, and accessible via standard HTTP/S protocols.")

        # Determine Weaknesses
        weaknesses: List[str] = []
        if not metadata.is_https:
            weaknesses.append("Insecure plain HTTP connection exposes traffic to eavesdropping and browser security warnings.")
        if not metadata.security_headers.get("content-security-policy"):
            weaknesses.append("Missing Content-Security-Policy (CSP) exposes frontend to cross-site scripting (XSS).")
        if not metadata.security_headers.get("strict-transport-security"):
            weaknesses.append("Lack of HSTS allows SSL-stripping vulnerabilities on first user visits.")
        if not metadata.meta_description:
            weaknesses.append("Absence of meta description harms search engine result click-through rates (CTR).")
        if metadata.load_time_ms > 1200:
            weaknesses.append(f"Elevated server response latency ({metadata.load_time_ms}ms) impairs Core Web Vitals.")
        if not metadata.html_lang:
            weaknesses.append("Missing HTML language attribute compromises accessibility for screen readers.")
        if not weaknesses:
            weaknesses.append("Minor optimization opportunities in header hygiene and social metadata.")

        # Build prioritized action plan
        action_plan: List[AIActionPlanItem] = []
        rank = 1

        # Check for critical security headers
        if not metadata.security_headers.get("strict-transport-security"):
            action_plan.append(
                AIActionPlanItem(
                    priority_rank=rank,
                    action="Configure Strict-Transport-Security (HSTS) with Preload",
                    category=CategoryType.SECURITY,
                    effort="Quick Win (< 15 mins)",
                    expected_impact="Protects 100% of returning users against SSL-stripping and downgrade attacks.",
                    code_example="Strict-Transport-Security: max-age=31536000; includeSubDomains; preload",
                )
            )
            rank += 1

        if not metadata.security_headers.get("content-security-policy"):
            action_plan.append(
                AIActionPlanItem(
                    priority_rank=rank,
                    action="Implement Content-Security-Policy Header",
                    category=CategoryType.SECURITY,
                    effort="Medium (1-3 hours)",
                    expected_impact="Drastically mitigates Cross-Site Scripting (XSS) and unauthorized data exfiltration.",
                    code_example="Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https:; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;",
                )
            )
            rank += 1

        if not metadata.meta_description:
            action_plan.append(
                AIActionPlanItem(
                    priority_rank=rank,
                    action="Add Optimized Meta Description Tag",
                    category=CategoryType.SEO,
                    effort="Quick Win (< 15 mins)",
                    expected_impact="Boosts organic search click-through rate (CTR) by up to 25%.",
                    code_example=f'<meta name="description" content="Official site for {metadata.title or "your brand"}. Explore our developer solutions and platform.">',
                )
            )
            rank += 1

        if not metadata.has_open_graph:
            action_plan.append(
                AIActionPlanItem(
                    priority_rank=rank,
                    action="Add Social Graph & Twitter Card Meta Tags",
                    category=CategoryType.SEO,
                    effort="Quick Win (< 15 mins)",
                    expected_impact="Transforms plain link shares on Slack, Twitter/X, and LinkedIn into rich preview cards.",
                    code_example='<meta property="og:title" content="Site Title" />\n<meta property="og:description" content="Description" />\n<meta property="og:image" content="https://example.com/og.png" />\n<meta name="twitter:card" content="summary_large_image" />',
                )
            )
            rank += 1

        if metadata.images_missing_alt > 0:
            action_plan.append(
                AIActionPlanItem(
                    priority_rank=rank,
                    action=f"Remediate {metadata.images_missing_alt} Missing Image Alt Attributes",
                    category=CategoryType.ACCESSIBILITY,
                    effort="Medium (1-3 hours)",
                    expected_impact="Ensures WCAG 2.1 compliance and allows search engines to index image assets.",
                    code_example='<img src="dashboard.webp" alt="SitePulse AI real-time dashboard analytics preview" />',
                )
            )
            rank += 1

        if not metadata.html_lang:
            action_plan.append(
                AIActionPlanItem(
                    priority_rank=rank,
                    action="Declare Primary Language in <html> Tag",
                    category=CategoryType.ACCESSIBILITY,
                    effort="Quick Win (< 15 mins)",
                    expected_impact="Enables correct speech synthesis in assistive screen readers and automated translation tools.",
                    code_example='<html lang="en">',
                )
            )
            rank += 1

        # Executive summary
        total_issues_count = len(issues)
        summary = (
            f"SitePulse AI evaluated {metadata.final_url} and identified {total_issues_count} technical improvement areas "
            f"across SEO, Security, Performance, and Accessibility. "
            f"The primary risks center around {'insecure transport and ' if not metadata.is_https else ''}"
            f"missing defensive HTTP security headers and search engine visibility gaps. "
            f"Following the prioritized action plan below will substantially enhance the site's security posture and Core Web Vitals."
        )

        custom_advice = (
            "Recommendation for production: deploy an edge reverse proxy (Cloudflare, Fastly, or Nginx) "
            "to automate HTTP security headers, Brotli compression, and SSL enforcement without requiring application code changes."
        )

        return AIAnalysisReport(
            model_used=f"{model} (Rule-Based Synthesis Engine)",
            executive_summary=summary,
            strengths=strengths,
            critical_weaknesses=weaknesses,
            action_plan=action_plan,
            custom_advice=custom_advice,
            is_fallback=True,
        )

    async def chat(
        self,
        message: str,
        url: Optional[str] = None,
        context_issues: Optional[List[AuditIssue]] = None,
        model: Optional[str] = None,
    ) -> str:
        """Handles interactive developer questions about fixes, configs, or recommendations."""
        selected_model = model or self.default_model
        health = await self.check_health()

        if health["connected"]:
            try:
                system_prompt = (
                    "You are SitePulse AI Assistant, an expert web engineering copilot. "
                    "Provide clear, concise, actionable solutions with complete code snippets (e.g. Nginx, Apache, HTML, React, Next.js). "
                    "Be friendly, professional, and directly address the user's question."
                )
                context_str = ""
                if url:
                    context_str += f"Target Website: {url}\n"
                if context_issues:
                    context_str += f"Issues on this site:\n" + "\n".join([f"- [{i.category.value}] {i.title}: {i.description}" for i in context_issues[:8]])

                prompt = f"{system_prompt}\n\nContext:\n{context_str}\n\nUser Question: {message}\n\nAnswer:"
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(
                        f"{self.base_url}/api/generate",
                        json={"model": selected_model, "prompt": prompt, "stream": False},
                    )
                    if resp.status_code == 200:
                        return resp.json().get("response", "").strip()
            except Exception as exc:
                logger.warning(f"Ollama chat error: {exc}")

        # Intelligent fallback chat replies based on topic
        lower_msg = message.lower()
        if "csp" in lower_msg or "content security policy" in lower_msg:
            return (
                "**Content-Security-Policy (CSP) Implementation Guide**:\n\n"
                "A solid baseline CSP directive for modern websites:\n"
                "```http\n"
                "Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https:; style-src 'self' 'unsafe-inline' https:; img-src 'self' data: https:; font-src 'self' data: https:; connect-src 'self' https:;\n"
                "```\n\n"
                "**In Nginx**:\n"
                "```nginx\n"
                "add_header Content-Security-Policy \"default-src 'self'; script-src 'self' 'unsafe-inline' https:; style-src 'self' 'unsafe-inline' https:; img-src 'self' data: https:;\" always;\n"
                "```\n"
                "Start with `Content-Security-Policy-Report-Only` first to monitor violations in your browser console before enforcing it."
            )
        elif "hsts" in lower_msg or "strict-transport-security" in lower_msg:
            return (
                "**HTTP Strict Transport Security (HSTS)**:\n\n"
                "HSTS instructs browsers to strictly communicate with your server over HTTPS only.\n\n"
                "**Nginx Configuration**:\n"
                "```nginx\n"
                "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains; preload\" always;\n"
                "```\n\n"
                "Once configured and tested, you can submit your domain to the official Chrome HSTS preload list at [hstspreload.org](https://hstspreload.org)."
            )
        elif "sitemap" in lower_msg or "robots" in lower_msg:
            return (
                "**Robots.txt & Sitemap Setup**:\n\n"
                "Create a `robots.txt` in your website root:\n"
                "```txt\n"
                "User-agent: *\n"
                "Allow: /\n\n"
                "Sitemap: https://yourdomain.com/sitemap.xml\n"
                "```\n\n"
                "For your `sitemap.xml`, ensure all canonical URLs are listed with `<lastmod>` timestamps for rapid re-crawling."
            )
        elif "alt" in lower_msg or "accessibility" in lower_msg or "a11y" in lower_msg:
            return (
                "**Image Alt Attribute Best Practices**:\n\n"
                "1. **Informational Images**: Describe the content and function accurately:\n"
                '   `<img src="chart.png" alt="Bar chart showing 42% revenue increase in Q3" />`\n'
                "2. **Decorative Images**: Use empty alt so screen readers skip them:\n"
                '   `<img src="divider.svg" alt="" role="presentation" />`\n'
                "3. **Buttons/Links containing only icons**: Provide an `aria-label` or `alt`:\n"
                '   `<button aria-label="Close modal"><img src="x.svg" alt="" /></button>`'
            )
        else:
            return (
                f"**SitePulse AI Advisory**:\n\n"
                f"Regarding your query: *\"{message}\"*:\n\n"
                "To optimize your website for maximum reliability, SEO ranking, and security:\n"
                "1. **Deploy Security Headers**: Implement HSTS, CSP, and X-Content-Type-Options via your CDN/reverse proxy.\n"
                "2. **Optimize Core Web Vitals**: Compress assets with WebP/AVIF, enable Gzip/Brotli, and lazy-load below-the-fold media.\n"
                "3. **Ensure Semantic HTML**: Maintain a strict heading hierarchy (one H1 per page), declare `lang='en'`, and specify descriptive meta descriptions.\n\n"
                "*Note: Connect Ollama locally with `ollama run gemma4` to unlock continuous contextual deep-dive conversational reasoning.*"
            )


ai_advisor = AIAdvisor()
