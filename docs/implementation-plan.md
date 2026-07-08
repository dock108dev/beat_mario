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
.venv/bin/python -m smb3_agent review log artifacts/fceux/water_to_node_10_up_right_A/fceux_1_1.log
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
.venv/bin/python -m smb3_agent review compare \
  artifacts/goals/world_1_king/20260706T202815Z \
  artifacts/fceux/water_to_node_10_up_right_A
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
.venv/bin/python -m pytest -q
.venv/bin/python -m smb3_agent command parse "run world 1 king gate 3 times"
```

Pass condition:

- Command maps to a goal, attempts count, run mode, and validation policy.

### Step 4.2: Add command runner

Implementation:

- Execute parsed commands through existing goal/segment APIs.
- Preserve artifacts and write a command trace.

Validation gate:

```bash
export SMB3_GAME_FILE=/path/to/local-game-file
.venv/bin/python -m smb3_agent command run "run world 1 king gate 3 times"
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
export SMB3_GAME_FILE=/path/to/local-game-file
.venv/bin/python -m smb3_agent observe run-segment world_1_1 --sample-frames 15
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
.venv/bin/python -m smb3_agent recovery simulate life_lost --goal world_1_king
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
.venv/bin/python -m smb3_agent recovery simulate wrong_map_node --goal world_1_king
```

Pass condition:

- Recovery respects the goal contract.
- It does not silently bridge when bridge steps are disallowed.

## Phase 6: Attempt Lab and Route Iteration

Goal: make every user observation and route change durable before expanding into
less-known route territory.

See `docs/attempt-lab.md` for the source-of-truth workflow.

Current status:

- Steps 6.1 through 6.9 are implemented.
- The lab handles sessions, notes, grouped issues, one or many proposals, UI
  summaries, Codex task packets, variant validation, and guarded promotion.
- The next gap is the actual UI shell and route-patch application workflow.

### Step 6.1: Attempt session manifest

Implementation:

- Add a session manifest model. [implemented]
- Store session artifacts under `artifacts/sessions/<session_id>/`. [implemented]
- Record command text, goal, route variant, speed, capture settings, attempt
  count, start/end timestamps, and output artifact paths.
- Add a `lab start` command that wraps existing command/goal runners and writes
  the manifest. [implemented]

Validation gate:

```bash
export SMB3_GAME_FILE=/path/to/local-game-file
.venv/bin/python -m smb3_agent lab start "show me the route at 4x" --attempts 1
```

Pass condition:

- Command exits zero or records a classified run failure.
- A session manifest is written.
- Manifest includes requested speed, actual run settings, route log path, and
  route variant.

### Step 6.2: Human note capture

Implementation:

- Add a note model using `data/lab/note-template.yaml` as the initial contract. [implemented]
- Add `lab note latest`. [implemented]
- Support free-form notes plus optional anchors:
  - segment id
  - attempt number
  - frame
  - event
  - wall-clock seconds
  - in-game timer
  - screenshot
- Preserve the user's raw text separately from machine interpretation. [implemented]

Validation gate:

```bash
.venv/bin/python -m smb3_agent lab note latest \
  "1-1 around 320 timer: falls into the hole and usually gets lucky"
