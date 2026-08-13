from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import subprocess

import pytest

from smb3_agent.fceux_harness import AttemptSummary, BatchSummary
from smb3_agent.goals import GoalRunResult, load_goal_contract
from smb3_agent.reliability import (
    BATTLESHIPS_FINAL_EVENT,
    BIG_TANKS_FINAL_EVENT,
    FINAL_EVENT,
    HAND_TRAPS_JET_FINAL_EVENT,
    WORLD_8_8_2_FINAL_EVENT,
    WORLD_8_SUPER_TANKS_FINAL_EVENT,
    run_reliability_gate,
    run_watchable_playback,
)
from smb3_agent.segments import load_segment_catalog


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _milestone_events(goal_id: str = "world_8_double_whistle") -> list[str]:
    contract = load_goal_contract(Path(f"data/goals/{goal_id}.yaml"))
    catalog = load_segment_catalog(contract.catalog_path)
    return [catalog.by_id[segment_id].acceptance_event for segment_id in contract.segments]


def _write_execution(
    artifacts_dir: Path,
    *,
    timed_out: bool = False,
    returncode: int | None = 0,
    launch_error: str | None = None,
) -> None:
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.joinpath("fceux_execution.json").write_text(
        json.dumps(
            {
                "timed_out": timed_out,
                "returncode": returncode,
                "launch_error": launch_error,
            }
        )
    )
    artifacts_dir.joinpath("fceux_stdout.log").write_text("retained stdout\n")
    artifacts_dir.joinpath("fceux_stderr.log").write_text("retained stderr\n")


def _write_log(
    artifacts_dir: Path,
    events: list[str],
    *,
    extra_line: str | None = None,
    include_tick: bool = False,
) -> None:
    lines = []
    if include_tick:
        lines.append("frame=1 event=tick world_number=0 object_set=0 form=0")
    for frame, event in enumerate(events, start=10):
        suffix = ""
        if event == FINAL_EVENT:
            suffix = (
                " world_number=7 object_set=0 item_0=9 item_1=8 form=0 "
                "evidence=world_number_7_object_set_0_after_warp_pipe"
            )
        elif event == "post_probe_world_8_big_tanks_entered":
            suffix = (
                " x=24 y=368 world_number=7 object_set=10 "
                "stage_identity=world_8_big_tanks "
                "evidence=normal_down_right_A_from_32_80"
            )
        elif event == "post_probe_world_8_big_tanks_gameplay":
            suffix = (
                " x=600 y=300 world_number=7 object_set=10 "
                "evidence=normal_autoscroll_gameplay"
            )
        elif event == "post_probe_world_8_big_tanks_clear":
            suffix = (
                " world_number=7 object_set=10 "
                "evidence=treasure_chest_super_star_collected_with_game_return_flag"
            )
        elif event == BIG_TANKS_FINAL_EVENT:
            suffix = (
                " world_number=7 object_set=0 map_cursor_x=64 map_cursor_y=112 "
                "evidence=stable_world_8_map_after_game_clear"
            )
        elif event == "post_probe_world_8_battleships_entered":
            suffix = (
                " x=0 y=320 entry_x=0 entry_y=320 entry_air=0 world_number=7 "
                "object_set=10 map_enter_via_id=13 map_node_x=128 map_node_y=112 "
                "stage_identity=world_8_battleships "
                "evidence=normal_right_right_automatic_entry_from_64_112"
            )
        elif event == "post_probe_world_8_battleships_gameplay":
            suffix = (
                " world_number=7 object_set=10 "
                "evidence=normal_autoscroll_fleet_gameplay"
            )
        elif event == "post_probe_world_8_battleships_clear":
            suffix = (
                " world_number=7 object_set=10 return_map=1 mario_alive=1 "
                "player_is_dying=0 boss_object_id_75_active=0 boss_stomps=4 "
                "evidence=game_owned_return_map_transition_after_defeated_boss_object"
            )
        elif event == BATTLESHIPS_FINAL_EVENT:
            suffix = (
                " world_number=7 object_set=0 map_cursor_x=128 map_cursor_y=112 "
                "hand_trap_region_accessible=1 hand_trap_entered=0 player_is_dying=0 "
                "evidence=stable_world_8_map_after_boom_boom"
            )
        elif event == HAND_TRAPS_JET_FINAL_EVENT:
            suffix = (
                " world_number=7 object_set=0 map_page=2 map_cursor_x=64 "
                "map_cursor_y=112 dark_area_traversed=1 world_8_1_accessible=1 "
                "world_8_1_entered=0 player_is_dying=0 "
                "evidence=stable_world_8_map_with_world_8_1_accessible"
            )
        elif event == WORLD_8_8_2_FINAL_EVENT:
            suffix = (
                " world_number=7 object_set=0 map_page=2 map_cursor_x=64 "
                "map_cursor_y=144 fortress_accessible=1 fortress_entered=0 "
                "evidence=normal_right_input_reached_accessible_world_8_fortress_node"
            )
        elif event == WORLD_8_SUPER_TANKS_FINAL_EVENT:
            suffix = (
                " world_number=7 object_set=0 map_page=2 map_cursor_x=96 "
                "map_cursor_y=144 bowser_castle_accessible=1 "
                "bowser_castle_entered=0 stable_frames=180 "
                "evidence=stable_world_8_map_with_bowser_castle_accessible"
            )
        lines.append(f"frame={frame} event={event}{suffix}")
    if extra_line is not None:
        lines.append(extra_line)
    artifacts_dir.joinpath("fceux_1_1.log").write_text("\n".join(lines) + "\n")


