# Attempt Lab

The attempt lab is the next layer of the project. It turns route execution into
an evidence-backed iteration loop:

```text
run route
-> capture artifacts
-> add human notes
-> group notes into route issues
-> review evidence by issue
-> propose route variants
-> validate variant
-> promote, keep, or discard
```

This comes before broader route expansion. The project already proved that
explicit control plus user guidance can clear and bridge sections. The next
problem is making every correction durable, reviewable, and repeatable.

## Goals

- Run any supported goal or segment at a chosen review speed.
- Capture enough evidence to explain what happened without relying on memory.
- Attach human notes during or after an attempt.
- Anchor notes to segment, wall-clock time, frame, state snapshot, or in-game
  timer when available.
- Review batches of notes and traces together.
- Group notes into durable issues by segment, severity, and type.
- Generate route variant proposals per actionable issue instead of overwriting
  known-working routes.
- Validate variants against explicit gates before promotion.
- Produce UI-ready session, note, issue, review, and proposal files.
- Produce Codex-ready task packets for patch/review work.

## Non-Goals

- Do not add a real-time LLM controller yet.
- Do not silently mutate baseline routes.
- Do not treat watchable-speed runs as reliability gates.
- Do not expand to World 8 until the attempt lab can preserve notes, grouped
  issues, variants, and review output.

## Attempt Session

An attempt session is the top-level artifact for a run or batch of runs.

Minimum fields:

```yaml
session_id: 20260706T230000Z_world_1_king
goal_id: world_1_king
route_variant: world_1_baseline
run_mode: gate
requested_speed: 4
attempts_requested: 3
started_at: 2026-07-06T23:00:00Z
artifacts_dir: artifacts/sessions/20260706T230000Z_world_1_king
inputs:
  command: show me the route at 4x
  game_file_env: SMB3_GAME_FILE
outputs:
  route_log: fceux_1_1.log
  state_trace: state_trace.jsonl
  screenshots_dir: images
  notes_file: notes.yaml
  review_file: review.md
  variant_proposal: variant_proposal.yaml
```

The session artifact should make it possible to answer:

- What did the user ask for?
- Which route variant was used?
- What speed and capture settings were active?
- Where did the run succeed or fail?
- Which notes were attached?
- Which route issues were created?
- Which route changes were proposed?
- Which proposals were validated?

## Speed Policy

The CLI should accept speeds from `1x` to `100x`, but the semantics must be
clear:

- `1x`: watchable, useful for human observation.
- `2x` to `10x`: review speed, useful for quick inspection.
- `maximum` or high multiplier: reliability speed, useful for gates.

The artifact must record:

- requested speed
- emulator speed mode or frame sleep used
- screenshot capture on/off
- tick capture on/off
- real elapsed time
- frame count
- in-game timer values when available

Watchable speed can change timing. A route can be easier or harder under
capture and throttle settings, so promotion gates should use the configured
reliability mode unless a specific watchable-mode gate is being tested.

## Human Notes

Human notes are first-class artifacts, not chat leftovers.

Example:

```yaml
notes:
  - id: note_001
    created_at: 2026-07-06T23:04:12Z
    author: user
    segment_id: world_1_1
    anchor:
      type: in_game_timer
      value: 320
    severity: harden
    text: Mario falls into the hole around 320 remaining and usually survives by luck.
    expected_change: Add a safer jump or slowdown before this hole.
```

Supported anchors should start simple:

- `segment_id`
- `attempt_number`
- `frame`
- `event`
- `wall_clock_seconds`
- `in_game_timer`
- `screenshot`

The review step should preserve raw text and add machine interpretation in a
separate field. It should never rewrite the user's note as if the interpretation
were the original observation.

## Issue Ledger

The issue ledger is the missing layer between raw notes and route proposals.
Multiple notes from one run should be grouped without forcing the user to process
one segment at a time.

Example:

```yaml
issues:
  - id: issue_world_1_1_001
    session_id: 20260706T230000Z_world_1_king
    segment_id: world_1_1
    type: route_hardening
    priority: medium
    status: open
    source_notes:
      - note_001
    summary: Mario falls into a hole at 283 on the clock.
    proposed_next_step: Add a safer jump or progress guard near the hazard.
  - id: issue_world_1_3_001
    session_id: 20260706T230000Z_world_1_king
    segment_id: world_1_3
    type: expected_behavior
    priority: none
    status: accepted
    source_notes:
      - note_002
    summary: Leaving 1-3 through the whistle path is expected.
    proposed_next_step: Do not treat this as a failed course clear.
  - id: issue_world_1_fortress_001
    session_id: 20260706T230000Z_world_1_king
    segment_id: world_1_fortress
    type: recovery_bug
    priority: high
    status: open
    source_notes:
      - note_003
    summary: Fortress death appears to leak inputs and sends the route toward 1-4.
    proposed_next_step: Add input cleanup and post-death map-state recovery.
```

Supported issue types:

- `route_hardening`
- `input_timing`
- `recovery_bug`
- `wrong_route_state`
- `expected_behavior`
- `positive_evidence`
- `unknown`

The reviewer should produce one issue per distinct location/problem. Positive
evidence and expected behavior are useful, but they should not create route
patch proposals.

## Review Output

