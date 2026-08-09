# Validation Gates

Validation keeps contract proof, live topology proof, assisted diagnostics, and
repeatable route proof separate. Passing a lower level never implies a higher
one.

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
- `execution_status=planned`
- `executable=false`
- fifteen ordered segments and zero active bridges

The planned status is correct until safe World 2 arrival and all later
transitions are implemented and live-validated.

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
- unimplemented segments remain `planned`.

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

## Gate 5: Fail-closed execution

```bash
.venv/bin/python -m smb3_agent goal run world_8_double_whistle
.venv/bin/python -m smb3_agent command run \
  "run world 8 double whistle arrival"
```

Current pass condition: both commands exit non-zero with
`planned and not yet executable` and say that no diagnostic fallback is
permitted. They must never invoke the World 1 king preset.

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
- planned steps say `Planned`, not solved;
- exactly one strong primary button remains;
- stable semantic class hooks remain present.

## Gate 8: Live safe-World-2 boundary

This gate is not yet passing.

Required future command shape:

```bash
export SMB3_GAME_FILE=/path/to/local-game-file
.venv/bin/python -m smb3_agent goal run world_8_double_whistle \
  --game-file "$SMB3_GAME_FILE" \
  --attempts 5 \
  --capture-images
```

First promotion boundary:

- real 1-5, 1-6, and Airship gameplay after both whistles;
- genuine World 2 map observation;
- two whistle items still observable;
- no completion-flag, map-position, airship-stage, or inventory bridge;
- structured logs and minimal screenshots in ignored artifacts.

Do not implement or promote later Warp Zone segments until this boundary is
repeatable.

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