def _goal_result(contract, artifacts_dir: Path, events: list[str], passed: bool) -> GoalRunResult:
    post_probe_events = tuple(event for event in events if event.startswith("post_probe_"))
    last_post_probe = post_probe_events[-1] if post_probe_events else None
    return GoalRunResult(
        contract=contract,
        summary=BatchSummary(
            attempts=(
                AttemptSummary(
                    attempt=1,
                    success=passed,
                    bad_state=not passed,
                    reached_end=passed,
                    goal_area=passed,
                    max_x=2848 if passed else 100,
                ),
            ),
            post_probe_last_event=last_post_probe,
            post_probe_clear=passed,
            post_probe_events=post_probe_events,
        ),
        artifacts_dir=artifacts_dir,
        metrics_passed=passed,
    )


def _fake_runner_factory(
    calls: list[dict],
    *,
    failing_run: int | None = None,
    partial_count: int | None = None,
    timed_out: bool = False,
    omit_log: bool = False,
    corrupt_log: bool = False,
    extra_line: str | None = None,
    include_tick: bool = False,
    write_image: bool = False,
    goal_id: str = "world_8_double_whistle",
):
    milestones = _milestone_events(goal_id)

    def fake_runner(contract, **kwargs):
        calls.append(kwargs)
        artifacts_dir = kwargs["artifacts_dir"]
        run_index = len(calls)
        is_failure = failing_run == run_index
        _write_execution(
            artifacts_dir,
            timed_out=timed_out and is_failure,
            returncode=None if timed_out and is_failure else 0,
        )
        events = milestones if not is_failure else milestones[: partial_count or 3]
        if not omit_log:
            if corrupt_log and is_failure:
                artifacts_dir.joinpath("fceux_1_1.log").write_bytes(b"\xff\xfe\x00")
            else:
                _write_log(
                    artifacts_dir,
                    events,
                    extra_line=extra_line if is_failure else None,
                    include_tick=include_tick,
                )
        if write_image:
            image_dir = artifacts_dir / "images"
            image_dir.mkdir(parents=True, exist_ok=True)
            pixel = bytes([0, 10, 20, 30])
            focused_events = (
                [
                    "post_probe_world_8_map_arrival",
                    "post_probe_world_8_big_tanks_entered",
                    "post_probe_world_8_big_tanks_gameplay",
                    "post_probe_world_8_big_tanks_clear",
                    BIG_TANKS_FINAL_EVENT,
                ]
                if goal_id == "world_8_big_tanks"
                else [
                    "post_probe_world_8_big_tanks_post_clear",
                    "post_probe_world_8_battleships_entered",
                    "post_probe_world_8_battleships_gameplay",
                    "post_probe_world_8_battleships_clear",
                    BATTLESHIPS_FINAL_EVENT,
                ]
                if goal_id == "world_8_battleships"
                else [
                    "post_probe_world_8_battleships_post_clear",
                    "post_probe_world_8_hand_trap_right_entered",
                    "post_probe_world_8_hand_trap_right_gameplay",
                    "post_probe_world_8_hand_trap_right_reward",
                    "post_probe_world_8_hand_trap_right_post_clear",
                    "post_probe_world_8_hand_trap_center_entered",
                    "post_probe_world_8_hand_trap_center_gameplay",
                    "post_probe_world_8_hand_trap_center_reward",
                    "post_probe_world_8_hand_trap_center_post_clear",
                    "post_probe_world_8_hand_trap_left_entered",
                    "post_probe_world_8_hand_trap_left_gameplay",
                    "post_probe_world_8_hand_trap_left_reward",
                    "post_probe_world_8_hand_trap_left_post_clear",
                    "post_probe_world_8_jet_entered",
                    "post_probe_world_8_jet_gameplay",
                    "post_probe_world_8_jet_boss_defeated",
                    HAND_TRAPS_JET_FINAL_EVENT,
                ]
                if goal_id == "world_8_hand_traps_jet"
                else [
                    "post_probe_world_8_jet_post_clear",
                    "post_probe_world_8_1_entered",
                    "post_probe_world_8_1_gameplay",
                    "post_probe_world_8_1_goal_card",
                    "post_probe_world_8_1_post_clear",
                    "post_probe_world_8_2_entered",
                    "post_probe_world_8_2_gameplay",
                    "post_probe_world_8_2_goal_card",
                    WORLD_8_8_2_FINAL_EVENT,
                ]
                if goal_id == "world_8_8_2"
                else [
                    "post_probe_world_8_2_post_clear",
                    "post_probe_world_8_fortress_entered",
                    "post_probe_world_8_fortress_gameplay",
                    "post_probe_world_8_fortress_switch_activated",
                    "post_probe_world_8_fortress_boss_defeated",
                    "post_probe_world_8_fortress_post_clear",
                    "post_probe_world_8_super_tanks_entered",
                    "post_probe_world_8_super_tanks_gameplay",
                    "post_probe_world_8_super_tanks_final_pipe",
                    "post_probe_world_8_super_tanks_boss_defeated",
                    WORLD_8_SUPER_TANKS_FINAL_EVENT,
                ]
                if goal_id == "world_8_super_tanks"
                else []
            )
            image_events = focused_events or ["review"]
            for index, event in enumerate(image_events, start=1):
                image_dir.joinpath(f"{index:06d}_{event}.gd").write_bytes(
                    b"FCEUXGD0000"[:11] + pixel * (256 * 224)
                )
        return _goal_result(contract, artifacts_dir, events, not is_failure)

    return fake_runner


