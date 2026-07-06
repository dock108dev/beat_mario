from pathlib import Path

import pytest
import yaml

from smb3_agent.fceux_harness import AttemptSummary, BatchSummary
from smb3_agent.goals import (
    GoalValidationError,
    evaluate_success_metrics,
    load_goal_contract,
    resolve_goal_path,
)


def test_load_world_1_king_goal_contract() -> None:
    contract = load_goal_contract(Path("data/goals/world_1_king.yaml"))

    assert contract.id == "world_1_king"
    assert contract.preset == "fceux_world_1_king"
    assert "world_1_fortress_whistle" in contract.bridged_segments
    assert contract.segments[0] == "fresh_start_to_1_1"


def test_goal_contract_reports_missing_required_fields(tmp_path: Path) -> None:
    bad_contract = tmp_path / "bad.yaml"
    bad_contract.write_text(yaml.safe_dump({"id": "bad_goal"}))

    with pytest.raises(GoalValidationError, match="Missing required field"):
        load_goal_contract(bad_contract)


def test_goal_contract_rejects_bridge_not_in_route(tmp_path: Path) -> None:
    raw = yaml.safe_load(Path("data/goals/world_1_king.yaml").read_text())
    raw["bridged_segments"] = ["not_in_route"]
    bad_contract = tmp_path / "bad_bridge.yaml"
    bad_contract.write_text(yaml.safe_dump(raw))

    with pytest.raises(GoalValidationError, match="bridged_segments not present"):
        load_goal_contract(bad_contract)


def test_goal_success_metrics_pass_for_king_summary() -> None:
    contract = load_goal_contract(Path("data/goals/world_1_king.yaml"))
    summary = BatchSummary(
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
        post_probe_max_x=432,
        post_probe_last_event="post_probe_1_airship_success_king",
        post_probe_clear=True,
    )

    assert evaluate_success_metrics(contract, summary) is True


def test_goal_success_metrics_fail_without_final_event() -> None:
    contract = load_goal_contract(Path("data/goals/world_1_king.yaml"))
    summary = BatchSummary(
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
        post_probe_last_event="post_probe_1_4_after",
        post_probe_clear=False,
    )

    assert evaluate_success_metrics(contract, summary) is False


def test_resolve_goal_path_accepts_id() -> None:
    assert resolve_goal_path("world_1_king") == Path("data/goals/world_1_king.yaml")

