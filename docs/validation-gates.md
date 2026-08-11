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

## Gate 8: Rank 27 end-to-end reliability

```bash
export SMB3_GAME_FILE=/path/to/local-game-file
.venv/bin/python -m smb3_agent reliability run
```

Pass condition:

- five requested runs create five distinct `run_NN` directories;
- every run record says one attempt, new FCEUX process, fresh power-on game,
  clean product environment, and unthrottled reliability mode;
- all 15 acceptance events from the active segment catalog appear in contract
  order;
- every run reports `metrics_passed=true` and final event
  `post_probe_world_8_map_arrival`;
- every final observer boundary is `world_number=7`, `object_set=0`;
- no bridge, mutation, savestate/search, diagnostic route, retry checkpoint, or
  prior emulator process contributes evidence;
- completed and successful runs are both five, success rate is `1.0`, and
  `overall_pass=true`.

Any failure leaves its route log when created, FCEUX stdout/stderr, execution
record, last accepted segment, first missing milestone, final observable state,
classification, and next bounded investigation. Missing or ambiguous evidence
fails closed. The aggregate report and per-run reports live under the ignored
`artifacts/reliability/world_8_double_whistle/` tree.

## Gate 9: Watchable review playback

```bash
.venv/bin/python -m smb3_agent reliability watch
```

Pass condition: the same product route completes from a fresh game, review
images and a state/tick trace are retained, and `review/contact_sheet.png` is
created. The report must say `review_only`, `promotable=false`, and
`counts_toward_reliability=false`. The default frame throttle is 0.0035 seconds.
Capture and throttle overhead can change gameplay, so this result never repairs
or supplements a failed reliability aggregate.

Both live commands stop at the genuine World 8 map boundary. Entering or playing
World 8 is outside Rank 27.

Accepted 2026-08-10 Rank 27 evidence:

```text
artifacts/reliability/world_8_double_whistle/20260810T160716.743170Z_reliability/
artifacts/review/world_8_double_whistle/20260810T160828.873705Z_watchable/
```

The authoritative report records 5/5, success rate `1.0`, all 15 milestones,
`metrics_passed=true`, the required final event, accepted World 8 map state,
and byte-identical SHA-256 logs. The watchable report records a successful
review-only route, 1,398 converted review images, a 621-line tick trace, and a
contact sheet; it is excluded from reliability evidence.

## Gate 10: Rank 28 goal and extension contract

```bash
.venv/bin/python -m smb3_agent goal validate \
  data/goals/world_8_big_tanks.yaml
.venv/bin/python -m smb3_agent goal status world_8_big_tanks
```

Pass condition:

- the goal is an executable `product_goal` using
  `fceux_world_8_big_tanks`;
- `world_8_double_whistle` is the declared prefix and remains unchanged at 15
  segments;
- the resolved goal contains that prefix plus exactly
  `world_8_big_tanks_clear`, for 16 ordered events and zero bridges;
- map arrival, stage entry, stage gameplay, boss defeat, chest/clear, and
  stable post-clear state are distinct observer-derived boundaries;
- no later World 8 segment is selected.

## Gate 11: Rank 28 authoritative reliability

```bash
.venv/bin/python -m smb3_agent reliability run \
  --goal world_8_big_tanks \
  --game-file "$SMB3_GAME_FILE"
```

Pass condition:

- three requested runs create three isolated directories and three new FCEUX
  processes, each with one power-on attempt;
- all 16 ordered events pass without savestate, retry, bridge, mutation,
  discovery search, or diagnostic fallback;
- each run contains the five authoritative focused PNGs for map arrival,
  entry, gameplay, clear, and post-clear;
- boss disappearance during Mario death is rejected; the boss must enter its
  defeated state while Mario remains alive and lives are unchanged;
- clear requires the chest reward plus the return-map flag, not a self-declared
  event;
- the final stable observation is World 8 map state at cursor `(64,112)`, and
  no next-stage entry appears;
- all three runs pass, success rate is `1.0`, and `overall_pass=true`.

Accepted evidence:

```text
artifacts/reliability/world_8_big_tanks/20260810T190157.201466Z_reliability/
```

## Gate 12: Rank 28 watchable review

```bash
.venv/bin/python -m smb3_agent reliability watch \
  --goal world_8_big_tanks \
  --game-file "$SMB3_GAME_FILE" \
  --throttle-seconds 0.0001
```

Pass condition: one fresh route passes; the contact sheet contains exactly the
five focused review frames; the state/tick trace is retained; and the report
says `review_only`, `promotable=false`, and
`counts_toward_reliability=false`. The accepted review is under:

```text
artifacts/review/world_8_big_tanks/20260810T212112.984218Z_watchable/
```

The Rank 28 watchable path is validated at a `0.0001`-second throttle. A slower
`0.0035`-second review run diverged during the accepted prefix and remains
review-only failure evidence; it did not affect the unthrottled 3/3 result.

## Gate 13: Default-goal regression after Rank 28

