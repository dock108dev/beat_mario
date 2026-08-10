# Route Status

Last updated: 2026-08-10.

## Default goal

`world_8_double_whistle` is the product source of truth. It ends only on a
genuine World 8 map observation. The owner corrected the route boundary during
live investigation: Mario must clear the final World 1 castle/airship, arrive
safely in World 2 with both whistles, and use the first whistle from World 2.

The default goal is `executable`. Rank 27 launched five independent fresh FCEUX
processes; all five completed all 15 route steps, reported
`metrics_passed=true`, and ended at `post_probe_world_8_map_arrival`. Their
structured logs are byte-identical. A separate throttled playback also passed
and produced review images, ticks, and a contact sheet, but is explicitly
non-promotable. The legacy `world_1_king` gate remains a separate diagnostic.

## Rank 28 separate goal

`world_8_big_tanks` is an executable product goal separate from the default.
It declares `world_8_double_whistle` as its prefix, reuses all 15 accepted
arrival segments without copying them, and adds exactly one segment:
`world_8_big_tanks_clear`.

From the accepted World 8 map at cursor `(32,80)`, normal down/right/A input
reached Big Tanks. The promoted controller traverses the autoscrolling tanks,
enters the end pipe, defeats the Boomerang Brother, avoids the remaining
projectile, and collects the chest. Success requires the additional Super Star
inventory item and the game's return-to-map flag, followed by a stable World 8
map observation at cursor `(64,112)`. The goal stops there, before another
World 8 stage.

The authoritative command passed 3/3:

```bash
.venv/bin/python -m smb3_agent reliability run \
  --goal world_8_big_tanks \
  --game-file roms/smb3.nes
```

Accepted aggregate:

```text
artifacts/reliability/world_8_big_tanks/20260810T190157.201466Z_reliability/
```

All three fresh processes completed the 16 ordered events, reported
`metrics_passed=true`, retained all five focused screenshots, and produced the
same structured-log SHA-256:

```text
38ee2fb807d67fabfc4be08a2eef447d3631510ba2ab8e3386a32068a538ffa2
```

The separate review-only run passed with a `0.0001`-second throttle:

```text
artifacts/review/world_8_big_tanks/20260810T212112.984218Z_watchable/
```

Its five-frame contact sheet covers map arrival, stage entry, real tank
gameplay, chest/clear, and the post-clear map. Its 633-line state/tick trace and
contact sheet are non-promotable and do not count toward the 3/3 gate.

After Rank 28 changes, the unchanged default reliability profile passed 5/5
again at:

```text
artifacts/reliability/world_8_double_whistle/20260810T212451.471392Z_reliability/
```

## Rank 27 reliability evidence

The authoritative command passed 5/5:

```bash
.venv/bin/python -m smb3_agent reliability run --game-file roms/smb3.nes
```

Accepted aggregate:

```text
artifacts/reliability/world_8_double_whistle/20260810T160716.743170Z_reliability/
```

Every `run_01` through `run_05` record shows a new process, one attempt, fresh
game, clean product environment, zero throttle, all 15 ordered milestones,
`metrics_passed=true`, and final `world_number=7`, `object_set=0`. All FCEUX
processes exited zero. The five route-log SHA-256 values are identical:

```text
610c95128c06207d6a04bd7d41f4f1e2e4e59cd6b8d807570e4a85e4a0adb8df
```

The separate watchable command passed:

```bash
.venv/bin/python -m smb3_agent reliability watch --game-file roms/smb3.nes
```

Review-only artifacts:

```text
artifacts/review/world_8_double_whistle/20260810T160828.873705Z_watchable/
```

The report is labeled `review_only`, `promotable=false`, and
`counts_toward_reliability=false`. It retained 1,398 source/converted review
images, a 621-line state/tick trace, and `review/contact_sheet.png`.

Two fail-closed classifications were observed before final acceptance. A broken
`game-file.nes` symlink was classified `preflight` with zero executions. The
first live batch recorded 4/5 because FCEUX 2.6.6 received SIGSEGV during raw
`os.exit()` Qt teardown after run 5 had already written a complete,
byte-identical passing route log. That process remained failed. The route script
was changed to FCEUX's supported `emu.exit()` API, covered by a ROM-free test,
and the complete five-run gate was rerun successfully. No gameplay,
observer/contract, prohibited-tactic, timeout, or artifact-integrity failure was
observed in the accepted batch.

## Ordered route

| Order | Route step | Role | Active execution | Current capability |
| ---: | --- | --- | --- | --- |
| 1 | Fresh start to 1-1 | game prerequisite | normal gameplay | solved |
| 2 | 1-1 | game prerequisite | normal gameplay | solved |
| 3 | 1-2 | game prerequisite | normal gameplay | solved |
| 4 | Collect 1-3 whistle | objective milestone | normal gameplay | solved in three fresh accepted replays |
| 5 | Collect Fortress whistle | objective milestone | normal gameplay | solved in three fresh accepted replays |
| 6 | 1-5 | game prerequisite | normal gameplay | solved in three fresh accepted replays |
| 7 | 1-6 | game prerequisite | normal gameplay | solved in three fresh accepted replays |
| 8 | Airship / King | game prerequisite | normal gameplay | solved in three fresh accepted replays |
| 9 | World 2 map with two whistles | objective milestone | normal gameplay | solved; both whistles and `item_2=9` observed |
| 10 | First whistle from World 2 | objective milestone | normal gameplay | solved after settled World 2 spawn |
| 11 | Warp Zone 5/6/7 tier | objective milestone | normal gameplay | solved and observed before second whistle |
| 12 | Second whistle from Warp Zone | objective milestone | normal gameplay | solved; whistle count fell to zero |
| 13 | Warp Zone World 8 tier | objective milestone | normal gameplay | solved and independently observed |
| 14 | World 8 pipe | objective milestone | normal gameplay | solved via right then A from the World 8 tier |
| 15 | World 8 map arrival | objective milestone | normal gameplay | solved; `world_number=7`, `object_set=0` |
| 16 | World 8 Big Tanks clear | objective milestone in separate goal | normal gameplay | solved 3/3; stable post-clear map return |

