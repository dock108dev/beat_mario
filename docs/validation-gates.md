# Validation Gates

Use this file as the source of truth for what must pass after implementation
work. A change is not done until its relevant gate passes or the failure is
documented.

## Gate 0: Repo Hygiene

Command:

```bash
git status --short --ignored
```

Pass condition:

- Source/docs/tests intended for review are visible as tracked changes.
- Runtime artifacts and local emulator files are ignored.
- No generated screenshot/log directories are staged.

## Gate 1: Unit Tests

Command:

```bash
python -m pytest -q
```

Pass condition:

```text
4 passed
```

The exact count may grow, but the suite must pass.

## Gate 2: World 1-1 Reliability

Command:

```bash
python -m smb3_agent task fceux-1-1 \
  --attempts 10 \
  --artifacts-dir artifacts/fceux/cli_gate_1_1 \
  --require-perfect
```

Pass condition:

```text
successes=10/10
bad_states=0/10
```

This gate proves the base route runner can start from a fresh flow and clear
World 1-1 reliably.

## Gate 3: Current World 1 King Route

Command:

```bash
python -m smb3_agent task fceux-world-1-king \
  --attempts 10 \
  --artifacts-dir artifacts/fceux/world_1_king \
  --require-perfect
```

Pass condition:

```text
successes=10/10
bad_states=0/10
post_probe_last_event=post_probe_1_airship_success_king
post_probe_clear=true
```

This gate proves the current route reaches the king-transition marker. It does
not prove every segment is solved by regular gameplay. See
`docs/route-status.md`.

## Gate 4: Watchable Demo

Command:

```bash
SMB3_AGENT_FRAME_SLEEP_SECONDS=0.0035 \
python -m smb3_agent task fceux-world-1-king \
  --attempts 1 \
  --artifacts-dir artifacts/fceux/show_world_1_king \
  --capture-images \
  --capture-ticks
```

Pass condition:

- The emulator visibly runs the route.
- If it fails, the failure is reviewed as demo-mode instability, not confused
  with the reliability gate.

Important note:

Visible throttle and screenshot capture can change timing. A watchable demo is
evidence for review, not the source of truth for reliability.

## Gate 5: Contact Sheet Review

Command:

```bash
python -m smb3_agent task fceux-contact-sheet \
  --input-dir artifacts/fceux/show_world_1_king/images
```

Pass condition:

- PNG frames and a contact sheet are produced.
- The sheet is used to inspect where a segment failed or transitioned.

## Gate 6: Log Review

Command:

```bash
python -m smb3_agent task review-fceux-log \
  --log artifacts/fceux/world_1_king/fceux_1_1.log \
  --attempts 10
```

Pass condition:

- Summary matches the expected pass/fail outcome.
- Post-probe fields identify the final route event.

## Future Gates

These are planned gates and should become real commands as the implementation
plan progresses.

```bash
python -m smb3_agent goal validate data/goals/world_1_king.yaml
python -m smb3_agent goal run world_1_king --attempts 3
python -m smb3_agent segment validate data/segments/world_1.yaml
python -m smb3_agent goal status world_1_king
python -m smb3_agent command parse "run world 1 king gate 3 times"
python -m smb3_agent command run "run world 1 king gate 3 times"
python -m smb3_agent recovery simulate life_lost --goal world_1_king
```

Each future command should be added with tests before it becomes a required
gate.
