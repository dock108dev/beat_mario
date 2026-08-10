from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any, Callable

from smb3_agent.fceux_harness import BatchSummary, parse_fceux_log
from smb3_agent.fceux_images import (
    convert_gd_directory,
    load_gd_screenshot,
    write_contact_sheet,
)
from smb3_agent.goals import (
    ACTIVE_PRODUCT_GOAL_ID,
    GoalContract,
    GoalRunResult,
    load_goal_contract,
    resolve_goal_path,
    run_goal_contract,
)
from smb3_agent.segments import (
    SegmentCatalog,
    load_segment_catalog,
    validate_goal_segments,
)


FINAL_EVENT = "post_probe_world_8_map_arrival"
BIG_TANKS_FINAL_EVENT = "post_probe_world_8_big_tanks_post_clear"
BATTLESHIPS_FINAL_EVENT = "post_probe_world_8_battleships_post_clear"
RELIABILITY_ARTIFACTS_ROOT = Path("artifacts/reliability/world_8_double_whistle")
WATCHABLE_ARTIFACTS_ROOT = Path("artifacts/review/world_8_double_whistle")
EVENT_RE = re.compile(r"\bevent=(?P<event>[A-Za-z0-9_]+)\b")
FIELD_RE = re.compile(r"(?P<key>[A-Za-z][A-Za-z0-9_]*)=(?P<value>\S+)")
FAILURE_EVENT_TOKENS = (
    "bad_state",
    "_failed",
    "_life_lost",
    "_missing",
    "_mismatch",
    "_no_entry",
    "_unstable",
    "_wrong_",
    "_death",
    "_stall",
    "_timeout",
    "_false_clear",
    "_unexpected_next_stage",
    "_ambiguous_",
)
PROHIBITED_SEARCH_TOKENS = (
    "_search_candidate",
    "_search_checkpoint",
    "_search_complete",
    "_search_entered",
    "_search_failed",
    "_search_success",
    "_search_best",
    "post_probe_1_2_search_",
    "post_probe_1_3_power_search_",
    "post_probe_1_3_white_search_",
    "post_probe_1_3_block_clear_search_",
    "post_probe_1_6_goal_card_search_",
    "post_probe_1_6_opening_search_",
    "post_probe_1_6_segment_search_",
    "post_probe_world_1_roamer_search_",
)
PROHIBITED_ARTIFACT_SUFFIXES = (
    ".sav",
    ".state",
    ".fm2",
    ".nes",
)


@dataclass(frozen=True)
class ReliabilityProfile:
    goal_id: str
    preset: str
    final_event: str
    minimum_authoritative_runs: int
    accepted_boundary: dict[str, int]
    focused_events: tuple[str, ...] = ()
    require_byte_identical_logs: bool = False


RELIABILITY_PROFILES = {
    ACTIVE_PRODUCT_GOAL_ID: ReliabilityProfile(
        goal_id=ACTIVE_PRODUCT_GOAL_ID,
        preset="fceux_world_8_double_whistle",
        final_event=FINAL_EVENT,
        minimum_authoritative_runs=5,
        accepted_boundary={"world_number": 7, "object_set": 0},
    ),
    "world_8_big_tanks": ReliabilityProfile(
        goal_id="world_8_big_tanks",
        preset="fceux_world_8_big_tanks",
        final_event=BIG_TANKS_FINAL_EVENT,
        minimum_authoritative_runs=3,
        accepted_boundary={
            "world_number": 7,
            "object_set": 0,
            "map_cursor_x": 32,
            "map_cursor_y": 80,
        },
        focused_events=(
            "post_probe_world_8_map_arrival",
            "post_probe_world_8_big_tanks_entered",
            "post_probe_world_8_big_tanks_gameplay",
            "post_probe_world_8_big_tanks_clear",
            "post_probe_world_8_big_tanks_post_clear",
        ),
    ),
    "world_8_battleships": ReliabilityProfile(
        goal_id="world_8_battleships",
        preset="fceux_world_8_battleships",
        final_event=BATTLESHIPS_FINAL_EVENT,
        minimum_authoritative_runs=3,
        accepted_boundary={
            "world_number": 7,
            "object_set": 0,
            "map_cursor_x": 128,
            "map_cursor_y": 112,
        },
        focused_events=(
            "post_probe_world_8_big_tanks_post_clear",
            "post_probe_world_8_battleships_entered",
            "post_probe_world_8_battleships_gameplay",
            "post_probe_world_8_battleships_clear",
            "post_probe_world_8_battleships_post_clear",
        ),
        require_byte_identical_logs=True,
    ),
}


