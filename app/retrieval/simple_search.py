from __future__ import annotations

import re
from typing import Any


TOKEN_RE = re.compile(r"[A-Za-z0-9_\-]+")


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text)]


def score_text(query: str, text: str, title: str | None = None) -> float:
    query_tokens = tokenize(query)
    if not query_tokens:
        return 0.0

    haystack = f"{title or ''} {text}".strip().lower()
    haystack_tokens = tokenize(haystack)
    if not haystack_tokens:
        return 0.0

    score = 0.0

    for token in query_tokens:
        token_count = haystack_tokens.count(token)
        score += token_count

        if title and token in title.lower():
            score += 1.5

    if query.lower() in haystack:
        score += 2.0

    max_score = max(len(query_tokens) * 4.0, 1.0)
    normalized = min(score / max_score, 1.0)
    return round(normalized, 4)


def top_k_search(
    query: str,
    rows: list[dict[str, Any]],
    *,
    text_field: str = "text",
    title_field: str = "title",
    top_k: int = 5,
) -> list[dict[str, Any]]:
    scored: list[tuple[float, dict[str, Any]]] = []

    for row in rows:
        text = str(row.get(text_field, "") or "")
        title = row.get(title_field)
        score = score_text(query, text, title)
        if score > 0:
            scored.append((score, row))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {**row, "_score": score}
        for score, row in scored[:top_k]
    ]