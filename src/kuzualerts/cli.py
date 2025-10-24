"""Command-line interface mirroring the GitNexus coordination workflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .service import KuzuAlertsService, bootstrap_from_file, load_sample_data


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="KuzuAlerts command line toolkit")
    subparsers = parser.add_subparsers(dest="command")

    project_parser = subparsers.add_parser("project", help="Project management commands")
    project_sub = project_parser.add_subparsers(dest="project_command")

    project_list = project_sub.add_parser("list", help="List registered projects")
    project_list.add_argument("--search", help="Filter projects by keyword", default="")

    project_create = project_sub.add_parser("create", help="Register a new project")
    project_create.add_argument("key")
    project_create.add_argument("name")
    project_create.add_argument("description")
    project_create.add_argument("--tags", nargs="*", default=[])

    alert_parser = subparsers.add_parser("alert", help="Alert management commands")
    alert_sub = alert_parser.add_subparsers(dest="alert_command")

    alert_list = alert_sub.add_parser("list", help="List alerts")
    alert_list.add_argument("--search", help="Filter alerts", default="")
    alert_list.add_argument("--project", help="Filter by project key", default="")

    alert_create = alert_sub.add_parser("create", help="Create an alert")
    alert_create.add_argument("identifier")
    alert_create.add_argument("title")
    alert_create.add_argument("narrative")
    alert_create.add_argument("project_key")
    alert_create.add_argument("impact")
    alert_create.add_argument("--owners", nargs="*", default=[])
    alert_create.add_argument("--references", nargs="*", default=[])

    parser.add_argument(
        "--bootstrap",
        help="Optional JSON/YAML state export to pre-load",
    )

    parser.add_argument(
        "--export",
        help="Path to write the session state back to JSON",
    )

    return parser


def handle_project_commands(args: argparse.Namespace, service: KuzuAlertsService) -> None:
    command = args.project_command
    if command == "list":
        projects = service.search_projects(args.search) if args.search else service.list_projects()
        for project in projects:
            tags = ", ".join(project.tags) if project.tags else "no-tags"
            print(f"{project.key}: {project.name} [{tags}]\n  {project.description}")
    elif command == "create":
        project = service.register_project(
            key=args.key,
            name=args.name,
            description=args.description,
            tags=args.tags,
        )
        print(f"Registered project {project.key}: {project.name}")
    else:
        raise SystemExit("Unknown project command")


def handle_alert_commands(args: argparse.Namespace, service: KuzuAlertsService) -> None:
    command = args.alert_command
    if command == "list":
        if args.project:
            alerts = service.alerts_for_project(args.project)
        elif args.search:
            alerts = service.search_alerts(args.search)
        else:
            alerts = service.list_alerts()
        for alert in alerts:
            owners = ", ".join(alert.owners) if alert.owners else "unassigned"
            print(f"{alert.summary()} -> {alert.project_key} | owners: {owners}")
    elif command == "create":
        alert = service.create_alert(
            identifier=args.identifier,
            title=args.title,
            narrative=args.narrative,
            project_key=args.project_key,
            impact=args.impact,
            owners=args.owners,
            references=args.references,
        )
        print(f"Created alert {alert.summary()} for project {alert.project_key}")
    else:
        raise SystemExit("Unknown alert command")


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    service = KuzuAlertsService()
    if args.bootstrap:
        bootstrap_from_file(service, args.bootstrap)

    if args.command == "project":
        handle_project_commands(args, service)
    elif args.command == "alert":
        handle_alert_commands(args, service)
    else:
        parser.print_help()

    if args.export:
        payload = service.export_state()
        Path(args.export).write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    main()