```bash
.venv/bin/python -m smb3_agent reliability run \
  --game-file "$SMB3_GAME_FILE"
```

Pass condition: omitting `--goal` still selects `world_8_double_whistle`, runs
five fresh processes, completes only its 15 events, and stops at
`post_probe_world_8_map_arrival`. The post-change gate passed 5/5 under:

```text
artifacts/reliability/world_8_double_whistle/20260810T212451.471392Z_reliability/
```

## Gate 14: Legacy king diagnostic

```bash
.venv/bin/python -m smb3_agent goal validate data/goals/world_1_king.yaml
.venv/bin/python -m smb3_agent goal status world_1_king
```

Pass condition:

- the goal identifies itself as `diagnostic_route`;
- its explicit bridges remain visible;
- no default product command or Route Lab route selects it;
- a diagnostic pass is never reported as World 8 progress.

## Gate 15: Tracked-surface hygiene

```bash
git diff --check
git status --short
git ls-files | rg -i '\.(nes|fds|sav|fc[0-9]|state)$' && exit 1 || true
```

Pass condition: only intentional source, catalog, test, and documentation
changes are tracked; local game assets and generated evidence remain ignored.

## Gate 16: Rank 33 disposable route-patch loop

```bash
.venv/bin/python -m pytest -q tests/test_route_patch.py
```

Pass condition: the reviewed parent fixture fails its intended assertion, the
patched detached candidate passes, comparison recommends the exact diff,
promotion verifies postimages, and rollback restores the original bytes. CLI
import and HTTP Route Lab actions must share one backend lifecycle and artifact
set.

Accepted 2026-08-10 Rank 33 ROM-free result: 135 tests passed in the canonical
gate, including 20 route-patch cases after parameter expansion.

## Gate 17: Rank 33 safety and atomicity

The same ROM-free suite must reject unreviewed or stale patches, path and
symlink escape, undeclared/generated/binary files, commands and self-approval,
malformed/duplicate/no-op operations, parent execution, candidate or validation
artifact tampering, dirty targets, duplicate promotion, partial promotion, and
rollback over later edits. Documentation-only validation is non-promotable.

## Gate 18: Rank 33 required live regressions

```bash
.venv/bin/python -m smb3_agent reliability run \
  --goal world_8_double_whistle --runs 5 --game-file "$SMB3_GAME_FILE"
.venv/bin/python -m smb3_agent reliability run \
  --goal world_8_big_tanks --runs 3 --game-file "$SMB3_GAME_FILE"
```

Pass condition: Rank 27 remains 5/5 at the World 8 arrival boundary and Rank 28
remains 3/3 at the Big Tanks post-clear map. These are product-route regression
proof, not a demonstration patch, and do not extend later World 8 gameplay.

Accepted Rank 33 regression reports:

```text
artifacts/reliability/world_8_double_whistle/20260810T215451.255693Z_reliability/
artifacts/reliability/world_8_big_tanks/20260810T215605.922925Z_reliability/
```

## Gate 19: Battleships goal and observer contract

```bash
.venv/bin/python -m smb3_agent goal validate \
  data/goals/world_8_battleships.yaml
.venv/bin/python -m smb3_agent goal status world_8_battleships
```

Pass condition:

- `world_8_double_whistle` remains 15 segments and `world_8_big_tanks` remains
  16 segments;
- `world_8_battleships` composes the Big Tanks goal plus exactly
  `world_8_battleships_clear`, for 17 ordered events and zero bridges;
- selection uses `fceux_world_8_battleships` without fallback;
- the four ordered catalog-owned acceptance events prove exact entry, gameplay,
  game-owned clear, and stable post-clear map state;
- wrong stage or entry, death, false clear, missing or reordered events, stall,
  timeout, later-stage entry, and ambiguous evidence fail closed.

## Gate 20: Battleships authoritative reliability

```bash
.venv/bin/python -m smb3_agent reliability run \
  --goal world_8_battleships \
  --game-file "$SMB3_GAME_FILE"
```

Pass condition: at least three isolated fresh-power-on processes each make one
attempt, complete all 17 milestones, report `metrics_passed=true`, retain the
five required focused screenshots, keep Mario alive, observe the live object
`75` to defeated-transition object `74` replacement and the game return flag,
and stabilize at cursor `(128,112)` without Hand Trap entry. The aggregate also
requires byte-identical logs, `success_rate=1.0`, and `overall_pass=true`.

Accepted evidence:

```text
artifacts/reliability/world_8_battleships/20260810T225906.177318Z_reliability/
```

## Gate 21: Battleships watchable review

```bash
.venv/bin/python -m smb3_agent reliability watch \
  --goal world_8_battleships \
  --game-file "$SMB3_GAME_FILE" \
  --throttle-seconds 0.0001
```

Pass condition: the route passes from fresh power-on; the contact sheet contains
exactly the five focused frames; the tick trace is retained; and the report says
`review_only`, `promotable=false`, and `counts_toward_reliability=false`.

Accepted evidence:

