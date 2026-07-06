from __future__ import annotations

import json
import re
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from smb3_agent.commands import AgentCommand, CommandParseError, parse_command
from smb3_agent.fceux_harness import BatchSummary
from smb3_agent.goals import GoalRunResult, load_goal_contract, resolve_goal_path, run_goal_contract
from smb3_agent.review import LogEvent, parse_log_events, review_log


LATEST_SESSION_PATH = Path("artifacts/sessions/latest.txt")
BASELINE_VARIANT_PATH = Path("data/variants/world_1_baseline.yaml")
SUPPORTED_VARIANT_STATUSES = {"proposed", "validated", "promoted", "archived"}


class LabError(ValueError):
    pass


@dataclass(frozen=True)
class LabSessionResult:
    session_id: str
    session_dir: Path
    manifest_path: Path
    command: AgentCommand
    goal_result: GoalRunResult
    route_variant: str
    requested_speed: float
    attempts_requested: int
    run_settings: dict[str, Any]

    def to_text(self) -> str:
        lines = [
            f"session_id={self.session_id}",
            f"session_dir={self.session_dir}",
            f"manifest={self.manifest_path}",
            self.command.to_text(),
            f"route_variant={self.route_variant}",
            f"requested_speed={self.requested_speed:g}",
            f"attempts_requested={self.attempts_requested}",
            f"speed_mode={self.run_settings['speed_mode']}",
            f"frame_sleep_seconds={self.run_settings['frame_sleep_seconds']}",
            f"capture_images={str(self.run_settings['capture_images']).lower()}",
            f"capture_ticks={str(self.run_settings['capture_ticks']).lower()}",
            self.goal_result.summary.to_text(),
            f"metrics_passed={str(self.goal_result.metrics_passed).lower()}",
            f"notes_file={self.session_dir / 'notes.yaml'}",
            f"review_file={self.session_dir / 'review.md'}",
        ]
        return "\n".join(lines)


@dataclass(frozen=True)
class LabNoteResult:
    session_id: str
    notes_path: Path
    note: dict[str, Any]

    def to_text(self) -> str:
        anchor = self.note.get("anchor", {})
        lines = [
            f"session_id={self.session_id}",
            f"notes_file={self.notes_path}",
            f"note_id={self.note['id']}",
            f"segment_id={self.note['segment_id']}",
            f"anchor_type={anchor.get('type')}",
            f"anchor_value={anchor.get('value')}",
            f"severity={self.note['severity']}",
            f"text={self.note['text']}",
        ]
        return "\n".join(lines)


@dataclass(frozen=True)
class LabReviewResult:
    session_id: str
    review_path: Path
    review_yaml_path: Path
    review: dict[str, Any]

    def to_text(self) -> str:
        lines = [
            f"session_id={self.session_id}",
            f"review_file={self.review_path}",
            f"review_yaml={self.review_yaml_path}",
            f"result={self.review['result']}",
            f"primary_segment={self.review['primary_segment']}",
            f"classification={self.review['classification']}",
            f"hypothesis={self.review['hypothesis']}",
            f"recommended_experiment={self.review['recommended_experiment']}",
            f"confidence={self.review['confidence']}",
            f"notes={len(self.review['linked_notes'])}",
        ]
        return "\n".join(lines)


@dataclass(frozen=True)
class VariantProposalResult:
    variant_id: str
    proposal_path: Path
    session_proposal_path: Path
    proposal: dict[str, Any]

    def to_text(self) -> str:
        return "\n".join(
            [
                f"variant_id={self.variant_id}",
                f"proposal={self.proposal_path}",
                f"session_proposal={self.session_proposal_path}",
                f"parent_variant={self.proposal['parent_variant']}",
                f"status={self.proposal['status']}",
                f"source_session={self.proposal['source_session']}",
                f"source_notes={','.join(self.proposal['source_notes'])}",
                f"validation_command={self.proposal['validation']['command']}",
            ]
        )


