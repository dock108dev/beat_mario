# SMB3 Route Agent

Local proof-of-concept for a user-steered game agent.

The immediate target is Super Mario Bros. 3 on a local NES emulator. The larger
target is an agent workbench that can accept user goals, turn them into route
contracts, operate a game, observe state, recover from failures, and explain
what changed between attempts.

## Current State

The repo currently has:

- A FCEUX-backed route runner with structured logs.
- A strict World 1-1 reliability gate.
- A World 1 route gate that reaches the king-transition marker using a mix of
  scripted gameplay and explicit bridge steps.
- Screenshot/contact-sheet tooling for review.
- Phase 6 attempt-lab scaffolding for sessions, human notes, route variants,
  and evidence-backed iteration.
- Mario Route Lab, a local evidence-first UI for running World 1, reviewing
  artifacts, teaching selected locations, and creating Codex-task packets.
- Parser tests for route summaries and post-probe success markers.

See [docs/route-status.md](docs/route-status.md) for what is solved, bridged,
flaky, and still unknown.

## Setup

```bash
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

FCEUX must be available on `PATH`. Local game files, emulator state, and proof
artifacts stay outside git.

## Main Commands

Run unit tests:

```bash
python -m pytest -q
```

Run the strict World 1-1 gate:

```bash
python -m smb3_agent task fceux-1-1 \
  --game-file "$SMB3_GAME_FILE" \
  --attempts 10 \
  --artifacts-dir artifacts/fceux/cli_gate_1_1 \
  --require-perfect
```

Run the current World 1 king-transition gate:

```bash
python -m smb3_agent task fceux-world-1-king \
  --game-file "$SMB3_GAME_FILE" \
  --attempts 10 \
  --artifacts-dir artifacts/fceux/world_1_king \
  --require-perfect
```

Validate and run the first goal contract:

```bash
python -m smb3_agent goal validate data/goals/world_1_king.yaml
export SMB3_GAME_FILE=/path/to/local-game-file
python -m smb3_agent goal run world_1_king --attempts 3
```

Inspect the World 1 segment catalog:

```bash
python -m smb3_agent segment validate data/segments/world_1.yaml
python -m smb3_agent goal status world_1_king
```

Use the command interface:

```bash
python -m smb3_agent command parse "run world 1 king gate 3 times"
export SMB3_GAME_FILE=/path/to/local-game-file
python -m smb3_agent command run "run world 1 king gate 3 times"
```

Observe and simulate recovery:

```bash
export SMB3_GAME_FILE=/path/to/local-game-file
python -m smb3_agent observe run-segment world_1_1 --sample-frames 15
python -m smb3_agent recovery simulate life_lost --goal world_1_king
python -m smb3_agent recovery simulate wrong_map_node --goal world_1_king
```

Phase 6 attempt-lab commands are available. Their contracts are documented in
`docs/attempt-lab.md` and scaffolded under `data/lab/`.

Use the attempt lab:

```bash
python -m smb3_agent lab start "show me the route at 4x" --attempts 1
python -m smb3_agent lab note latest "1-1 around 320 timer: falls into the hole and usually gets lucky"
python -m smb3_agent lab review latest
python -m smb3_agent lab propose-variant latest
```

Batch review lab commands:

```bash
python -m smb3_agent lab issues latest
python -m smb3_agent lab propose-variants latest
python -m smb3_agent lab ui-summary latest
python -m smb3_agent lab codex-task latest --issue ISSUE_ID
```

Serve Mario Route Lab:

```bash
python -m smb3_agent lab ui --host 127.0.0.1 --port 8765
```

Mario Route Lab uses player-facing locations such as `Map`, `1-1`, `1-3`,
`Fortress`, `Airship`, and `King`. The screen is organized around Route,
Evidence, Teach This Section, Things Mario Still Gets Wrong, and Recent
Observations. Backend route labels stay out of the normal UI workflow.

Review an existing log:

```bash
python -m smb3_agent review log artifacts/fceux/world_1_king/fceux_1_1.log
python -m smb3_agent review compare artifacts/fceux/world_1_king artifacts/fceux/show_world1_king_4x_001
python -m smb3_agent task review-fceux-log \
  --log artifacts/fceux/world_1_king/fceux_1_1.log \
  --attempts 10
```

## Project Docs

- [Product direction](docs/product-direction.md)
- [Goal contract](docs/goal-contract.md)
- [Agent architecture](docs/agent-architecture.md)
- [Attempt lab](docs/attempt-lab.md)
- [World 1 lab guide](docs/world-1-lab-guide.md)
- [Mario Route Lab](docs/mario-route-lab.md)
- [Local Route Lab assets](docs/local-assets.md)
- [Implementation plan](docs/implementation-plan.md)
- [Validation gates](docs/validation-gates.md)
- [Route status](docs/route-status.md)
- [FCEUX harness notes](docs/fceux-harness.md)

## Working Rule

Every implementation step must end with a validation gate. If a gate fails, the
next implementation step is to explain and repair that failure before expanding
scope.
