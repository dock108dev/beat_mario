# SMB3 Route Agent

Local, evidence-first automation and review tooling for a Super Mario Bros. 3
route. The accepted cumulative route starts from power-on, collects both World
1 Warp Whistles, reaches World 2, uses both whistles, completes World 8, defeats
Bowser, observes the Princess rescue and credits, and stops at the stable final
screen.

The repository contains no game file. ROMs, savestates, screenshots, logs, and
generated evidence remain ignored and local-only.

## Requirements

- Python 3.11 or newer
- [`uv`](https://docs.astral.sh/uv/) for the locked development environment
- FCEUX on `PATH` only for live gameplay or review runs
- macOS only for the optional legacy Mednafen diagnostics

## Setup

From the repository root:

```bash
uv sync --locked --extra dev
```

The equivalent existing-environment installation is:

```bash
.venv/bin/python -m pip install -e '.[dev]'
```

## Validate the repository

Run the same ROM-free gate used by GitHub Actions:

```bash
PYTHON=.venv/bin/python scripts/validate_phase0.sh
```

The gate checks tracked-file hygiene, shell syntax, Ruff, all ROM-free tests,
the default goal and segment contracts, deterministic route status, and a Route
Lab render smoke. It does not run an emulator or prove live gameplay.

Useful focused commands:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m smb3_agent goal validate world_8_finish_game
.venv/bin/python -m smb3_agent goal status world_8_finish_game
.venv/bin/python -m smb3_agent lab ui-render --output /tmp/beat-mario-route-lab.html
```

## Supported flows

The default product goal remains `world_8_double_whistle`. Later goal contracts
compose that accepted prefix without changing it:

| Goal | Accepted boundary | Authoritative runs |
| --- | --- | ---: |
| `world_8_double_whistle` | World 8 map arrival | 5 |
| `world_8_big_tanks` | Big Tanks post-clear map | 3 |
| `world_8_battleships` | Battleships post-clear map | 3 |
| `world_8_hand_traps_jet` | All Hand Traps and Jet post-clear map | 3 |
| `world_8_8_2` | World 8-2 clear and Fortress access | 3 |
| `world_8_super_tanks` | Super Tanks clear and Bowser's Castle access | 3 |
| `world_8_finish_game` | Stable game-owned ending | 3 |

Run an authoritative fresh-process gate with a local game file:

```bash
export SMB3_GAME_FILE=/absolute/path/to/local-game-file.nes
.venv/bin/python -m smb3_agent reliability run --goal world_8_finish_game
```

Run one throttled, review-only playback:

```bash
.venv/bin/python -m smb3_agent reliability watch --goal world_8_finish_game
```

Review playback never counts as authoritative reliability evidence. See
[World 8 reliability gates](docs/reliability-gate.md) for exact pass rules and
artifact layout.

## Mario Route Lab

Route Lab is a loopback-only operator surface for route evidence, notes,
issues, and reviewed route patches:

```bash
.venv/bin/python -m smb3_agent lab ui --host 127.0.0.1 --port 8765
```

It is not designed for network exposure. See [Mario Route Lab](docs/mario-route-lab.md),
[security](docs/security.md), and [error handling](docs/error-handling.md).

Executable route changes use only the normalized route-patch lifecycle:

```bash
.venv/bin/python -m smb3_agent lab patch import PATCH.yaml
.venv/bin/python -m smb3_agent lab patch review PATCH_ID
.venv/bin/python -m smb3_agent lab patch preview PATCH_ID
.venv/bin/python -m smb3_agent lab patch prepare PATCH_ID
.venv/bin/python -m smb3_agent lab patch validate PATCH_ID
.venv/bin/python -m smb3_agent lab patch compare PATCH_ID
.venv/bin/python -m smb3_agent lab patch promote PATCH_ID --confirm PATCH_ID
```

## Documentation

Start with [the documentation index](docs/README.md). Key references are:

- [Development and repository structure](docs/development.md)
- [Single sources of truth](docs/ssot.md)
- [Goal contracts](docs/goal-contract.md)
- [Route status and accepted evidence](docs/route-status.md)
- [Route patch schema](docs/route-patch-schema.md)
- [Agent architecture](docs/agent-architecture.md)

## Working rules

- Goal contracts and accepted evidence define product truth.
- Green ROM-free tests are not live gameplay acceptance.
- Product runs start from power-on and prohibit bridges, savestates, search,
  blind mutation, and diagnostic fallback.
- Credentials and local game/evidence assets must never be committed.
