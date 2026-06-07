from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class LabelEvidence:
    source: str
    text: str


@dataclass
class DiscoveredField:
    field_key: str
    label: str | None
    field_type: str
    required: bool
    options: list[str]
    current_value: str | None
    step_index: int
    is_upload: bool
    evidence: list[LabelEvidence] = field(default_factory=list)


_UPLOAD_HINTS = re.compile(r"upload|attach|resume|cover.?letter|cv\b|dropzone", re.I)
_NEXT_HINTS = re.compile(r"\b(next|continue|save and continue)\b", re.I)
_DATE_HINTS = re.compile(r"\b(date|start date|available|when can you)\b", re.I)
_SALARY_HINTS = re.compile(r"\b(salary|compensation|pay range|expected pay)\b", re.I)


def _normalize_label(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _label_for_id(html: str, element_id: str) -> LabelEvidence | None:
    match = re.search(
        rf'<label[^>]+for=["\']{re.escape(element_id)}["\'][^>]*>([^<]+)',
        html,
        re.I,
    )
    if match:
        return LabelEvidence("label[for]", _normalize_label(match.group(1)))
    return None


def _nearby_heading(html: str, pos: int) -> LabelEvidence | None:
    prefix = html[max(0, pos - 800) : pos]
    headings = re.findall(r"<h[1-4][^>]*>([^<]+)</h[1-4]>", prefix, re.I)
    if headings:
        return LabelEvidence("section_heading", _normalize_label(headings[-1]))
    return None


def _parse_options(tag: str) -> list[str]:
    return [_normalize_label(m) for m in re.findall(r"<option[^>]*>([^<]+)</option>", tag, re.I)]


def _field_key(name: str | None, element_id: str | None, idx: int) -> str:
    if name:
        return name
    if element_id:
        return element_id
    return f"field_{idx}"


def detect_steps(html: str) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = [{"index": 0, "title": "Step 1"}]
    for match in re.finditer(
        r'<(?:div|section)[^>]*(?:data-step|data-automation-id)=["\']([^"\']+)["\']',
        html,
        re.I,
    ):
        steps.append({"index": len(steps), "title": match.group(1)})
    if len(steps) == 1 and _NEXT_HINTS.search(html):
        steps.append({"index": 1, "title": "Step 2"})
    return steps


def scan_form_html(html: str, *, step_index: int = 0) -> list[DiscoveredField]:
    fields: list[DiscoveredField] = []
    idx = 0

    patterns = [
        (r"<input\b([^>]*)>", "input"),
        (r"<textarea\b([^>]*)>", "textarea"),
        (r"<select\b([^>]*)>[\s\S]*?</select>", "select"),
    ]
    for pattern, tag in patterns:
        for match in re.finditer(pattern, html, re.I):
            attrs = match.group(1) if tag != "select" else match.group(0)
            attr_blob = match.group(0)
            input_type = re.search(r'type=["\']([^"\']+)', attrs, re.I)
            ftype = (input_type.group(1).lower() if input_type else tag).lower()
            if ftype in ("hidden", "submit", "button", "image"):
                continue
            name_m = re.search(r'name=["\']([^"\']+)', attrs, re.I)
            id_m = re.search(r'id=["\']([^"\']+)', attrs, re.I)
            required = bool(re.search(r"\brequired\b", attrs, re.I))
            aria_label = re.search(r'aria-label=["\']([^"\']+)', attrs, re.I)
            placeholder = re.search(r'placeholder=["\']([^"\']+)', attrs, re.I)
            value_m = re.search(r'value=["\']([^"\']*)', attrs, re.I)

            evidence: list[LabelEvidence] = []
            element_id = id_m.group(1) if id_m else None
            if element_id:
                lbl = _label_for_id(html, element_id)
                if lbl:
                    evidence.append(lbl)
            if aria_label:
                evidence.append(LabelEvidence("aria-label", aria_label.group(1)))
            if placeholder:
                evidence.append(LabelEvidence("placeholder", placeholder.group(1)))
            heading = _nearby_heading(html, match.start())
            if heading:
                evidence.append(heading)

            label = evidence[0].text if evidence else None
            options = _parse_options(attr_blob) if tag == "select" else []
            is_upload = ftype == "file" or bool(_UPLOAD_HINTS.search(attr_blob + (label or "")))
            fields.append(
                DiscoveredField(
                    field_key=_field_key(
                        name_m.group(1) if name_m else None,
                        element_id,
                        idx,
                    ),
                    label=label,
                    field_type="file" if is_upload else ftype,
                    required=required,
                    options=options,
                    current_value=value_m.group(1) if value_m and value_m.group(1) else None,
                    step_index=step_index,
                    is_upload=is_upload,
                    evidence=evidence,
                )
            )
            idx += 1

    for match in re.finditer(
        r'<(?:div|span|button)[^>]+role=["\'](?:combobox|listbox)["\'][^>]*>',
        html,
        re.I,
    ):
        tag = match.group(0)
        aria = re.search(r'aria-label=["\']([^"\']+)', tag, re.I)
        evidence = [LabelEvidence("role", "combobox")]
        if aria:
            evidence.append(LabelEvidence("aria-label", aria.group(1)))
        label = aria.group(1) if aria else "Combobox"
        fields.append(
            DiscoveredField(
                field_key=f"combobox_{idx}",
                label=label,
                field_type="combobox",
                required=False,
                options=[],
                current_value=None,
                step_index=step_index,
                is_upload=False,
                evidence=evidence,
            )
        )
        idx += 1

    return fields


def scan_multistep_form(html: str) -> list[DiscoveredField]:
    steps = detect_steps(html)
    if len(steps) <= 1:
        return scan_form_html(html, step_index=0)

    chunks = re.split(r"<form\b", html, flags=re.I)
    if len(chunks) > 1:
        combined: list[DiscoveredField] = []
        for i, chunk in enumerate(chunks[1:], start=0):
            combined.extend(scan_form_html(f"<form{chunk}", step_index=i))
        if combined:
            return combined

    mid = len(html) // 2
    first = scan_form_html(html[:mid], step_index=0)
    second = scan_form_html(html[mid:], step_index=1)
    return first + second
