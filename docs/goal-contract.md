# Goal Contract

A goal contract is the structured version of a user's game objective.

The contract is the bridge between:

- Natural language user steering.
- Route planning.
- Segment execution.
- Recovery decisions.
- Validation gates.
- Attempt review.

## Contract Shape

```yaml
id: world_1_king
game: smb3
user_directive: "Reach the World 1 king transition from a fresh start."

objective:
  type: route_completion
  target: world_1_king_transition

route:
  segments:
    - fresh_start_to_1_1
    - world_1_1_clear
    - world_1_2_clear
    - world_1_3_whistle
    - world_1_fortress_whistle
    - world_1_remaining_path
    - world_1_airship_to_king

constraints:
  prefer_real_gameplay: true
  allow_bridge_steps: true
  preserve_attempt_artifacts: true
  explain_failures: true

allowed_tactics:
  scripted_inputs: true
  memory_observation: true
  known_transition_bridge: true
  blind_state_mutation: false

success_metrics:
  - id: all_attempts_clear_1_1
    type: summary_field
    field: success_count
    equals: total
  - id: reaches_king_transition
    type: final_event
    value: post_probe_1_airship_success_king
  - id: post_probe_clear
    type: summary_field
    field: post_probe_clear
    equals: true

recovery_policy:
  life_lost:
    action: reclassify_state
    continue_if_contract_allows: true
  wrong_map_node:
    action: correct_known_state_or_stop
  timeout:
    action: stop_and_review
  unknown_state:
    action: capture_artifacts_and_stop
```

## Required Fields

Every goal contract should include:

- `id`
- `game`
- `user_directive`
- `objective`
- `route.segments`
- `constraints`
- `allowed_tactics`
- `success_metrics`
- `recovery_policy`

## Allowed Tactics

The agent needs to distinguish how progress was achieved.

| Tactic | Meaning |
| --- | --- |
| `scripted_inputs` | Controller inputs are executed by script. |
| `memory_observation` | Emulator state is read to observe game facts. |
| `known_transition_bridge` | A known transition is forced to keep route work moving. |
| `blind_state_mutation` | Arbitrary state edits without a known route reason. Should stay false. |

Bridge steps are not automatically bad. They are bad when they are hidden.
Contracts should make them explicit.

## Recovery Policy

Recovery is the first place where this becomes more than a route script.

For SMB3, the agent should eventually handle:

- Mario loses a life but has remaining lives.
- The route returns to the map after death instead of after clear.
- Mario is on the wrong map node.
- The segment enters the wrong screen.
- The route is stuck in a transition.

The recovery manager should ask the contract what is allowed before acting.

## Validation

Command:

```bash
.venv/bin/python -m smb3_agent goal validate data/goals/world_1_king.yaml
```

Pass condition:

- Required fields exist.
- Every success metric has a supported evaluator.
- Recovery actions are recognized.
- Bridge usage is explicit.

Segment catalog cross-checks are a Phase 2 responsibility.

## First Implementation Target

Do not add LLM interpretation before the contract layer is stable.

First build:

1. YAML contract loader.
2. Pydantic or dataclass validator.
3. `goal validate` CLI command.
4. Static `world_1_king` contract.
5. `goal run world_1_king` wrapper around the existing preset.

Validation gate:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m smb3_agent goal validate data/goals/world_1_king.yaml
export SMB3_GAME_FILE=/path/to/local-game-file
.venv/bin/python -m smb3_agent goal run world_1_king --attempts 3
```
