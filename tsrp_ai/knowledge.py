"""Small, permission-aware Markdown knowledge base for TSRP AI."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "data" / "knowledge" / "manifest.json"


def _load_manifest() -> list[dict[str, Any]]:
    if not MANIFEST.exists():
        return []
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def _tokens(value: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]{2,}", value.lower())}


def search_knowledge(question: str, requester_role_ids: set[str] | None = None,
                     public_only: bool = False, limit: int = 4) -> list[dict[str, str]]:
    """Authorize each document BEFORE reading or scoring its contents."""
    requester_role_ids = requester_role_ids or set()
    question_tokens = _tokens(question)
    matches: list[tuple[int, dict[str, str]]] = []

    for entry in _load_manifest():
        visibility = entry.get("visibility", "restricted")
        allowed = {str(x) for x in entry.get("allowed_role_ids", [])}
        if visibility == "public":
            authorized = True
        else:
            authorized = bool(allowed) and bool(allowed.intersection(requester_role_ids))
        if public_only and visibility != "public":
            authorized = False
        if not authorized:
            continue

        rel_path = Path(str(entry.get("path", "")))
        if rel_path.is_absolute() or ".." in rel_path.parts:
            continue
        path = ROOT / rel_path
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        title = str(entry.get("title") or path.stem)
        body_tokens = _tokens(title + " " + content)
        score = len(question_tokens.intersection(body_tokens))
        if score:
            matches.append((score, {
                "title": title,
                "path": rel_path.as_posix(),
                "content": content[:9000],
            }))

    matches.sort(key=lambda item: item[0], reverse=True)
    return [doc for _, doc in matches[:limit]]