@dataclass(frozen=True)
class ReliabilityResult:
    report: dict[str, Any]
    report_path: Path

    @property
    def passed(self) -> bool:
        return bool(self.report.get("overall_pass"))

    def to_text(self) -> str:
        lines = [
            f"mode={self.report['mode']}",
            f"goal_id={self.report.get('goal_id')}",
            f"source_commit={self.report.get('source_commit')}",
            f"requested_runs={self.report.get('requested_runs')}",
            f"completed_runs={self.report.get('completed_runs')}",
            f"successful_runs={self.report.get('successful_runs')}",
            f"success_rate={self.report.get('success_rate')}",
            f"overall_pass={str(self.passed).lower()}",
            f"byte_identical_logs={str(bool(self.report.get('byte_identical_logs'))).lower()}",
            f"artifacts_dir={self.report.get('artifacts_dir')}",
            f"report_path={self.report_path}",
        ]
        for run in self.report.get("runs", ()):  # pragma: no branch - compact output
            lines.append(
                "run_{index:02d}={result} final_event={event} metrics_passed={metrics} "
                "classification={classification} artifacts={artifacts}".format(
                    index=run["run_index"],
                    result=run["result"],
                    event=run.get("final_event"),
                    metrics=str(bool(run.get("metrics_passed"))).lower(),
                    classification=run.get("failure_classification"),
                    artifacts=run["artifacts_dir"],
                )
            )
        return "\n".join(lines)


@dataclass(frozen=True)
class WatchableResult:
    report: dict[str, Any]
    report_path: Path

    @property
    def passed(self) -> bool:
        return bool(self.report.get("review_pass"))

    def to_text(self) -> str:
        run = self.report.get("run", {})
        return "\n".join(
            (
                "mode=watchable",
                "validation_policy=review_only",
                "counts_toward_reliability=false",
                f"goal_id={self.report.get('goal_id')}",
                f"route_passed={str(bool(run.get('passed'))).lower()}",
                f"review_pass={str(self.passed).lower()}",
                f"final_event={run.get('final_event')}",
                f"metrics_passed={str(bool(run.get('metrics_passed'))).lower()}",
                f"contact_sheet={self.report.get('contact_sheet')}",
                f"tick_trace={self.report.get('tick_trace')}",
                f"artifacts_dir={self.report.get('artifacts_dir')}",
                f"report_path={self.report_path}",
            )
        )