def test_five_runs_are_isolated_single_attempt_fresh_invocations(tmp_path: Path) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")

    result = run_reliability_gate(
        game_path=game_path,
        artifacts_root=tmp_path / "reliability",
        goal_runner=_fake_runner_factory(calls),
        emulator_resolver=lambda _: "/fake/fceux",
    )

    assert result.passed is True
    assert result.report["successful_runs"] == 5
    assert result.report["success_rate"] == 1.0
    assert len(calls) == 5
    assert {call["attempts"] for call in calls} == {1}
    assert len({call["artifacts_dir"] for call in calls}) == 5
    assert all(call["clean_product_env"] is True for call in calls)
    assert all(call["frame_sleep_seconds"] == 0.0 for call in calls)
    for run in result.report["runs"]:
        invocation = json.loads(
            Path(run["artifacts_dir"]).joinpath("invocation.json").read_text()
        )
        assert invocation["new_fceux_process"] is True
        assert invocation["reuse_savestate"] is False
        assert invocation["reuse_retry_checkpoint"] is False
        assert invocation["attempts"] == 1


def test_one_failure_fails_aggregate_and_preserves_all_run_artifacts(tmp_path: Path) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")

    result = run_reliability_gate(
        game_path=game_path,
        artifacts_root=tmp_path / "reliability",
        goal_runner=_fake_runner_factory(calls, failing_run=3, partial_count=6),
        emulator_resolver=lambda _: "/fake/fceux",
    )

    assert result.passed is False
    assert result.report["completed_runs"] == 5
    assert result.report["successful_runs"] == 4
    assert len(result.report["runs"]) == 5
    failed = result.report["runs"][2]
    assert failed["failure_classification"] == "observer/contract"
    for run in result.report["runs"]:
        run_dir = Path(run["artifacts_dir"])
        assert run_dir.joinpath("run_report.json").is_file()
        assert run_dir.joinpath("fceux_stdout.log").is_file()
        assert run_dir.joinpath("fceux_stderr.log").is_file()


def test_fewer_than_five_successes_are_not_an_authoritative_pass(tmp_path: Path) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")
    result = run_reliability_gate(
        game_path=game_path,
        requested_runs=4,
        artifacts_root=tmp_path / "reliability",
        goal_runner=_fake_runner_factory(calls),
        emulator_resolver=lambda _: "/fake/fceux",
    )

    assert result.report["successful_runs"] == 4
    assert result.report["success_rate"] == 1.0
    assert result.passed is False


def test_big_tanks_requires_three_isolated_fresh_successes(tmp_path: Path) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")

    result = run_reliability_gate(
        game_path=game_path,
        goal_id="world_8_big_tanks",
        artifacts_root=tmp_path / "big-tanks",
        goal_runner=_fake_runner_factory(
            calls, goal_id="world_8_big_tanks", write_image=True
        ),
        emulator_resolver=lambda _: "/fake/fceux",
    )

    assert result.passed is True
    assert result.report["requested_runs"] == 3
    assert result.report["minimum_authoritative_runs"] == 3
    assert result.report["successful_runs"] == 3
    assert result.report["required_final_event"] == BIG_TANKS_FINAL_EVENT
    assert result.report["route_segment_count"] == 16
    assert len(calls) == 3
    assert all(call["attempts"] == 1 for call in calls)
    for run in result.report["runs"]:
        invocation = json.loads(
            Path(run["artifacts_dir"]).joinpath("invocation.json").read_text()
        )
        assert invocation["runner_preset"] == "fceux_world_8_big_tanks"
        assert invocation["new_fceux_process"] is True
        assert invocation["reuse_savestate"] is False
        assert len(run["focused_screenshots"]) == 5
        assert all(Path(path).is_file() for path in run["focused_screenshots"])


def test_two_big_tanks_successes_are_not_authoritative(tmp_path: Path) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")

    result = run_reliability_gate(
        game_path=game_path,
        goal_id="world_8_big_tanks",
        requested_runs=2,
        artifacts_root=tmp_path / "big-tanks",
        goal_runner=_fake_runner_factory(
            calls, goal_id="world_8_big_tanks", write_image=True
        ),
        emulator_resolver=lambda _: "/fake/fceux",
    )

    assert result.report["successful_runs"] == 2
    assert result.passed is False