@dataclass(frozen=True)
class VariantCompareResult:
    variant_id: str
    report_path: Path
    report: dict[str, Any]

    def to_text(self) -> str:
        outcome = self.report["variant_outcome"]
        return "\n".join(
            [
                f"variant_id={self.variant_id}",
                f"report={self.report_path}",
                f"parent_variant={self.report['parent_variant']}",
                f"status={self.report['status']}",
                f"successes={outcome.get('successes', 'unknown')}",
                f"failure_class={outcome.get('failure_class', 'unknown')}",
                f"metrics_passed={str(outcome.get('metrics_passed', False)).lower()}",
                f"recommendation={self.report['recommendation']}",
            ]
        )


@dataclass(frozen=True)
class VariantPromotionResult:
    variant_id: str
    baseline_path: Path
    backup_path: Path
    promotion_path: Path

    def to_text(self) -> str:
        return "\n".join(
            [
                f"variant_id={self.variant_id}",
                f"baseline={self.baseline_path}",
                f"backup={self.backup_path}",
                f"promotion={self.promotion_path}",
                "promoted=true",
            ]
        )


def start_session(
    raw_command: str,
    *,
    game_path: Path,
    attempts: int,
    artifacts_root: Path = Path("artifacts/sessions"),
    route_variant: str = "world_1_baseline",
    capture_images: bool = False,
    capture_ticks: bool = True,
) -> LabSessionResult:
    command = parse_command(raw_command)
    if command.action not in {"run_goal", "show_route"}:
        raise LabError(f"Lab cannot start command action yet: {command.action}")
    if command.goal is None:
        raise LabError("Lab command did not resolve to a goal")

    requested_speed = _requested_speed(command)
    run_mode = command.run_mode or "gate"
    session_id = _new_session_id(command.goal)
    session_dir = artifacts_root / session_id
    goal_dir = session_dir / "goal"
    started_at = _now()
    run_settings = _run_settings_for_speed(requested_speed, run_mode, capture_images, capture_ticks)

    contract = load_goal_contract(resolve_goal_path(command.goal))
    attempts_requested = attempts if attempts > 0 else command.attempts or 1
    goal_result = run_goal_contract(
        contract,
        game_path=game_path,
        attempts=attempts_requested,
        artifacts_dir=goal_dir,
        capture_images=run_settings["capture_images"],
        capture_ticks=run_settings["capture_ticks"],
        env_overrides=tuple(run_settings["env_overrides"]),
    )
    ended_at = _now()

    manifest = _session_manifest(
        session_id=session_id,
        command=command,
        route_variant=route_variant,
        requested_speed=requested_speed,
        attempts=attempts_requested,
        session_dir=session_dir,
        goal_result=goal_result,
        run_settings=run_settings,
        started_at=started_at,
        ended_at=ended_at,
    )
    manifest_path = session_dir / "session.yaml"
    _write_yaml(manifest_path, manifest)
    _write_yaml(session_dir / "notes.yaml", {"notes": []})
    _write_latest_session(session_dir)

    return LabSessionResult(
        session_id=session_id,
        session_dir=session_dir,
        manifest_path=manifest_path,
        command=command,
        goal_result=goal_result,
        route_variant=route_variant,
        requested_speed=requested_speed,
        attempts_requested=attempts_requested,
        run_settings=run_settings,
    )


def add_note_to_latest(
    text: str,
    *,
    segment_id: str | None = None,
    attempt_number: int | None = None,
    anchor_type: str | None = None,
    anchor_value: str | int | float | None = None,
    severity: str = "note",
) -> LabNoteResult:
    return add_note(
        _latest_session_dir(),
        text,
        segment_id=segment_id,
        attempt_number=attempt_number,
        anchor_type=anchor_type,
        anchor_value=anchor_value,
        severity=severity,
    )


