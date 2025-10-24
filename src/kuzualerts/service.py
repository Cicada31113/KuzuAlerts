"""Application services orchestrating hackathon-era collaboration flows."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Sequence

from .models import Alert, Impact, Project, parse_impact
from .repository import InMemoryRepository


class KuzuAlertsService:
    """Coordinates project and alert lifecycles."""

    def __init__(self, repository: InMemoryRepository | None = None) -> None:
        self._repository = repository or InMemoryRepository()

    # Project APIs -------------------------------------------------------
    def register_project(
        self,
        key: str,
        name: str,
        description: str,
        *,
        tags: Sequence[str] | None = None,
    ) -> Project:
        project = Project(key=key, name=name, description=description, tags=list(tags or []))
        self._repository.upsert_project(project)
        return project

    def list_projects(self) -> List[Project]:
        return sorted(self._repository.iter_projects(), key=lambda item: item.key)

    def search_projects(self, query: str) -> List[Project]:
        return self._repository.find_projects(query)

    # Alert APIs ---------------------------------------------------------
    def create_alert(
        self,
        identifier: str,
        title: str,
        narrative: str,
        *,
        project_key: str,
        impact: Impact | str,
        owners: Sequence[str] | None = None,
        references: Sequence[str] | None = None,
    ) -> Alert:
        impact_value = parse_impact(impact) if isinstance(impact, str) else impact
        alert = Alert(
            identifier=identifier,
            title=title,
            narrative=narrative,
            project_key=project_key,
            impact=impact_value,
            owners=list(owners or []),
            references=list(references or []),
        )
        self._repository.upsert_alert(alert)
        return alert

    def list_alerts(self) -> List[Alert]:
        return sorted(self._repository.iter_alerts(), key=lambda item: item.created_at, reverse=True)

    def search_alerts(self, query: str) -> List[Alert]:
        return self._repository.find_alerts(query)

    def alerts_for_project(self, project_key: str) -> List[Alert]:
        return self._repository.alerts_for_project(project_key)

    # Serialization helpers ---------------------------------------------
    def export_state(self) -> dict:
        return {
            "projects": [asdict(project) for project in self._repository.iter_projects()],
            "alerts": [asdict(alert) for alert in self._repository.iter_alerts()],
        }

    def import_state(self, payload: dict) -> None:
        for project_payload in payload.get("projects", []):
            self.register_project(
                key=project_payload["key"],
                name=project_payload["name"],
                description=project_payload.get("description", ""),
                tags=project_payload.get("tags", []),
            )
        for alert_payload in payload.get("alerts", []):
            self.create_alert(
                identifier=alert_payload["identifier"],
                title=alert_payload["title"],
                narrative=alert_payload.get("narrative", ""),
                project_key=alert_payload["project_key"],
                impact=alert_payload.get("impact", Impact.MEDIUM.value),
                owners=alert_payload.get("owners", []),
                references=alert_payload.get("references", []),
            )


def load_sample_data(path: str | Path) -> dict:
    """Load a sample JSON or YAML export like we used during the hackathon."""

    path = Path(path)
    content = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        return _load_yaml(content)
    return json.loads(content)


def _load_yaml(content: str) -> dict:
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError as exc:  # pragma: no cover - dependency optional
        raise RuntimeError(
            "PyYAML must be installed to parse YAML exports."
        ) from exc
    return yaml.safe_load(content)


def bootstrap_from_file(service: KuzuAlertsService, path: str | Path) -> None:
    """Convenience helper to hydrate the service from serialized state."""

    payload = load_sample_data(path)
    service.import_state(payload)