def test_battleships_requires_three_fresh_successes_and_five_images(
    tmp_path: Path,
) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")
    result = run_reliability_gate(
        game_path=game_path,
        goal_id="world_8_battleships",
        artifacts_root=tmp_path / "battleships",
        goal_runner=_fake_runner_factory(
            calls, goal_id="world_8_battleships", write_image=True
        ),
        emulator_resolver=lambda _: "/fake/fceux",
    )

    assert result.passed is True
    assert result.report["requested_runs"] == 3
    assert result.report["successful_runs"] == 3
    assert result.report["route_segment_count"] == 17
    assert result.report["required_final_event"] == BATTLESHIPS_FINAL_EVENT
    assert all(len(run["focused_screenshots"]) == 5 for run in result.report["runs"])
    assert all(call["clean_product_env"] is True for call in calls)


def test_two_battleships_successes_are_not_authoritative(tmp_path: Path) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")
    result = run_reliability_gate(
        game_path=game_path,
        goal_id="world_8_battleships",
        requested_runs=2,
        artifacts_root=tmp_path / "battleships",
        goal_runner=_fake_runner_factory(
            calls, goal_id="world_8_battleships", write_image=True
        ),
        emulator_resolver=lambda _: "/fake/fceux",
    )

    assert result.report["successful_runs"] == 2
    assert result.report["success_rate"] == 1.0
    assert result.passed is False


def test_hand_traps_jet_requires_three_fresh_successes_and_17_images(
    tmp_path: Path,
) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")
    result = run_reliability_gate(
        game_path=game_path,
        goal_id="world_8_hand_traps_jet",
        artifacts_root=tmp_path / "hand-traps-jet",
        goal_runner=_fake_runner_factory(
            calls, goal_id="world_8_hand_traps_jet", write_image=True
        ),
        emulator_resolver=lambda _: "/fake/fceux",
    )

    assert result.passed is True
    assert result.report["requested_runs"] == 3
    assert result.report["minimum_authoritative_runs"] == 3
    assert result.report["successful_runs"] == 3
    assert result.report["route_segment_count"] == 21
    assert result.report["bridged_segment_count"] == 0
    assert result.report["required_final_event"] == HAND_TRAPS_JET_FINAL_EVENT
    assert result.report["byte_identical_logs"] is True
    assert all(len(run["focused_screenshots"]) == 17 for run in result.report["runs"])
    assert all(run["accepted_boundary_matches"] is True for run in result.report["runs"])
    assert all(call["attempts"] == 1 for call in calls)
    assert all(call["clean_product_env"] is True for call in calls)


def test_two_hand_traps_jet_successes_are_not_authoritative(tmp_path: Path) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")
    result = run_reliability_gate(
        game_path=game_path,
        goal_id="world_8_hand_traps_jet",
        requested_runs=2,
        artifacts_root=tmp_path / "hand-traps-jet",
        goal_runner=_fake_runner_factory(
            calls, goal_id="world_8_hand_traps_jet", write_image=True
        ),
        emulator_resolver=lambda _: "/fake/fceux",
    )

    assert result.report["successful_runs"] == 2
    assert result.report["success_rate"] == 1.0
    assert result.passed is False


@pytest.mark.parametrize("mode", ["missing", "duplicate", "corrupt"])
def test_hand_traps_jet_rejects_invalid_focused_screenshot_sets(
    tmp_path: Path, mode: str
) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")
    base_runner = _fake_runner_factory(
        calls, goal_id="world_8_hand_traps_jet", write_image=True
    )

    def damaged_runner(contract, **kwargs):
        result = base_runner(contract, **kwargs)
        image_dir = kwargs["artifacts_dir"] / "images"
        target = next(image_dir.glob("*_post_probe_world_8_jet_gameplay.gd"))
        if mode == "missing":
            target.unlink()
        elif mode == "duplicate":
            image_dir.joinpath(
                "999999_post_probe_world_8_jet_gameplay.gd"
            ).write_bytes(target.read_bytes())
        else:
            target.write_bytes(b"corrupt")
        return result

    result = run_reliability_gate(
        game_path=game_path,
        goal_id="world_8_hand_traps_jet",
        requested_runs=1,
        artifacts_root=tmp_path / mode,
        goal_runner=damaged_runner,
        emulator_resolver=lambda _: "/fake/fceux",
    )

    run = result.report["runs"][0]
    assert run["passed"] is False
    assert run["failure_classification"] == "artifact-integrity"
    assert run["screenshot_evidence_error"] is not None