def run_reliability_gate(
    *,
    game_path: Path,
    requested_runs: int | None = None,
    artifacts_root: Path | None = None,
    timeout_seconds: int = 180,
    goal_id: str = ACTIVE_PRODUCT_GOAL_ID,
    goal_runner: Callable[..., GoalRunResult] = run_goal_contract,
    emulator_resolver: Callable[[str], str | None] = shutil.which,
    progress: Callable[[str], None] | None = None,
) -> ReliabilityResult:
    profile = _reliability_profile(goal_id)
    capture_images = bool(profile.focused_events)
    if requested_runs is None:
        requested_runs = profile.minimum_authoritative_runs
    if artifacts_root is None:
        artifacts_root = Path("artifacts/reliability") / goal_id
    started_at = datetime.now(timezone.utc)
    artifacts_dir = _new_artifacts_dir(artifacts_root, "reliability")
    report_path = artifacts_dir / "reliability_report.json"
    artifacts_dir.mkdir(parents=True, exist_ok=False)

    base_report = _base_report(
        mode="reliability",
        validation_policy="authoritative_all_runs_required",
        artifacts_dir=artifacts_dir,
        started_at=started_at,
        goal_id=goal_id,
    )
    base_report.update(
        {
            "requested_runs": requested_runs,
            "minimum_authoritative_runs": profile.minimum_authoritative_runs,
            "completed_runs": 0,
            "successful_runs": 0,
            "success_rate": 0.0,
            "overall_pass": False,
            "runs": [],
            "capture_settings": {
                "capture_images": capture_images,
                "capture_ticks": False,
                "frame_sleep_seconds": 0.0,
                "throttle": "unthrottled",
            },
        }
    )

    try:
        contract, catalog, milestones = _load_product_contract(
            game_path=game_path,
            emulator_resolver=emulator_resolver,
            requested_runs=requested_runs,
            profile=profile,
        )
    except Exception as exc:
        base_report["preflight"] = {
            "passed": False,
            "failure_classification": "preflight",
            "detail": f"{type(exc).__name__}: {exc}",
            "recommended_investigation": _recommendation("preflight", None),
        }
        _finish_report(base_report, started_at)
        _write_json(report_path, base_report)
        return ReliabilityResult(report=base_report, report_path=report_path)

    base_report.update(_contract_identity(contract, catalog, profile))
    base_report["preflight"] = {"passed": True}
    runs: list[dict[str, Any]] = []
    for run_index in range(1, requested_runs + 1):
        run_dir = artifacts_dir / f"run_{run_index:02d}"
        run_dir.mkdir(parents=True, exist_ok=False)
        invocation = _invocation_record(
            run_index=run_index,
            mode="reliability",
            run_dir=run_dir,
            timeout_seconds=timeout_seconds,
            capture_images=capture_images,
            capture_ticks=False,
            frame_sleep_seconds=0.0,
            contract=contract,
        )
        _write_json(run_dir / "invocation.json", invocation)
        if progress is not None:
            progress(f"reliability run {run_index}/{requested_runs} starting")

        goal_result: GoalRunResult | None = None
        run_exception: Exception | None = None
        run_started_at = datetime.now(timezone.utc)
        try:
            goal_result = goal_runner(
                contract,
                game_path=game_path,
                attempts=1,
                artifacts_dir=run_dir,
                capture_images=capture_images,
                capture_ticks=False,
                clean_product_env=True,
                frame_sleep_seconds=0.0,
                timeout_seconds=timeout_seconds,
            )
        except Exception as exc:
            run_exception = exc

        run_report = _inspect_run(
            run_index=run_index,
            mode="reliability",
            run_dir=run_dir,
            contract=contract,
            milestones=milestones,
            goal_result=goal_result,
            run_exception=run_exception,
            started_at=run_started_at,
            capture_images=capture_images,
            capture_ticks=False,
            frame_sleep_seconds=0.0,
            required_final_event=profile.final_event,
            required_image_events=profile.focused_events,
        )
        _write_json(run_dir / "run_report.json", run_report)
        runs.append(run_report)
        if progress is not None:
            progress(
                f"reliability run {run_index}/{requested_runs} {run_report['result']}"
            )

    successes = sum(1 for run in runs if run["passed"])
    log_hashes = [run["structured_log_sha256"] for run in runs]
    non_null_hashes = [digest for digest in log_hashes if digest is not None]
    byte_identical_logs = len(non_null_hashes) == requested_runs and len(
        set(non_null_hashes)
    ) == 1
    base_report.update(
        {
            "runs": runs,
            "completed_runs": len(runs),
            "successful_runs": successes,
            "success_rate": round(successes / requested_runs, 6),
            "overall_pass": requested_runs >= profile.minimum_authoritative_runs
            and len(runs) == requested_runs
            and successes == requested_runs
            and (byte_identical_logs or not profile.require_byte_identical_logs),
            "structured_log_sha256s": log_hashes,
            "byte_identical_logs": byte_identical_logs,
            "failure_classifications": dict(
                Counter(
                    run["failure_classification"]
                    for run in runs
                    if run["failure_classification"] is not None
                )
            ),
        }
    )
    _finish_report(base_report, started_at)
    _write_json(report_path, base_report)
    return ReliabilityResult(report=base_report, report_path=report_path)


