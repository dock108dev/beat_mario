from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from smb3_agent.fceux_harness import AttemptSummary, BatchSummary
from smb3_agent.goals import GoalRunResult
from smb3_agent.lab import (
    add_batch_notes_to_latest,
    build_issue_ledger_latest,
    propose_variants_from_latest,
    start_session,
    write_ui_summary_latest,
)
from smb3_agent.lab_ui import render_lab_ui


def test_lab_ui_renders_route_map_and_batch_note_form(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _prepare_ui_lab(monkeypatch, tmp_path)
    start_session(
        "show me the route at 4x",
        game_path=tmp_path / "local-game-file",
        attempts=1,
        artifacts_root=tmp_path / "artifacts/sessions",
    )
    add_batch_notes_to_latest(
        [
            {
                "segment_id": "world_1_1_clear",
                "text": "1-1 falls into hole at 283 on clock.",
                "severity": "harden",
            },
            {
                "segment_id": "world_1_fortress_whistle",
                "text": "Castle dies first try and carry-over inputs send the route to 1-4.",
                "severity": "harden",
            },
        ]
    )
    build_issue_ledger_latest()
    propose_variants_from_latest()

    html = render_lab_ui()

    assert "World 1 Lab" in html
    assert "Route Map" in html
    assert 'name="note__world_1_1_clear"' in html
    assert "World 1 Fortress Whistle" in html
    assert "Create Codex Task" in html
    assert "world_1_fortress_whistle_recovery" in html


def test_ui_summary_contains_segment_counts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _prepare_ui_lab(monkeypatch, tmp_path)
    start_session(
        "show me the route at 4x",
        game_path=tmp_path / "local-game-file",
        attempts=1,
        artifacts_root=tmp_path / "artifacts/sessions",
    )
    add_batch_notes_to_latest(
        [
            {
                "segment_id": "world_1_1_clear",
                "text": "1-1 falls into hole at 283 on clock.",
                "severity": "harden",
            },
            {
                "segment_id": "world_1_3_whistle",
                "text": "1-3 whistle exit is expected.",
                "severity": "note",
            },
        ]
    )
    build_issue_ledger_latest()
    propose_variants_from_latest()

    summary = write_ui_summary_latest().summary
    segment_map = {segment["id"]: segment for segment in summary["segments"]}

    assert segment_map["world_1_1_clear"]["notes"] == 1
    assert segment_map["world_1_1_clear"]["issues"] == 1
    assert segment_map["world_1_1_clear"]["proposals"] == 1
    assert segment_map["world_1_3_whistle"]["notes"] == 1
    assert segment_map["world_1_3_whistle"]["proposals"] == 0


def _prepare_ui_lab(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    tmp_path.joinpath("data/variants").mkdir(parents=True)
    tmp_path.joinpath("data/segments").mkdir(parents=True)
    tmp_path.joinpath("artifacts/sessions").mkdir(parents=True)
    tmp_path.joinpath("local-game-file").write_text("placeholder")
    tmp_path.joinpath("data/segments/world_1.yaml").write_text(
        yaml.safe_dump(
            {
                "catalog_id": "world_1",
                "segments": [
                    {"id": "world_1_1_clear", "name": "World 1-1", "status": "solved"},
                    {"id": "world_1_3_whistle", "name": "World 1-3 Whistle", "status": "solved"},
                    {
                        "id": "world_1_fortress_whistle",
                        "name": "World 1 Fortress Whistle",
                        "status": "bridged",
                    },
                ],
            }
        )
    )
    monkeypatch.setattr("smb3_agent.lab.load_goal_contract", lambda path: SimpleNamespace(id="world_1_king"))
    monkeypatch.setattr("smb3_agent.lab.resolve_goal_path", lambda goal: Path(f"data/goals/{goal}.yaml"))
    monkeypatch.setattr("smb3_agent.lab.run_goal_contract", _fake_run_goal_contract)


def _fake_run_goal_contract(
    contract,
    *,
    game_path,
    attempts,
    artifacts_dir,
    capture_images=False,
    capture_ticks=False,
    env_overrides=(),
):
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.joinpath("fceux_1_1.log").write_text(
        "\n".join(
            [
                "frame=10 event=attempt_1_start x=24 y=384",
                "frame=50 event=attempt_1_success_course_clear x=8192 y=0",
                "frame=80 event=post_probe_1_airship_success_king x=432 y=4192",
            ]
        )
    )
    return GoalRunResult(
        contract=contract,
        summary=BatchSummary(
            attempts=(
                AttemptSummary(
                    attempt=1,
                    success=True,
                    bad_state=False,
                    reached_end=True,
                    goal_area=True,
                    max_x=2848,
                ),
            ),
            post_probe_last_event="post_probe_1_airship_success_king",
            post_probe_clear=True,
        ),
        artifacts_dir=artifacts_dir,
        metrics_passed=True,
    )
