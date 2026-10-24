from bs4 import BeautifulSoup
from app.services.tech_detector import TechDetector


def test_tech_detector_identifies_nextjs_and_tailwind():
    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <meta name="generator" content="Next.js" />
        <script src="/_next/static/chunks/main.js"></script>
      </head>
      <body class="flex flex-col min-h-screen bg-slate-900 text-white">
        <div id="__next">
          <h1 class="text-3xl font-bold">Hello SitePulse</h1>
        </div>
      </body>
    </html>
    """
    headers = {
        "server": "cloudflare",
        "cf-ray": "12345678",
        "x-nextjs-cache": "HIT",
    }
    soup = BeautifulSoup(html, "html.parser")

    techs = TechDetector.detect(soup, headers, html)
    tech_names = [t.name for t in techs]

    assert "Next.js" in tech_names
    assert "React" in tech_names
    assert "Tailwind CSS" in tech_names
    assert "Cloudflare" in tech_names


def test_tech_detector_identifies_wordpress_and_nginx():
    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <meta name="generator" content="WordPress 6.4.2" />
        <link rel="stylesheet" href="https://example.com/wp-content/themes/theme/style.css">
      </head>
      <body>
        <h1>Blog Post</h1>
      </body>
    </html>
    """
    headers = {
        "server": "nginx/1.22.1",
        "x-powered-by": "PHP/8.2.0",
    }
    soup = BeautifulSoup(html, "html.parser")

    techs = TechDetector.detect(soup, headers, html)
    tech_names = [t.name for t in techs]

    assert "WordPress" in tech_names
    assert "Nginx" in tech_names
    assert "PHP" in tech_names