def run_watchable_playback(
    *,
    game_path: Path,
    artifacts_root: Path | None = None,
    frame_sleep_seconds: float = 0.0035,
    timeout_seconds: int = 600,
    contact_sheet_columns: int = 4,
    goal_id: str = ACTIVE_PRODUCT_GOAL_ID,
    goal_runner: Callable[..., GoalRunResult] = run_goal_contract,
    emulator_resolver: Callable[[str], str | None] = shutil.which,
    progress: Callable[[str], None] | None = None,
) -> WatchableResult:
    profile = _reliability_profile(goal_id)
    if artifacts_root is None:
        artifacts_root = Path("artifacts/review") / goal_id
    started_at = datetime.now(timezone.utc)
    artifacts_dir = _new_artifacts_dir(artifacts_root, "watchable")
    report_path = artifacts_dir / "watchable_report.json"
    artifacts_dir.mkdir(parents=True, exist_ok=False)
    report = _base_report(
        mode="watchable",
        validation_policy="review_only",
        artifacts_dir=artifacts_dir,
        started_at=started_at,
        goal_id=goal_id,
    )
    report.update(
        {
            "review_only": True,
            "promotable": False,
            "counts_toward_reliability": False,
            "review_pass": False,
            "capture_settings": {
                "capture_images": True,
                "capture_ticks": True,
                "frame_sleep_seconds": frame_sleep_seconds,
                "throttle": "watchable",
            },
        }
    )

    try:
        if frame_sleep_seconds <= 0:
            raise ValueError("watchable frame sleep must be greater than zero")
        contract, catalog, milestones = _load_product_contract(
            game_path=game_path,
            emulator_resolver=emulator_resolver,
            requested_runs=1,
            profile=profile,
        )
    except Exception as exc:
        report["preflight"] = {
            "passed": False,
            "failure_classification": "preflight",
            "detail": f"{type(exc).__name__}: {exc}",
            "recommended_investigation": _recommendation("preflight", None),
        }
        _finish_report(report, started_at)
        _write_json(report_path, report)
        return WatchableResult(report=report, report_path=report_path)

    report.update(_contract_identity(contract, catalog, profile))
    report["preflight"] = {"passed": True}
    invocation = _invocation_record(
        run_index=1,
        mode="watchable",
        run_dir=artifacts_dir,
        timeout_seconds=timeout_seconds,
        capture_images=True,
        capture_ticks=True,
        frame_sleep_seconds=frame_sleep_seconds,
        contract=contract,
    )
    invocation.update(
        {
            "validation_policy": "review_only",
            "counts_toward_reliability": False,
            "promotable": False,
        }
    )
    _write_json(artifacts_dir / "invocation.json", invocation)
    if progress is not None:
        progress("watchable review-only playback starting")

    goal_result: GoalRunResult | None = None
    run_exception: Exception | None = None
    try:
        goal_result = goal_runner(
            contract,
            game_path=game_path,
            attempts=1,
            artifacts_dir=artifacts_dir,
            capture_images=True,
            capture_ticks=True,
            clean_product_env=True,
            frame_sleep_seconds=frame_sleep_seconds,
            timeout_seconds=timeout_seconds,
        )
    except Exception as exc:
        run_exception = exc

    run_report = _inspect_run(
        run_index=1,
        mode="watchable",
        run_dir=artifacts_dir,
        contract=contract,
        milestones=milestones,
        goal_result=goal_result,
        run_exception=run_exception,
        started_at=started_at,
        capture_images=True,
        capture_ticks=True,
        frame_sleep_seconds=frame_sleep_seconds,
        required_final_event=profile.final_event,
        required_image_events=(),
    )
    tick_trace_path = artifacts_dir / "state_tick_trace.log"
    _write_tick_trace(artifacts_dir / "fceux_1_1.log", tick_trace_path)

    contact_sheet_path = artifacts_dir / "review" / "contact_sheet.png"
    contact_sheet_error: str | None = None
    converted_count = 0
    try:
        converted = convert_gd_directory(
            artifacts_dir / "images", artifacts_dir / "review" / "png"
        )
        converted_count = len(converted)
        focused = _focused_images(converted, profile.focused_events)
        write_contact_sheet(focused, contact_sheet_path, columns=contact_sheet_columns)
    except Exception as exc:
        contact_sheet_error = f"{type(exc).__name__}: {exc}"

    review_pass = (
        run_report["passed"]
        and contact_sheet_error is None
        and tick_trace_path.is_file()
    )
    report.update(
        {
            "run": run_report,
            "route_passed": run_report["passed"],
            "review_pass": review_pass,
            "converted_review_images": converted_count,
            "focused_review_images": len(focused) if contact_sheet_error is None else 0,
            "contact_sheet": str(contact_sheet_path)
            if contact_sheet_path.is_file()
            else None,
            "contact_sheet_error": contact_sheet_error,
            "tick_trace": str(tick_trace_path) if tick_trace_path.is_file() else None,
        }
    )
    if not tick_trace_path.is_file() and contact_sheet_error is None:
        report["tick_trace_error"] = "state/tick trace was not created"
        contact_sheet_error = "state/tick trace was not created"
    if contact_sheet_error is not None and run_report["failure_classification"] is None:
        report["failure_classification"] = "artifact-integrity"
        report["recommended_investigation"] = _recommendation(
            "artifact-integrity", run_report.get("first_missing_milestone")
        )
    _finish_report(report, started_at)
    _write_json(artifacts_dir / "run_report.json", run_report)
    _write_json(report_path, report)
    if progress is not None:
        progress(f"watchable review-only playback {'passed' if review_pass else 'failed'}")
    return WatchableResult(report=report, report_path=report_path)