def add_note(
    session_dir: Path,
    text: str,
    *,
    segment_id: str | None = None,
    attempt_number: int | None = None,
    anchor_type: str | None = None,
    anchor_value: str | int | float | None = None,
    severity: str = "note",
) -> LabNoteResult:
    if not text:
        raise LabError("Note text is required")
    manifest = _load_session_manifest(session_dir)
    notes_path = session_dir / "notes.yaml"
    notes_doc = _load_yaml(notes_path, default={"notes": []})
    notes = notes_doc.setdefault("notes", [])
    if not isinstance(notes, list):
        raise LabError(f"Invalid notes file: {notes_path}")

    note = {
        "id": _next_note_id(notes),
        "created_at": _now(),
        "author": "user",
        "segment_id": segment_id or _infer_segment_id(text),
        "attempt_number": attempt_number,
        "anchor": _note_anchor(text, anchor_type, anchor_value),
        "severity": severity,
        "text": text,
        "expected_change": _expected_change(text),
        "interpretation": {
            "status": "pending_review",
            "classification": None,
            "linked_events": [],
        },
    }
    notes.append(note)
    _write_yaml(notes_path, notes_doc)
    return LabNoteResult(session_id=str(manifest["session_id"]), notes_path=notes_path, note=note)


def review_latest_session() -> LabReviewResult:
    return review_session(_latest_session_dir())


def review_session(session_dir: Path) -> LabReviewResult:
    manifest = _load_session_manifest(session_dir)
    notes = _load_notes(session_dir)
    route_log = _route_log_path(session_dir, manifest)
    report = review_log(route_log, expected_attempts=int(manifest["attempts_requested"]))
    events = parse_log_events(route_log)
    linked_notes = [_interpret_note(note, events) for note in notes]
    primary_segment = _primary_segment(report.failed_segment, linked_notes)
    classification = _classification(report.failure_class, linked_notes)
    recommended = _recommendation(report.next_experiment, linked_notes)
    result = "passing_evidence" if classification == "none" else "needs_route_hardening"
    review = {
        "review_id": "review_001",
        "session_id": manifest["session_id"],
        "result": result,
        "primary_segment": primary_segment,
        "linked_notes": linked_notes,
        "evidence": _review_evidence(report, linked_notes),
        "classification": classification,
        "hypothesis": _hypothesis(classification, primary_segment, linked_notes),
        "recommended_experiment": recommended,
        "confidence": _confidence(classification, linked_notes),
        "route_review": {
            "failure_class": report.failure_class,
            "failed_segment": report.failed_segment,
            "last_event": report.last_event,
            "max_x": report.max_x,
            "post_probe_clear": report.summary.post_probe_clear,
            "successes": f"{report.summary.success_count}/{report.summary.total}",
        },
    }
    review_yaml_path = session_dir / "review.yaml"
    review_path = session_dir / "review.md"
    _write_yaml(review_yaml_path, review)
    review_path.write_text(_review_markdown(review), encoding="utf-8")
    return LabReviewResult(
        session_id=str(manifest["session_id"]),
        review_path=review_path,
        review_yaml_path=review_yaml_path,
        review=review,
    )


def propose_variant_from_latest() -> VariantProposalResult:
    return propose_variant(_latest_session_dir())


def propose_variant(session_dir: Path) -> VariantProposalResult:
    manifest = _load_session_manifest(session_dir)
    review_path = session_dir / "review.yaml"
    if not review_path.is_file():
        review_session(session_dir)
    review = _load_yaml(review_path)
    source_notes = [note["id"] for note in review.get("linked_notes", [])]
    variant_id = _variant_id(review)
    proposal = {
        "variant_id": variant_id,
        "parent_variant": manifest.get("route_variant", "world_1_baseline"),
        "status": "proposed",
        "created_at": _now(),
        "reason": review["recommended_experiment"],
        "source_session": manifest["session_id"],
        "source_notes": source_notes,
        "changes": [
            {
                "file": _suggested_change_file(review["primary_segment"]),
                "summary": review["recommended_experiment"],
            }
        ],
        "validation": {
            "command": f"python -m smb3_agent lab run-variant {variant_id} --attempts 10",
            "promotion_gate": "10/10 for targeted segment or configured goal gate, with no parent-route regression",
        },
        "outcome": {
            "status": "untested",
            "artifacts_dir": None,
        },
    }
    proposal_path = Path("data/variants") / f"{variant_id}.yaml"
    session_proposal_path = session_dir / "variant_proposal.yaml"
    _write_yaml(proposal_path, proposal)
    _write_yaml(session_proposal_path, proposal)
    return VariantProposalResult(
        variant_id=variant_id,
        proposal_path=proposal_path,
        session_proposal_path=session_proposal_path,
        proposal=proposal,
    )


