from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from smb3_agent.fceux_harness import BatchSummary, run_fceux_1_1
from smb3_agent.presets import WORLD_1_KING_ENV


SUPPORTED_PRESETS = {"fceux_world_1_king"}
SUPPORTED_METRIC_TYPES = {"summary_field", "final_event"}
SUPPORTED_SUMMARY_FIELDS = {
    "success_count",
    "bad_state_count",
    "total",
    "post_probe_clear",
    "post_probe_last_event",
}
SUPPORTED_RECOVERY_ACTIONS = {
    "capture_artifacts_and_stop",
    "correct_known_state_or_stop",
    "reclassify_state",
    "restart_goal",
    "stop_and_review",
}


class GoalValidationError(ValueError):
    pass


@dataclass(frozen=True)
class GoalContract:
    id: str
    game: str
    user_directive: str
    objective: dict[str, Any]
    route: dict[str, Any]
    constraints: dict[str, Any]
    allowed_tactics: dict[str, Any]
    success_metrics: tuple[dict[str, Any], ...]
    recovery_policy: dict[str, Any]
    runner: dict[str, Any]
    bridged_segments: tuple[str, ...]
    path: Path

    @property
    def segments(self) -> tuple[str, ...]:
        return tuple(self.route["segments"])

    @property
    def preset(self) -> str:
        return str(self.runner["preset"])


@dataclass(frozen=True)
class GoalRunResult:
    contract: GoalContract
    summary: BatchSummary
    artifacts_dir: Path
    metrics_passed: bool


def resolve_goal_path(goal: str, goals_dir: Path = Path("data/goals")) -> Path:
    candidate = Path(goal)
    if candidate.exists():
        return candidate
    return goals_dir / f"{goal}.yaml"


def load_goal_contract(path: Path) -> GoalContract:
    if not path.is_file():
        raise GoalValidationError(f"Goal contract not found: {path}")

    raw = yaml.safe_load(path.read_text()) or {}
    if not isinstance(raw, dict):
        raise GoalValidationError("Goal contract must be a YAML mapping")

    _require_fields(
        raw,
        (
            "id",
            "game",
            "user_directive",
            "objective",
            "route",
            "constraints",
            "allowed_tactics",
            "success_metrics",
            "recovery_policy",
            "runner",
        ),
    )

    _require_type(raw, "id", str)
    _require_type(raw, "game", str)
    _require_type(raw, "user_directive", str)
    _require_type(raw, "objective", dict)
    _require_type(raw, "route", dict)
    _require_type(raw, "constraints", dict)
    _require_type(raw, "allowed_tactics", dict)
    _require_type(raw, "success_metrics", list)
    _require_type(raw, "recovery_policy", dict)
    _require_type(raw, "runner", dict)

    route = raw["route"]
    _require_fields(route, ("segments",))
    segments = route["segments"]
    if not isinstance(segments, list) or not segments or not all(isinstance(item, str) for item in segments):
        raise GoalValidationError("route.segments must be a non-empty list of strings")

    runner = raw["runner"]
    _require_fields(runner, ("backend", "preset", "script", "artifacts_root", "require_perfect"))
    if runner["preset"] not in SUPPORTED_PRESETS:
        raise GoalValidationError(f"Unsupported runner preset: {runner['preset']}")

    bridged_segments = raw.get("bridged_segments", ())
    if not isinstance(bridged_segments, list) or not all(isinstance(item, str) for item in bridged_segments):
        raise GoalValidationError("bridged_segments must be a list of strings")
    unknown_bridges = sorted(set(bridged_segments).difference(segments))
    if unknown_bridges:
        raise GoalValidationError(f"bridged_segments not present in route.segments: {', '.join(unknown_bridges)}")

    metrics = tuple(raw["success_metrics"])
    if not metrics:
        raise GoalValidationError("success_metrics must be non-empty")
    for index, metric in enumerate(metrics):
        _validate_metric(index, metric)

    for state, policy in raw["recovery_policy"].items():
        if not isinstance(policy, dict):
            raise GoalValidationError(f"recovery_policy.{state} must be a mapping")
        action = policy.get("action")
        if action not in SUPPORTED_RECOVERY_ACTIONS:
            raise GoalValidationError(f"Unsupported recovery action for {state}: {action}")

    return GoalContract(
        id=raw["id"],
        game=raw["game"],
        user_directive=raw["user_directive"],
        objective=raw["objective"],
        route=route,
        constraints=raw["constraints"],
        allowed_tactics=raw["allowed_tactics"],
        success_metrics=metrics,
        recovery_policy=raw["recovery_policy"],
        runner=runner,
        bridged_segments=tuple(bridged_segments),
        path=path,
    )


def run_goal_contract(
    contract: GoalContract,
    *,
    game_path: Path,
    attempts: int,
    artifacts_dir: Path | None = None,
    capture_images: bool = False,
    capture_ticks: bool = False,
    env_overrides: tuple[str, ...] = (),
) -> GoalRunResult:
    if contract.preset != "fceux_world_1_king":
        raise GoalValidationError(f"Unsupported runner preset: {contract.preset}")

    run_dir = artifacts_dir or _default_artifacts_dir(contract)
    summary = run_fceux_1_1(
        game_path=game_path,
        script_path=Path(contract.runner["script"]),
        artifacts_dir=run_dir,
        attempts=attempts,
        capture_images=capture_images,
        capture_ticks=capture_ticks,
        post_1_1_probe="run_1_castle_after_1_6",
        env_overrides=WORLD_1_KING_ENV + tuple(contract.runner.get("env", ())) + env_overrides,
    )
    return GoalRunResult(
        contract=contract,
        summary=summary,
        artifacts_dir=run_dir,
        metrics_passed=evaluate_success_metrics(contract, summary),
    )


def evaluate_success_metrics(contract: GoalContract, summary: BatchSummary) -> bool:
    return all(_metric_passes(metric, summary) for metric in contract.success_metrics)


def _default_artifacts_dir(contract: GoalContract) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path(contract.runner["artifacts_root"]) / timestamp


def _metric_passes(metric: dict[str, Any], summary: BatchSummary) -> bool:
    metric_type = metric["type"]
    if metric_type == "final_event":
        return summary.post_probe_last_event == metric["value"]
    if metric_type == "summary_field":
        actual = getattr(summary, metric["field"])
        expected = metric["equals"]
        if expected == "total":
            expected = summary.total
        return actual == expected
    raise GoalValidationError(f"Unsupported success metric type: {metric_type}")


def _validate_metric(index: int, metric: Any) -> None:
    if not isinstance(metric, dict):
        raise GoalValidationError(f"success_metrics[{index}] must be a mapping")
    _require_fields(metric, ("id", "type"))
    if metric["type"] not in SUPPORTED_METRIC_TYPES:
        raise GoalValidationError(f"Unsupported success metric type: {metric['type']}")
    if metric["type"] == "summary_field":
        _require_fields(metric, ("field", "equals"))
        if metric["field"] not in SUPPORTED_SUMMARY_FIELDS:
            raise GoalValidationError(f"Unsupported summary field: {metric['field']}")
    if metric["type"] == "final_event":
        _require_fields(metric, ("value",))


def _require_fields(data: dict[str, Any], fields: tuple[str, ...]) -> None:
    missing = [field for field in fields if field not in data]
    if missing:
        raise GoalValidationError(f"Missing required field(s): {', '.join(missing)}")


def _require_type(data: dict[str, Any], field: str, expected_type: type) -> None:
    if not isinstance(data[field], expected_type):
        raise GoalValidationError(f"{field} must be {expected_type.__name__}")