def _load_product_contract(
    *,
    game_path: Path,
    emulator_resolver: Callable[[str], str | None],
    requested_runs: int,
    profile: ReliabilityProfile,
) -> tuple[GoalContract, SegmentCatalog, tuple[dict[str, str], ...]]:
    if requested_runs < 1:
        raise ValueError("requested run count must be at least one")
    if not game_path.is_file():
        raise FileNotFoundError(f"Local game file not found: {game_path}")
    if emulator_resolver("fceux") is None:
        raise FileNotFoundError("fceux executable was not found on PATH")

    contract = load_goal_contract(resolve_goal_path(profile.goal_id))
    catalog = load_segment_catalog(contract.catalog_path)
    validate_goal_segments(contract, catalog)
    if contract.id != profile.goal_id:
        raise ValueError("reliability gate cannot fall back to another goal")
    if contract.goal_type != "product_goal":
        raise ValueError("active reliability gate requires a product_goal contract")
    if contract.preset != profile.preset:
        raise ValueError("reliability gate cannot use a diagnostic preset")
    if not contract.executable:
        raise ValueError("active product contract is not executable")
    if contract.bridged_segments:
        raise ValueError("active product contract declares bridged segments")
    if any(step.execution_mode != "normal_gameplay" for step in contract.route_steps):
        raise ValueError("active product contract contains a non-gameplay route step")
    if contract.allowed_tactics.get("known_transition_bridge") is not False:
        raise ValueError("active product contract does not explicitly forbid bridges")
    if contract.allowed_tactics.get("blind_state_mutation") is not False:
        raise ValueError("active product contract does not explicitly forbid mutation")
    if contract.runner.get("env"):
        raise ValueError("reliability mode does not permit route environment overrides")
    script_path = Path(contract.runner["script"])
    if not script_path.is_file():
        raise FileNotFoundError(f"Product route script not found: {script_path}")

    milestones: list[dict[str, str]] = []
    for step in contract.route_steps:
        segment = catalog.by_id[step.id]
        if segment.status != "solved":
            raise ValueError(f"product segment is not solved: {segment.id}")
        if segment.acceptance_event is None:
            raise ValueError(f"product segment lacks acceptance_event: {segment.id}")
        milestones.append(
            {"segment_id": segment.id, "event": segment.acceptance_event}
        )
    if milestones[-1]["event"] != profile.final_event:
        raise ValueError("final product segment does not own the required final event")
    return contract, catalog, tuple(milestones)


