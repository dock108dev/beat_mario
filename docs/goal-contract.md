# Goal Contract

A goal contract is the machine-readable source of truth for a user objective.
The default product contract remains
`data/goals/world_8_double_whistle.yaml`. Rank 28 adds the explicitly selected
`data/goals/world_8_big_tanks.yaml` contract without changing that default.

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

Route need and execution status are separate. All 15 default product steps and
the one Big Tanks extension step are `normal_gameplay`; the legacy
diagnostic's bridges remain isolated and are not product proof.

## Default contract shape

```yaml
id: world_8_double_whistle
game: smb3
goal_type: product_goal
execution_status: executable
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
    - id: world_1_6_clear
      classification: game_prerequisite
      execution_mode: normal_gameplay
      evidence: [live_fceux_2026-08-09_1_6_fresh_playback]
    - id: world_1_airship_to_king
      classification: game_prerequisite
      execution_mode: normal_gameplay
      evidence: [live_fceux_2026-08-09_world_8_fresh_playback_x3]
    - id: world_2_map_arrival_with_two_whistles
      classification: objective_milestone
      execution_mode: normal_gameplay
      evidence: [live_fceux_2026-08-09_world_8_fresh_playback_x3]
    - id: world_2_first_whistle_use
      classification: objective_milestone
      execution_mode: normal_gameplay
      evidence: [live_fceux_2026-08-09_world_8_fresh_playback_x3]
    - id: world_8_map_arrival
      classification: objective_milestone
      execution_mode: normal_gameplay
      evidence: [live_fceux_2026-08-09_world_8_fresh_playback_x3]

runner:
  preset: fceux_world_8_double_whistle
  executable: true
```

The real contract contains every ordered step. Each step has non-empty evidence
and an explicit execution mode. Unknown classifications, modes, presets,
recovery actions, bridge declarations, duplicate segments, and missing catalog
segments fail validation.

## Default route invariants

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

## Rank 28 composed contract

The Big Tanks goal declares the accepted default goal as its prefix and owns
only the new segment:

```yaml
id: world_8_big_tanks
game: smb3
goal_type: product_goal
execution_status: executable

objective:
  type: route_completion
  target: world_8_big_tanks_post_clear

route:
  prefix_goal: world_8_double_whistle
  catalog: data/segments/world_8_double_whistle.yaml
  segments:
    - id: world_8_big_tanks_clear
      classification: objective_milestone
      execution_mode: normal_gameplay

runner:
  preset: fceux_world_8_big_tanks
  executable: true
```

Resolution produces the unchanged 15-segment prefix followed by exactly one
extension segment. Prefix cycles, cross-catalog composition, a missing prefix,
duplicate segments, or an unsupported preset fail validation.

The extension cannot pass on World 8 map arrival or stage entry. Its ordered
observer evidence requires Big Tanks entry, genuine scrolling gameplay, live
boss defeat with no life loss, chest collection and game return-map flag, then
a stable World 8 map observation at cursor `(64,112)`. The final success event
is `post_probe_world_8_big_tanks_post_clear`; no later World 8 stage may be
entered.

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
.venv/bin/python -m smb3_agent goal validate \
  data/goals/world_8_big_tanks.yaml
.venv/bin/python -m smb3_agent goal status world_8_big_tanks
```

`goal run world_8_double_whistle` executes the product preset directly and
never routes to `world_1_king`. The Big Tanks preset is selected only by the
separate goal.
