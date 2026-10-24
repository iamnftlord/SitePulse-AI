import asyncio
import ipaddress
import logging
import socket
from typing import Optional, Set
from urllib.parse import urlparse

logger = logging.getLogger("sitepulse.security")

# Blocked IP networks according to IANA and RFC standards
BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),          # Current network (only valid as source)
    ipaddress.ip_network("10.0.0.0/8"),          # RFC 1918 Private IPv4
    ipaddress.ip_network("100.64.0.0/10"),       # RFC 6598 Carrier-grade NAT
    ipaddress.ip_network("127.0.0.0/8"),         # RFC 1122 Loopback
    ipaddress.ip_network("169.254.0.0/16"),      # RFC 3927 Link-local / Cloud metadata (AWS, GCP, Azure)
    ipaddress.ip_network("172.16.0.0/12"),       # RFC 1918 Private IPv4
    ipaddress.ip_network("192.0.0.0/24"),        # RFC 6890 IETF Protocol Assignments
    ipaddress.ip_network("192.0.2.0/24"),        # RFC 5737 Documentation (TEST-NET-1)
    ipaddress.ip_network("192.88.99.0/24"),      # RFC 3068 6to4 Relay Anycast
    ipaddress.ip_network("192.168.0.0/16"),      # RFC 1918 Private IPv4
    ipaddress.ip_network("198.18.0.0/15"),       # RFC 2544 Network Benchmark Tests
    ipaddress.ip_network("198.51.100.0/24"),     # RFC 5737 Documentation (TEST-NET-2)
    ipaddress.ip_network("203.0.113.0/24"),      # RFC 5737 Documentation (TEST-NET-3)
    ipaddress.ip_network("224.0.0.0/4"),         # RFC 5771 Multicast
    ipaddress.ip_network("240.0.0.0/4"),         # RFC 1112 Reserved
    ipaddress.ip_network("255.255.255.255/32"),  # Broadcast
    # IPv6 Blocked Ranges
    ipaddress.ip_network("::/128"),              # Unspecified
    ipaddress.ip_network("::1/128"),             # Loopback
    ipaddress.ip_network("fc00::/7"),            # Unique Local (RFC 4193)
    ipaddress.ip_network("fe80::/10"),           # Link-Local Unicast (RFC 4291)
    ipaddress.ip_network("ff00::/8"),            # Multicast (RFC 4291)
]

BLOCKED_HOSTNAMES: Set[str] = {
    "localhost",
    "localhost.localdomain",
    "metadata.google.internal",
    "instance-data",
    "metadata",
}


class SSRFValidationError(Exception):
    """Raised when an inspected URL targets an internal or disallowed network resource."""
    pass


def is_ip_blocked(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Checks whether an IP address belongs to private, loopback, or cloud metadata ranges."""
    for network in BLOCKED_NETWORKS:
        if ip in network:
            return True
    return False


async def validate_target_url(url: str, allow_private: bool = False) -> str:
    """
    Validates submitted target URL against Server-Side Request Forgery (SSRF) threats.
    
    1. Enforces HTTP/HTTPS protocols only.
    2. Forbids embedded userinfo (e.g. user:pass@host).
    3. Resolves DNS asynchronously.
    4. Rejects all loopback, RFC 1918 private, link-local, and cloud metadata IPs.
    """
    clean_url = url.strip()
    parsed = urlparse(clean_url)

    if parsed.scheme.lower() not in ("http", "https"):
        raise SSRFValidationError(f"Invalid URL scheme '{parsed.scheme}'. Only HTTP and HTTPS are permitted.")

    if not parsed.netloc:
        raise SSRFValidationError("Target URL must contain a valid domain name or public host.")

    if parsed.username or parsed.password:
        raise SSRFValidationError("URLs with embedded user credentials (user:pass@) are not allowed.")

    hostname = parsed.hostname
    if not hostname:
        raise SSRFValidationError("Target URL contains an empty or unparseable host.")

    hostname_lower = hostname.lower().strip(".")
    if hostname_lower in BLOCKED_HOSTNAMES:
        raise SSRFValidationError(f"Inspection of restricted internal host '{hostname}' is forbidden.")

    if allow_private:
        return clean_url

    # Check if hostname is already a raw IP
    try:
        raw_ip = ipaddress.ip_address(hostname_lower)
        if is_ip_blocked(raw_ip):
            raise SSRFValidationError(f"Target IP address '{raw_ip}' is in a private or restricted network range.")
        return clean_url
    except ValueError:
        # Not a raw IP literal, proceed to asynchronous DNS resolution
        pass

    # Resolve hostname asynchronously to verify all associated IP addresses
    loop = asyncio.get_running_loop()
    try:
        addr_info = await loop.getaddrinfo(
            hostname,
            parsed.port or (443 if parsed.scheme == "https" else 80),
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as exc:
        raise SSRFValidationError(f"Could not resolve DNS for domain '{hostname}': {exc}") from exc

    resolved_ips: Set[str] = set()
    for entry in addr_info:
        sockaddr = entry[4]
        ip_str = sockaddr[0]
        resolved_ips.add(ip_str)

    if not resolved_ips:
        raise SSRFValidationError(f"No IP addresses found for host '{hostname}'.")

    for ip_str in resolved_ips:
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            if is_ip_blocked(ip_obj):
                logger.warning(f"Blocked SSRF attempt: '{hostname}' resolved to restricted IP '{ip_str}'")
                raise SSRFValidationError(
                    f"Access to '{hostname}' is denied because it resolves to a restricted internal address."
                )
        except ValueError:
            raise SSRFValidationError(f"Invalid IP address resolved from host '{hostname}'.")

    return clean_url
