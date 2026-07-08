# Validation Gates

Use this file as the source of truth for what must pass after implementation
work. A change is not done until its relevant gate passes or the failure is
documented.

## Gate 0: Repo Hygiene

Command:

```bash
PYTHON=.venv/bin/python scripts/validate_phase0.sh
```

Pass condition:

- Whitespace checks pass.
- Source/docs/tests intended for review are visible as tracked or untracked
  changes.
- Runtime artifacts and local emulator files are ignored.
- No generated screenshot/log directories are staged.
- Unit tests pass.

## Gate 1: Unit Tests

Command:

```bash
.venv/bin/python -m pytest -q
```

Pass condition:

```text
4 passed
```

The exact count may grow, but the suite must pass.

## Gate 2: World 1-1 Reliability

Command:

```bash
export SMB3_GAME_FILE=/path/to/local-game-file
python -m smb3_agent task fceux-1-1 \
  --game-file "$SMB3_GAME_FILE" \
  --attempts 10 \
  --artifacts-dir artifacts/fceux/cli_gate_1_1 \
  --require-perfect
```

Pass condition:

```text
successes=10/10
bad_states=0/10
```

This gate proves the base route runner can start from a fresh flow and clear
World 1-1 reliably.

## Gate 3: Current World 1 King Route

Command:

```bash
export SMB3_GAME_FILE=/path/to/local-game-file
python -m smb3_agent task fceux-world-1-king \
  --game-file "$SMB3_GAME_FILE" \
  --attempts 10 \
  --artifacts-dir artifacts/fceux/world_1_king \
  --require-perfect
```

Pass condition:

```text
successes=10/10
bad_states=0/10
post_probe_last_event=post_probe_1_airship_success_king
post_probe_clear=true
```

This gate proves the current route reaches the king-transition marker. It does
not prove every segment is solved by regular gameplay. See
`docs/route-status.md`.

## Gate 4: Watchable Demo

Command:

```bash
SMB3_AGENT_FRAME_SLEEP_SECONDS=0.0035 \
python -m smb3_agent task fceux-world-1-king \
  --attempts 1 \
  --artifacts-dir artifacts/fceux/show_world_1_king \
  --capture-images \
  --capture-ticks
```

Pass condition:

- The emulator visibly runs the route.
- If it fails, the failure is reviewed as demo-mode instability, not confused
  with the reliability gate.

Important note:

Visible throttle and screenshot capture can change timing. A watchable demo is
evidence for review, not the source of truth for reliability.

## Gate 5: Contact Sheet Review

Command:

```bash
python -m smb3_agent task fceux-contact-sheet \
  --input-dir artifacts/fceux/show_world_1_king/images
```

Pass condition:

- PNG frames and a contact sheet are produced.
- The sheet is used to inspect where a segment failed or transitioned.

## Gate 6: Log Review

Command:

```bash
python -m smb3_agent task review-fceux-log \
  --log artifacts/fceux/world_1_king/fceux_1_1.log \
  --attempts 10
```

Pass condition:

- Summary matches the expected pass/fail outcome.
- Post-probe fields identify the final route event.

## Gate 7: Goal Contract

Command:

```bash
.venv/bin/python -m smb3_agent goal validate data/goals/world_1_king.yaml
```

Pass condition:

```text
valid=true
goal_id=world_1_king
```

The validator must reject missing required fields with a clear error.

## Gate 8: Goal Run

Command:

```bash
export SMB3_GAME_FILE=/path/to/local-game-file
.venv/bin/python -m smb3_agent goal run world_1_king --attempts 3
```

Pass condition:

```text
successes=3/3
post_probe_last_event=post_probe_1_airship_success_king
post_probe_clear=true
metrics_passed=true
```

The command must also print the `artifacts_dir` used for the run.

## Gate 9: Segment Catalog

Command:

```bash
.venv/bin/python -m smb3_agent segment validate data/segments/world_1.yaml
```

Pass condition:

```text
valid=true
catalog_id=world_1
segments=9
goal_id=world_1_king
goal_segments=9
```

The validator must reject unsupported statuses, duplicate ids, missing required
fields, and goal references to missing segments.

