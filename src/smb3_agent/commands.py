from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from smb3_agent.goals import GoalRunResult, load_goal_contract, resolve_goal_path, run_goal_contract


RUN_WORLD_1_KING_RE = re.compile(
    r"^run\s+world\s+1\s+king\s+gate(?:\s+(?P<attempts>\d+)\s+times?)?$",
    re.IGNORECASE,
)
SHOW_ROUTE_RE = re.compile(r"^show\s+me\s+the\s+route(?:\s+at\s+(?P<speed>\d+(?:\.\d+)?)x)?$", re.IGNORECASE)
REVIEW_LATEST_FAILED_RE = re.compile(r"^review\s+the\s+latest\s+failed\s+run$", re.IGNORECASE)
CONTINUE_AFTER_LIFE_LOSS_RE = re.compile(
    r"^continue\s+after\s+losing\s+a\s+life\s+if\s+the\s+route\s+allows\s+it$",
    re.IGNORECASE,
)


class CommandParseError(ValueError):
    pass


@dataclass(frozen=True)
class AgentCommand:
    action: str
    raw: str
    goal: str | None = None
    attempts: int | None = None
    run_mode: str | None = None
    validation_policy: str | None = None
    speed: float | None = None
    recovery_policy: str | None = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)

    def to_text(self) -> str:
        lines = [
            f"action={self.action}",
            f"raw={self.raw}",
        ]
        if self.goal is not None:
            lines.append(f"goal={self.goal}")
        if self.attempts is not None:
            lines.append(f"attempts={self.attempts}")
        if self.run_mode is not None:
            lines.append(f"run_mode={self.run_mode}")
        if self.validation_policy is not None:
            lines.append(f"validation_policy={self.validation_policy}")
        if self.speed is not None:
            lines.append(f"speed={self.speed:g}")
        if self.recovery_policy is not None:
            lines.append(f"recovery_policy={self.recovery_policy}")
        return "\n".join(lines)


@dataclass(frozen=True)
class CommandRunResult:
    command: AgentCommand
    goal_result: GoalRunResult
    trace_path: Path
    next_action: str

    def to_text(self) -> str:
        lines = [
            self.command.to_text(),
            f"artifacts_dir={self.goal_result.artifacts_dir}",
            f"trace_path={self.trace_path}",
            self.goal_result.summary.to_text(),
            f"metrics_passed={str(self.goal_result.metrics_passed).lower()}",
            f"next_action={self.next_action}",
        ]
        return "\n".join(lines)


def parse_command(raw: str) -> AgentCommand:
    normalized = " ".join(raw.strip().split())
    if not normalized:
        raise CommandParseError("Command is empty")

    match = RUN_WORLD_1_KING_RE.match(normalized)
    if match is not None:
        attempts = int(match.group("attempts") or "1")
        return AgentCommand(
            action="run_goal",
            raw=normalized,
            goal="world_1_king",
            attempts=attempts,
            run_mode="gate",
            validation_policy="require_goal_metrics",
        )

    match = SHOW_ROUTE_RE.match(normalized)
    if match is not None:
        speed = float(match.group("speed") or "1")
        return AgentCommand(
            action="show_route",
            raw=normalized,
            goal="world_1_king",
            run_mode="watch",
            validation_policy="review_only",
            speed=speed,
        )

    if REVIEW_LATEST_FAILED_RE.match(normalized):
        return AgentCommand(
            action="review_latest_failed",
            raw=normalized,
            run_mode="review",
            validation_policy="review_only",
        )

    if CONTINUE_AFTER_LIFE_LOSS_RE.match(normalized):
        return AgentCommand(
            action="set_recovery_policy",
            raw=normalized,
            goal="world_1_king",
            run_mode="recovery",
            validation_policy="contract_allows",
            recovery_policy="continue_after_life_loss_if_allowed",
        )

    raise CommandParseError(f"Unsupported command: {raw}")


def run_command(
    raw: str,
    *,
    game_path: Path,
    artifacts_dir: Path | None = None,
) -> CommandRunResult:
    command = parse_command(raw)
    if command.action != "run_goal":
        raise CommandParseError(f"Command action is not executable yet: {command.action}")
    if command.goal is None or command.attempts is None:
        raise CommandParseError("Run command did not resolve to a goal and attempt count")

    root_dir = artifacts_dir or _default_command_dir(command)
    goal_artifacts_dir = root_dir / "goal"
    contract = load_goal_contract(resolve_goal_path(command.goal))
    goal_result = run_goal_contract(
        contract,
        game_path=game_path,
        attempts=command.attempts,
        artifacts_dir=goal_artifacts_dir,
    )
    trace_path = root_dir / "command_trace.json"
    _write_trace(trace_path, command, goal_result)
    return CommandRunResult(
        command=command,
        goal_result=goal_result,
        trace_path=trace_path,
        next_action=_next_action(goal_result.metrics_passed),
    )


def _default_command_dir(command: AgentCommand) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    goal = command.goal or "no_goal"
    return Path("artifacts/commands") / goal / timestamp


def _write_trace(trace_path: Path, command: AgentCommand, goal_result: GoalRunResult) -> None:
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    trace = {
        "command": asdict(command),
        "artifacts_dir": str(goal_result.artifacts_dir),
        "summary": {
            "success_count": goal_result.summary.success_count,
            "bad_state_count": goal_result.summary.bad_state_count,
            "total": goal_result.summary.total,
            "post_probe_last_event": goal_result.summary.post_probe_last_event,
            "post_probe_clear": goal_result.summary.post_probe_clear,
        },
        "metrics_passed": goal_result.metrics_passed,
    }
    trace_path.write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n")


def _next_action(metrics_passed: bool) -> str:
    if metrics_passed:
        return "Promote this command run as passing evidence or continue to the next implementation phase."
    return "Run review log on the command artifact log and repair the failed segment before expanding scope."

