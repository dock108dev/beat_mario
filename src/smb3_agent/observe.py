from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from smb3_agent.fceux_harness import BatchSummary, run_fceux_1_1
from smb3_agent.review import LogEvent, parse_log_events


SUPPORTED_SEGMENT_ALIASES = {
    "world_1_1": "world_1_1_clear",
    "world_1_1_clear": "world_1_1_clear",
}


class ObserveError(ValueError):
    pass


@dataclass(frozen=True)
class StateSnapshot:
    frame: int | None
    event: str
    mode: str
    segment: str
    progress: str
    x: int | None
    y: int | None
    form: int | None
    lives: int | None
    map_cursor_x: int | None
    map_cursor_y: int | None
    final: bool = False


@dataclass(frozen=True)
class ObserveResult:
    segment: str
    artifacts_dir: Path
    trace_path: Path
    snapshots: tuple[StateSnapshot, ...]
    summary: BatchSummary

    def to_text(self) -> str:
        final_state = self.snapshots[-1] if self.snapshots else None
        lines = [
            f"segment={self.segment}",
            f"artifacts_dir={self.artifacts_dir}",
            f"trace_path={self.trace_path}",
            f"snapshots={len(self.snapshots)}",
            f"progress_markers={','.join(_unique_progress(self.snapshots))}",
            f"successes={self.summary.success_count}/{self.summary.total}",
            f"bad_states={self.summary.bad_state_count}/{self.summary.total}",
        ]
        if final_state is not None:
            lines.extend(
                [
                    f"final_event={final_state.event}",
                    f"final_progress={final_state.progress}",
                    f"final_success={str(final_state.progress == 'success').lower()}",
                ]
            )
        return "\n".join(lines)


def run_observed_segment(
    segment: str,
    *,
    game_path: Path,
    sample_frames: int,
    artifacts_dir: Path | None = None,
) -> ObserveResult:
    segment_id = resolve_segment_alias(segment)
    if segment_id != "world_1_1_clear":
        raise ObserveError(f"Unsupported observed segment: {segment}")
    if sample_frames <= 0:
        raise ObserveError("sample_frames must be positive")

    run_dir = artifacts_dir or _default_observe_dir(segment_id)
    summary = run_fceux_1_1(
        game_path=game_path,
        script_path=Path("scripts/fceux_1_1_agent.lua"),
        artifacts_dir=run_dir,
        attempts=1,
        capture_ticks=True,
    )
    events = parse_log_events(run_dir / "fceux_1_1.log")
    snapshots = build_state_trace(events, segment=segment_id, sample_frames=sample_frames)
    trace_path = run_dir / "state_trace.jsonl"
    write_state_trace(trace_path, snapshots)
    return ObserveResult(
        segment=segment_id,
        artifacts_dir=run_dir,
        trace_path=trace_path,
        snapshots=snapshots,
        summary=summary,
    )


def build_state_trace(
    events: tuple[LogEvent, ...],
    *,
    segment: str,
    sample_frames: int,
) -> tuple[StateSnapshot, ...]:
    snapshots: list[StateSnapshot] = []
    last_sampled_frame: int | None = None
    for event in events:
        include = False
        if event.event != "tick":
            include = True
        elif event.frame is not None and (
            last_sampled_frame is None or event.frame - last_sampled_frame >= sample_frames
        ):
            include = True
            last_sampled_frame = event.frame
        if include:
            snapshots.append(_snapshot_from_event(event, segment=segment, final=False))

    if snapshots:
        last = snapshots[-1]
        snapshots[-1] = StateSnapshot(
            **{
                **asdict(last),
                "progress": _terminal_progress(snapshots) or last.progress,
                "final": True,
            }
        )
    return tuple(snapshots)


def write_state_trace(trace_path: Path, snapshots: tuple[StateSnapshot, ...]) -> None:
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    with trace_path.open("w") as trace_file:
        for snapshot in snapshots:
            trace_file.write(json.dumps(asdict(snapshot), sort_keys=True) + "\n")


def resolve_segment_alias(segment: str) -> str:
    try:
        return SUPPORTED_SEGMENT_ALIASES[segment]
    except KeyError as exc:
        raise ObserveError(f"Unsupported observed segment: {segment}") from exc


def _snapshot_from_event(event: LogEvent, *, segment: str, final: bool) -> StateSnapshot:
    return StateSnapshot(
        frame=event.frame,
        event=event.event,
        mode=_infer_mode(event),
        segment=segment,
        progress=_infer_progress(event),
        x=_optional_int(event.fields.get("x")),
        y=_optional_int(event.fields.get("y")),
        form=_optional_int(event.fields.get("form")),
        lives=_optional_int(event.fields.get("lives") or event.fields.get("life_count") or event.fields.get("m_count")),
        map_cursor_x=_optional_int(event.fields.get("map_cursor_x")),
        map_cursor_y=_optional_int(event.fields.get("map_cursor_y")),
        final=final,
    )


def _infer_mode(event: LogEvent) -> str:
    if event.event.startswith("post_probe_") or "map_cursor_x" in event.fields:
        return "map_or_transition"
    if event.event.startswith("attempt_") or event.event == "tick":
        return "level"
    return "unknown"


def _infer_progress(event: LogEvent) -> str:
    if "success" in event.event:
        return "success"
    if "bad_state" in event.event:
        return "failure"
    if "reached_end" in event.event or "goal_area" in event.event:
        return "progress"
    if event.event.endswith("_start"):
        return "start"
    return "running"


def _optional_int(value: str | None) -> int | None:
    if value is None or not value.removeprefix("-").isdigit():
        return None
    return int(value)


def _default_observe_dir(segment: str) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path("artifacts/observe") / segment / timestamp


def _unique_progress(snapshots: tuple[StateSnapshot, ...]) -> tuple[str, ...]:
    seen: list[str] = []
    for snapshot in snapshots:
        if snapshot.progress not in seen:
            seen.append(snapshot.progress)
    return tuple(seen)


def _terminal_progress(snapshots: list[StateSnapshot]) -> str | None:
    if any(snapshot.progress == "success" for snapshot in snapshots):
        return "success"
    if any(snapshot.progress == "failure" for snapshot in snapshots):
        return "failure"
    return None
