from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

from jober_api.config import settings

_BLOCKED_HOSTS = frozenset({"localhost", "metadata.google.internal"})


class OutboundUrlError(ValueError):
    pass


def validate_outbound_url(url: str) -> str:
    """Reject URLs that could target internal networks (SSRF guard)."""
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https"):
        msg = "Only http(s) URLs are allowed"
        raise OutboundUrlError(msg)
    if settings.jober_env == "production" and parsed.scheme != "https":
        msg = "Only https URLs are allowed in production"
        raise OutboundUrlError(msg)
    host = (parsed.hostname or "").lower().rstrip(".")
    if not host or host in _BLOCKED_HOSTS or host.endswith(".local"):
        msg = "URL host is not allowed"
        raise OutboundUrlError(msg)
    try:
        addr_infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        msg = "URL host could not be resolved"
        raise OutboundUrlError(msg) from exc
    for info in addr_infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            msg = "URL resolves to a private or reserved address"
            raise OutboundUrlError(msg)
    return url
