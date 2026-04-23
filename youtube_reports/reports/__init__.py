"""Report implementations.

Importing this package registers all built-in reports in the registry.
"""
from youtube_reports.reports import clickbait  # noqa: F401  (registers report)
from youtube_reports.reports.base import Report, get_report, available_reports

__all__ = ["Report", "get_report", "available_reports"]
