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
    assert contract.goal_type == "diagnostic_route"
    assert contract.preset == "fceux_world_1_king"
    assert "world_1_fortress_whistle" not in contract.bridged_segments
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
        post_probe_events=(
            "post_probe_1_fortress_whistle_room_success",
            "post_probe_1_airship_success_king",
        ),
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


def test_goal_success_metrics_reject_fortress_whistle_bridge() -> None:
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
        post_probe_last_event="post_probe_1_airship_success_king",
        post_probe_clear=True,
        post_probe_events=(
            "post_probe_1_fortress_bridge_second_whistle",
            "post_probe_1_airship_success_king",
        ),
    )

    assert evaluate_success_metrics(contract, summary) is False


def test_resolve_goal_path_accepts_id() -> None:
    assert resolve_goal_path("world_1_king") == Path("data/goals/world_1_king.yaml")


def test_active_product_goal_is_world_2_first_double_whistle_world_8_arrival() -> None:
    contract = load_goal_contract(Path("data/goals/world_8_double_whistle.yaml"))
    roles = {step.id: step.classification for step in contract.route_steps}

    assert contract.goal_type == "product_goal"
    assert contract.objective["target"] == "world_8_map_arrival"
    assert contract.execution_status == "executable"
    assert contract.executable is True
    assert contract.preset == "fceux_world_8_double_whistle"
    assert "world_1_3_whistle" in contract.segments
    assert "world_1_fortress_whistle" in contract.segments
    assert roles["world_1_3_whistle"] == "objective_milestone"
    assert roles["world_1_fortress_whistle"] == "objective_milestone"


def test_active_route_matches_owner_corrected_world_2_boundary() -> None:
    contract = load_goal_contract(Path("data/goals/world_8_double_whistle.yaml"))
    roles = {step.id: step for step in contract.route_steps}

    assert "world_1_4_clear" not in contract.segments
    assert roles["world_1_5_water_path"].classification == "game_prerequisite"
    assert roles["world_1_5_water_path"].evidence
    assert roles["world_1_6_clear"].classification == "game_prerequisite"
    assert roles["world_1_6_clear"].evidence
    assert roles["world_1_airship_to_king"].classification == "game_prerequisite"
    assert contract.segments.index("world_1_airship_to_king") < contract.segments.index(
        "world_2_map_arrival_with_two_whistles"
    )
    assert contract.segments.index("world_2_map_arrival_with_two_whistles") < contract.segments.index(
        "world_2_first_whistle_use"
    )
    assert "world_2_first_whistle_use" in contract.segments
    assert "world_7_entry" not in contract.segments


def test_active_route_orders_distinct_whistle_and_warp_zone_transitions() -> None:
    contract = load_goal_contract(Path("data/goals/world_8_double_whistle.yaml"))

    ordered = (
        "world_2_first_whistle_use",
        "warp_zone_5_6_7_tier",
        "warp_zone_second_whistle_use",
        "warp_zone_world_8_tier",
        "world_8_pipe_entry",
        "world_8_map_arrival",
    )
    assert tuple(sorted(ordered, key=contract.segments.index)) == ordered


def test_active_goal_only_passes_on_world_8_map_arrival() -> None:
    contract = load_goal_contract(Path("data/goals/world_8_double_whistle.yaml"))
    attempts = (
        AttemptSummary(
            attempt=1,
            success=True,
            bad_state=False,
            reached_end=True,
            goal_area=True,
            max_x=2848,
        ),
    )
    required_events = (
        "post_probe_1_3_whistle_room_success",
        "post_probe_1_fortress_whistle_room_success",
        "post_probe_world_2_map_two_whistles",
        "post_probe_world_2_first_whistle_used",
        "post_probe_warp_zone_second_whistle_used",
    )
    king_summary = BatchSummary(
        attempts=attempts,
        post_probe_last_event="post_probe_1_airship_success_king",
        post_probe_clear=True,
        post_probe_events=required_events + ("post_probe_1_airship_success_king",),
    )
    world_8_summary = BatchSummary(
        attempts=attempts,
        post_probe_last_event="post_probe_world_8_map_arrival",
        post_probe_clear=True,
        post_probe_events=required_events + ("post_probe_world_8_map_arrival",),
    )

    assert evaluate_success_metrics(contract, king_summary) is False
    assert evaluate_success_metrics(contract, world_8_summary) is True