```

Pass condition:

- Latest session receives a note.
- The note file validates.
- Raw note text is preserved exactly.

### Step 6.3: Session review

Implementation:

- Add `lab review latest`. [implemented]
- Join notes, route log events, state trace, and screenshots when available. [implemented for route logs and notes]
- Produce a review artifact with:
  - linked notes
  - nearest trace evidence
  - failure or hardening classification
  - hypothesis
  - recommended experiment

Validation gate:

```bash
.venv/bin/python -m smb3_agent lab review latest
```

Pass condition:

- Review references the session manifest and note ids.
- Review does not invent facts not present in artifacts.
- Review recommends one concrete route experiment or explains why it cannot.

### Step 6.4: Variant proposal

Implementation:

- Add a route variant model using `data/lab/variant-proposal-template.yaml` as
  the initial contract. [implemented]
- Add `lab propose-variant latest`. [implemented]
- Generate a proposed variant from the review without modifying the baseline. [implemented]
- Include parent variant, source session, source notes, intended files, and
  validation command.

Validation gate:

```bash
.venv/bin/python -m smb3_agent lab propose-variant latest
```

Pass condition:

- A variant proposal file is written.
- Parent route and source note ids are recorded.
- Baseline files are unchanged.

### Step 6.5: Variant validation and promotion

Implementation:

- Add `lab run-variant`. [implemented]
- Add `lab compare-variant`. [implemented]
- Add `lab promote-variant`. [implemented]
- Promotion must backup the previous baseline metadata and record the validation
  artifact that justified promotion.

Validation gate:

```bash
export SMB3_GAME_FILE=/path/to/local-game-file
.venv/bin/python -m smb3_agent lab run-variant world_1_1_harden_hole_320_a --attempts 10
.venv/bin/python -m smb3_agent lab compare-variant world_1_1_harden_hole_320_a
```

Pass condition:

- Variant run writes a normal session artifact.
- Comparison reports success rate, failure classes, and changed files.
- Promotion is blocked unless the configured gate passes.

### Step 6.6: Issue ledger

Implementation:

- Add an issue ledger model using `data/lab/issue-ledger-template.yaml` as the
  initial contract. [implemented]
- Add `lab issues latest`. [implemented]
- Group notes by segment and problem type. [implemented]
- Support issue types:
  - `route_hardening`
  - `input_timing`
  - `recovery_bug`
  - `wrong_route_state`
  - `expected_behavior`
  - `positive_evidence`
  - `unknown`
- Mark expected behavior and positive evidence as non-actionable. [implemented]
- Prioritize high-impact recovery bugs over lower-risk hardening notes. [implemented]

Validation gate:

```bash
.venv/bin/python -m smb3_agent lab issues latest
```

Pass condition:

- Every note is represented in one issue.
- Notes from different segments produce distinct issues.
- Expected behavior and positive evidence do not create route patch proposals.
- The fortress carry-over/death issue is prioritized above a minor 1-1 hardening
  issue.

### Step 6.7: Multi-proposal generation

Implementation:

- Add `lab propose-variants latest`. [implemented]
- Generate one proposal per actionable issue. [implemented]
- Include source issue id, source notes, priority, relevant files, and validation
  command. [implemented]
- Keep the existing `lab propose-variant latest` as a compatibility shortcut for
  the highest-priority actionable issue.

Validation gate:

```bash
.venv/bin/python -m smb3_agent lab propose-variants latest
```

Pass condition:

- One proposal is produced for each actionable issue.
- Non-actionable evidence issues are skipped.
- Proposals are independent and can be validated separately.

### Step 6.8: Backend summary artifact

Implementation:

- Add `lab ui-summary latest`. [implemented]
- Produce a compact JSON/YAML file for compatibility and debugging.
  [implemented]
- Include route segments, note counts, issue counts, highest priority issue,
  proposal count, validation status, and artifact links.

Validation gate:

```bash
.venv/bin/python -m smb3_agent lab ui-summary latest
```

Pass condition:

- Output can summarize backend route state without parsing raw logs.
- Each backend route entry shows notes, issues, and proposal state.
- The latest session can be reopened from the summary.

### Step 6.9: Codex task packet

Implementation:

- Add `lab codex-task latest --issue ISSUE_ID`. [implemented]
- Use `data/lab/codex-task-template.yaml` as the initial contract.
- Include session manifest, notes, issue ledger, selected issue, relevant log
  excerpts, segment catalog, relevant route files, and validation command.
- Codex task packets should request a patch proposal and validation plan; the
  lab still owns applying, validating, comparing, and promoting. [implemented]

Validation gate:

```bash
.venv/bin/python -m smb3_agent lab codex-task latest --issue ISSUE_ID
```

Pass condition:

- Task packet includes enough context for Codex CLI to work without chat
  history.
- Packet names the selected issue and excludes unrelated notes unless needed for
  context.
- Packet includes the expected validation command.

## Phase 7: Mario Route Lab

Goal: replace repetitive CLI note entry with an evidence-first Mario Route Lab
over the same session, note, issue, review, and variant artifacts.

Current status:

- Phase 7 is implemented as a standard-library local web UI named Mario Route
  Lab.
- The UI is served by `python -m smb3_agent lab ui`.
- The UI can also be rendered once with `python -m smb3_agent lab ui-render`.
- The UI reads/writes the same session, note, issue, proposal, and Codex-task
  artifacts as the CLI.
- The UI uses the World 1 location model in
  `data/worlds/world_1_locations.yaml`.
- The visible workflow is Route, Evidence, Teach This Section, Things Mario
  Still Gets Wrong, and Recent Observations.

### Step 7.1: Player-facing location model

Implementation:

- Add a World 1 location model with player-facing labels and objectives.
  [implemented]
- Render locations such as Map, 1-1, 1-3, Fortress, Airship, and King as the
  primary UI vocabulary. [implemented]
- Keep backend route/script identifiers out of the normal UI labels.
  [implemented]

Validation gate:

```bash
python -m smb3_agent lab ui-render --output artifacts/ui/latest.html
```

Pass condition:

- HTML contains Mario Route Lab, Route, Evidence, and Teach This Section.
- HTML contains player-facing World 1 locations.
- HTML does not depend on old route-map labels for the primary workflow.

### Step 7.2: Teaching panel

Implementation:

- Let the user add teaching notes across multiple locations. [implemented]
- Expose note labels for failure, expected behavior, route instruction,
  validation note, and positive evidence while writing the existing underlying
  note severities. [implemented]
- Submit all notes to the same latest session. [implemented]
- Run issue grouping after submission. [implemented]

Validation gate:

```bash
python -m smb3_agent lab ui --host 127.0.0.1 --port 8765
```

Pass condition:

- A batch note submission creates grouped issues without requiring one command
  per location.
- The UI refreshes issue and proposal artifacts after note submission.

### Step 7.3: Run and validation controls

Implementation:

- Add a speed selector for 1x through 100x. [implemented]
- Add attempts and mode selectors. [implemented]
- Add Run World 1, Unit Tests, Phase Gate, and Render Check controls.
  [implemented]
- Record the last command result in `artifacts/ui/last_command.yaml`.
  [implemented]

Validation gate:

```bash
python -m smb3_agent lab ui-render --output artifacts/ui/latest.html
```

Pass condition:

- The UI exposes run speed, attempt count, run mode, unit-test, phase-gate, and
  render-check controls.
- The phase gate uses the same Python interpreter that launched the UI.

### Step 7.4: Codex task buttons

Implementation:

- Show actionable issues in the UI. [implemented]
- Add a Codex task button for actionable issues. [implemented]
- Reuse `lab codex-task latest --issue ISSUE_ID`. [implemented]

Validation gate:

```bash
python -m smb3_agent lab codex-task latest --issue ISSUE_ID
```

Pass condition:

- UI-created Codex task packets use the same schema as CLI-created packets.

## Phase 8: Research Unknown Routes

Goal: handle World 8 and other less-known route sections through the attempt lab
instead of one-off scripting.

### Step 8.1: Route research notes

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
- Each planned segment has a proposed first attempt-lab session command.

### Step 8.2: First World 8 segment proof

Implementation:

- Start from a known World 8 state.
- Build the first segment as a small run with logs and screenshots.
- Use attempt-lab notes and variants for each correction.

Validation gate:

```bash
python -m smb3_agent goal run world_8_first_segment --attempts 5
```

Pass condition:

- At least one successful run or a classified blocker with artifacts.
- Any user observations are captured as notes instead of remaining only in chat.

## Phase 9: Generalize Beyond SMB3

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