def test_hand_traps_jet_rejects_wrong_final_map_boundary(tmp_path: Path) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")
    base_runner = _fake_runner_factory(
        calls, goal_id="world_8_hand_traps_jet", write_image=True
    )

    def wrong_boundary_runner(contract, **kwargs):
        result = base_runner(contract, **kwargs)
        log_path = kwargs["artifacts_dir"] / "fceux_1_1.log"
        log_path.write_text(
            log_path.read_text().replace(
                "map_page=2 map_cursor_x=64 map_cursor_y=112",
                "map_page=1 map_cursor_x=96 map_cursor_y=80",
            )
        )
        return result

    result = run_reliability_gate(
        game_path=game_path,
        goal_id="world_8_hand_traps_jet",
        requested_runs=1,
        artifacts_root=tmp_path / "wrong-boundary",
        goal_runner=wrong_boundary_runner,
        emulator_resolver=lambda _: "/fake/fceux",
    )

    run = result.report["runs"][0]
    assert run["passed"] is False
    assert run["accepted_boundary_matches"] is False
    assert run["failure_classification"] == "wrong-boundary"


def test_world_8_8_2_requires_three_fresh_successes_and_exactly_nine_images(
    tmp_path: Path,
) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")
    result = run_reliability_gate(
        game_path=game_path,
        goal_id="world_8_8_2",
        artifacts_root=tmp_path / "world-8-8-2",
        goal_runner=_fake_runner_factory(
            calls, goal_id="world_8_8_2", write_image=True
        ),
        emulator_resolver=lambda _: "/fake/fceux",
    )

    assert result.passed is True
    assert result.report["requested_runs"] == 3
    assert result.report["minimum_authoritative_runs"] == 3
    assert result.report["successful_runs"] == 3
    assert result.report["success_rate"] == 1.0
    assert result.report["route_segment_count"] == 23
    assert result.report["bridged_segment_count"] == 0
    assert result.report["required_final_event"] == WORLD_8_8_2_FINAL_EVENT
    assert result.report["byte_identical_logs"] is True
    assert all(len(run["focused_screenshots"]) == 9 for run in result.report["runs"])
    assert all(run["accepted_boundary_matches"] is True for run in result.report["runs"])
    assert all(call["attempts"] == 1 for call in calls)
    assert all(call["clean_product_env"] is True for call in calls)


def test_two_world_8_8_2_successes_are_not_authoritative(tmp_path: Path) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")
    result = run_reliability_gate(
        game_path=game_path,
        goal_id="world_8_8_2",
        requested_runs=2,
        artifacts_root=tmp_path / "world-8-8-2",
        goal_runner=_fake_runner_factory(
            calls, goal_id="world_8_8_2", write_image=True
        ),
        emulator_resolver=lambda _: "/fake/fceux",
    )

    assert result.report["successful_runs"] == 2
    assert result.report["success_rate"] == 1.0
    assert result.passed is False


def test_world_8_super_tanks_requires_three_fresh_successes_and_eleven_images(
    tmp_path: Path,
) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")
    result = run_reliability_gate(
        game_path=game_path,
        goal_id="world_8_super_tanks",
        artifacts_root=tmp_path / "world-8-super-tanks",
        goal_runner=_fake_runner_factory(
            calls, goal_id="world_8_super_tanks", write_image=True
        ),
        emulator_resolver=lambda _: "/fake/fceux",
    )

    assert result.passed is True
    assert result.report["requested_runs"] == 3
    assert result.report["successful_runs"] == 3
    assert result.report["route_segment_count"] == 25
    assert result.report["bridged_segment_count"] == 0
    assert result.report["required_final_event"] == WORLD_8_SUPER_TANKS_FINAL_EVENT
    assert result.report["byte_identical_logs"] is True
    assert all(len(run["focused_screenshots"]) == 11 for run in result.report["runs"])
    assert all(call["attempts"] == 1 for call in calls)
    assert all(call["timeout_seconds"] == 600 for call in calls)


@pytest.mark.parametrize("mode", ["missing", "duplicate", "corrupt"])
def test_world_8_super_tanks_rejects_invalid_focused_screenshot_sets(
    tmp_path: Path, mode: str
) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")
    base_runner = _fake_runner_factory(
        calls, goal_id="world_8_super_tanks", write_image=True
    )

    def damaged_runner(contract, **kwargs):
        result = base_runner(contract, **kwargs)
        image_dir = kwargs["artifacts_dir"] / "images"
        target = next(
            image_dir.glob("*_post_probe_world_8_super_tanks_boss_defeated.gd")
        )
        if mode == "missing":
            target.unlink()
        elif mode == "duplicate":
            image_dir.joinpath(
                "999999_post_probe_world_8_super_tanks_boss_defeated.gd"
            ).write_bytes(target.read_bytes())
        else:
            target.write_bytes(b"corrupt")
        return result

    result = run_reliability_gate(
        game_path=game_path,
        goal_id="world_8_super_tanks",
        requested_runs=1,
        artifacts_root=tmp_path / mode,
        goal_runner=damaged_runner,
        emulator_resolver=lambda _: "/fake/fceux",
    )

    run = result.report["runs"][0]
    assert run["passed"] is False
    assert run["failure_classification"] == "artifact-integrity"


