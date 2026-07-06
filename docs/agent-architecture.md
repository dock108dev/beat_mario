# Agent Architecture

The target system is a live game-agent workbench, not a pile of one-off route
scripts. The current FCEUX runner is the first emulator adapter and execution
backend.

## Components

```text
User Directive
  -> Goal Contract
  -> Route Planner
  -> Segment Runner
  -> Emulator Adapter
  -> State Observer
  -> Recovery Manager
  -> Attempt Logger
  -> Note Collector
  -> Reviewer
  -> Variant Manager
  -> Knowledge Store
```

## Goal Contract

The contract defines what the agent is trying to do and what tradeoffs are
allowed. It should be machine-readable and reviewable by a human.

Responsibilities:

- Store the user's directive.
- Define objective, constraints, and success metrics.
- Define allowed tactics, such as real gameplay only, assisted transition, or
  known-state bridge.
- Define recovery policy for life loss, wrong state, timeout, and unknown state.

## Route Planner

The planner maps a goal contract to route segments.

For SMB3, a route is a sequence such as:

```text
fresh_start
-> world_1_1
-> world_1_2
-> world_1_3_whistle
-> world_1_fortress_whistle
-> remaining_world_1_path
-> airship_or_king_transition
```

The planner should be conservative. It should prefer known segment gates over
inventing broad behavior.

## Segment Runner

The runner executes one segment at a time.

Each segment needs:

- Start condition.
- Success condition.
- Failure conditions.
- Input strategy.
- State observations.
- Retry/recovery policy.
- Evidence artifacts.

The current Lua route runner already has several implicit segments. The next
step is to promote those into an explicit segment catalog.

## Emulator Adapter

The adapter hides emulator-specific details.

Current adapter:

- FCEUX Lua script for memory-aware state reads and controller writes.
- Python harness for launching, logging, parsing, and screenshot conversion.

Future adapters can target different emulators or games as long as they provide:

- `observe_state`
- `send_input`
- `save_checkpoint`
- `load_checkpoint`
- `reset`
- `capture_artifacts`

## State Observer

The observer turns raw emulator state into game facts.

Examples:

- Current mode: map, level, transition, death, inventory, special scene.
- Mario position, form, movement state, and lives.
- Map cursor position and world progress.
- Inventory state.
- Segment progress markers.

The observer must be able to detect "we died and returned to map" as different
from "we cleared the level and returned to map."

## Recovery Manager

Recovery is the difference between a scripted bot and a useful agent.

Initial recovery cases:

- Life lost inside a segment: log death, decide whether to continue from next
  life or reset the segment.
- Wrong map node: run map-position correction only if the route contract allows
  bridge steps.
- Timeout or stuck state: capture screenshots and stop the segment.
- Known transition bug: apply an explicit bridge and label the artifact as
  bridged.

The manager should never hide a bridge or recovery decision. It should log the
mode used.

## Reviewer

The reviewer explains failed attempts and recommends the next experiment.

Minimum output:

```text
segment: world_1_4
result: failed
classification: input_timing
evidence: last progress marker was x=639, then bad_state
likely cause: lost form or speed before the moving-platform gap
next experiment: reduce throttle/capture overhead or adjust the gap trigger
```

LLM review is useful here, but the facts must come from logs and artifacts.

## Note Collector

The note collector preserves user observations as artifacts attached to a
specific attempt session.

Examples:

- "1-1 around 320 timer: falls into the hole and usually gets lucky."
- "Castle flight starts too far right, then hits the ceiling blocks."
- "This run is watchable-speed only; do not promote from it."

Notes should preserve the raw user text and optional anchors such as segment,
attempt number, frame, event, screenshot, wall-clock time, or in-game timer.
Machine interpretation belongs in the review, not in the raw note.

## Variant Manager

The variant manager protects the known-working route while experiments happen.

Responsibilities:

- Create proposed variants from reviews.
- Record parent variant, source session, source notes, and intended changes.
- Run validation gates against a variant.
- Compare variant results with parent results.
- Promote only when the configured gate passes.
- Preserve enough metadata to roll back a bad promotion.

## Knowledge Store

Durable knowledge should be explicit, not buried in chat history.

Examples:

- "World 1-3 whistle requires the white-block crouch route."
- "The fortress whistle route requires flight; current implementation uses a
  bridge."
- "Visible demo throttle can change timing and should not be treated as a
  reliability gate."
- "World 1-4 is currently flaky under watchable capture mode."

This can start as YAML/Markdown and later move into structured storage.
