# Attempt Lab

The attempt lab is the next layer of the project. It turns route execution into
an evidence-backed iteration loop:

```text
run route
-> capture artifacts
-> add human notes
-> review evidence
-> propose route variant
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
- Review notes and traces together.
- Generate route variant proposals instead of overwriting known-working routes.
- Validate variants against explicit gates before promotion.

## Non-Goals

- Do not add a real-time LLM controller yet.
- Do not silently mutate baseline routes.
- Do not treat watchable-speed runs as reliability gates.
- Do not expand to World 8 until the attempt lab can preserve notes, variants,
  and review output.

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
- What route change was proposed?
- Was that change validated?

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

## Review Output

Review output should combine logs, state trace, screenshots, and notes.

Minimum review fields:

```yaml
review_id: review_001
session_id: 20260706T230000Z_world_1_king
result: needs_route_hardening
primary_segment: world_1_1
evidence:
  - note_001
  - event: attempt_1_progress
  - frame: 1820
classification: input_timing
hypothesis: Jump timing before the hole is too optimistic.
recommended_experiment: Add a route variant with an earlier jump trigger.
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
- A proposed variant records its parent route and reason.
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
changes:
  - file: data/routes/scripts/world_1_1_clear_v0.yaml
    summary: Adjust jump before hole and add verification marker.
validation:
  command: python -m smb3_agent lab validate-variant world_1_1_harden_hole_320_a --attempts 10
  promotion_gate: 10/10 for world_1_1, no regression in world_1_king smoke
```

## Initial Commands To Build

These are the intended commands for the next implementation phase.

```bash
python -m smb3_agent lab start "show me the route at 4x" --attempts 1
python -m smb3_agent lab note latest "1-1 around 320 timer: falls into the hole and usually gets lucky"
python -m smb3_agent lab review latest
python -m smb3_agent lab propose-variant latest
python -m smb3_agent lab run-variant world_1_1_harden_hole_320_a --attempts 10
python -m smb3_agent lab promote-variant world_1_1_harden_hole_320_a
```

The first implementation does not need to support every command. It should build
the session and note model first, then add variant proposals, then controlled
promotion.

## Phase 6 Build Order

1. Session manifest model and artifact directory layout.
2. Note model and `lab note latest`.
3. Speed-aware run wrapper that records exact run settings.
4. Review command that joins notes with route logs.
5. Variant proposal scaffold.
6. Variant validation command.
7. Promotion command with backup and rollback metadata.

## Validation Philosophy

The lab is done when the user can make a note such as:

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