def test_world_8_super_tanks_failure_reports_last_good_and_first_missing(
    tmp_path: Path,
) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")
    result = run_reliability_gate(
        game_path=game_path,
        goal_id="world_8_super_tanks",
        requested_runs=1,
        artifacts_root=tmp_path / "failure",
        goal_runner=_fake_runner_factory(
            calls,
            goal_id="world_8_super_tanks",
            failing_run=1,
            partial_count=24,
            extra_line="frame=999 event=post_probe_world_8_super_tanks_timeout",
            write_image=True,
        ),
        emulator_resolver=lambda _: "/fake/fceux",
    )

    run = result.report["runs"][0]
    assert run["failure_classification"] == "timeout"
    assert run["last_accepted_segment"] == "world_8_fortress_clear"
    assert run["first_missing_milestone"] == {
        "segment_id": "world_8_super_tanks_clear",
        "event": WORLD_8_SUPER_TANKS_FINAL_EVENT,
    }


@pytest.mark.parametrize("mode", ["missing", "duplicate", "corrupt"])
def test_world_8_8_2_rejects_invalid_focused_screenshot_sets(
    tmp_path: Path, mode: str
) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")
    base_runner = _fake_runner_factory(
        calls, goal_id="world_8_8_2", write_image=True
    )

    def damaged_runner(contract, **kwargs):
        result = base_runner(contract, **kwargs)
        image_dir = kwargs["artifacts_dir"] / "images"
        target = next(image_dir.glob("*_post_probe_world_8_2_goal_card.gd"))
        if mode == "missing":
            target.unlink()
        elif mode == "duplicate":
            image_dir.joinpath("999999_post_probe_world_8_2_goal_card.gd").write_bytes(
                target.read_bytes()
            )
        else:
            target.write_bytes(b"corrupt")
        return result

    result = run_reliability_gate(
        game_path=game_path,
        goal_id="world_8_8_2",
        requested_runs=1,
        artifacts_root=tmp_path / mode,
        goal_runner=damaged_runner,
        emulator_resolver=lambda _: "/fake/fceux",
    )

    run = result.report["runs"][0]
    assert run["passed"] is False
    assert run["failure_classification"] == "artifact-integrity"
    assert run["screenshot_evidence_error"] is not None


def test_world_8_8_2_rejects_wrong_fortress_boundary(tmp_path: Path) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")
    base_runner = _fake_runner_factory(
        calls, goal_id="world_8_8_2", write_image=True
    )

    def wrong_boundary_runner(contract, **kwargs):
        result = base_runner(contract, **kwargs)
        log_path = kwargs["artifacts_dir"] / "fceux_1_1.log"
        log_path.write_text(
            log_path.read_text().replace(
                "map_page=2 map_cursor_x=64 map_cursor_y=144",
                "map_page=2 map_cursor_x=32 map_cursor_y=144",
            )
        )
        return result

    result = run_reliability_gate(
        game_path=game_path,
        goal_id="world_8_8_2",
        requested_runs=1,
        artifacts_root=tmp_path / "wrong-boundary",
        goal_runner=wrong_boundary_runner,
        emulator_resolver=lambda _: "/fake/fceux",
    )

    run = result.report["runs"][0]
    assert run["passed"] is False
    assert run["accepted_boundary_matches"] is False
    assert run["failure_classification"] == "wrong-boundary"


def test_world_8_8_2_failure_reports_last_good_and_first_missing(
    tmp_path: Path,
) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")
    result = run_reliability_gate(
        game_path=game_path,
        goal_id="world_8_8_2",
        requested_runs=1,
        artifacts_root=tmp_path / "world-8-8-2-failure",
        goal_runner=_fake_runner_factory(
            calls,
            goal_id="world_8_8_2",
            failing_run=1,
            partial_count=22,
            extra_line="frame=99 event=post_probe_world_8_2_timeout",
            write_image=True,
        ),
        emulator_resolver=lambda _: "/fake/fceux",
    )

    run = result.report["runs"][0]
    assert run["failure_classification"] == "timeout"
    assert run["last_accepted_segment"] == "world_8_1_clear"
    assert run["first_missing_milestone"] == {
        "segment_id": "world_8_2_clear",
        "event": WORLD_8_8_2_FINAL_EVENT,
    }


def test_only_battleships_requires_byte_identical_logs(tmp_path: Path) -> None:
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")

    def run_with_distinct_log(goal_id: str, artifacts_root: Path):
        calls: list[dict] = []
        base_runner = _fake_runner_factory(
            calls,
            goal_id=goal_id,
            write_image=goal_id == "world_8_battleships",
        )

        def distinct_runner(contract, **kwargs):
            result = base_runner(contract, **kwargs)
            log_path = kwargs["artifacts_dir"] / "fceux_1_1.log"
            with log_path.open("a") as handle:
                handle.write(f"frame=999 event=diagnostic_variant_{len(calls)}\n")
            return result

        return run_reliability_gate(
            game_path=game_path,
            goal_id=goal_id,
            artifacts_root=artifacts_root,
            goal_runner=distinct_runner,
            emulator_resolver=lambda _: "/fake/fceux",
        )

    default = run_with_distinct_log(
        "world_8_double_whistle", tmp_path / "default-distinct"
    )
    battleships = run_with_distinct_log(
        "world_8_battleships", tmp_path / "battleships-distinct"
    )

    assert default.report["byte_identical_logs"] is False
    assert default.passed is True
    assert battleships.report["byte_identical_logs"] is False
    assert battleships.passed is False