def _inspect_run(
    *,
    run_index: int,
    mode: str,
    run_dir: Path,
    contract: GoalContract,
    milestones: tuple[dict[str, str], ...],
    goal_result: GoalRunResult | None,
    run_exception: Exception | None,
    started_at: datetime,
    capture_images: bool,
    capture_ticks: bool,
    frame_sleep_seconds: float,
    required_final_event: str,
    required_image_events: tuple[str, ...],
) -> dict[str, Any]:
    log_path = run_dir / "fceux_1_1.log"
    execution_path = run_dir / "fceux_execution.json"
    execution, execution_error = _read_json(execution_path)
    log_sha256: str | None = None
    log_text: str | None = None
    log_error: str | None = None
    if not log_path.is_file():
        log_error = "structured route log is missing"
    else:
        payload = log_path.read_bytes()
        log_sha256 = hashlib.sha256(payload).hexdigest()
        if not payload:
            log_error = "structured route log is empty"
        else:
            try:
                log_text = payload.decode("utf-8", errors="strict")
            except UnicodeDecodeError as exc:
                log_error = f"structured route log is not valid UTF-8: {exc}"

    events = _events(log_text or "")
    last_good, first_missing = _milestone_progress(events, milestones)
    prohibited = _prohibited_evidence(log_text or "", events, run_dir)
    failure_event = next(
        (
            event
            for event in events
            if any(token in event for token in FAILURE_EVENT_TOKENS)
        ),
        None,
    )
    summary: BatchSummary | None = goal_result.summary if goal_result is not None else None
    if summary is None and log_text is not None:
        try:
            summary = parse_fceux_log(log_path, expected_attempts=1)
        except Exception as exc:
            log_error = log_error or f"structured route log is unparseable: {exc}"

    final_event = summary.post_probe_last_event if summary is not None else None
    metrics_passed = bool(goal_result and goal_result.metrics_passed)
    timed_out = bool(execution and execution.get("timed_out"))
    returncode = execution.get("returncode") if execution else None
    launch_error = execution.get("launch_error") if execution else None
    complete_contract = first_missing is None and len(last_good) == len(milestones)
    success_candidate = (
        complete_contract and metrics_passed and final_event == required_final_event
    )
    focused_screenshots, screenshot_evidence_error = _focused_screenshot_evidence(
        run_dir, required_image_events if success_candidate else ()
    )
    passed = (
        run_exception is None
        and execution_error is None
        and execution is not None
        and not timed_out
        and not launch_error
        and returncode == 0
        and log_error is None
        and screenshot_evidence_error is None
        and not prohibited
        and complete_contract
        and metrics_passed
        and final_event == required_final_event
    )
    classification = None if passed else _classify_failure(
        execution=execution,
        execution_error=execution_error,
        log_error=log_error or screenshot_evidence_error,
        prohibited=prohibited,
        failure_event=failure_event,
        run_exception=run_exception,
    )
    finished_at = datetime.now(timezone.utc)
    final_observable = _final_observable(log_text or "")
    artifact_files = sorted(
        str(path.relative_to(run_dir)) for path in run_dir.rglob("*") if path.is_file()
    )
    report = {
        "run_index": run_index,
        "mode": mode,
        "validation_policy": "authoritative" if mode == "reliability" else "review_only",
        "counts_toward_reliability": mode == "reliability",
        "passed": passed,
        "result": "passed" if passed else "failed",
        "goal_id": contract.id,
        "runner_preset": contract.preset,
        "single_attempt": True,
        "fresh_process": True,
        "fresh_game": True,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "elapsed_seconds": round((finished_at - started_at).total_seconds(), 6),
        "artifacts_dir": str(run_dir),
        "artifact_files": artifact_files,
        "route_log": str(log_path) if log_path.is_file() else None,
        "fceux_stdout": str(run_dir / "fceux_stdout.log"),
        "fceux_stderr": str(run_dir / "fceux_stderr.log"),
        "structured_log_sha256": log_sha256,
        "metrics_passed": metrics_passed,
        "final_event": final_event,
        "required_final_event": required_final_event,
        "contract_milestones_completed": len(last_good),
        "contract_milestones_required": len(milestones),
        "complete_ordered_contract": complete_contract,
        "last_accepted_product_event": last_good[-1]["event"] if last_good else None,
        "last_accepted_segment": last_good[-1]["segment_id"] if last_good else None,
        "first_missing_milestone": first_missing,
        "first_violated_event": prohibited[0] if prohibited else failure_event,
        "final_observable": final_observable,
        "capture_settings": {
            "capture_images": capture_images,
            "capture_ticks": capture_ticks,
            "frame_sleep_seconds": frame_sleep_seconds,
            "throttle": "unthrottled" if frame_sleep_seconds == 0 else "watchable",
        },
        "execution": execution,
        "execution_metadata_error": execution_error,
        "log_integrity_error": log_error,
        "focused_screenshots": focused_screenshots,
        "screenshot_evidence_error": screenshot_evidence_error,
        "prohibited_evidence": prohibited,
        "exception": f"{type(run_exception).__name__}: {run_exception}"
        if run_exception is not None
        else None,
        "failure_classification": classification,
        "recommended_investigation": _recommendation(classification, first_missing)
        if classification is not None
        else None,
    }
    return report


def _focused_screenshot_evidence(
    run_dir: Path, required_events: tuple[str, ...]
) -> tuple[list[str], str | None]:
    if not required_events:
        return [], None
    image_dir = run_dir / "images"
    output_dir = run_dir / "evidence" / "png"
    output_dir.mkdir(parents=True, exist_ok=True)
    screenshots: list[str] = []
    try:
        for index, event in enumerate(required_events, start=1):
            candidates = sorted(image_dir.glob(f"*_{event}.gd"))
            if not candidates:
                raise FileNotFoundError(f"missing screenshot for {event}")
            output_path = output_dir / f"{index:02d}_{event}.png"
            load_gd_screenshot(candidates[-1]).save(output_path)
            screenshots.append(str(output_path))
    except Exception as exc:
        return screenshots, f"{type(exc).__name__}: {exc}"
    return screenshots, None


def _milestone_progress(
    events: list[str], milestones: tuple[dict[str, str], ...]
) -> tuple[list[dict[str, str]], dict[str, str] | None]:
    accepted: list[dict[str, str]] = []
    cursor = 0
    for milestone in milestones:
        try:
            offset = events[cursor:].index(milestone["event"])
        except ValueError:
            return accepted, dict(milestone)
        cursor += offset + 1
        accepted.append(dict(milestone))
    return accepted, None


