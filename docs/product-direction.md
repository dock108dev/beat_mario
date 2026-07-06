# Product Direction

This repo is not just a Mario scripting project. It is the first proof of a
larger user-steered game agent.

The long-term product idea is an agent that can operate a game under a user's
intent. The user should be able to describe goals, constraints, risk tolerance,
and preferences. The agent should convert that into an operating contract, run
the game, observe outcomes, recover from mistakes, and report what happened.

For SMB3, the user directive might be:

```text
Reach World 8 using the double-whistle route. Prefer real gameplay when
available, but use explicit bridge steps for already-understood transitions
while the workbench is being built.
```

For a future shop, city, or life sim, the directive might be:

```text
Make the business feel premium, but keep cash above the reserve floor and do
not let inventory go stale.
```

The reusable primitive is the same in both cases: a goal contract.

## Goal Contract

A goal contract is the structured version of what the user wants.

```yaml
goal_contract:
  id: world_1_king
  user_directive: "Reach the World 1 king transition from a fresh start."
  objective:
    type: route_completion
    target: world_1_king_transition
  constraints:
    prefer_real_gameplay: true
    allow_bridge_steps: true
    preserve_attempt_artifacts: true
    explain_failures: true
  success_metrics:
    - all_attempts_clear_1_1
    - post_probe_clear_is_true
    - final_event_is_post_probe_1_airship_success_king
  recovery_policy:
    on_life_loss: reclassify_state_and_continue_if_route_allows
    on_wrong_map_position: reload_or_rebridge_known_checkpoint
    on_unknown_state: stop_and_capture_review_artifacts
```

## Why SMB3 First

SMB3 is useful because it forces the hard parts early:

- Real-time input timing.
- Observable and hidden state.
- Death, lives, and restart paths.
- Map navigation.
- Route segments with different mechanics.
- User corrections that must become durable knowledge.

The first milestone is not a perfect game-playing AI. The first milestone is a
workbench that can turn user intent into route execution, evidence, and the next
experiment.

## Product Thesis

Build a user-steered gameplay agent that can:

1. Parse a goal into a contract.
2. Choose a route or experiment plan.
3. Execute through an emulator adapter.
4. Observe game state continuously.
5. Adjust when lives, map position, inventory, or segment state changes.
6. Produce a useful report and next action.

SMB3 proves the control, observation, recovery, and route-learning loop. The same
shape can later operate a store sim, city sim, management game, or custom
playtest sandbox.
