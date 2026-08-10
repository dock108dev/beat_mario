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
- Fresh accepted playback now clears the real Airship/King route, waits for
  Mario to settle in World 2 with both whistles, uses the first whistle there,
  uses the second from the 5/6/7 Warp Zone tier, and arrives on the genuine
  World 8 map.
- The first whistle must be used from the World 2 map. The second must be used
  from the Warp Zone before a numbered-world pipe is entered.
- Only `post_probe_world_8_map_arrival` can satisfy the active goal. The legacy
  king marker cannot.
- The active product runner is executable and passed three fresh, byte-identical,
  no-bridge playbacks plus an independent `goal run` validation.
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

The active goal runs the product route directly and never falls back to the
king diagnostic.

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
