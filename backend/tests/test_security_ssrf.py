import pytest
from app.core.security import SSRFValidationError, validate_target_url, is_ip_blocked
import ipaddress


def test_blocked_ip_ranges():
    """Verifies that RFC 1918, loopback, and metadata IPs are correctly recognized as blocked."""
    assert is_ip_blocked(ipaddress.ip_address("127.0.0.1"))
    assert is_ip_blocked(ipaddress.ip_address("10.0.0.1"))
    assert is_ip_blocked(ipaddress.ip_address("172.16.0.1"))
    assert is_ip_blocked(ipaddress.ip_address("192.168.1.1"))
    assert is_ip_blocked(ipaddress.ip_address("169.254.169.254"))
    assert is_ip_blocked(ipaddress.ip_address("0.0.0.0"))
    assert is_ip_blocked(ipaddress.ip_address("::1"))

    # Public IP should not be blocked
    assert not is_ip_blocked(ipaddress.ip_address("8.8.8.8"))
    assert not is_ip_blocked(ipaddress.ip_address("1.1.1.1"))
    assert not is_ip_blocked(ipaddress.ip_address("140.82.121.3"))


@pytest.mark.asyncio
async def test_ssrf_rejects_disallowed_schemes():
    """Rejects file://, ftp://, gopher:// schemes."""
    with pytest.raises(SSRFValidationError, match="Invalid URL scheme"):
        await validate_target_url("file:///etc/passwd")

    with pytest.raises(SSRFValidationError, match="Invalid URL scheme"):
        await validate_target_url("ftp://example.com/archive.zip")

    with pytest.raises(SSRFValidationError, match="Invalid URL scheme"):
        await validate_target_url("gopher://127.0.0.1:70")


@pytest.mark.asyncio
async def test_ssrf_rejects_embedded_credentials():
    """Rejects URLs with user:password embedded credentials."""
    with pytest.raises(SSRFValidationError, match="embedded user credentials"):
        await validate_target_url("http://admin:secret@example.com")


@pytest.mark.asyncio
async def test_ssrf_rejects_raw_private_ips():
    """Rejects raw private and cloud metadata IP literals."""
    with pytest.raises(SSRFValidationError, match="private or restricted"):
        await validate_target_url("http://127.0.0.1/")

    with pytest.raises(SSRFValidationError, match="private or restricted"):
        await validate_target_url("http://169.254.169.254/latest/meta-data/")

    with pytest.raises(SSRFValidationError, match="private or restricted"):
        await validate_target_url("http://10.0.0.5:8080/internal")

    with pytest.raises(SSRFValidationError, match="private or restricted"):
        await validate_target_url("http://192.168.1.100/admin")


@pytest.mark.asyncio
async def test_ssrf_rejects_local_hostnames():
    """Rejects localhost and reserved internal hostnames."""
    with pytest.raises(SSRFValidationError, match="restricted internal host"):
        await validate_target_url("http://localhost:3000/")

    with pytest.raises(SSRFValidationError, match="restricted internal host"):
        await validate_target_url("http://metadata.google.internal/computeMetadata/v1/")


@pytest.mark.asyncio
async def test_ssrf_allows_valid_public_domain():
    """Allows valid public domain names."""
    url = "https://example.com"
    validated = await validate_target_url(url)
    assert validated == url