def test_battleships_failure_retains_big_tanks_boundary_and_missing_milestone(
    tmp_path: Path,
) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")
    result = run_reliability_gate(
        game_path=game_path,
        goal_id="world_8_battleships",
        requested_runs=1,
        artifacts_root=tmp_path / "battleships-failure",
        goal_runner=_fake_runner_factory(
            calls,
            goal_id="world_8_battleships",
            failing_run=1,
            partial_count=16,
            extra_line="frame=99 event=post_probe_world_8_battleships_wrong_stage",
            write_image=True,
        ),
        emulator_resolver=lambda _: "/fake/fceux",
    )

    run = result.report["runs"][0]
    assert run["failure_classification"] == "wrong-stage"
    assert run["last_accepted_segment"] == "world_8_big_tanks_clear"
    assert run["first_missing_milestone"] == {
        "segment_id": "world_8_battleships_clear",
        "event": BATTLESHIPS_FINAL_EVENT,
    }


def test_battleships_rejects_missing_or_corrupt_focused_screenshot(
    tmp_path: Path,
) -> None:
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")

    for mode in ("missing", "corrupt"):
        calls: list[dict] = []
        base_runner = _fake_runner_factory(
            calls, goal_id="world_8_battleships", write_image=True
        )

        def damaged_runner(contract, *, _mode=mode, **kwargs):
            result = base_runner(contract, **kwargs)
            target = kwargs["artifacts_dir"] / "images" / (
                "000005_post_probe_world_8_battleships_post_clear.gd"
            )
            if _mode == "missing":
                target.unlink()
            else:
                target.write_bytes(b"corrupt")
            return result

        result = run_reliability_gate(
            game_path=game_path,
            goal_id="world_8_battleships",
            requested_runs=1,
            artifacts_root=tmp_path / f"battleships-{mode}",
            goal_runner=damaged_runner,
            emulator_resolver=lambda _: "/fake/fceux",
        )

        run = result.report["runs"][0]
        assert run["passed"] is False
        assert run["failure_classification"] == "artifact-integrity"
        assert run["screenshot_evidence_error"] is not None


def test_big_tanks_failure_retains_prefix_boundary_and_missing_segment(
    tmp_path: Path,
) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")

    result = run_reliability_gate(
        game_path=game_path,
        goal_id="world_8_big_tanks",
        requested_runs=1,
        artifacts_root=tmp_path / "big-tanks-failure",
        goal_runner=_fake_runner_factory(
            calls,
            goal_id="world_8_big_tanks",
            failing_run=1,
            partial_count=15,
            extra_line="frame=99 event=post_probe_world_8_big_tanks_wrong_stage",
        ),
        emulator_resolver=lambda _: "/fake/fceux",
    )

    run = result.report["runs"][0]
    assert run["failure_classification"] == "wrong-stage"
    assert run["last_accepted_segment"] == "world_8_map_arrival"
    assert run["first_missing_milestone"] == {
        "segment_id": "world_8_big_tanks_clear",
        "event": BIG_TANKS_FINAL_EVENT,
    }
    assert Path(run["route_log"]).is_file()
    assert Path(run["fceux_stdout"]).is_file()
    assert Path(run["fceux_stderr"]).is_file()


def test_timeout_is_classified_with_partial_artifacts(tmp_path: Path) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")
    result = run_reliability_gate(
        game_path=game_path,
        requested_runs=1,
        artifacts_root=tmp_path / "reliability",
        goal_runner=_fake_runner_factory(
            calls, failing_run=1, partial_count=4, timed_out=True
        ),
        emulator_resolver=lambda _: "/fake/fceux",
    )

    run = result.report["runs"][0]
    assert run["failure_classification"] == "timeout"
    assert run["structured_log_sha256"] is not None
    assert Path(run["fceux_stdout"]).is_file()
    assert run["first_missing_milestone"]["segment_id"] is not None


def test_emulator_launch_and_gameplay_failures_are_distinct(tmp_path: Path) -> None:
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")

    def launch_failure(contract, **kwargs):
        artifacts_dir = kwargs["artifacts_dir"]
        _write_execution(
            artifacts_dir,
            returncode=None,
            launch_error="FileNotFoundError: fceux",
        )
        raise FileNotFoundError("fceux")

    launch_result = run_reliability_gate(
        game_path=game_path,
        requested_runs=1,
        artifacts_root=tmp_path / "launch",
        goal_runner=launch_failure,
        emulator_resolver=lambda _: "/fake/fceux",
    )
    assert (
        launch_result.report["runs"][0]["failure_classification"]
        == "emulator-launch"
    )

    calls: list[dict] = []
    gameplay_result = run_reliability_gate(
        game_path=game_path,
        requested_runs=1,
        artifacts_root=tmp_path / "gameplay",
        goal_runner=_fake_runner_factory(
            calls,
            failing_run=1,
            partial_count=15,
            extra_line="frame=99 event=post_probe_world_8_map_missing",
        ),
        emulator_resolver=lambda _: "/fake/fceux",
    )
    assert (
        gameplay_result.report["runs"][0]["failure_classification"]
        == "gameplay"
    )


