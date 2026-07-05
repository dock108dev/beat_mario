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

## World 1-2 Clear Gate

The current 1-2 route runs as a post-1-1 probe. It clears 1-1, enters 1-2
from the map, executes the memory-aware 1-2 route, and exits non-zero unless
the 1-2 probe reports a course clear:

```bash
python -m smb3_agent task fceux-1-1 --attempts 1 --artifacts-dir artifacts/fceux/gate_1_2 --after-attempt-frames 900 --post-1-1-probe run_1_2_naive --require-perfect --require-post-probe-clear
```

Passing means:

```text
successes=1/1
post_probe_clear=true
```

The 1-2 success marker requires the route to reach the goal card threshold and
then hit the normal level transition. This avoids counting a near-miss or invalid
transition as a clear.

For screenshot-backed review:

```bash
python -m smb3_agent task fceux-1-1 --attempts 1 --artifacts-dir artifacts/fceux/inspect_1_2 --capture-images --capture-ticks --after-attempt-frames 900 --post-1-1-probe run_1_2_naive --require-perfect --require-post-probe-clear
python -m smb3_agent task fceux-contact-sheet --input-dir artifacts/fceux/inspect_1_2/images
```

For quick Lua parameter sweeps, pass explicit overrides:

```bash
python -m smb3_agent task fceux-1-1 --attempts 1 --artifacts-dir artifacts/fceux/probe_run_1_2_hill_32 --post-1-1-probe run_1_2_naive --after-attempt-frames 900 --set-env SMB3_1_2_HILL_ENEMY_JUMP_FRAMES=32 --require-perfect
```

Current 1-2 tuning keys:

```text
SMB3_1_2_ENEMY_MIN_DX
SMB3_1_2_ENEMY_MAX_DX
SMB3_1_2_ENEMY_JUMP_FRAMES
SMB3_1_2_HILL_ENEMY_JUMP_FRAMES
SMB3_1_2_HILL_ENEMY_START
SMB3_1_2_HILL_ENEMY_END
SMB3_1_2_HILL_DELAY_FRAMES
SMB3_1_2_HILL_JUMP_FRAMES
SMB3_1_2_HILL_SLOW_FRAMES
SMB3_1_2_LATE_JUMP_START
SMB3_1_2_LATE_DELAY_FRAMES
SMB3_1_2_LATE_JUMP_FRAMES
SMB3_1_2_LATE_SLOW_FRAMES
SMB3_1_2_GOAL_JUMP_START
SMB3_1_2_GOAL_JUMP_FRAMES
SMB3_1_2_GOAL_CARRY_FRAMES
```
