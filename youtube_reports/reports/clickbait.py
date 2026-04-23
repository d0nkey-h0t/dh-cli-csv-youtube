"""Clickbait report: high CTR, low retention."""
from __future__ import annotations

from typing import Iterable

from youtube_reports.reports.base import Report

CTR_THRESHOLD = 15.0
RETENTION_THRESHOLD = 40.0


def _to_float(value: str) -> float | None:
    """Parse a CSV cell as float, treating blanks as missing."""
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


class ClickbaitReport(Report):
    """Videos that look like clickbait: CTR > 15 and retention_rate < 40."""

    name = "clickbait"
    headers = ("title", "ctr", "retention_rate")

    def build(self, rows: Iterable[dict[str, str]]) -> list[list[object]]:
        selected: list[tuple[str, float, float]] = []
        for row in rows:
            ctr = _to_float(row.get("ctr", ""))
            retention = _to_float(row.get("retention_rate", ""))
            title = (row.get("title") or "").strip()
            if ctr is None or retention is None or not title:
                continue
            if ctr > CTR_THRESHOLD and retention < RETENTION_THRESHOLD:
                selected.append((title, ctr, retention))

        selected.sort(key=lambda item: item[1], reverse=True)
        return [[title, ctr, retention] for title, ctr, retention in selected]
