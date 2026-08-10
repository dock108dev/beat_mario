from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path


STATE_RE = re.compile(r"\battempt_(?P<attempt>\d+)_(?P<event>[A-Za-z0-9_]+)\b")
X_RE = re.compile(r"\bx=(?P<x>-?\d+)\b")
EVENT_RE = re.compile(r"\bevent=(?P<event>[A-Za-z0-9_]+)\b")


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
    post_probe_max_x: int = -1
    post_probe_last_event: str | None = None
    post_probe_clear: bool = False
    post_probe_events: tuple[str, ...] = ()

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
        if self.post_probe_max_x >= 0:
            lines.append(f"post_probe_max_x={self.post_probe_max_x}")
        if self.post_probe_last_event is not None:
            lines.append(f"post_probe_last_event={self.post_probe_last_event}")
        lines.append(f"post_probe_clear={str(self.post_probe_clear).lower()}")
        return "\n".join(lines)


def parse_fceux_log(
    log_path: Path,
    expected_attempts: int | None = None,
    *,
    allow_bridges: bool = False,
) -> BatchSummary:
    text = log_path.read_text(errors="replace")
    seen_attempts: set[int] = set()
    success: set[int] = set()
    bad_state: set[int] = set()
    reached_end: set[int] = set()
    goal_area: set[int] = set()
    max_x: dict[int, int] = {}
    current_attempt: int | None = None
    post_probe_max_x = -1
    post_probe_last_event: str | None = None
    post_probe_clear = False
    post_probe_events: list[str] = []
    playback_contaminated = False
    valid_1_6_goal_card_seen = False
    valid_1_6_course_transition = False
    valid_world_1_roamer_defeat = False
    valid_world_2_first_whistle = False
    valid_warp_zone_5_6_7_tier = False
    valid_warp_zone_second_whistle = False
    valid_warp_zone_world_8_tier = False
    valid_world_8_pipe_entry = False

    for line in text.splitlines():
        event_match = EVENT_RE.search(line)
        event = event_match.group("event") if event_match is not None else None
        x_match = X_RE.search(line)
        if event is not None and event.startswith("post_probe_"):
            post_probe_events.append(event)
            post_probe_last_event = event
            if event.startswith("post_probe_1_6_opening_search") or event.startswith(
                "post_probe_1_6_segment_search"
            ):
                playback_contaminated = True
                post_probe_clear = False
            if event.startswith("post_probe_world_1_roamer_search"):
                playback_contaminated = True
                post_probe_clear = False
            if "_bridge" in event and not allow_bridges:
                playback_contaminated = True
                post_probe_clear = False
            if "_discovery_" in event:
                playback_contaminated = True
                post_probe_clear = False
            if event == "post_probe_world_1_roamer_detected":
                valid_world_1_roamer_defeat = False
                post_probe_clear = False
            if event in {
                "post_probe_world_1_roamer_life_lost",
                "post_probe_world_1_roamer_failed",
                "post_probe_world_1_roamer_fixed_attack_failed",
            }:
                valid_world_1_roamer_defeat = False
                post_probe_clear = False
            if event == "post_probe_1_6_goal_card":
                valid_1_6_goal_card_seen = (
                    "evidence=card_internal_state_nonzero" in line
                    and "form_before_clear=3" in line
                )
            if event == "post_probe_1_6_success_course_clear":
                valid_1_6_course_transition = (
                    valid_1_6_goal_card_seen
                    and "evidence=card_internal_state_then_course_transition" in line
                )
            if event == "post_probe_1_6_map_returned":
                post_probe_clear = (
                    valid_1_6_course_transition
                    and "evidence=object_set_0_after_course_transition" in line
                    and "object_set=0" in line
                    and not playback_contaminated
                )
            if event == "post_probe_world_1_roamer_defeated_in_battle":
                valid_world_1_roamer_defeat = (
                    "evidence=enemy_id_-127_removed" in line
                    and "form_after=3" in line
                    and "return_map=0" in line
                    and "item_0=12" in line
                    and "item_1=12" in line
                )
            if event == "post_probe_world_1_roamer_map_returned":
                post_probe_clear = (
                    valid_world_1_roamer_defeat
                    and "evidence=object_set_0_after_roamer_defeat" in line
                    and "object_set=0" in line
                    and "item_0=12" in line
                    and "item_1=12" in line
                    and not playback_contaminated
                )
            if event in {
                "post_probe_1_castle_no_entry",
                "post_probe_1_castle_bad_state",
                "post_probe_1_airship_boss_room_missing",
                "post_probe_world_2_whistle_inventory_mismatch",
                "post_probe_world_2_map_missing",
                "post_probe_world_2_first_whistle_missing",
                "post_probe_warp_zone_5_6_7_missing",
                "post_probe_warp_zone_second_whistle_missing",
                "post_probe_warp_zone_world_8_tier_missing",
                "post_probe_world_8_pipe_position_missing",
                "post_probe_world_8_map_missing",
                "post_probe_world_8_map_unstable",
            }:
                post_probe_clear = False
            elif event in {
                "post_probe_1_2_enter",
                "post_probe_1_3_enter",
                "post_probe_1_fortress_enter",
                "post_probe_1_5_enter",
                "post_probe_1_5_water_enter",
                "post_probe_1_6_enter",
                "post_probe_1_castle_enter",
            } or event.startswith("post_probe_1_fortress_enter_") or event.startswith(
                "post_probe_1_4_enter"
            ) or event.startswith("post_probe_1_5_enter") or event.startswith(
                "post_probe_1_5_water_enter"
            ) or event.startswith(
                "post_probe_1_6_enter"
            ) or event.startswith(
                "post_probe_1_6_level_enter"
            ) or event.startswith(
                "post_probe_1_castle_enter"
            ) or event.startswith(
                "post_probe_1_airship_enter_after_roamer"
            ):
                post_probe_clear = False
                post_probe_max_x = -1
            if event in {
                "post_probe_1_2_success_course_clear",
                "post_probe_1_3_whistle_room_success",
                "post_probe_1_fortress_whistle_room_success",
                "post_probe_1_4_success_course_clear",
                "post_probe_1_5_success_course_clear",
                "post_probe_1_5_water_success_course_clear",
                "post_probe_world_8_map_arrival",
            }:
                post_probe_clear = not playback_contaminated
            if event == "post_probe_1_airship_success_king" and allow_bridges:
                post_probe_clear = True
            if event == "post_probe_world_2_map_two_whistles":
                post_probe_clear = (
                    "evidence=world_number_1_object_set_0" in line
                    and "world_number=1" in line
                    and "object_set=0" in line
                    and "item_0=12" in line
                    and "item_1=12" in line
                    and not playback_contaminated
                )
            if event == "post_probe_world_2_first_whistle_started":
                valid_world_2_first_whistle = False
                post_probe_clear = False
            if event == "post_probe_world_2_first_whistle_used":
                valid_world_2_first_whistle = (
                    "evidence=two_to_one_whistle_after_A_input" in line
                    and "source_world=2" in line
                    and "world_number=1" in line
                )
            if event == "post_probe_warp_zone_5_6_7_tier":
                valid_warp_zone_5_6_7_tier = (
                    valid_world_2_first_whistle
                    and "evidence=warp_cursor_64_112_after_world_2_whistle" in line
                    and "world_number=8" in line
                    and "map_cursor_x=64" in line
                    and "map_cursor_y=112" in line
                )
            if event == "post_probe_warp_zone_second_whistle_started":
                valid_warp_zone_second_whistle = False
                post_probe_clear = False
            if event == "post_probe_warp_zone_second_whistle_used":
                valid_warp_zone_second_whistle = (
                    valid_world_2_first_whistle
                    and valid_warp_zone_5_6_7_tier
                    and "evidence=one_to_zero_whistles_after_A_input_from_5_6_7_tier"
                    in line
                )
            if event == "post_probe_warp_zone_world_8_tier":
                valid_warp_zone_world_8_tier = (
                    valid_warp_zone_second_whistle
                    and "evidence=warp_cursor_128_144_after_second_whistle" in line
                    and "world_number=8" in line
                    and "map_cursor_x=128" in line
                    and "map_cursor_y=144" in line
                )
            if event == "post_probe_world_8_pipe_entered":
                valid_world_8_pipe_entry = (
                    valid_warp_zone_world_8_tier
                    and "evidence=A_input_from_warp_cursor_160_144" in line
                    and "world_number=8" in line
                    and "map_cursor_x=160" in line
                    and "map_cursor_y=144" in line
                )
            if event == "post_probe_world_8_map_arrival":
                post_probe_clear = (
                    valid_world_2_first_whistle
                    and valid_warp_zone_second_whistle
                    and valid_warp_zone_world_8_tier
                    and valid_world_8_pipe_entry
                    and "evidence=world_number_7_object_set_0_after_warp_pipe" in line
                    and "world_number=7" in line
                    and "object_set=0" in line
                    and all(f"item_{index}=12" not in line for index in range(10))
                    and not playback_contaminated
                )
            if x_match is not None:
                x = int(x_match.group("x"))
                if 0 <= x < 8192:
                    post_probe_max_x = max(post_probe_max_x, x)

        state_match = STATE_RE.search(line)
        if state_match is not None:
            current_attempt = int(state_match.group("attempt"))
            attempt_event = state_match.group("event")
            seen_attempts.add(current_attempt)
            if attempt_event == "success_course_clear":
                success.add(current_attempt)
            elif attempt_event == "bad_state":
                bad_state.add(current_attempt)
            elif attempt_event == "reached_end_x":
                reached_end.add(current_attempt)
            elif attempt_event == "goal_area":
                goal_area.add(current_attempt)

        if current_attempt is not None and x_match is not None:
            x = int(x_match.group("x"))
            if 0 <= x < 8192:
                max_x[current_attempt] = max(x, max_x.get(current_attempt, -1))

    if expected_attempts is not None:
        attempts = range(1, expected_attempts + 1)
    else:
        attempts = range(1, max(seen_attempts or {0}) + 1)

    return BatchSummary(
        attempts=tuple(
            AttemptSummary(
                attempt=attempt,
                success=attempt in success,
                bad_state=attempt in bad_state,
                reached_end=attempt in reached_end,
                goal_area=attempt in goal_area,
                max_x=max_x.get(attempt, -1),
            )
            for attempt in attempts
        ),
        post_probe_max_x=post_probe_max_x,
        post_probe_last_event=post_probe_last_event,
        post_probe_clear=post_probe_clear,
        post_probe_events=tuple(post_probe_events),
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
    env_overrides: tuple[str, ...] = (),
    allow_bridges: bool = False,
    clean_product_env: bool = False,
    frame_sleep_seconds: float = 0.0,
    timeout_seconds: int | None = None,
) -> BatchSummary:
    if not game_path.is_file():
        raise FileNotFoundError(f"Local game file not found: {game_path}")

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    log_path = artifacts_dir / "fceux_1_1.log"
    stdout_path = artifacts_dir / "fceux_stdout.log"
    stderr_path = artifacts_dir / "fceux_stderr.log"
    image_dir = artifacts_dir / "images"

    env = os.environ.copy()
    if clean_product_env:
        env = {key: value for key, value in env.items() if not key.startswith("SMB3_")}
    env["SMB3_AGENT_LOG"] = str(log_path.resolve())
    env["SMB3_AGENT_ATTEMPTS"] = str(attempts)
    if frame_sleep_seconds > 0:
        env["SMB3_AGENT_FRAME_SLEEP_SECONDS"] = str(frame_sleep_seconds)
    else:
        env.pop("SMB3_AGENT_FRAME_SLEEP_SECONDS", None)
    if after_attempt_frames is not None:
        env["SMB3_AFTER_ATTEMPT_FRAMES"] = str(after_attempt_frames)
    if capture_ticks:
        env["SMB3_CAPTURE_TICKS"] = "1"
    if post_1_1_probe:
        env["SMB3_POST_1_1_PROBE"] = post_1_1_probe
    for item in env_overrides:
        key, separator, value = item.partition("=")
        if not key or separator != "=":
            raise ValueError(f"Invalid environment override: {item}")
        env[key] = value
    if capture_images:
        image_dir.mkdir(parents=True, exist_ok=True)
        env["SMB3_AGENT_IMAGE_DIR"] = str(image_dir.resolve())
    else:
        env.pop("SMB3_AGENT_IMAGE_DIR", None)

    effective_timeout = timeout_seconds or int(
        env.get("SMB3_FCEUX_TIMEOUT_SECONDS", "180")
    )
    started_at = datetime.now(timezone.utc)
    execution = {
        "started_at": started_at.isoformat(),
        "attempts": attempts,
        "fresh_process": True,
        "clean_product_env": clean_product_env,
        "frame_sleep_seconds": frame_sleep_seconds,
        "capture_images": capture_images,
        "capture_ticks": capture_ticks,
        "timeout_seconds": effective_timeout,
        "timed_out": False,
        "returncode": None,
        "launch_error": None,
    }
    execution_path = artifacts_dir / "fceux_execution.json"
    launch_error: OSError | None = None
    try:
        with stdout_path.open("wb") as stdout_file, stderr_path.open("wb") as stderr_file:
            completed = subprocess.run(
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
                stdout=stdout_file,
                stderr=stderr_file,
                timeout=effective_timeout,
            )
            execution["returncode"] = completed.returncode
    except subprocess.TimeoutExpired:
        execution["timed_out"] = True
    except OSError as exc:
        execution["launch_error"] = f"{type(exc).__name__}: {exc}"
        launch_error = exc
    finally:
        finished_at = datetime.now(timezone.utc)
        execution["finished_at"] = finished_at.isoformat()
        execution["elapsed_seconds"] = round(
            (finished_at - started_at).total_seconds(), 6
        )
        execution_path.write_text(
            json.dumps(execution, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if launch_error is not None:
        raise launch_error
    return parse_fceux_log(
        log_path, expected_attempts=attempts, allow_bridges=allow_bridges
    )