Review output should combine logs, state trace, screenshots, notes, and issue
ledger entries.

Minimum review fields:

```yaml
review_id: review_001
session_id: 20260706T230000Z_world_1_king
result: issues_identified
primary_issue: issue_world_1_fortress_001
primary_location: world_1_fortress
issue_count: 3
actionable_issue_count: 2
evidence:
  - note_001
  - event: attempt_1_progress
  - frame: 1820
classification: recovery_bug
hypothesis: Fortress death cleanup is leaking input into map navigation.
recommended_experiment: Add input release/reset and map-state reclassification after fortress death.
confidence: medium
```

The reviewer may use Codex for synthesis, but the facts must come from artifacts.

## Variant Lifecycle

Route edits should happen through variants:

```text
baseline
-> proposed variant
-> validation candidate
-> promoted baseline or archived experiment
```

Rules:

- Baseline route files are not edited directly by review automation.
- A proposed variant records its parent route, source issue, source notes, and
  reason.
- Every actionable issue can produce zero or one proposed variant.
- Every variant has a validation command.
- Promotion requires a passing gate.
- Failed variants stay available for comparison unless explicitly cleaned.

Example:

```yaml
variant_id: world_1_1_harden_hole_320_a
parent_variant: world_1_baseline
status: proposed
reason: Harden user-noted hole risk around timer 320.
source_notes:
  - note_001
source_issue: issue_world_1_1_001
changes:
  - file: data/routes/scripts/world_1_1_clear_v0.yaml
    summary: Adjust jump before hole and add verification marker.
validation:
  command: python -m smb3_agent lab validate-variant world_1_1_harden_hole_320_a --attempts 10
  promotion_gate: 10/10 for world_1_1, no regression in world_1_king smoke
```

## UI Contract

The next UI should not parse route logs directly. It should read and write the
same structured files the CLI uses.

First UI shape:

```text
World 1 control panel
-> choose speed and run mode
-> run or validate
-> select player-facing location
-> add note
-> mark note as note, harden, bug, objective, map action, or guide detail
-> submit note batch
-> review grouped issues
-> choose proposals to validate
```

Minimum UI data endpoints/files:

- latest session manifest
- World 1 location model
- notes file
- issue ledger
- review summary
- variant proposals
- validation result summaries

The CLI remains the source of truth until the UI exists. The UI is a front end
over session, note, issue, review, and variant artifacts.

## Codex Task Packets

Codex should be used as a patch/review engineer, not as a hidden live controller.
The lab should generate a task packet with enough evidence for Codex CLI to make
or review a route change.

Packet contents:

- user objective
- session manifest
- notes
- issue ledger
- selected issue
- nearby route-log excerpts
- current segment catalog
- relevant route source files
- requested validation command
- expected output format

Planned command:

```bash
python -m smb3_agent lab codex-task latest --issue ISSUE_ID
```

The packet should ask for a concrete patch proposal and validation plan. The lab
should still own applying, validating, comparing, and promoting changes.

## Commands To Build

These are the intended commands for the next implementation phase.

```bash
python -m smb3_agent lab start "show me the route at 4x" --attempts 1
python -m smb3_agent lab note latest "1-1 around 320 timer: falls into the hole and usually gets lucky"
python -m smb3_agent lab review latest
python -m smb3_agent lab issues latest
python -m smb3_agent lab propose-variants latest
python -m smb3_agent lab codex-task latest --issue ISSUE_ID
python -m smb3_agent lab run-variant world_1_1_harden_hole_320_a --attempts 10
python -m smb3_agent lab promote-variant world_1_1_harden_hole_320_a
```

The implemented lab pass supports sessions, notes, issue ledgers, one review
artifact, single or multi-proposal creation, UI-ready summaries, Codex task
packets, variant validation, and guarded promotion.

## Phase 6 Build Order

1. Session manifest model and artifact directory layout.
2. Note model and `lab note latest`.
3. Speed-aware run wrapper that records exact run settings.
4. Review command that joins notes with route logs.
5. Variant proposal scaffold.
6. Variant validation command.
7. Promotion command with backup and rollback metadata.
8. Issue ledger grouped by segment and problem type.
9. Multi-proposal generation from actionable issues.
10. UI-ready session/control-panel summary.
11. Codex task packet generation for selected issues.

## Validation Philosophy

The initial lab implementation was enough when the user could make a note such
as:

```text
1-1 around 320 timer: falls into the hole and usually gets lucky
```

and the system can:

1. Attach the note to the latest attempt.
2. Find nearby trace evidence.
3. Recommend a route hardening experiment.
4. Save a proposed variant.
5. Run that variant against a gate.
6. Compare the result to the parent route.

The next lab milestone is done when the user can submit a batch such as:

```text
1-1 falls into hole at 283 on clock.
1-2 and 1-3 are perfect. 1-3 whistle exit is expected.
Castle dies first try, then carry-over inputs seem to send the route to 1-4.
```

and the system can:

1. Preserve every note.
2. Group notes into segment issues.
3. Mark positive/expected notes as non-actionable evidence.
4. Prioritize the fortress recovery issue above the 1-1 hardening issue.
5. Generate separate route proposals for each actionable issue.
6. Generate a Codex task packet for the selected proposal.
