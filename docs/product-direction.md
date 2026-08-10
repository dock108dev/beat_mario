# Product Direction

This repo is the first proof of a user-steered game agent, not merely a Mario
input script. A user goal becomes a route contract; the workbench executes what
is available, observes state, preserves evidence, recovers only within policy,
and reports the next bounded experiment.

## Active SMB3 goal

The product source of truth is `world_8_double_whistle`:

```text
fresh game
-> collect the World 1-3 Warp Whistle
-> collect the World 1 Fortress Warp Whistle
-> clear the game-required World 1 path through 1-5 and 1-6
-> clear the Airship and complete the King transition
-> arrive safely on the World 2 map with both whistles
-> use the first whistle from World 2
-> observe the Warp Zone 5/6/7 tier
-> use the second whistle while still in the Warp Zone
-> observe the World 8 tier
-> enter the World 8 pipe
-> observe a genuine World 8 map arrival
```

World 1-4 is not part of this route. World 7 appears only as a visible label in
the first Warp Zone tier; the route does not enter World 7. World 8 gameplay is
outside the arrival boundary.

The owner-corrected route requires World 2 before whistle use. Therefore the
Airship/King is an intermediate prerequisite, not a destination. The legacy
`world_1_king` contract remains a diagnostic route and cannot satisfy the
product goal.

## Evidence policy

The local game's observable behavior is authoritative. The proof levels stay
separate:

1. Contract/static proof: schemas, catalog cross-checks, status output, tests,
   and deterministic Route Lab HTML agree.
2. Live topology proof: fresh FCEUX observations show concrete map, inventory,
   and transition states.
3. Assisted investigation: an explicit bridge or test setup may orient work,
   but is labeled and cannot prove normal gameplay reliability.
4. Executable route proof: the selected goal completes repeatably with only
   tactics its contract allows.

The active goal is executable. Three fresh no-bridge playbacks and one promoted
goal-run validation reached the genuine World 8 map boundary.

## Goal contract

A contract owns:

- the user directive and final observable target;
- the ordered route and its referenced segment catalog;
- whether each step is an objective milestone or game prerequisite;
- execution mode (`normal_gameplay`, `bridge`, or `planned`);
- allowed tactics, recovery policy, and success metrics;
- executable versus planned status.

Commands, status rendering, review mappings, and Mario Route Lab consume that
contract instead of maintaining a separate default route.

## Product thesis

Build a workbench that can:

1. Convert user intent into a reviewable contract.
2. Select a justified route.
3. Execute through an emulator adapter.
4. Observe map, level, inventory, transition, and failure state.
5. Recover only when the contract permits it.
6. Produce useful evidence and a bounded next action.
7. Turn user observations into validated route variants.

SMB3 proves this control/evidence loop before the same shape is generalized to
management, city, shop, or life simulations.
