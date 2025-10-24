"""Domain models for KuzuAlerts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class Impact(str, Enum):
    """Impact levels used across the project."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(slots=True)
class Project:
    """Represents a workspace derived from the hackathon planning thread."""

    key: str
    name: str
    description: str
    tags: List[str] = field(default_factory=list)

    def matches(self, query: str) -> bool:
        """Return True if the project metadata contains the query text."""

        query_lower = query.lower()
        haystack = " ".join([self.key, self.name, self.description, *self.tags]).lower()
        return query_lower in haystack


@dataclass(slots=True)
class Alert:
    """Represents a tactical alert created during the hackathon discussions."""

    identifier: str
    title: str
    narrative: str
    impact: Impact
    project_key: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    owners: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)

    def summary(self) -> str:
        """Return a concise summary string."""

        return f"[{self.impact.upper()}] {self.title} (#{self.identifier})"

    def matches(self, query: str) -> bool:
        """Return True when any field contains the query string."""

        query_lower = query.lower()
        fields = [
            self.identifier,
            self.title,
            self.narrative,
            " ".join(self.owners),
            " ".join(self.references),
        ]
        return any(query_lower in field.lower() for field in fields)


def parse_impact(value: str) -> Impact:
    """Parse a string into an :class:`Impact` enum."""

    normalized = value.strip().lower()
    for item in Impact:
        if item.value == normalized:
            return item
    raise ValueError(f"Unsupported impact level: {value}")


def timestamp(value: Optional[str]) -> datetime:
    """Convert ISO formatted text into a datetime."""

    if not value:
        return datetime.utcnow()
    return datetime.fromisoformat(value)
