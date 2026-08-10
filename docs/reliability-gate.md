# World 8 Reliability Gate

Rank 27 proves repeatable arrival at the accepted World 8 map boundary. It does
not enter or play World 8.

## Authoritative command

From the repository root:

```bash
export SMB3_GAME_FILE=/path/to/local-game-file.nes
.venv/bin/python -m smb3_agent reliability run
```

Five runs are requested by default. Each run is structurally independent: the
orchestrator creates an isolated directory, records a single-attempt invocation,
and calls the existing `world_8_double_whistle` goal runner once. That call
launches a new FCEUX process from power-on. It cannot reuse an emulator process,
savestate, retry checkpoint, route bridge, mutation, discovery search, or the
legacy diagnostic route. Inherited `SMB3_*` route tuning is removed.

Passing requires all of the following:

- at least five runs were requested and every requested run completed;
- every run's structured log is present, valid, and parseable;
- the 15 `acceptance_event` values in the active segment catalog appear in the
  active contract's order;
- `metrics_passed=true` for every run;
- the final event is `post_probe_world_8_map_arrival` for every run;
- the accepted endpoint is observed as `world_number=7`, `object_set=0`;
- no prohibited event or local state artifact is detected;
- every FCEUX process exits successfully before its timeout.

Byte-identical SHA-256 log hashes are reported but are not required. Observable
contract success is authoritative.

## Watchable command

```bash
.venv/bin/python -m smb3_agent reliability watch
```

This command runs the same product goal once from a fresh game with the
documented 0.0035-second frame throttle. It captures review images and ticks,
extracts `state_tick_trace.log`, converts screenshots to PNG, and creates
`review/contact_sheet.png`. Its report always says:

```text
validation_policy=review_only
promotable=false
counts_toward_reliability=false
```

It writes beneath `artifacts/review/`, never under a reliability batch, and
cannot count toward the five authoritative runs. Capture and throttle overhead
may change route behavior.

## Artifact layout

An authoritative batch uses:

```text
artifacts/reliability/world_8_double_whistle/<timestamp>_reliability/
  reliability_report.json
  run_01/
    invocation.json
    fceux_execution.json
    fceux_1_1.log
    fceux_stdout.log
    fceux_stderr.log
    run_report.json
  run_02/ ... run_05/
```

A watchable review uses:

```text
artifacts/review/world_8_double_whistle/<timestamp>_watchable/
  invocation.json
  fceux_execution.json
  fceux_1_1.log
  fceux_stdout.log
  fceux_stderr.log
  state_tick_trace.log
  images/*.gd
  review/png/*.png
  review/contact_sheet.png
  run_report.json
  watchable_report.json
```

Each aggregate records goal and route-catalog hashes, source commit and dirty
state, start/finish/elapsed time, run count, artifact paths, contract metrics,
final events, structured-log SHA-256 values, success rate, and overall result.

## Failure behavior

Runs fail closed and retain all artifacts created before the failure. Reports
distinguish:

- `preflight`: local prerequisite or product-contract invariant failed;
- `emulator-launch`: FCEUX could not launch or exited abnormally;
- `timeout`: the fresh process exceeded its bounded runtime;
- `artifact-integrity`: execution metadata or the route log is missing, corrupt,
  empty, or unparseable;
- `prohibited-tactic`: bridge, mutation, savestate/search, or prohibited local
  state evidence appeared;
- `observer/contract`: the ordered contract or observer metrics did not pass;
- `gameplay`: an explicit bad-state, missing-state, life-loss, or gameplay
  failure marker appeared.

Every run report includes the last accepted product event and segment, the first
missing milestone, the first violated event when available, the final observable
map/mode/object set/inventory/lives/form, capture and throttle settings, and a
bounded recommended investigation. Unknown or ambiguous evidence is never a
pass.