def run_variant(
    variant_id: str,
    *,
    game_path: Path,
    attempts: int,
    artifacts_root: Path = Path("artifacts/sessions"),
) -> LabSessionResult:
    proposal_path = _variant_path(variant_id)
    proposal = _load_variant(proposal_path)
    if proposal["status"] not in {"proposed", "validated"}:
        raise LabError(f"Variant cannot be run from status: {proposal['status']}")

    result = start_session(
        f"run world 1 king gate {attempts} times",
        game_path=game_path,
        attempts=attempts,
        artifacts_root=artifacts_root,
        route_variant=variant_id,
        capture_images=False,
        capture_ticks=True,
    )
    status = "passed" if result.goal_result.metrics_passed else "failed"
    proposal["status"] = "validated"
    proposal["outcome"] = {
        "status": status,
        "artifacts_dir": str(result.session_dir),
        "session_id": result.session_id,
        "metrics_passed": result.goal_result.metrics_passed,
        "successes": f"{result.goal_result.summary.success_count}/{result.goal_result.summary.total}",
        "post_probe_clear": result.goal_result.summary.post_probe_clear,
    }
    _write_yaml(proposal_path, proposal)
    return result


def compare_variant(variant_id: str) -> VariantCompareResult:
    proposal_path = _variant_path(variant_id)
    proposal = _load_variant(proposal_path)
    outcome = proposal.get("outcome", {})
    report = {
        "variant_id": variant_id,
        "parent_variant": proposal["parent_variant"],
        "status": proposal["status"],
        "source_session": proposal["source_session"],
        "changed_files": [change["file"] for change in proposal.get("changes", [])],
        "variant_outcome": outcome,
        "recommendation": _variant_recommendation(outcome),
    }
    report_path = Path("data/variants") / f"{variant_id}.compare.yaml"
    _write_yaml(report_path, report)
    return VariantCompareResult(variant_id=variant_id, report_path=report_path, report=report)


def promote_variant(variant_id: str) -> VariantPromotionResult:
    proposal_path = _variant_path(variant_id)
    proposal = _load_variant(proposal_path)
    outcome = proposal.get("outcome", {})
    if proposal["status"] != "validated" or not outcome.get("metrics_passed"):
        raise LabError("Promotion refused: variant has no passing validation artifact")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = Path("data/variants/backups")
    promotion_dir = Path("data/variants/promotions")
    backup_path = backup_dir / f"world_1_baseline_{timestamp}.yaml"
    promotion_path = promotion_dir / f"{variant_id}_{timestamp}.yaml"
    backup_dir.mkdir(parents=True, exist_ok=True)
    promotion_dir.mkdir(parents=True, exist_ok=True)

    if BASELINE_VARIANT_PATH.exists():
        shutil.copyfile(BASELINE_VARIANT_PATH, backup_path)
    else:
        _write_yaml(backup_path, _default_baseline())

    baseline = {
        "variant_id": "world_1_baseline",
        "active_variant": variant_id,
        "promoted_at": _now(),
        "source_variant": str(proposal_path),
        "validation_session": outcome.get("session_id"),
        "validation_artifacts_dir": outcome.get("artifacts_dir"),
        "reason": proposal["reason"],
    }
    _write_yaml(BASELINE_VARIANT_PATH, baseline)
    proposal["status"] = "promoted"
    _write_yaml(proposal_path, proposal)
    promotion = {
        "variant_id": variant_id,
        "promoted_at": baseline["promoted_at"],
        "baseline": str(BASELINE_VARIANT_PATH),
        "backup": str(backup_path),
        "validation_artifacts_dir": outcome.get("artifacts_dir"),
    }
    _write_yaml(promotion_path, promotion)
    return VariantPromotionResult(
        variant_id=variant_id,
        baseline_path=BASELINE_VARIANT_PATH,
        backup_path=backup_path,
        promotion_path=promotion_path,
    )


