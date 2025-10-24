# KuzuAlerts

KuzuAlerts is a lightweight collaboration toolkit that reimagines the ideas we explored in the
GPT "해커톤" project while drawing architectural inspiration from the public
[GitNexus](https://github.com/Cicada31113/GitNexus) prototype. The goal is to provide a portable
workspace where hackathon teams can capture projects, discuss high-signal alerts, and iterate on
operational experiments without the overhead of a full platform deployment.

## Features

- **Project registry** – Track hackathon initiatives and the tags, narratives, and themes that
  motivated them during our brainstorming sessions.
- **Alert lifecycle** – Record concrete follow-ups, experiments, or incidents associated with each
  project and annotate them with owners, impact levels, and supporting references.
- **State import/export** – Quickly bootstrap a session from a JSON/YAML artifact (just like we did
  when jumping between GPT threads) and export the evolving state for async reviews.
- **Command-line workflow** – A focused CLI mirrors the coordination steps we refined during the
  GitNexus hackathon rehearsal, making it easy to triage and share updates in real time.

## Project structure

```
.
├── data/                   # Sample bootstrap data inspired by our hackathon scenario
├── src/kuzualerts/         # Core package with models, repositories, services, and CLI
├── tests/                  # Automated coverage of the primary collaboration workflows
└── pyproject.toml          # Build metadata for packaging and local installs
```

## Getting started

1. **Create a virtual environment** (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Install the package in editable mode**:

   ```bash
   pip install -e .
   ```

   If you want to load the bundled YAML sample, also install PyYAML:

   ```bash
   pip install pyyaml
   ```

3. **Run the tests** to ensure everything matches the hackathon baseline:

   ```bash
   pytest
   ```

4. **Explore the CLI**:

   ```bash
   python -m kuzualerts.cli --bootstrap data/sample_alerts.yaml project list
   python -m kuzualerts.cli --bootstrap data/sample_alerts.yaml alert list
   python -m kuzualerts.cli project create HACK "Hackathon Retro" "Post-event synthesis" --tags retro gpt
   python -m kuzualerts.cli alert create A-200 "Retro brainstorm" "Outline the GPT learnings" HACK medium --owners ara jin
   ```

5. **Export a session**:

   ```bash
   python -m kuzualerts.cli --bootstrap data/sample_alerts.yaml --export export.json alert list
   ```

## Design notes

- The `InMemoryRepository` mirrors the whiteboard storage we prototyped during the GitNexus build,
  keeping the implementation approachable for teammates who want to extend it.
- `KuzuAlertsService` orchestrates the collaboration lifecycle and exposes serialization helpers for
  rapid iteration during hackathons.
- The `kuzualerts.cli` module offers a single entry point for on-call rotation reviews, pitch
  sessions, or quick experiments while staying close to the GPT "해커톤" planning guidance.
- Tests in `tests/test_service.py` codify the minimum expectations we established in the GPT thread,
  ensuring future tweaks continue to honor those decisions.

## Contributing

1. Fork the repository and create a feature branch.
2. Install development dependencies (`pip install -r requirements-dev.txt`) if you add new tooling.
3. Run `pytest` and update/add tests as needed.
4. Submit a pull request summarizing the hackathon-inspired improvements.

Feel free to adapt the workflows to your own GPT project retrospectives—KuzuAlerts is meant to be a
starting point for lightweight coordination experiments.
