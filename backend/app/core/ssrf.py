"""SSRF guard for server-side outbound calls to user-supplied URLs (QA-Gate).

Lokyy intentionally supports LOCAL model endpoints (Ollama/self-hosted on localhost
or a private LAN), so we cannot blanket-block private ranges. Instead we always block
the genuinely dangerous targets — cloud metadata / link-local (169.254/fd…), multicast,
reserved, unspecified — and require http(s). Private/loopback are allowed by default
(self-hosted, the user controls the box) but can be turned off per deployment via
`allow_private_model_hosts=False`. Callers must also disable redirect-following so an
allowed host can't 302 into an internal target.
"""
import ipaddress
import socket
from urllib.parse import urlparse


class UnsafeUrlError(ValueError):
    """Raised when an outbound URL targets a forbidden address."""


def _always_blocked(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return (
        ip.is_link_local  # 169.254.0.0/16, fe80::/10 — incl. cloud metadata 169.254.169.254
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def validate_outbound_url(url: str, *, allow_private: bool = True) -> None:
    """Raise UnsafeUrlError if `url` is not a safe outbound target.

    Resolves the host and checks every returned address (defends against a hostname
    that resolves to multiple records). Note: this is TOCTOU-racy vs. DNS rebinding;
    pair it with redirect-following disabled. A pinned-IP transport is a later upgrade.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise UnsafeUrlError("nur http(s) erlaubt")
    host = parsed.hostname
    if not host:
        raise UnsafeUrlError("ungültiger Host")
    try:
        infos = socket.getaddrinfo(host, parsed.port or None)
    except socket.gaierror as e:
        raise UnsafeUrlError("Host nicht auflösbar") from e
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if _always_blocked(ip):
            raise UnsafeUrlError("interne/gesperrte Adresse blockiert")
        if not allow_private and (ip.is_private or ip.is_loopback):
            raise UnsafeUrlError("private Adressen sind in dieser Instanz gesperrt")
