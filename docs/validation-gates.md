# Validation Gates

Validation keeps contract proof, live topology proof, assisted diagnostics, and
repeatable route proof separate. Passing a lower level never implies a higher
one.

## Canonical ROM-free gate

```bash
PYTHON=.venv/bin/python scripts/validate_phase0.sh
```

This is the single local and hosted entrypoint for the complete ROM-free
surface. On GitHub Actions it runs with Python 3.11 on `ubuntu-latest`, with
read-only repository contents permission and no secrets. The gate fails fast
across tracked and changed-file whitespace, Bash syntax, Ruff linting, forbidden
tracked files, pytest, the active goal contract, the active segment catalog,
deterministic goal status, and the Mario Route Lab HTML contract.

The hosted gate proves that those contracts install and execute on a headless
Unix runner without a game file, FCEUX, Mednafen, savestate, display server, or
generated evidence. It does not prove that Mario can execute the route. Live
FCEUX route proof remains a local macOS gate with explicit game-file authority.
The legacy Quartz/ApplicationServices Mednafen modules are also macOS-only:
ROM-free CLI commands do not import them, and Linux reports an explicit
unsupported-platform error if one of those commands is intentionally selected.

Mario Route Lab HTML is rendered into a securely created temporary directory
during the canonical gate, checked for non-empty semantic content, and removed
automatically. It is neither tracked nor uploaded by hosted CI.

## Gate 1: ROM-free suite

```bash
.venv/bin/python -m pytest -q
```

Pass condition: all tests pass without a local game asset.

## Gate 2: Active goal contract

```bash
.venv/bin/python -m smb3_agent goal validate \
  data/goals/world_8_double_whistle.yaml
```

Pass condition:

- `goal_id=world_8_double_whistle`
- `goal_type=product_goal`
- `execution_status=executable`
- `executable=true`
- `preset=fceux_world_8_double_whistle`
- fifteen ordered segments and zero active bridges

## Gate 3: Active segment catalog

```bash
.venv/bin/python -m smb3_agent segment validate \
  data/segments/world_8_double_whistle.yaml \
  --goal world_8_double_whistle
```

Pass condition:

- every active segment exists in the declared catalog;
- World 1-4 is absent;
- 1-5, 1-6, and Airship/King are present as the path to World 2;
- World 2 arrival, both whistle uses, both Warp Zone tiers, pipe entry, and
  World 8 map arrival are distinct;
- all 15 promoted segments are `solved` after accepted live proof.

## Gate 4: Deterministic status

```bash
.venv/bin/python -m smb3_agent goal status world_8_double_whistle
```

Pass condition:

- output is ordered from the contract;
- every row includes classification, execution mode, catalog status, bridge
  flag, method, and evidence;
- World 2 map arrival precedes first-whistle use;
- second-whistle use follows the 5/6/7 tier and precedes the World 8 tier;
- only the final row is World 8 map arrival.

## Gate 5: Product execution

```bash
.venv/bin/python -m smb3_agent goal run world_8_double_whistle \
  --game-file "$SMB3_GAME_FILE"
.venv/bin/python -m smb3_agent command run \
  "run world 8 double whistle arrival" \
  --game-file "$SMB3_GAME_FILE"
```

Pass condition: both commands select `fceux_world_8_double_whistle`, reach the
final map marker, and report `metrics_passed=true`. They must never invoke the
World 1 king preset.

## Gate 6: Success-marker isolation

Covered by the ROM-free suite.

Pass condition:

- both whistle acquisition events are required;
- `post_probe_1_airship_success_king` fails the active goal;
- missing World 2 arrival fails;
- missing either whistle-use event fails;
- only final event `post_probe_world_8_map_arrival` can satisfy the active goal.

## Gate 7: Mario Route Lab render contract

```bash
.venv/bin/python -m smb3_agent lab ui-render \
  --output artifacts/ui/world_8_double_whistle.html
```

Inspect the deterministic HTML:

```bash
rg -n \
  -e "Run World 8 Route" \
  -e "World 2 Map" \
  -e "First Whistle \(World 2\)" \
  -e "Warp Zone 5 / 6 / 7" \
  -e "Second Whistle \(Warp Zone\)" \
  -e "Warp Zone World 8" \
  -e "World 8 Pipe" \
  -e "World 8 Map" \
  artifacts/ui/world_8_double_whistle.html
```

Pass condition:

- route rows exactly match the selected contract order;
- 1-4 is absent;
- 1-5, 1-6, and Airship/King are shown as required path;
- solved steps say `Learned`, not planned;
- exactly one strong primary button remains;
- stable semantic class hooks remain present.

This explicit `artifacts/` command is for local inspection only and its output
is ignored. The canonical local/hosted gate instead renders to a temporary
directory and deletes the HTML after the assertions pass.

## Gate 8: Live product boundary

This gate passes. Three fresh no-bridge replays reached World 8 with
byte-identical logs, followed by an independent promoted goal-run pass.

Accepted command shape:

```bash
export SMB3_GAME_FILE=/path/to/local-game-file
.venv/bin/python -m smb3_agent goal run world_8_double_whistle \
  --game-file "$SMB3_GAME_FILE" \
  --attempts 1 \
  --capture-images
```

Accepted boundary:

- retain the accepted real 1-5, 1-6, and observer-gated Hammer Bro prefix;
- real Airship/King gameplay after both whistles;
- genuine World 2 map observation;
- two whistle items still observable;
- first whistle use after Mario settles in World 2;
- second whistle use from the observed 5/6/7 tier;
- World 8 tier, pipe entry, and genuine World 8 map observation;
- no completion-flag, map-position, airship-stage, or inventory bridge;
- structured logs and minimal screenshots in ignored artifacts.

## Gate 9: Legacy king diagnostic

```bash
.venv/bin/python -m smb3_agent goal validate data/goals/world_1_king.yaml
.venv/bin/python -m smb3_agent goal status world_1_king
```

Pass condition:

- the goal identifies itself as `diagnostic_route`;
- its explicit bridges remain visible;
- no default product command or Route Lab route selects it;
- a diagnostic pass is never reported as World 8 progress.

## Gate 10: Tracked-surface hygiene

```bash
git diff --check
git status --short
git ls-files | rg -i '\.(nes|fds|sav|fc[0-9]|state)$' && exit 1 || true
```

Pass condition: only intentional source, catalog, test, and documentation
changes are tracked; local game assets and generated evidence remain ignored.
