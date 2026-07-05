from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import yaml

from smb3_agent.backends.mednafen import key_down, key_up, tap


def execute_input_script(script_path: Path, trace_path: Path) -> list[dict[str, Any]]:
    if not script_path.exists():
        raise FileNotFoundError(f"Input script not found: {script_path}")

    raw = yaml.safe_load(script_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("steps"), list):
        raise ValueError(f"Input script must be a mapping with a steps list: {script_path}")

    trace_path.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    events: list[dict[str, Any]] = []

    with trace_path.open("w", encoding="utf-8") as trace_file:
        for index, step in enumerate(raw["steps"]):
            if not isinstance(step, dict):
                raise ValueError(f"Step {index} must be a mapping")
            event = execute_step(index, step, start)
            events.append(event)
            trace_file.write(json.dumps(event) + "\n")

    return events


def execute_step(index: int, step: dict[str, Any], start: float) -> dict[str, Any]:
    if "wait" in step:
        duration = float(step["wait"])
        time.sleep(duration)
        return event(index, "wait", None, duration, start)

    if "tap" in step:
        button = str(step["tap"])
        duration = float(step.get("duration", 0.08))
        tap(button, duration)
        return event(index, "tap", button, duration, start)

    if "hold" in step:
        button = str(step["hold"])
        key_down(button)
        return event(index, "hold", button, None, start)

    if "release" in step:
        button = str(step["release"])
        key_up(button)
        return event(index, "release", button, None, start)

    raise ValueError(f"Unsupported input step {index}: {step}")


def event(
    index: int,
    action: str,
    button: str | None,
    duration_seconds: float | None,
    start: float,
) -> dict[str, Any]:
    return {
        "ts": round(time.monotonic() - start, 4),
        "index": index,
        "action": action,
        "button": button,
        "duration_seconds": duration_seconds,
    }