def _session_manifest(
    *,
    session_id: str,
    command: AgentCommand,
    route_variant: str,
    requested_speed: float,
    attempts: int,
    session_dir: Path,
    goal_result: GoalRunResult,
    run_settings: dict[str, Any],
    started_at: str,
    ended_at: str,
) -> dict[str, Any]:
    return {
        "session_id": session_id,
        "goal_id": command.goal,
        "route_variant": route_variant,
        "run_mode": command.run_mode,
        "requested_speed": requested_speed,
        "attempts_requested": attempts,
        "started_at": started_at,
        "ended_at": ended_at,
        "artifacts_dir": str(session_dir),
        "inputs": {
            "command": command.raw,
            "game_file_env": "SMB3_GAME_FILE",
        },
        "run_settings": {
            key: value for key, value in run_settings.items() if key != "env_overrides"
        },
        "outputs": {
            "route_log": "goal/fceux_1_1.log",
            "state_trace": "state_trace.jsonl",
            "screenshots_dir": "goal/images",
            "notes_file": "notes.yaml",
            "review_file": "review.md",
            "variant_proposal": "variant_proposal.yaml",
        },
        "result": {
            "status": "passed" if goal_result.metrics_passed else "failed",
            "metrics_passed": goal_result.metrics_passed,
            "successes": f"{goal_result.summary.success_count}/{goal_result.summary.total}",
            "bad_states": f"{goal_result.summary.bad_state_count}/{goal_result.summary.total}",
            "post_probe_last_event": goal_result.summary.post_probe_last_event,
            "post_probe_clear": goal_result.summary.post_probe_clear,
        },
    }


def _run_settings_for_speed(
    speed: float,
    run_mode: str,
    capture_images: bool,
    capture_ticks: bool,
) -> dict[str, Any]:
    if speed < 1 or speed > 100:
        raise LabError("Speed must be between 1 and 100")
    if speed >= 100:
        frame_sleep = 0
        speed_mode = "maximum"
    elif run_mode == "watch" or speed < 100:
        frame_sleep = round(1 / (60 * speed), 6)
        speed_mode = "normal"
    else:
        frame_sleep = 0
        speed_mode = "maximum"
    env_overrides = [
        f"SMB3_AGENT_SPEED_MODE={speed_mode}",
        f"SMB3_AGENT_FRAME_SLEEP_SECONDS={frame_sleep}",
    ]
    return {
        "emulator": "fceux",
        "speed_mode": speed_mode,
        "frame_sleep_seconds": frame_sleep,
        "capture_images": capture_images,
        "capture_ticks": capture_ticks,
        "env_overrides": env_overrides,
    }


def _requested_speed(command: AgentCommand) -> float:
    if command.speed is not None:
        return float(command.speed or 1)
    return 100