## Gate 10: Goal Status

Command:

```bash
.venv/bin/python -m smb3_agent goal status world_1_king
```

Pass condition:

- Output lists every route segment in goal order.
- Solved, flaky, and bridged statuses are visible.
- Bridge flags are explicit for each segment.

## Gate 11: Log Review

Command:

```bash
.venv/bin/python -m smb3_agent review log artifacts/fceux/water_to_node_10_up_right_A/fceux_1_1.log
```

Pass condition:

- Output includes `failure_class`.
- Output includes `failed_segment`.
- Output includes `last_event`.
- Output includes one concrete `next_experiment`.

## Gate 12: Review Compare

Command:

```bash
.venv/bin/python -m smb3_agent review compare \
  artifacts/goals/world_1_king/20260706T202815Z \
  artifacts/fceux/water_to_node_10_up_right_A
```

Pass condition:

- Output includes both logs.
- Output includes both failure classes.
- Output explains why a passing reliability run and a watch/capture-style
  failure can differ.

## Gate 13: Command Parse

Command:

```bash
.venv/bin/python -m smb3_agent command parse "run world 1 king gate 3 times"
```

Pass condition:

```text
action=run_goal
goal=world_1_king
attempts=3
run_mode=gate
validation_policy=require_goal_metrics
```

## Gate 14: Command Run

Command:

```bash
export SMB3_GAME_FILE=/path/to/local-game-file
.venv/bin/python -m smb3_agent command run "run world 1 king gate 3 times"
```

Pass condition:

- Command runs the same goal gate as `goal run world_1_king --attempts 3`.
- Output includes `artifacts_dir`.
- Output includes `trace_path`.
- Output includes `metrics_passed=true`.
- Output includes one `next_action`.

## Gate 15: Observe Segment

Command:

```bash
export SMB3_GAME_FILE=/path/to/local-game-file
.venv/bin/python -m smb3_agent observe run-segment world_1_1 --sample-frames 15
```

Pass condition:

- Output includes `trace_path`.
- Output includes `progress_markers`.
- Output includes `final_success=true`.
- The JSONL trace includes a final snapshot.

## Gate 16: Life-Loss Recovery

Command:

```bash
.venv/bin/python -m smb3_agent recovery simulate life_lost --goal world_1_king
```

Pass condition:

```text
decision=continue_next_life
action=reclassify_state
```

The reason must cite the goal recovery policy.

## Gate 17: Wrong-Map Recovery

Command:

```bash
.venv/bin/python -m smb3_agent recovery simulate wrong_map_node --goal world_1_king
```

Pass condition:

```text
decision=correct_known_state
action=correct_known_state_or_stop
```

The decision must respect `constraints.allow_bridge_steps`; if bridge steps are
disabled, it must stop instead of silently correcting.

## Planned Gates

These gates cover the Phase 6 attempt-lab flow.

## Gate 18: Lab Session Start

Command:

```bash
export SMB3_GAME_FILE=/path/to/local-game-file
.venv/bin/python -m smb3_agent lab start "show me the route at 4x" --attempts 1
```

Pass condition:

- A session manifest is written under `artifacts/sessions/`.
- The manifest records requested speed, actual run settings, route variant,
  artifact paths, and result.

## Gate 19: Lab Note Latest

Command:

```bash
.venv/bin/python -m smb3_agent lab note latest \
  "1-1 around 320 timer: falls into the hole and usually gets lucky"
```

Pass condition:

- The note is appended to the latest session.
- Raw text is preserved exactly.
- Optional anchors are validated when provided.

## Gate 20: Lab Review Latest

Command:

```bash
.venv/bin/python -m smb3_agent lab review latest
```

Pass condition:

- Review links session, notes, and trace evidence.
- It recommends one concrete experiment or records why there is not enough
  evidence.

## Gate 21: Variant Proposal

Command:

```bash
.venv/bin/python -m smb3_agent lab propose-variant latest
```

Pass condition:

- A proposed variant records parent variant, source session, source notes,
  changed files, and validation command.
- Baseline files are unchanged.

## Gate 22: Variant Validation

