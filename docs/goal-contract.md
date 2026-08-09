# Goal Contract

A goal contract is the machine-readable source of truth for a user objective.
The active product contract is `data/goals/world_8_double_whistle.yaml`.

## Route semantics

- `objective_milestone`: directly required by the owner goal.
- `game_prerequisite`: traversal required to reach a later owner milestone.
- `optional`: available but unnecessary for the selected goal.
- `recovery_only`: used only after a classified failure and never on the
  nominal route.
- `diagnostic_route`: a supported test path that is not the product goal.
- `bridge`: an explicit temporary transition aid. It is an execution mode, not
  evidence that the game requires a segment. Bridge use must be declared and
  cannot satisfy a goal that disallows it.

Route need and execution status are separate. For example, World 1-6 is a
`game_prerequisite` in the owner-corrected route, while its current executable
capability is only `bridged`; the active contract therefore leaves that step
`planned` rather than treating the diagnostic bridge as product proof.

## Active contract shape

```yaml
id: world_8_double_whistle
game: smb3
goal_type: product_goal
execution_status: planned
user_directive: >-
  Collect both World 1 Warp Whistles, safely reach World 2, use both
  whistles, and arrive on the World 8 map.

objective:
  type: route_completion
  target: world_8_map_arrival

route:
  catalog: data/segments/world_8_double_whistle.yaml
  segments:
    - id: world_1_3_whistle
      classification: objective_milestone
      execution_mode: normal_gameplay
      evidence: [live_fceux_2026-08-09_first_whistle_inventory]
    - id: world_2_map_arrival_with_two_whistles
      classification: objective_milestone
      execution_mode: planned
      evidence: [owner_corrected_world_2_boundary]
    - id: world_2_first_whistle_use
      classification: objective_milestone
      execution_mode: planned
      evidence: [owner_corrected_world_2_boundary]
    - id: world_8_map_arrival
      classification: objective_milestone
      execution_mode: planned
      evidence: [owner_corrected_world_2_boundary]

runner:
  preset: unavailable
  executable: false
```

The real contract contains every ordered step. Each step has non-empty evidence
and an explicit execution mode. Unknown classifications, modes, presets,
recovery actions, bridge declarations, duplicate segments, and missing catalog
segments fail validation.

## Active route invariants

- Both World 1 whistle acquisitions are owner milestones.
- World 1-4 is absent.
- World 1-5 and World 1-6 are game prerequisites after the owner corrected the
  route to require the final World 1 castle and World 2 arrival.
- Airship/King is an intermediate game prerequisite.
- World 2 map arrival with two whistles occurs before first-whistle use.
- First-whistle use and second-whistle use are distinct.
- The second whistle is used from the Warp Zone, before entering a numbered
  pipe.
- The 5/6/7 tier, World 8 tier, World 8 pipe, and World 8 map are distinct
  observable states.
- `post_probe_1_airship_success_king` cannot satisfy this contract.
- Only `post_probe_world_8_map_arrival` can be the final success event.
- Planned segments are never rendered or reported as solved.

## Legacy diagnostic

`data/goals/world_1_king.yaml` is `goal_type: diagnostic_route`. It retains its
own honest validation and explicit bridges. It is executable only when
explicitly selected, and its king marker remains local to that diagnostic.

## Commands

```bash
.venv/bin/python -m smb3_agent goal validate \
  data/goals/world_8_double_whistle.yaml
.venv/bin/python -m smb3_agent segment validate \
  data/segments/world_8_double_whistle.yaml \
  --goal world_8_double_whistle
.venv/bin/python -m smb3_agent goal status world_8_double_whistle
```

`goal run world_8_double_whistle` currently fails with a planned/not-executable
message and never routes to `world_1_king`.