def _new_session_id(goal_id: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{timestamp}_{goal_id}"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _load_yaml(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.is_file():
        if default is not None:
            return default
        raise LabError(f"File not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise LabError(f"Expected YAML mapping: {path}")
    return data


def _write_latest_session(session_dir: Path) -> None:
    LATEST_SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    LATEST_SESSION_PATH.write_text(str(session_dir) + "\n", encoding="utf-8")


def _latest_session_dir() -> Path:
    if not LATEST_SESSION_PATH.is_file():
        raise LabError("No latest lab session exists")
    session_dir = Path(LATEST_SESSION_PATH.read_text(encoding="utf-8").strip())
    if not session_dir.is_dir():
        raise LabError(f"Latest session directory does not exist: {session_dir}")
    return session_dir


def _load_session_manifest(session_dir: Path) -> dict[str, Any]:
    return _load_yaml(session_dir / "session.yaml")


def _load_notes(session_dir: Path) -> list[dict[str, Any]]:
    notes_doc = _load_yaml(session_dir / "notes.yaml", default={"notes": []})
    notes = notes_doc.get("notes", [])
    if not isinstance(notes, list):
        raise LabError("notes.yaml must contain a notes list")
    return [note for note in notes if isinstance(note, dict)]


def _route_log_path(session_dir: Path, manifest: dict[str, Any]) -> Path:
    route_log = manifest.get("outputs", {}).get("route_log", "goal/fceux_1_1.log")
    return session_dir / str(route_log)


def _next_note_id(notes: list[Any]) -> str:
    return f"note_{len(notes) + 1:03d}"


def _infer_segment_id(text: str) -> str:
    lowered = text.lower()
    if "1-1" in lowered or "1 1" in lowered:
        return "world_1_1"
    if "1-2" in lowered or "1 2" in lowered:
        return "world_1_2"
    if "1-3" in lowered or "1 3" in lowered:
        return "world_1_3_whistle"
    if "fortress" in lowered or "castle" in lowered:
        return "world_1_fortress_whistle"
    return "unknown"


def _note_anchor(text: str, anchor_type: str | None, anchor_value: str | int | float | None) -> dict[str, Any]:
    if anchor_type is not None:
        return {"type": anchor_type, "value": _coerce_anchor_value(anchor_value)}
    timer_match = re.search(r"\b(?P<timer>\d{2,3})\s*(?:timer|seconds?\s+remaining|remaining)\b", text, re.I)
    if timer_match is None:
        timer_match = re.search(r"\baround\s+(?P<timer>\d{2,3})\b", text, re.I)
    if timer_match is not None:
        return {"type": "in_game_timer", "value": int(timer_match.group("timer"))}
    return {"type": "free_text", "value": None}


def _coerce_anchor_value(value: str | int | float | None) -> str | int | float | None:
    if isinstance(value, str) and value.removeprefix("-").isdigit():
        return int(value)
    return value


def _expected_change(text: str) -> str:
    lowered = text.lower()
    if "fall" in lowered or "hole" in lowered:
        return "Add a safer jump, slowdown, or verification marker around the noted hazard."
    if "too slow" in lowered:
        return "Adjust playback or input timing earlier while preserving the parent route gate."
    if "too fast" in lowered:
        return "Add a delay or guard before the noted action."
    return "Review trace evidence and propose one controlled route experiment."


def _interpret_note(note: dict[str, Any], events: tuple[LogEvent, ...]) -> dict[str, Any]:
    linked = _nearest_events(note, events)
    classification = _note_classification(note)
    interpreted = dict(note)
    interpreted["interpretation"] = {
        "status": "reviewed",
        "classification": classification,
        "linked_events": linked,
    }
    return interpreted


def _nearest_events(note: dict[str, Any], events: tuple[LogEvent, ...]) -> list[dict[str, Any]]:
    anchor = note.get("anchor", {})
    if anchor.get("type") == "frame" and isinstance(anchor.get("value"), int):
        target = int(anchor["value"])
        ordered = sorted(
            (event for event in events if event.frame is not None),
            key=lambda event: abs(int(event.frame or 0) - target),
        )
        return [_event_ref(event) for event in ordered[:3]]
    segment = note.get("segment_id")
    if segment == "world_1_1":
        segment_events = [event for event in events if event.event.startswith("attempt_")]
        return [_event_ref(event) for event in segment_events[-3:]]
    if events:
        return [_event_ref(events[-1])]
    return []


def _event_ref(event: LogEvent) -> dict[str, Any]:
    return {
        "frame": event.frame,
        "event": event.event,
        "x": event.fields.get("x"),
        "y": event.fields.get("y"),
    }


def _note_classification(note: dict[str, Any]) -> str:
    text = str(note.get("text", "")).lower()
    if "fall" in text or "hole" in text or "jump" in text:
        return "input_timing"
    if "wrong" in text or "map" in text:
        return "wrong_route_state"
    if "died" in text or "life" in text:
        return "life_lost"
    return "needs_review"


def _primary_segment(failed_segment: str, linked_notes: list[dict[str, Any]]) -> str:
    for note in linked_notes:
        segment = note.get("segment_id")
        if segment and segment != "unknown":
            return str(segment)
    return failed_segment


def _classification(failure_class: str, linked_notes: list[dict[str, Any]]) -> str:
    if linked_notes:
        note_class = linked_notes[0].get("interpretation", {}).get("classification")
        if note_class and note_class != "needs_review":
            return str(note_class)
    return failure_class


def _recommendation(route_experiment: str, linked_notes: list[dict[str, Any]]) -> str:
    for note in linked_notes:
        expected = note.get("expected_change")
        if expected:
            return str(expected)
    return route_experiment


def _review_evidence(report: Any, linked_notes: list[dict[str, Any]]) -> list[Any]:
    evidence: list[Any] = [note["id"] for note in linked_notes]
    evidence.append(
        {
            "event": report.last_event,
            "max_x": report.max_x,
            "successes": f"{report.summary.success_count}/{report.summary.total}",
        }
    )
    return evidence


def _hypothesis(classification: str, primary_segment: str, linked_notes: list[dict[str, Any]]) -> str:
    if linked_notes:
        return f"{primary_segment} needs a controlled route variant for the user-noted {classification} risk."
    if classification == "none":
        return "No route issue found in this session."
    return f"{primary_segment} needs review for {classification}."


def _confidence(classification: str, linked_notes: list[dict[str, Any]]) -> str:
    if classification == "none":
        return "high"
    if linked_notes:
        return "medium"
    return "low"


def _review_markdown(review: dict[str, Any]) -> str:
    lines = [
        "# Lab Review",
        "",
        f"- session: {review['session_id']}",
        f"- result: {review['result']}",
        f"- primary_segment: {review['primary_segment']}",
        f"- classification: {review['classification']}",
        f"- confidence: {review['confidence']}",
        "",
        "## Hypothesis",
        "",
        review["hypothesis"],
        "",
        "## Recommended Experiment",
        "",
        review["recommended_experiment"],
        "",
        "## Linked Notes",
        "",
    ]
    if review["linked_notes"]:
        for note in review["linked_notes"]:
            lines.append(f"- {note['id']}: {note['text']}")
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def _variant_id(review: dict[str, Any]) -> str:
    segment = re.sub(r"[^a-z0-9_]+", "_", str(review["primary_segment"]).lower()).strip("_") or "route"
    anchor = ""
    for note in review.get("linked_notes", []):
        anchor_data = note.get("anchor", {})
        if anchor_data.get("value") is not None:
            anchor = f"_{anchor_data['value']}"
            break
    base = f"{segment}_harden{anchor}_a"
    candidate = base
    index = 1
    while (Path("data/variants") / f"{candidate}.yaml").exists():
        index += 1
        candidate = f"{base[:-1]}{chr(96 + min(index, 26))}"
    return candidate


def _suggested_change_file(segment: str) -> str:
    if segment == "world_1_1":
        return "data/routes/scripts/world_1_1_clear_v0.yaml"
    return "scripts/fceux_1_1_agent.lua"


def _variant_path(variant_id: str) -> Path:
    path = Path("data/variants") / f"{variant_id}.yaml"
    if not path.is_file():
        raise LabError(f"Variant not found: {variant_id}")
    return path


def _load_variant(path: Path) -> dict[str, Any]:
    variant = _load_yaml(path)
    for field in ("variant_id", "parent_variant", "status", "outcome"):
        if field not in variant:
            raise LabError(f"Variant missing required field: {field}")
    if variant["status"] not in SUPPORTED_VARIANT_STATUSES:
        raise LabError(f"Unsupported variant status: {variant['status']}")
    return variant


def _variant_recommendation(outcome: dict[str, Any]) -> str:
    if not outcome or outcome.get("status") == "untested":
        return "Run the variant before comparing or promoting it."
    if outcome.get("metrics_passed"):
        return "Variant has passing evidence and is eligible for guarded promotion."
    return "Do not promote; inspect the variant session review first."


def _default_baseline() -> dict[str, Any]:
    return {
        "variant_id": "world_1_baseline",
        "active_variant": "world_1_baseline",
        "promoted_at": None,
        "source_variant": None,
        "validation_session": None,
        "validation_artifacts_dir": None,
        "reason": "Initial baseline metadata created by promotion guard.",
    }


def batch_summary_to_json(summary: BatchSummary) -> str:
    return json.dumps(asdict(summary), sort_keys=True)
