# SMB3 Route Agent

Local proof-of-concept for a user-steered game agent. The active product goal is
`world_8_double_whistle`:

> From a fresh game, collect both World 1 Warp Whistles, clear the required
> World 1 path, arrive safely on the World 2 map with both whistles, use the
> first whistle from World 2, use the second while still in the Warp Zone, and
> arrive on the genuine World 8 map.

World 8 arrival is the boundary. Playing or beating World 8 is outside the
current goal.

## Current truth

- The active contract and catalog are
  `data/goals/world_8_double_whistle.yaml` and
  `data/segments/world_8_double_whistle.yaml`.
- World 1-4 is not in the active route.
- World 1-5 and World 1-6 are retained as the route to the final World 1
  castle after the owner corrected the boundary to require World 2 before
  whistle use.
- The Airship/King transition is a required intermediate boundary, not success.
- The first whistle must be used from the World 2 map. The second must be used
  from the Warp Zone before a numbered-world pipe is entered.
- Only `post_probe_world_8_map_arrival` can satisfy the active goal. The legacy
  king marker cannot.
- The active runner is intentionally `planned`: safe World 2 arrival with both
  whistles and the later Warp Zone transitions are not yet executable as a
  validated end-to-end route.
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

## Active-goal commands

```bash
python -m pytest -q
python -m smb3_agent goal validate data/goals/world_8_double_whistle.yaml
python -m smb3_agent segment validate \
  data/segments/world_8_double_whistle.yaml \
  --goal world_8_double_whistle
python -m smb3_agent goal status world_8_double_whistle
python -m smb3_agent command parse \
  "run world 8 double whistle arrival 3 times"
```

Attempting to run the active goal fails clearly as not yet executable; it never
falls back to the king diagnostic.

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

## Project docs

- [Product direction](docs/product-direction.md)
- [Goal contract](docs/goal-contract.md)
- [Agent architecture](docs/agent-architecture.md)
- [Implementation plan](docs/implementation-plan.md)
- [Validation gates](docs/validation-gates.md)
- [Route status](docs/route-status.md)
- [Mario Route Lab](docs/mario-route-lab.md)
- [FCEUX harness](docs/fceux-harness.md)

## Working rule

Every implementation step ends with a validation gate. Contract tests do not
stand in for live game evidence; assisted topology checks do not stand in for a
safe, repeatable gameplay route.