def _prohibited_evidence(text: str, events: list[str], run_dir: Path) -> list[str]:
    evidence: list[str] = []
    lowered = text.lower()
    for event in events:
        if "_bridge" in event or "_discovery_" in event:
            evidence.append(event)
        elif any(token in event for token in PROHIBITED_SEARCH_TOKENS):
            evidence.append(event)
    for token in ("savestate", "memory_mutation", "position_mutation", "inventory_mutation"):
        if token in lowered:
            evidence.append(f"log_token:{token}")
    for path in run_dir.rglob("*"):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix in PROHIBITED_ARTIFACT_SUFFIXES or re.fullmatch(r"\.fc\d+", suffix):
            evidence.append(f"artifact:{path.relative_to(run_dir)}")
    return list(dict.fromkeys(evidence))


def _classify_failure(
    *,
    execution: dict[str, Any] | None,
    execution_error: str | None,
    log_error: str | None,
    prohibited: list[str],
    failure_event: str | None,
    run_exception: Exception | None,
) -> str:
    if execution and execution.get("timed_out"):
        return "timeout"
    if execution and execution.get("launch_error"):
        return "emulator-launch"
    if execution and execution.get("returncode") not in (0, None):
        return "emulator-launch"
    if execution_error is not None or log_error is not None or execution is None:
        return "artifact-integrity"
    if prohibited:
        return "prohibited-tactic"
    if failure_event is not None:
        classifications = {
            "wrong_map": "wrong-map",
            "wrong_stage": "wrong-stage",
            "wrong_entry_state": "wrong-entry-state",
            "death": "death",
            "stall": "gameplay-stall",
            "timeout": "timeout",
            "false_clear": "false-clear",
            "missing_post_clear": "missing-post-clear",
            "unexpected_next_stage": "unexpected-next-stage",
            "ambiguous": "ambiguous-state",
            "unstable_post_clear": "ambiguous-state",
        }
        for token, classification in classifications.items():
            if token in failure_event:
                return classification
        return "gameplay"
    if run_exception is not None and isinstance(run_exception, OSError):
        return "emulator-launch"
    return "observer/contract"


def _recommendation(
    classification: str | None, first_missing: dict[str, str] | None
) -> str:
    missing = first_missing["segment_id"] if first_missing else "the last accepted segment"
    recommendations = {
        "preflight": "Repair the reported local prerequisite or product-contract invariant, then rerun the exact gate.",
        "emulator-launch": "Inspect FCEUX stderr and the execution record; verify the executable and Lua script before retrying one fresh run.",
        "timeout": f"Inspect the trace after {missing}; reproduce one fresh run without adding retries, savestates, or mutation.",
        "artifact-integrity": "Inspect FCEUX stdout/stderr and logger creation; do not infer gameplay success from missing or corrupt evidence.",
        "prohibited-tactic": "Remove the prohibited route flag or artifact and rerun from a clean fresh process; this evidence is non-promotable.",
        "observer/contract": f"Compare the observer predicate at {missing} with the last accepted event and make only a bounded observer correction.",
        "gameplay": f"Review the final ticks and images around {missing}, then test the smallest input-timing correction in one fresh run.",
    }
    return recommendations.get(classification, "Inspect the retained run artifacts.")


def _final_observable(text: str) -> dict[str, Any]:
    fields: dict[str, str] = {}
    for line in reversed(text.splitlines()):
        if "event=" in line:
            fields = {match.group("key"): match.group("value") for match in FIELD_RE.finditer(line)}
            break
    inventory = {
        key: _to_int(value)
        for key, value in fields.items()
        if re.fullmatch(r"item_\d+", key)
    }
    return {
        "map": _to_int(fields.get("world_number")),
        "world_number": _to_int(fields.get("world_number")),
        "mode": fields.get("mode"),
        "object_set": _to_int(fields.get("object_set")),
        "map_cursor_x": _to_int(fields.get("map_cursor_x")),
        "map_cursor_y": _to_int(fields.get("map_cursor_y")),
        "inventory": inventory,
        "lives": _to_int(
            fields.get("lives") or fields.get("life_count") or fields.get("m_count")
        ),
        "form": _to_int(fields.get("form")),
        "player_is_dying": _to_int(fields.get("player_is_dying")),
        "starting_lives": _to_int(fields.get("starting_lives")),
        "current_lives": _to_int(fields.get("current_lives")),
        "hand_trap_entered": _to_int(fields.get("hand_trap_entered")),
        "event": fields.get("event"),
        "frame": _to_int(fields.get("frame")),
    }


