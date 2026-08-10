# SMB3 Route Agent

Local proof-of-concept for a user-steered game agent. The default product goal
remains `world_8_double_whistle`:

> From a fresh game, collect both World 1 Warp Whistles, clear the required
> World 1 path, arrive safely on the World 2 map with both whistles, use the
> first whistle from World 2, use the second while still in the Warp Zone, and
> arrive on the genuine World 8 map.

World 8 arrival remains that goal's boundary. Rank 28 adds a separate
`world_8_big_tanks` product goal: it reuses the accepted 15-segment prefix,
clears the first reachable World 8 stage (Big Tanks), observes the normal map
return, and stops before another stage. The cumulative `world_8_battleships`
goal reuses that accepted 16-segment route, clears Battleships, and stops on the
stable map before a Hand Trap.

## Current truth

- The default contract remains `data/goals/world_8_double_whistle.yaml`; it is
  still 15 segments and still stops at the World 8 map.
- `data/goals/world_8_big_tanks.yaml` is a distinct product contract. It
  composes the accepted default prefix with one catalog-owned segment,
  `world_8_big_tanks_clear`, for 16 ordered acceptance events.
- `data/goals/world_8_battleships.yaml` composes `world_8_big_tanks` with only
  `world_8_battleships_clear`, for 17 ordered events and zero bridges. The 15-
  and 16-segment goals remain unchanged.
- World 1-4 is not in the active route.
- World 1-5 and World 1-6 are retained as the route to the final World 1
  castle after the owner corrected the boundary to require World 2 before
  whistle use.
- The Airship/King transition is a required intermediate boundary, not success.
- Fresh accepted playback now clears the real Airship/King route, waits for
  Mario to settle in World 2 with both whistles, uses the first whistle there,
  uses the second from the 5/6/7 Warp Zone tier, and arrives on the genuine
  World 8 map.
- The first whistle must be used from the World 2 map. The second must be used
  from the Warp Zone before a numbered-world pipe is entered.
- Only `post_probe_world_8_map_arrival` can satisfy the default goal. The Big
  Tanks goal instead requires ordered entry, gameplay, boss defeat,
  chest/clear, and stable post-clear map evidence. Neither a king marker, map
  arrival alone, nor enemy disappearance can satisfy it.
- The default product runner is executable. Rank 27 passed the structural
  reliability gate with five fresh, byte-identical, no-bridge processes plus a
  separate successful review-only watchable playback and contact sheet.
- The Rank 28 runner is also executable. It passed three fresh, byte-identical,
  no-bridge processes with five authoritative screenshots per run and a
  separate watchable review.
- The Battleships runner passed three fresh, byte-identical, no-bridge
  processes with five authoritative screenshots per run. Its separate
  review-only playback passed at a validated `0.0001`-second throttle.
- Rank 33 completes the reviewed route-patch loop. CLI and Mario Route Lab use
  one hash-bound patch contract, detached candidate worktrees, internal
  validation profiles, exact atomic promotion, and conflict-safe rollback.
  No production route content was changed to prove the workflow.
- `world_1_king` remains available only as a legacy diagnostic route. It uses
  explicit bridges and is not product progress.

Generated logs, screenshots, emulator state, and the local game asset remain
ignored under `artifacts/` or other ignored local paths.

## Setup

```bash
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

FCEUX must be available on `PATH` for live diagnostics. ROM-free validation
does not require it.

## ROM-free validation and hosted CI

Run the same canonical gate used by GitHub Actions from the repository root:

```bash
PYTHON=.venv/bin/python scripts/validate_phase0.sh
```

The `.github/workflows/rom-free-ci.yml` workflow runs this gate on the Unix
hosted runner `ubuntu-latest` for pull requests, pushes to `main`, and manual
dispatches. It installs Python 3.11 development dependencies and proves tracked
file hygiene, Bash syntax, Ruff linting, the complete ROM-free pytest suite,
the active goal contract, the active segment catalog, deterministic goal
status, and the Mario Route Lab render contract.

Hosted CI does not prove live gameplay. The Quartz/ApplicationServices Mednafen
adapter and its input/capture dependencies are macOS-only and are imported only
when a matching Mednafen command runs. FCEUX execution, the local game file,
savestates, screenshots, and live route evidence remain separate local-only
proof. The hosted Route Lab smoke check writes HTML to a temporary directory,
asserts its semantic content, and removes it without tracking or uploading it.

## Goal commands

```bash
python -m pytest -q
python -m smb3_agent goal validate data/goals/world_8_double_whistle.yaml
python -m smb3_agent segment validate \
  data/segments/world_8_double_whistle.yaml \
  --goal world_8_double_whistle
python -m smb3_agent goal status world_8_double_whistle
python -m smb3_agent goal validate data/goals/world_8_big_tanks.yaml
python -m smb3_agent goal status world_8_big_tanks
python -m smb3_agent goal validate data/goals/world_8_battleships.yaml
python -m smb3_agent goal status world_8_battleships
python -m smb3_agent command parse \
  "run world 8 double whistle arrival 3 times"