```text
artifacts/review/world_8_battleships/20260810T224805.096938Z_watchable/
```

## Gate 22: Battleships regressions and hygiene

```bash
PYTHON=.venv/bin/python scripts/validate_phase0.sh
.venv/bin/python -m smb3_agent reliability run \
  --goal world_8_double_whistle --runs 5 --game-file "$SMB3_GAME_FILE"
.venv/bin/python -m smb3_agent reliability run \
  --goal world_8_big_tanks --runs 3 --game-file "$SMB3_GAME_FILE"
git diff --check
```

Pass condition: the canonical ROM-free gate passes; the unchanged Rank 27 goal
remains 5/5 and stops at World 8 arrival; the unchanged Rank 28 goal remains 3/3
and stops after Big Tanks; only intentional source, contract, test, and
documentation changes are uncommitted; and no ROM, state, generated evidence,
temporary worktree, log, screenshot, report, trace, or credential is tracked.

Accepted result: the canonical gate passed 158 tests. The live regression
reports are:

```text
artifacts/reliability/world_8_double_whistle/20260810T230007.756761Z_reliability/
artifacts/reliability/world_8_big_tanks/20260810T230122.959142Z_reliability/
```

## Gate 23: Hand Traps and Jet goal and observer contract

```bash
.venv/bin/python -m smb3_agent goal validate \
  data/goals/world_8_hand_traps_jet.yaml
.venv/bin/python -m smb3_agent goal status world_8_hand_traps_jet
```

Pass condition:

- the unchanged 17-segment Battleships goal is the declared prefix;
- right, center, and left Hand Traps plus Jet extend it to exactly 21 ordered
  segments and zero bridges;
- every trap has its own entry, gameplay, reward, and stable-return sequence;
- every Leaf is proved by reward object `82`, item id `3`, and inventory
  transition `0 -> 1`;
- Battleships preserves the P-Wing by using a Star and the underwater route;
- Jet consumes that saved P-Wing and records hazard-aware wait/advance pacing;
- the final accepted boundary is map page 2 cursor `(64,112)`, with World 8-1
  accessible and unentered.

## Gate 24: Hand Traps and Jet authoritative reliability

```bash
.venv/bin/python -m smb3_agent reliability run \
  --goal world_8_hand_traps_jet \
  --game-file "$SMB3_GAME_FILE"
```

Pass condition: at least three isolated fresh-power-on processes make one
attempt each; all 21 milestones and contract metrics pass; each run retains
exactly 17 distinct focused screenshots; logs are byte-identical; all three
runs finish alive at the exact accepted boundary; and no bridge, mutation,
savestate, search, retry checkpoint, diagnostic fallback, or World 8-1 entry
contributes evidence.

Accepted evidence:

```text
artifacts/reliability/world_8_hand_traps_jet/20260811T062336.029178Z_reliability/
```

The aggregate passed 3/3 with `success_rate=1.0`, `overall_pass=true`, and
structured-log SHA-256
`6b6f66ca679ca63bba97a76e3da3326f5f643d881880b24203ccb97de67ca8fa`.

## Gate 25: Hand Traps and Jet watchable review

```bash
.venv/bin/python -m smb3_agent reliability watch \
  --goal world_8_hand_traps_jet \
  --game-file "$SMB3_GAME_FILE" \
  --throttle-seconds 0.001
```

Pass condition: a fresh route passes; the review set contains exactly the 17
focused states; a 795-line state/tick trace and contact sheet are retained; and
the report says `review_only`, `promotable=false`, and
`counts_toward_reliability=false`.

Accepted evidence:

```text
artifacts/review/world_8_hand_traps_jet/20260811T060954.667404Z_watchable/
```

## Gate 26: Hand Traps and Jet regressions and hygiene

```bash
PYTHON=.venv/bin/python scripts/validate_phase0.sh
.venv/bin/python -m smb3_agent reliability run \
  --goal world_8_double_whistle --runs 5 --game-file "$SMB3_GAME_FILE"
.venv/bin/python -m smb3_agent reliability run \
  --goal world_8_big_tanks --runs 3 --game-file "$SMB3_GAME_FILE"
.venv/bin/python -m smb3_agent reliability run \
  --goal world_8_battleships --runs 3 --game-file "$SMB3_GAME_FILE"
git diff --check
```

Pass condition: the canonical ROM-free gate passes 184 tests; Rank 27 remains
5/5; Big Tanks and Battleships remain 3/3; each earlier goal stops at its own
accepted boundary; and only intentional source, contract, test, and
documentation changes remain uncommitted. No ROM, savestate, generated
evidence, log, screenshot, report, trace, temporary worktree, or credential is
tracked.

Accepted regression reports:

```text
artifacts/reliability/world_8_double_whistle/20260811T061710.427413Z_reliability/
artifacts/reliability/world_8_big_tanks/20260811T061936.683562Z_reliability/
artifacts/reliability/world_8_battleships/20260811T062230.086277Z_reliability/
```
