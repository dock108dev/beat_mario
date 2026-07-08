from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from smb3_agent.fceux_harness import AttemptSummary, BatchSummary
from smb3_agent.goals import GoalRunResult
from smb3_agent.lab import add_batch_notes_to_latest, build_issue_ledger_latest, start_session
from smb3_agent.lab_ui import build_control_panel_summary, render_lab_ui


def test_control_panel_renders_world_1_locations_and_controls(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _prepare_ui_lab(monkeypatch, tmp_path)
    start_session(
        "show me the route at 4x",
        game_path=tmp_path / "local-game-file",
        attempts=1,
        artifacts_root=tmp_path / "artifacts/sessions",
    )

    html = render_lab_ui()

    assert "World 1 Control Panel" in html
    assert "Run Controls" in html
    assert "World 1 Notes" in html
    assert "1-1" in html
    assert "1-3" in html
    assert "Fortress" in html
    assert "Airship" in html
    assert "King" in html
    assert "Unit Tests" in html
    assert "Phase Gate" in html
    assert 'name="note__world_1_1"' in html
    assert "World 1-3 Whistle" not in html
    assert "World 1 Fortress Whistle" not in html
    assert "world_1_1_clear" not in html
    assert "world_1_3_whistle" not in html
    assert "world_1_fortress_whistle" not in html


def test_control_panel_groups_notes_by_human_location(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
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
                "segment_id": "world_1_1",
                "text": "1-1 falls into hole at 283 on clock.",
                "severity": "harden",
            },
            {
                "segment_id": "world_1_fortress",
                "text": "Fortress needs Raccoon flight, not fire form.",
                "severity": "guide_detail",
            },
        ]
    )
    build_issue_ledger_latest()

    summary = build_control_panel_summary()
    locations = {location["id"]: location for location in summary["locations"]}

    assert locations["world_1_1"]["notes"] == 1
    assert locations["world_1_1"]["open_issues"] == 1
    assert locations["world_1_fortress"]["notes"] == 1
    assert locations["world_1_fortress"]["issues"] == 1
    assert locations["world_1_fortress"]["open_issues"] == 0
    assert summary["totals"]["notes"] == 2


def _prepare_ui_lab(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    tmp_path.joinpath("data/worlds").mkdir(parents=True)
    tmp_path.joinpath("data/segments").mkdir(parents=True)
    tmp_path.joinpath("artifacts/sessions").mkdir(parents=True)
    tmp_path.joinpath("local-game-file").write_text("placeholder")
    tmp_path.joinpath("data/worlds/world_1_locations.yaml").write_text(
        yaml.safe_dump(
            {
                "world": 1,
                "name": "Grass Land",
                "locations": [
                    {
                        "id": "world_1_map",
                        "label": "Map",
                        "default_status": "needs review",
                        "objective": "Navigate between required locations.",
                    },
                    {
                        "id": "world_1_1",
                        "label": "1-1",
                        "default_status": "works",
                        "objective": "Clear the level.",
                    },
                    {
                        "id": "world_1_3",
                        "label": "1-3",
                        "default_status": "works",
                        "objective": "Get the hidden item route.",
                    },
                    {
                        "id": "world_1_fortress",
                        "label": "Fortress",
                        "default_status": "blocked",
                        "objective": "Use flight above the ceiling.",
                    },
                    {
                        "id": "world_1_airship",
                        "label": "Airship",
                        "default_status": "needs review",
                        "objective": "Complete the moving stage.",
                    },
                    {
                        "id": "world_1_king",
                        "label": "King",
                        "default_status": "needs review",
                        "objective": "Confirm the world clear transition.",
                    },
                ],
            }
        )
    )
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
