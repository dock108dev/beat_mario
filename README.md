# SMB3 Route Agent

An automation harness for controlling and observing Super Mario Bros. 3 in a local NES emulator.

The first target is not a general game-playing AI. The first target is a reliable loop:

```text
launch emulator -> focus window -> capture game viewport -> send input -> save evidence
```

## Setup

```bash
source .venv/bin/activate
python -m pip install -e .
```

macOS must trust the app that launches the command for Accessibility:

```text
System Settings -> Privacy & Security -> Accessibility
```

Enable Codex, Terminal, iTerm, or whichever app launches the command. Quit and reopen that app after enabling it.

Place a legally obtained SMB3 NES game file at:

```text
./game-file.nes
```

NES game files, generated attempt artifacts, and local save states are intentionally not committed.

FCEUX is the current reliable route backend. The older Mednafen tasks remain useful for
window/capture experiments, but the working World 1-1 route uses FCEUX memory reads
and Lua input control.

## Controls

Mednafen player 1 is configured as:

```text
Arrows: D-pad
Z: B / run
X: A / jump
Return: Start
Tab: Select
```

## Probe

Run:

```bash
python -m smb3_agent probe mednafen
```

The probe launches Mednafen, focuses its window, autodetects the window bounds across monitors, captures before/after screenshots, presses Start, and writes artifacts under `artifacts/probes/`.

## Start Game

Run:

```bash
python -m smb3_agent task start-game
```

The task launches Mednafen, focuses its window, presses through the early Start flow, captures the game viewport after each step, writes artifacts under `artifacts/tasks/start-game/`, and refreshes detector fixtures under `data/fixtures/state/`.

## Enter 1-1

Run:

```bash
python -m smb3_agent task enter-1-1
```

The task starts a fresh game, enters World 1-1 from the World 1 map, captures each state transition, and refreshes `data/fixtures/state/level_1_1_start.png`.

## Checkpoint 1-1

Run:

```bash
python -m smb3_agent task checkpoint-1-1
```

The task starts a fresh game, enters World 1-1, verifies the final screenshot with the fixture detector, saves Mednafen state slot 0, and records which save-state file changed.

## Load 1-1 Checkpoint

Run:

```bash
python -m smb3_agent task load-checkpoint-1-1
```

The task launches Mednafen, loads save-state slot 0, captures the game viewport, and verifies the detector sees `LEVEL_1_1`.

## Run 1-1 Script

Run:

```bash
python -m smb3_agent task run-1-1-script
```

The task launches Mednafen, loads the 1-1 checkpoint, verifies the detector sees `LEVEL_1_1`, executes `data/routes/scripts/world_1_1_draft.yaml`, writes `input_trace.jsonl`, and captures the before/after frames.

Current verified route:

```bash
python -m smb3_agent task checkpoint-1-1 --slot 0
python -m smb3_agent task run-1-1-script --slot 0 --script data/routes/scripts/world_1_1_draft.yaml
```

The latest route clears World 1-1 from the clean 1-1 checkpoint and returns to the World 1 map.

## FCEUX 1-1 Reliability Gate

Run:

```bash
python -m smb3_agent task fceux-1-1 --attempts 10 --artifacts-dir artifacts/fceux/cli_gate_1_1 --require-perfect
```

The command runs `scripts/fceux_1_1_agent.lua`, writes a route log, parses the
attempt markers, and exits non-zero unless every attempt clears World 1-1.

Expected summary:

```text
successes=10/10
bad_states=0/10
```

If screenshots are enabled, convert FCEUX `.gd` captures to PNG and create a
contact sheet:

```bash
python -m smb3_agent task fceux-1-1 --attempts 1 --artifacts-dir artifacts/fceux/inspect_1_1 --capture-images
python -m smb3_agent task fceux-contact-sheet --input-dir artifacts/fceux/inspect_1_1/images
```

The contact sheet is a review aid only. Route success is based on route log
markers, not visual inspection.

## FCEUX Enter 1-2 Probe

Run:

```bash
python -m smb3_agent task fceux-1-1 --attempts 1 --artifacts-dir artifacts/fceux/probe_enter_1_2 --capture-images --capture-ticks --after-attempt-frames 900 --post-1-1-probe enter_1_2 --require-perfect
```

This clears World 1-1, waits for the World 1 map, moves right twice, presses A,
and captures the next level start. The confirmed 1-2 start signature is a level
screen with Mario near `x=24`.

To run the current naive 1-2 exploration after entering 1-2:

```bash
python -m smb3_agent task fceux-1-1 --attempts 1 --artifacts-dir artifacts/fceux/probe_run_1_2 --capture-images --capture-ticks --after-attempt-frames 900 --post-1-1-probe run_1_2_naive --require-perfect
python -m smb3_agent task review-fceux-log --log artifacts/fceux/probe_run_1_2/fceux_1_1.log --attempts 1
```

Current known result: the probe clears the first pipe gap and reaches roughly
`post_probe_max_x=1333` before failing in the steep-hill enemy cluster.

## Detect

Run:

```bash
python -m smb3_agent detect --image data/fixtures/state/world_1_map.png
```

The detector compares a screenshot against the stable state fixtures and returns the best state match with RMSE/confidence scores.
