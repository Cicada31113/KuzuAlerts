"""Unit tests capturing the hackathon-inspired workflows."""

from __future__ import annotations

from datetime import datetime

import pytest

from kuzualerts.models import Impact
from kuzualerts.repository import InMemoryRepository
from kuzualerts.service import KuzuAlertsService


@pytest.fixture()
def service() -> KuzuAlertsService:
    return KuzuAlertsService()


def test_register_and_list_projects(service: KuzuAlertsService) -> None:
    service.register_project("CORE", "Core", "Core systems", tags=["infra"])
    service.register_project("OPS", "Ops", "Operations", tags=["ops"])

    keys = [project.key for project in service.list_projects()]
    assert keys == ["CORE", "OPS"]


def test_create_alert(service: KuzuAlertsService) -> None:
    service.register_project("CORE", "Core", "Core systems")
    alert = service.create_alert(
        identifier="A-1",
        title="Latency spike",
        narrative="Investigate database",
        project_key="CORE",
        impact=Impact.HIGH,
        owners=["alice"],
        references=["doc"],
    )

    assert alert.impact is Impact.HIGH
    assert service.list_alerts()[0].identifier == "A-1"


def test_search_alerts(service: KuzuAlertsService) -> None:
    service.register_project("OPS", "Ops", "Operations")
    service.create_alert(
        identifier="A-2",
        title="Pager fatigue",
        narrative="Hand-off confusion",
        project_key="OPS",
        impact="medium",
        owners=["casey"],
        references=[],
    )

    results = service.search_alerts("pager")
    assert len(results) == 1
    assert results[0].identifier == "A-2"


def test_export_import_roundtrip() -> None:
    repository = InMemoryRepository()
    service = KuzuAlertsService(repository)
    service.register_project("OPS", "Ops", "Ops project")
    service.create_alert(
        identifier="A-3",
        title="Drift",
        narrative="Config drift",
        project_key="OPS",
        impact="low",
    )

    payload = service.export_state()
    new_service = KuzuAlertsService(InMemoryRepository())
    new_service.import_state(payload)

    assert len(new_service.list_projects()) == 1
    assert len(new_service.list_alerts()) == 1
