from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from smb3_agent.fceux_harness import BatchSummary, parse_fceux_log


@dataclass(frozen=True)
class LogEvent:
    frame: int | None
    event: str
    fields: dict[str, str]
    raw: str


@dataclass(frozen=True)
class ReviewReport:
    log_path: Path
    summary: BatchSummary
    failure_class: str
    failed_segment: str
    last_event: str
    max_x: int
    final_snapshot: dict[str, str]
    next_experiment: str

    def to_text(self) -> str:
        lines = [
            f"log={self.log_path}",
            f"successes={self.summary.success_count}/{self.summary.total}",
            f"bad_states={self.summary.bad_state_count}/{self.summary.total}",
            f"failure_class={self.failure_class}",
            f"failed_segment={self.failed_segment}",
            f"last_event={self.last_event}",
            f"max_x={self.max_x}",
            f"next_experiment={self.next_experiment}",
        ]
        if self.summary.post_probe_last_event is not None:
            lines.append(f"post_probe_last_event={self.summary.post_probe_last_event}")
        lines.append(f"post_probe_clear={str(self.summary.post_probe_clear).lower()}")
        snapshot = _format_snapshot(self.final_snapshot)
        if snapshot:
            lines.append(f"final_snapshot={snapshot}")
        return "\n".join(lines)


@dataclass(frozen=True)
class CompareReport:
    left: ReviewReport
    right: ReviewReport
    explanation: str

    def to_text(self) -> str:
        return "\n".join(
            [
                f"left_log={self.left.log_path}",
                f"left_successes={self.left.summary.success_count}/{self.left.summary.total}",
                f"left_failure_class={self.left.failure_class}",
                f"left_last_event={self.left.last_event}",
                f"right_log={self.right.log_path}",
                f"right_successes={self.right.summary.success_count}/{self.right.summary.total}",
                f"right_failure_class={self.right.failure_class}",
                f"right_last_event={self.right.last_event}",
                f"explanation={self.explanation}",
            ]
        )


def review_log(log_path: Path, expected_attempts: int | None = None) -> ReviewReport:
    events = parse_log_events(log_path)
    summary = parse_fceux_log(log_path, expected_attempts=expected_attempts)
    last = events[-1] if events else LogEvent(frame=None, event="none", fields={}, raw="")
    failure_class = classify_failure(summary, events)
    failed_segment = infer_failed_segment(summary, events)
    max_x = max((_event_x(event) for event in events), default=-1)
    return ReviewReport(
        log_path=log_path,
        summary=summary,
        failure_class=failure_class,
        failed_segment=failed_segment,
        last_event=last.event,
        max_x=max_x,
        final_snapshot=last.fields,
        next_experiment=suggest_next_experiment(failure_class, failed_segment, last.event),
    )


def compare_logs(left_log: Path, right_log: Path) -> CompareReport:
    left = review_log(left_log)
    right = review_log(right_log)
    explanation = _compare_explanation(left, right)
    return CompareReport(left=left, right=right, explanation=explanation)


def parse_log_events(log_path: Path) -> tuple[LogEvent, ...]:
    events: list[LogEvent] = []
    for line in log_path.read_text(errors="replace").splitlines():
        fields = _parse_fields(line)
        event = fields.get("event")
        if not event:
            continue
        frame = int(fields["frame"]) if _is_int(fields.get("frame")) else None
        events.append(LogEvent(frame=frame, event=event, fields=fields, raw=line))
    return tuple(events)


def classify_failure(summary: BatchSummary, events: tuple[LogEvent, ...]) -> str:
    if summary.success_count == summary.total and summary.post_probe_clear:
        return "none"
    if summary.bad_state_count:
        return "state_detection"
    last_event = events[-1].event if events else ""
    event_counts = Counter(event.event for event in events)
    if "dead" in last_event or "life_lost" in last_event:
        return "life_lost"
    if "bridge" in last_event or any("bridge" in event for event in event_counts):
        return "bridge_failure"
    if last_event.startswith("post_probe_") and not summary.post_probe_clear:
        return "wrong_route_state"
    if summary.success_count < summary.total:
        return "input_timing"
    return "unknown"


def infer_failed_segment(summary: BatchSummary, events: tuple[LogEvent, ...]) -> str:
    if summary.success_count == summary.total and summary.post_probe_clear:
        return "none"

    if summary.success_count < summary.total:
        return "world_1_1_clear"

    event_names = [event.event for event in events]
    for prefix, segment in (
        ("post_probe_1_2", "world_1_2_clear"),
        ("post_probe_1_3", "world_1_3_whistle"),
        ("post_probe_1_fortress", "world_1_fortress_whistle"),
        ("post_probe_1_4", "world_1_4_clear"),
        ("post_probe_1_5_water", "world_1_5_water_path"),
        ("post_probe_1_5", "world_1_5_clear"),
        ("post_probe_1_6", "world_1_6_clear"),
        ("post_probe_1_airship", "world_1_airship_to_king"),
    ):
        if any(event.startswith(prefix) for event in event_names):
            return segment
    return "unknown"


def suggest_next_experiment(failure_class: str, failed_segment: str, last_event: str) -> str:
    if failure_class == "none":
        return "No repair needed; promote this run as passing evidence."
    if failure_class == "input_timing":
        return f"Rerun {failed_segment} with capture disabled, then tune one timing window around max progress."
    if failure_class == "state_detection":
        return f"Add a guard screenshot/log snapshot around {last_event} before changing route inputs."
    if failure_class == "wrong_route_state":
        return f"Replay from the start of {failed_segment} and add a precondition check for the expected map or stage node."
    if failure_class == "life_lost":
        return "Use the goal recovery policy to decide whether to continue from the next life or restart the goal."
    if failure_class == "bridge_failure":
        return f"Inspect bridge preconditions for {failed_segment}; verify the memory marker before applying the bridge."
    return "Capture images and tick logs for the next run, then classify the last non-tick event manually."


def _compare_explanation(left: ReviewReport, right: ReviewReport) -> str:
    if left.failure_class == "none" and right.failure_class != "none":
        return (
            "Left passed while right failed. If the right run was watchable or captured frames, "
            "treat timing/capture overhead as a suspect before changing route logic."
        )
    if left.failure_class != "none" and right.failure_class == "none":
        return (
            "Right passed while left failed. Compare environment overrides and capture settings before retuning inputs."
        )
    if left.failure_class != right.failure_class:
        return "Runs failed differently; compare last events and final snapshots before changing shared route code."
    return "Runs have matching failure classes; focus on the shared failed segment and last event."


def _parse_fields(line: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for token in line.split():
        key, separator, value = token.partition("=")
        if key and separator:
            fields[key] = value
    return fields


def _is_int(value: str | None) -> bool:
    if value is None:
        return False
    return value.removeprefix("-").isdigit()


def _event_x(event: LogEvent) -> int:
    if not _is_int(event.fields.get("x")):
        return -1
    x = int(event.fields["x"])
    return x if 0 <= x < 8192 else -1


def _format_snapshot(fields: dict[str, str]) -> str:
    keys = (
        "frame",
        "x",
        "y",
        "sx",
        "sy",
        "air",
        "form",
        "lives",
        "life_count",
        "m_count",
        "x_speed",
        "p_meter",
        "map_cursor_x",
        "map_cursor_y",
        "map_page",
        "return_map",
    )
    return ",".join(f"{key}={fields[key]}" for key in keys if key in fields)