Command:

```bash
export SMB3_GAME_FILE=/path/to/local-game-file
.venv/bin/python -m smb3_agent lab run-variant world_1_1_harden_hole_320_a --attempts 10
```

Pass condition:

- Variant run writes a normal session artifact.
- Result can be compared to the parent variant.

## Gate 23: Variant Promotion Guard

Command:

```bash
.venv/bin/python -m smb3_agent lab promote-variant world_1_1_harden_hole_320_a
```

Pass condition:

- Promotion is refused without a passing validation artifact.
- If accepted, prior baseline metadata is preserved.

Promotion should be tested first on disposable variants. Do not promote a route
variant just because the command exists.

## Gate 24: Issue Ledger

Command:

```bash
.venv/bin/python -m smb3_agent lab issues latest
```

Pass condition:

- Every note is assigned to an issue.
- Issues are grouped by segment and type.
- Expected behavior and positive evidence are marked non-actionable.
- The highest-priority actionable issue is explicit.

## Gate 25: Multi-Proposal Generation

Command:

```bash
.venv/bin/python -m smb3_agent lab propose-variants latest
```

Pass condition:

- One proposal is produced per actionable issue.
- Each proposal records source issue, source notes, relevant files, and
  validation command.

## Gate 26: UI Summary

Command:

```bash
.venv/bin/python -m smb3_agent lab ui-summary latest
```

Pass condition:

- Output lists backend World 1 route entries with note, issue, proposal, and
  validation state.
- A reviewer can inspect the latest session without parsing raw route logs.

## Gate 27: Codex Task Packet

Command:

```bash
.venv/bin/python -m smb3_agent lab codex-task latest --issue ISSUE_ID
```

Pass condition:

- Packet includes session manifest, issue ledger, selected issue, relevant notes,
  route-log excerpt, segment catalog, relevant route files, and validation
  command.
- Packet is usable by Codex CLI without relying on chat history.

## Gate 28: Mario Route Lab Render

Command:

```bash
.venv/bin/python -m smb3_agent lab ui-render --output artifacts/ui/latest.html
```

Pass condition:

- HTML file is written.
- HTML contains `Mario Route Lab`.
- HTML contains `Route`, `Evidence`, `Teach This Section`, `Things Mario Still
  Gets Wrong`, and `Recent Observations`.
- HTML contains player-facing World 1 locations such as `Map`, `1-1`,
  `1-3`, `Fortress`, `Airship`, and `King`.
- HTML contains run inputs for speed, attempts, run mode, unit tests, phase
  gate, and render check.
- HTML contains teaching note inputs for locations.
- HTML does not depend on old top-level labels such as `World 1 Control Panel`,
  `World 1 Mission Control`, `Run Controls`, `World 1 Notes`, or
  `Route Health`.

## Gate 29: Mario Route Lab Server

Command:

```bash
.venv/bin/python -m smb3_agent lab ui --host 127.0.0.1 --port 8765
```

Pass condition:

- Server prints a local URL.
- `GET /` returns Mario Route Lab.
- `GET /artifacts/...` serves files under the local `artifacts/` tree for
  evidence review.
- `POST /notes` appends batch notes to the latest session and regenerates
  issues/proposals.
- `POST /run` starts a World 1 watch or gate run using the selected speed and
  attempt count when `SMB3_GAME_FILE` is set.
- `POST /test` can trigger unit tests, the phase gate, or the render check.
- `POST /codex-task` creates a Codex task packet for an actionable issue.

## Gate 30: Location Model

Command:

```bash
.venv/bin/python - <<'PY'
from pathlib import Path
import yaml

data = yaml.safe_load(Path("data/worlds/world_1_locations.yaml").read_text())
labels = {location["label"] for location in data["locations"]}
required = {"Map", "1-1", "1-2", "1-3", "Fortress", "Airship", "King"}
missing = sorted(required - labels)
if missing:
    raise SystemExit(f"missing labels: {missing}")
print("valid=true")
PY
```

Pass condition:

- The World 1 location model exists.
- Required player-facing locations are present.
- Each location has an objective for Mario Route Lab.