def _events(text: str) -> list[str]:
    return [match.group("event") for match in EVENT_RE.finditer(text)]


def _to_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _write_tick_trace(log_path: Path, trace_path: Path) -> None:
    if not log_path.is_file():
        return
    lines = [
        line
        for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        if "event=tick " in line or "event=agent_tick " in line
    ]
    if not lines:
        return
    trace_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _focused_images(
    converted: list[Path], focused_events: tuple[str, ...]
) -> list[Path]:
    if not focused_events:
        return converted
    focused = [
        path for event in focused_events for path in converted if event in path.name
    ]
    missing = [
        event for event in focused_events if not any(event in path.name for path in converted)
    ]
    if missing:
        raise ValueError(
            "missing focused review image(s): " + ", ".join(missing)
        )
    return focused


def _reliability_profile(goal_id: str) -> ReliabilityProfile:
    try:
        return RELIABILITY_PROFILES[goal_id]
    except KeyError as exc:
        raise ValueError(f"unsupported reliability goal: {goal_id}") from exc


def _base_report(
    *,
    mode: str,
    validation_policy: str,
    artifacts_dir: Path,
    started_at: datetime,
    goal_id: str,
) -> dict[str, Any]:
    commit, dirty = _source_state()
    return {
        "schema_version": 1,
        "mode": mode,
        "validation_policy": validation_policy,
        "goal_id": goal_id,
        "source_commit": commit,
        "source_dirty": dirty,
        "started_at": started_at.isoformat(),
        "artifacts_dir": str(artifacts_dir),
    }


def _contract_identity(
    contract: GoalContract,
    catalog: SegmentCatalog,
    profile: ReliabilityProfile,
) -> dict[str, Any]:
    return {
        "goal_id": contract.id,
        "goal_type": contract.goal_type,
        "runner_preset": contract.preset,
        "goal_contract": str(contract.path),
        "goal_contract_sha256": _sha256_file(contract.path),
        "route_catalog_id": catalog.catalog_id,
        "route_catalog": str(catalog.path),
        "route_catalog_sha256": _sha256_file(catalog.path),
        "route_segment_count": len(contract.segments),
        "bridged_segment_count": len(contract.bridged_segments),
        "accepted_boundary": profile.accepted_boundary,
        "required_final_event": profile.final_event,
    }


def _invocation_record(
    *,
    run_index: int,
    mode: str,
    run_dir: Path,
    timeout_seconds: int,
    capture_images: bool,
    capture_ticks: bool,
    frame_sleep_seconds: float,
    contract: GoalContract,
) -> dict[str, Any]:
    return {
        "run_index": run_index,
        "mode": mode,
        "goal_id": contract.id,
        "runner_preset": contract.preset,
        "artifacts_dir": str(run_dir),
        "attempts": 1,
        "new_fceux_process": True,
        "start_boundary": "power_on_fresh_game",
        "reuse_previous_process": False,
        "reuse_savestate": False,
        "reuse_retry_checkpoint": False,
        "allow_bridges": False,
        "allow_mutation": False,
        "allow_discovery_search": False,
        "allow_diagnostic_fallback": False,
        "clean_product_env": True,
        "capture_images": capture_images,
        "capture_ticks": capture_ticks,
        "frame_sleep_seconds": frame_sleep_seconds,
        "timeout_seconds": timeout_seconds,
    }


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.is_file():
        return None, f"execution metadata is missing: {path}"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, f"execution metadata is corrupt: {exc}"
    if not isinstance(raw, dict):
        return None, "execution metadata must be a JSON object"
    return raw, None


def _finish_report(report: dict[str, Any], started_at: datetime) -> None:
    finished_at = datetime.now(timezone.utc)
    report["finished_at"] = finished_at.isoformat()
    report["elapsed_seconds"] = round(
        (finished_at - started_at).total_seconds(), 6
    )


def _new_artifacts_dir(root: Path, label: str) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    return root / f"{timestamp}_{label}"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_state() -> tuple[str | None, bool | None]:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        check=False,
        capture_output=True,
        text=True,
    )
    resolved_commit = commit.stdout.strip() if commit.returncode == 0 else None
    dirty = bool(status.stdout.strip()) if status.returncode == 0 else None
    return resolved_commit, dirty
