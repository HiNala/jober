from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from playwright.sync_api import Locator, Page


@dataclass(frozen=True)
class ResolvedLocator:
    strategy: str
    selector: str
    locator: Locator


def _first_visible(locator: Locator) -> Locator | None:
    count = locator.count()
    for i in range(count):
        candidate = locator.nth(i)
        try:
            if candidate.is_visible():
                return candidate
        except Exception:  # noqa: BLE001
            continue
    return locator.first if count > 0 else None


def resolve_by_label(page: Page, label: str) -> ResolvedLocator | None:
    loc = page.get_by_label(label, exact=False)
    chosen = _first_visible(loc)
    if chosen is not None:
        return ResolvedLocator("label", f'label:"{label}"', chosen)
    return None


def resolve_by_role(
    page: Page,
    role: str,
    *,
    name: str | None = None,
) -> ResolvedLocator | None:
    loc = page.get_by_role(cast(Any, role), name=name) if name else page.get_by_role(cast(Any, role))
    chosen = _first_visible(loc)
    if chosen is not None:
        return ResolvedLocator("role", f'role={role} name={name!r}', chosen)
    return None


def resolve_by_placeholder(page: Page, placeholder: str) -> ResolvedLocator | None:
    loc = page.get_by_placeholder(placeholder, exact=False)
    chosen = _first_visible(loc)
    if chosen is not None:
        return ResolvedLocator("placeholder", f'placeholder:"{placeholder}"', chosen)
    return None


def resolve_by_stable_attrs(
    page: Page,
    *,
    field_key: str,
    label: str | None,
) -> ResolvedLocator | None:
    for selector in (
        f'[name="{field_key}"]',
        f'#{field_key}',
        f'[data-testid="{field_key}"]',
        f'[id="{field_key}"]',
    ):
        loc = page.locator(selector)
        chosen = _first_visible(loc)
        if chosen is not None:
            return ResolvedLocator("stable_attr", selector, chosen)
    if label:
        loc = page.locator(f'label:has-text("{label}") + input, label:has-text("{label}") + select')
        chosen = _first_visible(loc)
        if chosen is not None:
            return ResolvedLocator("text_near_field", f'label+input:{label}', chosen)
    return None


def resolve_field_locator(
    page: Page,
    *,
    label: str | None,
    field_key: str,
    field_type: str | None,
) -> ResolvedLocator:
    ftype = (field_type or "text").lower()
    role = "combobox" if ftype == "combobox" else None
    if role and label:
        resolved = resolve_by_role(page, role, name=label)
        if resolved:
            return resolved
    if label:
        for resolver in (
            lambda: resolve_by_label(page, label),
            lambda: resolve_by_placeholder(page, label),
            lambda: resolve_by_role(
                page,
                "textbox" if ftype in ("text", "email", "tel", "url") else ftype,
                name=label,
            ),
        ):
            resolved = resolver()
            if resolved:
                return resolved
    resolved = resolve_by_stable_attrs(page, field_key=field_key, label=label)
    if resolved:
        return resolved
    msg = f"Could not resolve locator for {label or field_key}"
    raise ValueError(msg)


def resolve_file_input(
    page: Page,
    *,
    control: str,
    field_key: str,
) -> ResolvedLocator:
    for resolver in (
        lambda: resolve_by_label(page, control),
        lambda: resolve_by_role(page, "button", name=control),
        lambda: resolve_by_stable_attrs(page, field_key=field_key, label=control),
    ):
        resolved = resolver()
        if resolved:
            input_loc = resolved.locator.locator('input[type="file"]')
            if input_loc.count() > 0:
                return ResolvedLocator(
                    f"{resolved.strategy}+file",
                    f'{resolved.selector} input[type="file"]',
                    input_loc.first,
                )
            if resolved.locator.evaluate("el => el.type === 'file'"):
                return resolved
    dropzone = page.locator(
        f'.dropzone:has-text("{control}"), [data-testid*="drop"]:has-text("{control}")'
    )
    chosen = _first_visible(dropzone)
    if chosen is not None:
        nested = chosen.locator('input[type="file"]')
        if nested.count() > 0:
            return ResolvedLocator("dropzone+file", "dropzone input[type=file]", nested.first)
    msg = f"Could not resolve upload control for {control}"
    raise ValueError(msg)
