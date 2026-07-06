# Implementation Plan

This plan turns the current route harness into a user-steered gameplay agent.
Every implementation step has a validation gate. Do not expand scope until the
gate for the current step passes or the failure is documented.

## Phase 0: Repo Readiness

Goal: make the project easy to resume without relying on chat history.

### Step 0.1: Keep the tracked surface clean

Implementation:

- Keep local game files, emulator state, screenshots, generated logs, and
  contact sheets out of git.
- Keep docs, tests, route scripts, fixtures, and source code tracked.
- Make README a project index, not a full route journal.

Validation gate:

```bash
PYTHON=.venv/bin/python scripts/validate_phase0.sh
```

Pass condition:

- Only intentional source/doc changes are uncommitted.
- Generated artifacts appear ignored.
- Tests pass.

### Step 0.2: Document current truth

Implementation:

- Maintain `docs/route-status.md`.
- Label each segment as `solved`, `flaky`, `bridged`, or `unknown`.
- Record latest validation command and result.

Validation gate:

```bash
export SMB3_GAME_FILE=/path/to/local-game-file
python -m smb3_agent task fceux-world-1-king \
  --game-file "$SMB3_GAME_FILE" \
  --attempts 3 \
  --artifacts-dir artifacts/fceux/doc_gate_world_1_king \
  --require-perfect
```

Pass condition:

- Command exits zero.
- Summary includes `post_probe_clear=true`.
- Route status doc matches the result.
- If `SMB3_GAME_FILE` is not set on a machine, the repo-only Phase 0 gate can
  still pass, but live route truth is not refreshed.

## Phase 1: Explicit Goal Contracts

Goal: stop encoding intent only in command flags and env overrides.

### Step 1.1: Add goal contract schema

Implementation:

- Add a `GoalContract` model.
- Store goal contracts under `data/goals/`.
- Include objective, constraints, success metrics, allowed tactics, and recovery
  policy.

Validation gate:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m smb3_agent goal validate data/goals/world_1_king.yaml
```

Pass condition:

- Contract loads and validates.
- Missing required fields produce a clear error.

### Step 1.2: Add World 1 king contract

Implementation:

- Create `data/goals/world_1_king.yaml`.
- Map it to the existing `fceux-world-1-king` preset.
- Record which parts are bridged.

Validation gate:

```bash
export SMB3_GAME_FILE=/path/to/local-game-file
.venv/bin/python -m smb3_agent goal run world_1_king --attempts 3
```

Pass condition:

- Command exits zero.
- It writes an attempt directory.
- Summary includes final event `post_probe_1_airship_success_king`.

## Phase 2: Segment Catalog

Goal: make route state inspectable and editable without reading the Lua file.

### Step 2.1: Add segment schema

Implementation:

- Add segment files under `data/segments/`.
- Each segment includes start condition, success condition, failure conditions,
  current method, and status.
- Supported statuses: `planned`, `solved`, `flaky`, `bridged`, `blocked`.

Validation gate:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m smb3_agent segment validate data/segments/world_1.yaml
```

Pass condition:

- Segment file validates.
- Every segment referenced by `world_1_king` exists.

### Step 2.2: Promote current route facts

Implementation:

- Document current World 1 segments.
- Mark 1-1, 1-2, and 1-3 according to current evidence.
- Mark bridge-dependent sections honestly.

Validation gate:

```bash
.venv/bin/python -m smb3_agent goal status world_1_king
```

Pass condition:

- Output lists every route segment in order.
- Output clearly identifies solved, flaky, and bridged sections.

## Phase 3: Attempt Review

Goal: make failed runs useful without manually scanning logs.

### Step 3.1: Structured failure classification

Implementation:

- Add a review module that reads route logs.
- Classify failures as:
  - `input_timing`
  - `state_detection`
  - `wrong_route_state`
  - `life_lost`
  - `bridge_failure`
  - `unknown`
- Include last event, max x, lives/form if available, and final state snapshot.

Validation gate:

```bash
python -m smb3_agent review log artifacts/fceux/show_world1_king_4x_001/fceux_1_1.log
```

Pass condition:

