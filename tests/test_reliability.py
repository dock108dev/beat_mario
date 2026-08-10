from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import subprocess

from smb3_agent.fceux_harness import AttemptSummary, BatchSummary
from smb3_agent.goals import GoalRunResult, load_goal_contract
from smb3_agent.reliability import (
    FINAL_EVENT,
    run_reliability_gate,
    run_watchable_playback,
)
from smb3_agent.segments import load_segment_catalog


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _milestone_events() -> list[str]:
    contract = load_goal_contract(Path("data/goals/world_8_double_whistle.yaml"))
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
):
    milestones = _milestone_events()

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
            image_dir.joinpath("000001_review.gd").write_bytes(
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
