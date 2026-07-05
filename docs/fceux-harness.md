# FCEUX Harness

The reliable World 1-1 route currently runs through FCEUX with a Lua route script.
This path is preferred for route work because it can read stable in-game state,
drive controller input directly, and emit structured log markers.

## World 1-1 Gate

```bash
python -m smb3_agent task fceux-1-1 --attempts 10 --artifacts-dir artifacts/fceux/cli_gate_1_1 --require-perfect
```

Passing means:

```text
successes=10/10
bad_states=0/10
```

The gate is intentionally strict. `--require-perfect` exits non-zero if any
attempt fails to clear the level.

## Route Markers

The Lua script writes markers that the Python harness parses:

```text
attempt_N_reached_end_x
attempt_N_goal_area
attempt_N_success_course_clear
attempt_N_bad_state
```

`success_course_clear` only counts if the route first reached the goal area.
This avoids mistaking a death or invalid transition for a completed level.

## Visual Review

For screenshot-backed review:

```bash
python -m smb3_agent task fceux-1-1 --attempts 1 --artifacts-dir artifacts/fceux/inspect_1_1 --capture-images
python -m smb3_agent task fceux-contact-sheet --input-dir artifacts/fceux/inspect_1_1/images
```

The contact sheet is useful for route tuning and debugging, but it is not the
source of truth for pass/fail. The structured log markers are.

## Next Segment

The next route target is World 1-2 entry:

1. Clear World 1-1 from a fresh boot path.
2. Wait until the World 1 map is stable.
3. Capture map screenshots and state bytes.
4. Move right twice and press A.
5. Confirm the 1-2 start with a level screen and Mario near `x=24`.
6. Save a reusable checkpoint once the 1-2 start is promoted from probe to route.

The current probe command is:

```bash
python -m smb3_agent task fceux-1-1 --attempts 1 --artifacts-dir artifacts/fceux/probe_enter_1_2 --capture-images --capture-ticks --after-attempt-frames 900 --post-1-1-probe enter_1_2 --require-perfect
```