- Review identifies the failed segment.
- Review gives one concrete next experiment.

### Step 3.2: Batch review report

Implementation:

- Summarize N attempts by success rate and failure class.
- Compare two artifact directories.
- Highlight timing/capture mode differences.

Validation gate:

```bash
python -m smb3_agent review compare \
  artifacts/fceux/world_1_king \
  artifacts/fceux/show_world1_king_4x_001
```

Pass condition:

- Report explains why reliability gate and watchable demo may differ.

## Phase 4: Command Interpreter

Goal: let the user command the agent in game terms, not only CLI flags.

### Step 4.1: Add command parser

Implementation:

- Add a parser for user commands such as:
  - "run world 1 king gate 10 times"
  - "show me the route at 4x"
  - "review the latest failed run"
  - "continue after losing a life if the route allows it"
- Start with deterministic parsing before adding an LLM.

Validation gate:

```bash
python -m pytest -q
python -m smb3_agent command parse "run world 1 king gate 3 times"
```

Pass condition:

- Command maps to a goal, attempts count, run mode, and validation policy.

### Step 4.2: Add command runner

Implementation:

- Execute parsed commands through existing goal/segment APIs.
- Preserve artifacts and write a command trace.

Validation gate:

```bash
python -m smb3_agent command run "run world 1 king gate 3 times"
```

Pass condition:

- Command runs the same gate as the lower-level CLI.
- Output includes artifact path, summary, and next recommended action.

## Phase 5: Live Observe/Adjust Loop

Goal: move from script execution to adaptive control.

### Step 5.1: Poll state during segments

Implementation:

- Add an observer loop that emits state snapshots every N frames.
- Track mode, position, lives, form, map node, inventory, and segment progress.
- Make route scripts able to ask "what state am I in now?"

Validation gate:

```bash
python -m smb3_agent observe run-segment world_1_1 --sample-frames 15
```

Pass condition:

- State trace includes progress markers and final success or failure state.

### Step 5.2: React to life loss

Implementation:

- Detect life loss from HUD/memory.
- If the goal contract allows continuing, reclassify current state and choose
  the next action:
  - continue next life
  - reset segment
  - reload known checkpoint
  - stop for review

Validation gate:

```bash
python -m smb3_agent recovery simulate life_lost --goal world_1_king
```

Pass condition:

- Recovery decision is deterministic and explains why it chose continue, reset,
  bridge, or stop.

### Step 5.3: Recover wrong map position

Implementation:

- Detect when map cursor or route state differs from expected.
- If the contract allows bridge/correction, apply known correction.
- Otherwise stop with a review artifact.

Validation gate:

```bash
python -m smb3_agent recovery simulate wrong_map_node --goal world_1_king
```

Pass condition:

- Recovery respects the goal contract.
- It does not silently bridge when bridge steps are disallowed.

## Phase 6: Research Unknown Routes

Goal: handle World 8 even though the user does not already know it.

### Step 6.1: Route research notes

Implementation:

- Add `docs/world-8-research.md`.
- Record required levels, known hazards, suspected hard segments, and source
  confidence.
- Convert notes into planned segments.

Validation gate:

```bash
python -m smb3_agent segment validate data/segments/world_8.yaml
```

Pass condition:

- World 8 has a planned segment list.
- Unknowns are explicit.

### Step 6.2: First World 8 segment proof

Implementation:

- Start from a known World 8 state.
- Build the first segment as a small run with logs and screenshots.

Validation gate:

```bash
python -m smb3_agent goal run world_8_first_segment --attempts 5
```

Pass condition:

- At least one successful run or a classified blocker with artifacts.

## Phase 7: Generalize Beyond SMB3

Goal: preserve the parts that apply to future sim/playtester products.

Implementation:

- Keep game-specific adapters isolated.
- Keep goal contracts, segment status, attempt review, and command parsing
  game-agnostic where practical.
- Extract common agent interfaces only after SMB3 has working examples.

Validation gate:

```bash
python -m pytest -q
python -m smb3_agent goal status world_1_king
```

Pass condition:

- SMB3 still works while generic abstractions are introduced.
