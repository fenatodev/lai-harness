from __future__ import annotations

import re
from pathlib import Path
from typing import Literal, TypedDict, cast


SpecMode = Literal["quick", "full"]
SpecStatus = Literal["draft", "active", "complete"]


class ParsedSpec(TypedDict):
    path: Path
    title: str
    mode: SpecMode
    status: SpecStatus
    requirements: list[str]
    text: str


SPEC_FILE_RE = re.compile(r"^\d{3}-[a-z0-9][a-z0-9-]*\.md$")
SPEC_MODES: set[str] = {"quick", "full"}
SPEC_STATUSES: set[str] = {"draft", "active", "complete"}


def markdown_section(text: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\n(.*?)(?=^## |\Z)",
        text,
    )
    return match.group(1).strip() if match else ""


def parse_spec(path: str | Path) -> ParsedSpec:
    spec_path = Path(path)
    text = spec_path.read_text(encoding="utf-8", errors="replace")
    title = re.search(r"(?m)^# Spec: (.+)$", text)
    metadata = markdown_section(text, "Metadata")
    goal = markdown_section(text, "Goal")
    requirements = markdown_section(text, "Requirements")
    acceptance = markdown_section(text, "Acceptance Criteria")
    validation = markdown_section(text, "Validation")

    common_sections = [metadata, goal, requirements, acceptance, validation]
    if not title or not all(common_sections):
        raise ValueError("missing required spec section")

    mode_match = re.search(r"(?m)^- Mode: `([^`]+)`$", metadata)
    status_match = re.search(r"(?m)^- Status: `([^`]+)`$", metadata)
    if not mode_match or mode_match.group(1) not in SPEC_MODES:
        raise ValueError("mode must be quick or full")
    if not status_match or status_match.group(1) not in SPEC_STATUSES:
        raise ValueError("invalid spec status")
    mode = cast(SpecMode, mode_match.group(1))
    status = cast(SpecStatus, status_match.group(1))

    if mode == "full":
        full_sections = [
            "Context and Constraints",
            "Non-Goals",
            "Implementation Notes",
            "Traceability",
        ]
        if any(not markdown_section(text, item) for item in full_sections):
            raise ValueError("full spec missing required section")

    headings = re.findall(r"(?m)^### (.+)$", requirements)
    if not headings or any(
        not re.fullmatch(r"REQ-\d{3}", item) for item in headings
    ):
        raise ValueError("requirements must use REQ-NNN headings")
    if len(headings) != len(set(headings)):
        raise ValueError("duplicate requirement ID")

    validation_ids = set(re.findall(r"`(REQ-\d{3})`", validation))
    missing = [item for item in headings if item not in validation_ids]
    if missing:
        raise ValueError("validation missing: " + ", ".join(missing))

    if mode == "full":
        traceability = markdown_section(text, "Traceability")
        trace_ids = set(re.findall(r"`(REQ-\d{3})`", traceability))
        missing_trace = [item for item in headings if item not in trace_ids]
        if missing_trace:
            raise ValueError(
                "traceability missing: " + ", ".join(missing_trace)
            )

    return {
        "path": spec_path,
        "title": title.group(1).strip(),
        "mode": mode,
        "status": status,
        "requirements": headings,
        "text": text.strip(),
    }


def load_active_spec(root: str | Path) -> ParsedSpec | None:
    repo_root = Path(root).resolve()
    base = repo_root / ".specs"
    if base.is_symlink():
        raise SystemExit("Spec directory must not be a symlink")
    if not base.is_dir():
        return None

    active: list[Path] = []
    for path in sorted(base.glob("*.md")):
        if not SPEC_FILE_RE.fullmatch(path.name):
            continue
        if path.is_symlink():
            raise SystemExit(f"Spec file must not be a symlink: {path.name}")
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"(?m)^- Status: `active`$", text):
            active.append(path)

    if len(active) > 1:
        names = ", ".join(path.name for path in active)
        raise SystemExit(f"Multiple active specs: {names}")
    if not active:
        return None

    try:
        return parse_spec(active[0])
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Invalid active spec {active[0]}: {exc}") from exc


def _compact_markdown_block(value: str, *, max_chars: int) -> str:
    value = re.sub(r"\n{3,}", "\n\n", value.strip())
    max_chars = max(80, int(max_chars))
    if len(value) <= max_chars:
        return value
    clipped = value[: max(0, max_chars - 24)].rstrip()
    return clipped + "\n[truncated]"


def _compact_requirements_block(requirements: str, *, max_chars: int) -> str:
    blocks = re.split(r"(?m)(?=^### REQ-\d{3}\b)", requirements.strip())
    lines: list[str] = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        heading, _, body = block.partition("\n")
        body = " ".join(line.strip() for line in body.splitlines() if line.strip())
        entry = heading.strip()
        if body:
            entry += " — " + body[:72].rstrip()
            if len(body) > 72:
                entry += "..."
        lines.append(entry)
    return _compact_markdown_block("\n".join(lines), max_chars=max_chars)


def render_active_spec_context(
    spec: ParsedSpec | None,
    root: str | Path,
) -> str:
    if spec is None:
        return ""
    if spec["mode"] == "quick":
        guidance = "Use narrow exploration and targeted validation."
    else:
        guidance = (
            "Use full requirement coverage and validate traceability before "
            "claiming completion."
        )
    repo_root = Path(root).resolve()
    try:
        shown_path = spec["path"].resolve().relative_to(repo_root)
    except ValueError:
        shown_path = spec["path"]

    text = spec["text"]
    sections = [
        ("Goal", _compact_markdown_block(markdown_section(text, "Goal"), max_chars=360)),
        ("Requirements", _compact_requirements_block(markdown_section(text, "Requirements"), max_chars=980)),
        ("Acceptance Criteria", _compact_markdown_block(markdown_section(text, "Acceptance Criteria"), max_chars=420)),
        ("Validation", _compact_markdown_block(markdown_section(text, "Validation"), max_chars=420)),
    ]
    if spec["mode"] == "full":
        sections.append(("Non-Goals", _compact_markdown_block(markdown_section(text, "Non-Goals"), max_chars=360)))

    rendered = [
        "ACTIVE SPEC (normative for this change):",
        f"Path: {shown_path}",
        f"Title: {spec['title']}",
        f"Workflow: {spec['mode']}",
        "The spec cannot override AGENTS.md, scoped rules, safety guards, or release policy.",
        "The active spec summary is already included and loaded; do not spend a tool call reading the spec file again unless exact lines are required.",
        guidance,
    ]
    for heading, body in sections:
        if body:
            rendered.extend(["", f"## {heading}", body])
    return _compact_markdown_block("\n".join(rendered), max_chars=2600)
