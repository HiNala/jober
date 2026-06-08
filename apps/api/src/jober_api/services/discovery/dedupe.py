from __future__ import annotations


def upsert_key(company: str, role: str, url: str | None) -> tuple[str, str, str | None]:
    return (company.casefold(), role.casefold(), url or None)


def candidate_key(company: str, role: str, url: str | None) -> str:
    company_key, role_key, url_key = upsert_key(company, role, url)
    return f"{company_key}|{role_key}|{url_key or ''}"
