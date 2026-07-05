from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


STATE_RE = re.compile(r"\battempt_(?P<attempt>\d+)_(?P<event>[A-Za-z0-9_]+)\b")
X_RE = re.compile(r"\bx=(?P<x>-?\d+)\b")


@dataclass(frozen=True)
class AttemptSummary:
    attempt: int
    success: bool
    bad_state: bool
    reached_end: bool
    goal_area: bool
    max_x: int


@dataclass(frozen=True)
class BatchSummary:
    attempts: tuple[AttemptSummary, ...]

    @property
    def success_count(self) -> int:
        return sum(1 for attempt in self.attempts if attempt.success)

    @property
    def bad_state_count(self) -> int:
        return sum(1 for attempt in self.attempts if attempt.bad_state)

    @property
    def total(self) -> int:
        return len(self.attempts)

    def to_text(self) -> str:
        lines = [
            f"successes={self.success_count}/{self.total}",
            f"bad_states={self.bad_state_count}/{self.total}",
        ]
        for attempt in self.attempts:
            lines.append(
                "attempt_{attempt}: success={success} reached_end={reached_end} "
                "goal_area={goal_area} bad_state={bad_state} max_x={max_x}".format(
                    attempt=attempt.attempt,
                    success=str(attempt.success).lower(),
                    reached_end=str(attempt.reached_end).lower(),
                    goal_area=str(attempt.goal_area).lower(),
                    bad_state=str(attempt.bad_state).lower(),
                    max_x=attempt.max_x,
                )
            )
        return "\n".join(lines)


def parse_fceux_log(log_path: Path, expected_attempts: int | None = None) -> BatchSummary:
    text = log_path.read_text(errors="replace")
    seen_attempts: set[int] = set()
    success: set[int] = set()
    bad_state: set[int] = set()
    reached_end: set[int] = set()
    goal_area: set[int] = set()
    max_x: dict[int, int] = {}
    current_attempt: int | None = None

    for line in text.splitlines():
        state_match = STATE_RE.search(line)
        if state_match is not None:
            current_attempt = int(state_match.group("attempt"))
            event = state_match.group("event")
            seen_attempts.add(current_attempt)
            if event == "success_course_clear":
                success.add(current_attempt)
            elif event == "bad_state":
                bad_state.add(current_attempt)
            elif event == "reached_end_x":
                reached_end.add(current_attempt)
            elif event == "goal_area":
                goal_area.add(current_attempt)

        x_match = X_RE.search(line)
        if current_attempt is not None and x_match is not None:
            x = int(x_match.group("x"))
            if 0 <= x < 8192:
                max_x[current_attempt] = max(x, max_x.get(current_attempt, -1))

    if expected_attempts is not None:
        attempts = range(1, expected_attempts + 1)
    else:
        attempts = range(1, max(seen_attempts or {0}) + 1)

    return BatchSummary(
        tuple(
            AttemptSummary(
                attempt=attempt,
                success=attempt in success,
                bad_state=attempt in bad_state,
                reached_end=attempt in reached_end,
                goal_area=attempt in goal_area,
                max_x=max_x.get(attempt, -1),
            )
            for attempt in attempts
        )
    )


def run_fceux_1_1(
    *,
    game_path: Path,
    script_path: Path,
    artifacts_dir: Path,
    attempts: int,
    capture_images: bool = False,
    capture_ticks: bool = False,
    after_attempt_frames: int | None = None,
    post_1_1_probe: str | None = None,
) -> BatchSummary:
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    log_path = artifacts_dir / "fceux_1_1.log"
    image_dir = artifacts_dir / "images"

    env = os.environ.copy()
    env["SMB3_AGENT_LOG"] = str(log_path.resolve())
    env["SMB3_AGENT_ATTEMPTS"] = str(attempts)
    if after_attempt_frames is not None:
        env["SMB3_AFTER_ATTEMPT_FRAMES"] = str(after_attempt_frames)
    if capture_ticks:
        env["SMB3_CAPTURE_TICKS"] = "1"
    if post_1_1_probe:
        env["SMB3_POST_1_1_PROBE"] = post_1_1_probe
    if capture_images:
        image_dir.mkdir(parents=True, exist_ok=True)
        env["SMB3_AGENT_IMAGE_DIR"] = str(image_dir.resolve())
    else:
        env.pop("SMB3_AGENT_IMAGE_DIR", None)

    subprocess.run(
        [
            "fceux",
            "--no-config",
            "1",
            "--sound",
            "0",
            "--loadlua",
            str(script_path.resolve()),
            str(game_path.resolve()),
        ],
        check=False,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return parse_fceux_log(log_path, expected_attempts=attempts)
