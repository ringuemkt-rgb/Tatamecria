"""Command-line entry points."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import typer

from neurojitsu.agents.orchestrator import ReportOrchestrator
from neurojitsu.settings import load_settings
from neurojitsu.storage.database import Database
from neurojitsu.synthetic.generator import dataframe_to_windows, generate_session_dataframe

app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.command()
def demo(
    output: Path = typer.Option(Path("outputs/demo"), help="Directory for generated artifacts"),
    participant_id: str = typer.Option("C001"),
    session_id: str = typer.Option("NJ-DEMO-001"),
    seed: int = typer.Option(42),
) -> None:
    """Run the complete synthetic workflow without personal data."""
    settings = load_settings()
    database = Database(
        settings.db_path,
        key=settings.db_key,
        allow_unencrypted_synthetic_only=settings.allow_unencrypted_synthetic_only,
    )
    dataframe = generate_session_dataframe(participant_id, session_id, seed=seed)
    windows = dataframe_to_windows(dataframe)
    started = windows[0].timestamp_start

    database.register_participant(participant_id, synthetic=True)
    existing = {row["session_id"] for row in database.list_sessions()}
    if session_id not in existing:
        database.create_session(session_id, participant_id, started)
    database.set_session_state(session_id, "processing")
    database.store_windows(windows)

    result = ReportOrchestrator().run(windows)
    output.mkdir(parents=True, exist_ok=True)
    json_path = output / f"{session_id}.json"
    html_path = output / f"{session_id}.html"
    agent_path = output / f"{session_id}-agents.json"
    json_text = result.payload.model_dump_json(indent=2)
    json_path.write_text(json_text, encoding="utf-8")
    html_path.write_text(result.html, encoding="utf-8")
    agent_path.write_text(
        json.dumps(result.agent_outputs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    database.store_report(session_id, participant_id, json_text, result.html)
    database.set_session_state(session_id, "review", ended_at=datetime.now(UTC))

    typer.echo(f"Demo completed: {json_path}")
    typer.echo(f"HTML report: {html_path}")
    typer.echo(f"Agent outputs: {agent_path}")


@app.command()
def verify() -> None:
    """Validate configuration and database security mode."""
    settings = load_settings()
    database = Database(
        settings.db_path,
        key=settings.db_key,
        allow_unencrypted_synthetic_only=settings.allow_unencrypted_synthetic_only,
    )
    typer.echo(f"Configuration: {settings.config_path}")
    typer.echo(f"Database: {settings.db_path}")
    typer.echo(f"Encrypted: {database.encrypted}")
    if not database.encrypted:
        typer.echo("Unencrypted mode is permitted only for synthetic data.")


if __name__ == "__main__":
    app()
