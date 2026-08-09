# Route Status

Last updated: 2026-08-09.

## Active goal

`world_8_double_whistle` is the product source of truth. It ends only on a
genuine World 8 map observation. The owner corrected the route boundary during
live investigation: Mario must clear the final World 1 castle/airship, arrive
safely in World 2 with both whistles, and use the first whistle from World 2.

The active goal is `planned`, not executable. The legacy `world_1_king` gate is
a separate diagnostic and is not progress completion.

## Ordered route

| Order | Route step | Role | Active execution | Current capability |
| ---: | --- | --- | --- | --- |
| 1 | Fresh start to 1-1 | game prerequisite | normal gameplay | solved |
| 2 | 1-1 | game prerequisite | normal gameplay | solved |
| 3 | 1-2 | game prerequisite | normal gameplay | solved |
| 4 | Collect 1-3 whistle | objective milestone | normal gameplay | solved, assisted map return follows |
| 5 | Collect Fortress whistle | objective milestone | normal gameplay | flaky; one fresh live success |
| 6 | 1-5 | game prerequisite | normal gameplay | solved in fresh live diagnostic |
| 7 | 1-6 | game prerequisite | planned | diagnostic bridge only |
| 8 | Airship / King | game prerequisite | planned | diagnostic bridges only |
| 9 | World 2 map with two whistles | objective milestone | planned | unverified |
| 10 | First whistle from World 2 | objective milestone | planned | unverified |
| 11 | Warp Zone 5/6/7 tier | objective milestone | planned | unverified |
| 12 | Second whistle from Warp Zone | objective milestone | planned | unverified |
| 13 | Warp Zone World 8 tier | objective milestone | planned | unverified |
| 14 | World 8 pipe | objective milestone | planned | unverified |
| 15 | World 8 map arrival | objective milestone | planned | unverified |

World 1-4 is absent. World 7 is not entered; it is only one of the labels on
the expected first Warp Zone tier.

## Fresh live investigation

The bounded FCEUX investigation wrote ignored artifacts under:

```text
artifacts/fceux/world_8_double_whistle_topology/
```

Observed facts:

- A fresh run collected the 1-3 whistle (`item_0=12`).
- The Fortress secret-room route collected the second whistle without the
  whistle-inventory bridge (`item_0=12`, `item_1=12`).
- The game returned to the World 1 map with both whistles visible in inventory.
- A fresh diagnostic continued through 1-5 with both whistles.
- The same diagnostic traversed 1-6 only with its declared bridge and preserved
  both whistles.
- The final-castle diagnostic used declared completion/map/airship bridges and
  failed at `post_probe_1_castle_bad_state`; it did not reach the king marker or
  World 2.

Before the owner's correction, a probe tested whistle use from World 1. Those
artifacts are retained as rejected-hypothesis evidence only. They are not part
of the active route and cannot support active-goal success.

## Proof levels

- Contract/test proof: active goal, catalog, CLI status, review mapping, Route
  Lab order, and regression tests agree.
- Live game proof: two whistles on the World 1 map and 1-5 traversal were
  observed; 1-6 was observed only through a diagnostic bridge.
- Assisted proof: the 1-3 return-to-map mode and later World 1 diagnostic
  bridges are explicit and cannot establish normal gameplay reliability.
- Executable route proof: unavailable.
- World 2-first Warp Zone and World 8 arrival proof: unavailable.

## Diagnostic route

The explicit command remains:

```bash
.venv/bin/python -m smb3_agent goal status world_1_king
```

It may be used to repair World 1, but `post_probe_1_airship_success_king` is not
a World 8 success marker and is rejected by the active goal metrics.

## Next bounded task

Implement and validate the safe boundary from the post-Fortress World 1 map,
through real 1-5/1-6/Airship gameplay, to an independently observed World 2 map
with both whistles still in inventory. Stop there; do not add the Warp Zone
sequence until that boundary is reliable.