def test_missing_and_corrupt_logs_are_artifact_integrity_failures(tmp_path: Path) -> None:
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")
    configurations = ((True, False), (False, True))

    for index, (omit_log, corrupt_log) in enumerate(configurations):
        calls: list[dict] = []
        result = run_reliability_gate(
            game_path=game_path,
            requested_runs=1,
            artifacts_root=tmp_path / f"reliability-{index}",
            goal_runner=_fake_runner_factory(
                calls,
                failing_run=1,
                omit_log=omit_log,
                corrupt_log=corrupt_log,
            ),
            emulator_resolver=lambda _: "/fake/fceux",
        )
        run = result.report["runs"][0]
        assert run["failure_classification"] == "artifact-integrity"
        assert run["log_integrity_error"] is not None


def test_last_good_and_first_missing_contract_milestones_are_reported(
    tmp_path: Path,
) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")
    result = run_reliability_gate(
        game_path=game_path,
        requested_runs=1,
        artifacts_root=tmp_path / "reliability",
        goal_runner=_fake_runner_factory(calls, failing_run=1, partial_count=3),
        emulator_resolver=lambda _: "/fake/fceux",
    )

    run = result.report["runs"][0]
    assert run["last_accepted_segment"] == "world_1_2_clear"
    assert run["last_accepted_product_event"] == "post_probe_1_2_success_course_clear"
    assert run["first_missing_milestone"] == {
        "segment_id": "world_1_3_whistle",
        "event": "post_probe_1_3_whistle_room_success",
    }


def test_watchable_playback_is_review_only_and_separate(tmp_path: Path) -> None:
    calls: list[dict] = []
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")
    result = run_watchable_playback(
        game_path=game_path,
        artifacts_root=tmp_path / "review",
        frame_sleep_seconds=0.0035,
        goal_runner=_fake_runner_factory(
            calls, include_tick=True, write_image=True
        ),
        emulator_resolver=lambda _: "/fake/fceux",
    )

    assert result.passed is True
    assert result.report["validation_policy"] == "review_only"
    assert result.report["counts_toward_reliability"] is False
    assert result.report["promotable"] is False
    assert result.report["contact_sheet"] is not None
    assert result.report["tick_trace"] is not None
    assert calls[0]["attempts"] == 1
    assert calls[0]["frame_sleep_seconds"] == 0.0035


def test_prohibited_tactics_cannot_pass(tmp_path: Path) -> None:
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")
    prohibited_lines = (
        "frame=99 event=post_probe_1_airship_stage_bridge",
        "frame=99 event=position_mutation",
        "frame=99 event=post_probe_1_6_opening_search_success savestate=loaded",
    )

    for index, line in enumerate(prohibited_lines):
        calls: list[dict] = []
        result = run_reliability_gate(
            game_path=game_path,
            requested_runs=1,
            artifacts_root=tmp_path / f"prohibited-{index}",
            goal_runner=_fake_runner_factory(
                calls, failing_run=1, partial_count=15, extra_line=line
            ),
            emulator_resolver=lambda _: "/fake/fceux",
        )
        assert result.report["runs"][0]["failure_classification"] == "prohibited-tactic"
        assert result.passed is False


def test_diagnostic_route_fallback_fails_preflight(
    monkeypatch, tmp_path: Path
) -> None:
    game_path = tmp_path / "local-game-file.nes"
    game_path.write_bytes(b"local-only")
    contract = load_goal_contract(Path("data/goals/world_8_double_whistle.yaml"))
    diagnostic = replace(
        contract,
        runner={**contract.runner, "preset": "fceux_world_1_king"},
    )
    monkeypatch.setattr(
        "smb3_agent.reliability.load_goal_contract", lambda _: diagnostic
    )

    result = run_reliability_gate(
        game_path=game_path,
        requested_runs=1,
        artifacts_root=tmp_path / "reliability",
        emulator_resolver=lambda _: "/fake/fceux",
    )

    assert result.report["completed_runs"] == 0
    assert result.report["preflight"]["failure_classification"] == "preflight"
    assert "diagnostic preset" in result.report["preflight"]["detail"]


def test_generated_evidence_and_local_game_assets_are_untracked_and_ignored() -> None:
    for path in (
        "artifacts/reliability/example/reliability_report.json",
        "artifacts/review/example/contact_sheet.png",
        "artifacts/review/example/fceux_1_1.log",
        "local-rank27-game.nes",
        "local-rank27.state",
    ):
        ignored = subprocess.run(
            ["git", "check-ignore", "--quiet", path],
            cwd=REPOSITORY_ROOT,
            check=False,
        )
        assert ignored.returncode == 0, path

    tracked_local_assets = subprocess.run(
        ["git", "ls-files", "*.nes", "*.state", "artifacts/*"],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert tracked_local_assets.stdout == ""
