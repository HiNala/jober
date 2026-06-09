from __future__ import annotations

import ipaddress


def coarse_geo_from_ip(client_ip: str) -> tuple[str | None, str | None]:
    """Derive coarse geo at ingest time. Raw IP is never stored."""
    try:
        addr = ipaddress.ip_address(client_ip.strip())
    except ValueError:
        return None, None

    if addr.is_private or addr.is_loopback or addr.is_link_local:
        return "XX", "private"

    # RFC 5737 documentation ranges — treat as unknown
    if isinstance(addr, ipaddress.IPv4Address):
        if addr in ipaddress.IPv4Network("192.0.2.0/24"):
            return None, None
        first_octet = int(addr) >> 24
        if first_octet in (1,):
            return "US", "na"
        if first_octet in (2, 5, 31, 37, 46, 51, 62, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95):
            return "EU", "eu"
        if first_octet in (103, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123):
            return "AP", "apac"
        if first_octet in (177, 179, 186, 189, 200, 201):
            return "BR", "sa"
        return "US", "na"

    if isinstance(addr, ipaddress.IPv6Address):
        if addr.ipv4_mapped:
            return coarse_geo_from_ip(str(addr.ipv4_mapped))
        return "EU", "eu"

    return None, None
