# Route Status

This file separates what the agent can actually play from what is currently
assisted or bridged. Keep it current after every route change.

Status values:

- `solved`: repeatable with a validation gate.
- `flaky`: sometimes works but needs tuning or recovery.
- `bridged`: progress is forced through a known state transition.
- `planned`: route is described but not implemented.
- `unknown`: route is not yet understood.

## Current Goal: World 1 King Transition

Command:

```bash
export SMB3_GAME_FILE=/path/to/local-game-file
python -m smb3_agent task fceux-world-1-king \
  --game-file "$SMB3_GAME_FILE" \
  --attempts 10 \
  --artifacts-dir artifacts/fceux/world_1_king \
  --require-perfect
```

Latest known pass condition:

```text
successes=10/10
post_probe_last_event=post_probe_1_airship_success_king
post_probe_clear=true
```

Latest Phase 0 truth refresh:

```bash
export SMB3_GAME_FILE=/path/to/local-game-file
python -m smb3_agent task fceux-world-1-king \
  --game-file "$SMB3_GAME_FILE" \
  --attempts 3 \
  --artifacts-dir artifacts/fceux/doc_gate_world_1_king \
  --require-perfect
```

Result:

```text
successes=3/3
bad_states=0/3
post_probe_last_event=post_probe_1_airship_success_king
post_probe_clear=true
```

Latest Phase 1 goal-contract run:

```bash
export SMB3_GAME_FILE=/path/to/local-game-file
python -m smb3_agent goal run world_1_king --attempts 3
```

Result:

```text
successes=3/3
bad_states=0/3
post_probe_last_event=post_probe_1_airship_success_king
post_probe_clear=true
metrics_passed=true
```

## Segment Table

This table is backed by `data/segments/world_1.yaml` and can be inspected with:

```bash
python -m smb3_agent goal status world_1_king
```

| Segment | Status | Evidence | Notes |
| --- | --- | --- | --- |
| Fresh start to World 1-1 | solved | FCEUX 1-1 gate | Handled by Lua route bootstrap. |
| World 1-1 clear | solved | `fceux-1-1 --attempts 10 --require-perfect` | Strongest current base gate. |
| World 1-2 clear | solved | `run_1_2_naive` post-probe | Cataloged but still implemented as a post-probe script. |
| World 1-3 whistle | solved | Whistle inventory marker | Route uses white-block whistle path. |
| World 1 fortress whistle | bridged | Second whistle bridge marker | Real flight/whistle play is not fully solved. |
| World 1-4 | flaky | Watchable demo failed here | Reliability gate may skip/bridge around parts; visible throttled run exposed instability. |
| World 1-5 / water path | bridged | Water map-position bridge | Needs real route implementation or explicit bridge policy. |
| World 1-6 | bridged | 1-6 clear bridge | Used to reach later World 1 state. |
| Airship/king transition | bridged | `post_probe_1_airship_success_king` | Current gate reaches king marker with explicit transition support. |
| World 8 route | unknown | None | Needs research and planned segment catalog. |

## Known Watch Mode Issue

Visible playback with frame sleep and screenshot capture can change timing. A
recent watchable run reached the post-fortress World 1-4 segment and failed
there:

```text
post_probe_last_event=post_probe_1_4_after
post_probe_clear=false
```

Treat watch mode as a debugging surface, not a reliability gate.

## Next Route Cleanup Targets

1. Add route-patch application from selected Codex task packets.
2. Replace or clearly isolate the fortress whistle bridge.
3. Stabilize World 1-4 under watchable/capture mode.
4. Start World 8 research as planned segments, not one giant route.
