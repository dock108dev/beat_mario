from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from smb3_agent.fceux_harness import AttemptSummary, BatchSummary
from smb3_agent.goals import GoalRunResult
from smb3_agent.lab import (
    LabError,
    add_note_to_latest,
    compare_variant,
    promote_variant,
    propose_variant_from_latest,
    review_latest_session,
    run_variant,
    start_session,
)


def test_lab_start_writes_session_manifest(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _prepare_lab(monkeypatch, tmp_path)

    result = start_session(
        "show me the route at 4x",
        game_path=tmp_path / "local-game-file",
        attempts=1,
        artifacts_root=tmp_path / "artifacts/sessions",
    )

    manifest = yaml.safe_load(result.manifest_path.read_text())
    assert manifest["goal_id"] == "world_1_king"
    assert manifest["requested_speed"] == 4
    assert manifest["run_settings"]["speed_mode"] == "normal"
    assert manifest["run_settings"]["frame_sleep_seconds"] == 0.004167
    assert manifest["outputs"]["route_log"] == "goal/fceux_1_1.log"
    assert result.session_dir.joinpath("notes.yaml").is_file()


def test_lab_note_latest_preserves_raw_text_and_infers_anchor(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _prepare_lab(monkeypatch, tmp_path)
    start_session(
        "show me the route at 4x",
        game_path=tmp_path / "local-game-file",
        attempts=1,
        artifacts_root=tmp_path / "artifacts/sessions",
    )

    text = "1-1 around 320 timer: falls into the hole and usually gets lucky"
    result = add_note_to_latest(text)

    assert result.note["text"] == text
    assert result.note["segment_id"] == "world_1_1"
    assert result.note["anchor"] == {"type": "in_game_timer", "value": 320}
    notes = yaml.safe_load(result.notes_path.read_text())
    assert notes["notes"][0]["text"] == text


def test_lab_review_and_variant_proposal_link_note_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _prepare_lab(monkeypatch, tmp_path)
    start_session(
        "show me the route at 4x",
        game_path=tmp_path / "local-game-file",
        attempts=1,
        artifacts_root=tmp_path / "artifacts/sessions",
    )
    add_note_to_latest("1-1 around 320 timer: falls into the hole and usually gets lucky")

    review = review_latest_session()
    proposal = propose_variant_from_latest()

    assert review.review["primary_segment"] == "world_1_1"
    assert review.review["classification"] == "input_timing"
    assert proposal.variant_id.startswith("world_1_1_harden_320_")
    assert proposal.proposal["source_notes"] == ["note_001"]
    assert proposal.proposal["changes"][0]["file"] == "data/routes/scripts/world_1_1_clear_v0.yaml"


def test_promote_variant_refuses_without_passing_validation(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _prepare_lab(monkeypatch, tmp_path)
    start_session(
        "show me the route at 4x",
        game_path=tmp_path / "local-game-file",
        attempts=1,
        artifacts_root=tmp_path / "artifacts/sessions",
    )
    add_note_to_latest("1-1 around 320 timer: falls into the hole and usually gets lucky")
    proposal = propose_variant_from_latest()

    with pytest.raises(LabError, match="Promotion refused"):
        promote_variant(proposal.variant_id)


def test_variant_run_compare_and_promote(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _prepare_lab(monkeypatch, tmp_path)
    start_session(
        "show me the route at 4x",
        game_path=tmp_path / "local-game-file",
        attempts=1,
        artifacts_root=tmp_path / "artifacts/sessions",
    )
    add_note_to_latest("1-1 around 320 timer: falls into the hole and usually gets lucky")
    proposal = propose_variant_from_latest()

    run_result = run_variant(
        proposal.variant_id,
        game_path=tmp_path / "local-game-file",
        attempts=2,
        artifacts_root=tmp_path / "artifacts/sessions",
    )
    compare = compare_variant(proposal.variant_id)
    promotion = promote_variant(proposal.variant_id)

    assert run_result.route_variant == proposal.variant_id
    assert "successes=2/2" in compare.to_text()
    assert promotion.baseline_path.is_file()
    assert promotion.backup_path.is_file()


def _prepare_lab(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    tmp_path.joinpath("data/variants").mkdir(parents=True)
    tmp_path.joinpath("artifacts/sessions").mkdir(parents=True)
    tmp_path.joinpath("local-game-file").write_text("placeholder")
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
    lines = []
    for attempt in range(1, attempts + 1):
        lines.extend(
            [
                f"frame=10 event=attempt_{attempt}_start x=24 y=384",
                f"frame=50 event=attempt_{attempt}_success_course_clear x=8192 y=0",
            ]
        )
    lines.append("frame=80 event=post_probe_1_airship_success_king x=432 y=4192")
    artifacts_dir.joinpath("fceux_1_1.log").write_text("\n".join(lines))
    return GoalRunResult(
        contract=contract,
        summary=BatchSummary(
            attempts=tuple(
                AttemptSummary(
                    attempt=attempt,
                    success=True,
                    bad_state=False,
                    reached_end=True,
                    goal_area=True,
                    max_x=2848,
                )
                for attempt in range(1, attempts + 1)
            ),
            post_probe_last_event="post_probe_1_airship_success_king",
            post_probe_clear=True,
        ),
        artifacts_dir=artifacts_dir,
        metrics_passed=True,
    )