Row 16 belongs only to `world_8_big_tanks`; the default contract still ends at
row 15. World 1-4 is absent. World 7 is not entered; it is only one of the
labels on the expected first Warp Zone tier.

## Fresh live investigation

The bounded FCEUX investigation wrote ignored artifacts under:

```text
artifacts/fceux/world_8_double_whistle_topology/
artifacts/fceux/world_8_double_whistle_rank10/
```

Observed facts:

- A fresh run collected the 1-3 whistle (`item_0=12`).
- The Fortress secret-room route collected the second whistle without the
  whistle-inventory bridge (`item_0=12`, `item_1=12`).
- The game returned to the World 1 map with both whistles visible in inventory.
- A fresh diagnostic continued through 1-5 with both whistles.
- A fresh power-on, single-attempt playback traversed 1-6 without discovery,
  savestate loads, position or inventory mutation, or bridge flags.
- The 1-6 end card changed its internal state from `0` to `4` while Mario was
  Raccoon (`form_before_clear=3`), followed by the normal course transition and
  an independently observed World 1 map return (`object_set=0`).
- Both whistles remained in inventory at the accepted 1-6 boundary
  (`item_0=12`, `item_1=12`).
- Normal `up,A` input from the post-1-6 node entered the roaming Hammer Bro
  battle with Raccoon form and both whistles. The observer now identifies that
  encounter instead of sending it to the castle controller.
- The accepted controller uses the overhead platform as a shield, brakes to
  `x=120`, and tail-attacks when the Bro jumps within 48 pixels. It requires 12
  consecutive absent-enemy frames while Mario is alive and still Raccoon
  before classifying the battle as won.
- Three independent fresh, no-savestate, no-search replays produced
  byte-identical logs and the same battle event frames: encounter `24469`, tail
  attack `24620`, enemy-removal proof `24803`, and normal map return `25196`.
- All three accepted replays retained `item_0=12` and `item_1=12`; collecting the
  Bro's chest added `item_2=9`. No savestate, position/inventory mutation, or
  bridge evidence was accepted.
- The promoted controller traversed the real Airship, entered its boss pipe
  with normal down input, defeated the Koopaling, and observed the normal King
  room transition without a bridge.
- World 2 was observed as `world_number=1`, `object_set=0` with both whistles
  (`item_0=12`, `item_1=12`) and the Hammer Bro reward (`item_2=9`).
- After Mario's World 2 spawn settled, B then A consumed the first whistle and
  produced the visible 5/6/7 tier at cursor `(64,112)`.
- The second whistle was used from that tier before any pipe entry, producing
  the World 8 tier at cursor `(128,144)`. Moving right to `(160,144)` and
  pressing A produced a genuine World 8 map at `world_number=7`.

Accepted Gate 1 evidence is under:

```text
artifacts/fceux/world_8_double_whistle_rank10/gate1_1_6_fresh_playback_v3/
```

Accepted roaming Hammer Bro evidence is under:

```text
artifacts/fceux/world_8_double_whistle_rank10/gate2_hammer_bro_fresh_playback_v1/
artifacts/fceux/world_8_double_whistle_rank10/gate2_hammer_bro_fresh_playback_v2/
artifacts/fceux/world_8_double_whistle_rank10/gate2_hammer_bro_fresh_playback_v3/
```

Accepted end-to-end product evidence is under:

```text
artifacts/fceux/world_8_double_whistle_rank10/gate4_world8_fresh_playback_v1/
artifacts/fceux/world_8_double_whistle_rank10/gate4_world8_fresh_playback_v2/
artifacts/fceux/world_8_double_whistle_rank10/gate4_world8_fresh_playback_v3/
artifacts/goals/world_8_double_whistle/final_validation/
```

Before the owner's correction, a probe tested whistle use from World 1. Those
artifacts are retained as rejected-hypothesis evidence only. They are not part
of the active route and cannot support active-goal success.

## Proof levels

- Contract/test proof: active goal, catalog, CLI status, review mapping, Route
  Lab order, and regression tests agree.
- Live game proof: every ordered state through genuine World 8 map arrival was
  observed in fresh, mutation-free, savestate-free playback. All three final
  logs are byte-identical.
- Assisted proof: the 1-3 return-to-map mode and later World 1 diagnostic
  bridges are explicit and cannot establish normal gameplay reliability.
- Executable route proof: available and independently passed through the
  promoted product goal runner.
- World 2-first Warp Zone and World 8 arrival proof: accepted.

## Diagnostic route

The explicit command remains:

```bash
.venv/bin/python -m smb3_agent goal status world_1_king
```

It may be used to repair World 1, but `post_probe_1_airship_success_king` is not
a World 8 success marker and is rejected by the active goal metrics.

## Current boundary

Rank 28 is complete at the normal Big Tanks post-clear map return. The default
Rank 27 goal remains unchanged at the genuine World 8 map arrival. Later World
8 stages and Rank 33 are unstarted and were not entered by this work.

## Roaming placement note

The World 1 Hammer Bro's map movement is RNG-driven: the game reads a random
byte, masks it to one of four directions, and then validates that move. An
exact fresh, frame-identical emulator replay therefore repeats the same RNG
state and produced the same post-1-6 encounter in all three accepted runs.
Merely taking the same semantic map path by hand at different timing is not a
guarantee. The route remains observer-driven and only enters the battle
controller when the roaming encounter is actually present.
