"""Storage layer abstractions for KuzuAlerts."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from .models import Alert, Project


class InMemoryRepository:
    """A simple repository meant to mirror the GitNexus hackathon prototype."""

    def __init__(self) -> None:
        self._projects: Dict[str, Project] = {}
        self._alerts: Dict[str, Alert] = {}

    # Project operations -------------------------------------------------
    def upsert_project(self, project: Project) -> None:
        self._projects[project.key] = project

    def get_project(self, key: str) -> Optional[Project]:
        return self._projects.get(key)

    def iter_projects(self) -> Iterable[Project]:
        return self._projects.values()

    # Alert operations ---------------------------------------------------
    def upsert_alert(self, alert: Alert) -> None:
        self._alerts[alert.identifier] = alert

    def get_alert(self, identifier: str) -> Optional[Alert]:
        return self._alerts.get(identifier)

    def iter_alerts(self) -> Iterable[Alert]:
        return self._alerts.values()

    # Search -------------------------------------------------------------
    def find_projects(self, query: str) -> List[Project]:
        return [project for project in self.iter_projects() if project.matches(query)]

    def find_alerts(self, query: str) -> List[Alert]:
        return [alert for alert in self.iter_alerts() if alert.matches(query)]

    def alerts_for_project(self, project_key: str) -> List[Alert]:
        return [alert for alert in self.iter_alerts() if alert.project_key == project_key]