```

All three goals run product routes directly and never fall back to the king
diagnostic. Omitting `--goal` from reliability commands preserves the Rank 27
default.

## Rank 27 reliability and watchable review

Set the local game path once, then run the authoritative gate:

```bash
export SMB3_GAME_FILE=/path/to/local-game-file.nes
.venv/bin/python -m smb3_agent reliability run
```

The command launches five separate FCEUX processes. Every process receives one
attempt, starts from power-on, writes to its own directory, and uses a sanitized
product environment with no throttle, savestate, retry checkpoint, bridge,
mutation, discovery search, or diagnostic fallback. The aggregate passes only
when at least five requested runs all report `metrics_passed=true`, complete all
15 catalog-owned acceptance events in order, and end at
`post_probe_world_8_map_arrival` with `world_number=7`, `object_set=0`.

Run the separate review-only playback with:

```bash
.venv/bin/python -m smb3_agent reliability watch
```

Watchable playback uses the documented `0.0035`-second frame throttle, captures
review images and ticks, and creates a contact sheet. It is always labeled
`review_only`, writes under `artifacts/review/`, and never counts toward the
five-run reliability result. Reliability evidence writes under
`artifacts/reliability/`. See [Reliability gate](docs/reliability-gate.md) for
the artifact layout, failure classifications, and exact pass rules.

## Rank 28 Big Tanks proof

Run the separate three-run gate:

```bash
.venv/bin/python -m smb3_agent reliability run \
  --goal world_8_big_tanks \
  --game-file "$SMB3_GAME_FILE"
```

Every run must complete the accepted 15-step prefix, enter Big Tanks by normal
map input, show genuine stage gameplay, defeat the chamber boss while Mario is
alive, collect the chest reward that triggers the course clear, and remain on
the returned World 8 map. Five focused PNGs are required in each run: map,
entry, gameplay, clear, and post-clear. The accepted aggregate is under
`artifacts/reliability/world_8_big_tanks/20260810T190157.201466Z_reliability/`.

The review-only command is:

```bash
.venv/bin/python -m smb3_agent reliability watch \
  --goal world_8_big_tanks \
  --game-file "$SMB3_GAME_FILE" \
  --throttle-seconds 0.0001
```

Its accepted contact sheet and tick trace are under
`artifacts/review/world_8_big_tanks/20260810T212112.984218Z_watchable/`. The
0.0001-second throttle is the validated Rank 28 review setting; the
authoritative gate remains unthrottled.

## World 8-Battleships proof

Run the cumulative 17-segment gate:

```bash
.venv/bin/python -m smb3_agent reliability run \
  --goal world_8_battleships \
  --game-file "$SMB3_GAME_FILE"
```

Every run begins at power-on, completes the accepted 16-segment prefix, consumes
the retained P-Wing through normal inventory input, moves right twice from the
Big Tanks post-clear cursor, and accepts the game's automatic Battleships entry.
The controller traverses the fleet, uses the normal end pipe, defeats Boom Boom,
and requires the game-owned object transition and return-map flag while Mario is
alive. It then stabilizes at cursor `(128,112)` without entering a Hand Trap.
The accepted 3/3 aggregate is under
`artifacts/reliability/world_8_battleships/20260810T225906.177318Z_reliability/`.

The separate review command is:

```bash
.venv/bin/python -m smb3_agent reliability watch \
  --goal world_8_battleships \
  --game-file "$SMB3_GAME_FILE" \
  --throttle-seconds 0.0001
```

Its accepted non-promotable report, tick trace, and five-frame contact sheet are
under
`artifacts/review/world_8_battleships/20260810T224805.096938Z_watchable/`.

## Legacy diagnostic

The explicitly named diagnostic remains useful for World 1 regression work:

```bash
python -m smb3_agent goal validate data/goals/world_1_king.yaml
python -m smb3_agent goal status world_1_king
python -m smb3_agent task fceux-world-1-king \
  --game-file "$SMB3_GAME_FILE" \
  --attempts 1 \
  --artifacts-dir artifacts/fceux/world_1_king_diagnostic
```

A diagnostic king-transition pass is not evidence of World 2 arrival, whistle
preservation, Warp Zone behavior, or World 8 arrival.

## Mario Route Lab

Render deterministic HTML:

```bash
python -m smb3_agent lab ui-render \
  --output artifacts/ui/world_8_double_whistle.html
```

Serve the local UI:

```bash
python -m smb3_agent lab ui --host 127.0.0.1 --port 8765
```

The Route list is ordered from the active goal contract. It shows World 2-first
double-whistle milestones and does not show World 1-4 as required.
Use the goal switcher to review the separate Big Tanks extension without
changing the default route.

## Rank 33 route patches

Reviewed issues and Codex task packets now converge on one executable,
hash-bound `beat-mario.route-patch/v1` artifact. The accepted working tree is
never used as an experiment: the backend previews the exact diff, applies it in
a detached temporary Git worktree, validates code from that candidate, compares
parent and candidate evidence, and promotes only the exact validated diff.

```bash
python -m smb3_agent lab patch import PATCH.yaml
python -m smb3_agent lab patch review PATCH_ID
python -m smb3_agent lab patch preview PATCH_ID
python -m smb3_agent lab patch prepare PATCH_ID
python -m smb3_agent lab patch validate PATCH_ID
python -m smb3_agent lab patch compare PATCH_ID
python -m smb3_agent lab patch promote PATCH_ID --confirm PATCH_ID
python -m smb3_agent lab patch rollback PATCH_ID --confirm PATCH_ID --reason "operator rollback"
```

Promotion and rollback are explicit and atomic. Neither commits, pushes, opens
a pull request, nor changes product route metadata outside the reviewed diff.
See [Route patch schema](docs/route-patch-schema.md).

## Project docs

- [Product direction](docs/product-direction.md)
- [Goal contract](docs/goal-contract.md)
- [Agent architecture](docs/agent-architecture.md)
- [Implementation plan](docs/implementation-plan.md)
- [Validation gates](docs/validation-gates.md)
- [Reliability gate](docs/reliability-gate.md)
- [Route status](docs/route-status.md)
- [Mario Route Lab](docs/mario-route-lab.md)
- [Route patch schema](docs/route-patch-schema.md)
- [FCEUX harness](docs/fceux-harness.md)

## Working rule

Every implementation step ends with a validation gate. Contract tests do not
stand in for live game evidence; assisted topology checks do not stand in for a
safe, repeatable gameplay route.
