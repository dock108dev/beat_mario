# Route Status

Last updated: 2026-08-09.

## Active goal

`world_8_double_whistle` is the product source of truth. It ends only on a
genuine World 8 map observation. The owner corrected the route boundary during
live investigation: Mario must clear the final World 1 castle/airship, arrive
safely in World 2 with both whistles, and use the first whistle from World 2.

The active goal is now `executable`. Three independent fresh product replays
completed all 15 route steps with byte-identical logs, and the promoted
`goal run world_8_double_whistle` command independently passed its metrics.
The legacy `world_1_king` gate remains a separate diagnostic.

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

World 1-4 is absent. World 7 is not entered; it is only one of the labels on
the expected first Warp Zone tier.

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

## Next bounded task

Rank 10 is complete at the genuine World 8 map boundary. World 8 gameplay is a
separate future goal; it was not started by this route.

## Roaming placement note

The World 1 Hammer Bro's map movement is RNG-driven: the game reads a random
byte, masks it to one of four directions, and then validates that move. An
exact fresh, frame-identical emulator replay therefore repeats the same RNG
state and produced the same post-1-6 encounter in all three accepted runs.
Merely taking the same semantic map path by hand at different timing is not a
guarantee. The route remains observer-driven and only enters the battle
controller when the roaming encounter is actually present.
