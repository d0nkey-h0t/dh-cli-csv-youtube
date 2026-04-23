"""Base class and registry for reports.

New reports are added by subclassing :class:`Report` and setting a unique
``name``. Subclasses are registered automatically.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, Iterable, Sequence


_REGISTRY: dict[str, type["Report"]] = {}


class Report(ABC):
    """Abstract base class for a CSV-derived report.

    Subclasses must define a unique ``name`` and implement
    :meth:`build`, which returns the table rows to display, and
    :attr:`headers`, which lists the column names.
    """

    name: ClassVar[str] = ""
    headers: ClassVar[Sequence[str]] = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if not cls.name:
            return
        if cls.name in _REGISTRY:
            raise ValueError(f"Report '{cls.name}' is already registered")
        _REGISTRY[cls.name] = cls

    @abstractmethod
    def build(self, rows: Iterable[dict[str, str]]) -> list[list[object]]:
        """Return the table rows that make up the report."""


def get_report(name: str) -> Report:
    """Instantiate a registered report by name."""
    try:
        cls = _REGISTRY[name]
    except KeyError as exc:
        raise ValueError(
            f"Unknown report '{name}'. Available: {', '.join(available_reports()) or 'none'}"
        ) from exc
    return cls()


def available_reports() -> list[str]:
    """Return the sorted list of registered report names."""
    return sorted(_REGISTRY)
