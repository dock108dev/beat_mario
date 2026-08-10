# World 1 Diagnostic Lab Guide

Use this guide when explicitly repairing the legacy World 1 king diagnostic.
It is not the active World 8 route and its result is not product progress.

## Setup

From the repo root:

```bash
source .venv/bin/activate
export SMB3_GAME_FILE=/path/to/local-game-file
```

FCEUX must be available on `PATH`.

## Watch A Route

Run the explicit diagnostic at regular review speed:

```bash
python -m smb3_agent lab start "run world 1 king diagnostic gate 1 times at 1x" --attempts 1
```

Watch faster:

```bash
python -m smb3_agent lab start "run world 1 king diagnostic gate 1 times at 4x" --attempts 1
python -m smb3_agent lab start "run world 1 king diagnostic gate 1 times at 10x" --attempts 1
```

Run a reliability-style gate:

```bash
python -m smb3_agent lab start "run world 1 king diagnostic gate 3 times" --attempts 3
```

Run the path at an explicit speed:

```bash
python -m smb3_agent lab start "run world 1 king diagnostic gate 3 times at 4x" --attempts 3
python -m smb3_agent lab start "run world 1 king diagnostic gate 1 times at 100x" --attempts 1
```

Speed notes:

- `1x` is for watching and taking notes.
- `2x` through `10x` is for faster review.
- Gate runs use maximum mode and should be treated as reliability evidence.
- Watchable runs can alter timing, so use them for diagnosis before promotion.

## Add Notes

After a run, attach notes to the latest session:

```bash
python -m smb3_agent lab note latest \
  "1-1 around 320 timer: falls into the hole and usually gets lucky"
```

With explicit anchors:

```bash
python -m smb3_agent lab note latest \
  "Castle flight starts too far right and hits ceiling blocks" \
  --segment fortress \
  --severity harden
```

The raw note text is preserved in the session's `notes.yaml`.

## Review The Session

```bash
python -m smb3_agent lab review latest
```

This writes:

- `review.md`
- `review.yaml`

The review links notes to route-log evidence and recommends one controlled
experiment.

Batch flow:

```bash
python -m smb3_agent lab issues latest
python -m smb3_agent lab propose-variants latest
python -m smb3_agent lab ui-summary latest
python -m smb3_agent lab codex-task latest --issue ISSUE_ID
```

## Propose A Variant

```bash
python -m smb3_agent lab propose-variant latest
```

This creates a YAML proposal under `data/variants/`. It does not edit the
baseline route.

For multi-note sessions, treat this as a compatibility shortcut. The intended
next behavior is one proposal per actionable issue.

## Apply And Validate A Route Patch

Create a Codex task for the reviewed issue, then import its normalized
`beat-mario.route-patch/v1` output:

```bash
python -m smb3_agent lab patch import PATCH.yaml
python -m smb3_agent lab patch review PATCH_ID
python -m smb3_agent lab patch preview PATCH_ID
python -m smb3_agent lab patch prepare PATCH_ID
python -m smb3_agent lab patch validate PATCH_ID
python -m smb3_agent lab patch compare PATCH_ID
```

Validation runs the actual patched candidate in a detached Git worktree and
records separate parent evidence. Descriptive variants cannot validate.

## Promotion Guard

Promotion is intentionally guarded:

```bash
python -m smb3_agent lab promote-variant world_1_1_harden_320_a
python -m smb3_agent lab patch promote PATCH_ID --confirm PATCH_ID
```

The route-patch command refuses unless review, candidate application, validation,
comparison, hashes, artifacts, HEAD, and the accepted worktree all pass. It
writes the exact validated bytes plus an inverse rollback artifact.

## Current World 1 Workflow

1. Run `lab start "run world 1 king diagnostic gate 1 times at 1x" --attempts 1`.
2. Add notes while the issue is fresh.
3. Run `lab review latest`.
4. Run `lab propose-variant latest`.
5. Import, review, preview, and prepare the exact patch.
6. Validate its isolated candidate and compare it with the parent.
7. Promote only the exact recommended diff with patch-id confirmation.

Example loop:

```bash
python -m smb3_agent lab start "run world 1 king diagnostic gate 1 times at 4x" --attempts 1
python -m smb3_agent lab note latest "1-4 platform gap is inconsistent under watch speed"
python -m smb3_agent lab review latest
python -m smb3_agent lab propose-variant latest
python -m smb3_agent lab codex-task latest --issue ISSUE_ID
python -m smb3_agent lab patch import PATCH.yaml
python -m smb3_agent lab patch review PATCH_ID
python -m smb3_agent lab patch prepare PATCH_ID
python -m smb3_agent lab patch validate PATCH_ID
python -m smb3_agent lab patch compare PATCH_ID
```

Replace `PATCH_ID` with the id in the imported contract.

## Batch Workflow

Use this shape when you have notes across several World 1 locations:

1. Run the route once.
2. Add notes across many locations.
3. Generate an issue ledger.
4. Review grouped issues.
5. Generate one proposal per actionable issue.
6. Create a Codex task packet for the issue you want patched first.
7. Validate only the selected reviewed patch in its candidate worktree.

Example command flow:

```bash
python -m smb3_agent lab start "run world 1 king diagnostic gate 1 times at 4x" --attempts 1
python -m smb3_agent lab note latest "1-1 falls into hole at 283 on clock." --segment world_1_1 --severity harden
python -m smb3_agent lab note latest "1-2 and 1-3 are perfect. 1-3 whistle exit is expected." --segment world_1_3 --severity note
python -m smb3_agent lab note latest "Castle dies first try every time, then carry-over inputs seem to send the route to 1-4." --segment fortress --severity harden
python -m smb3_agent lab issues latest
python -m smb3_agent lab propose-variants latest
python -m smb3_agent lab codex-task latest --issue ISSUE_ID
```

## Mario Route Lab

Start Mario Route Lab:

```bash
python -m smb3_agent lab ui --host 127.0.0.1 --port 8765
```

Open:

```text
http://127.0.0.1:8765
```

The UI lets you:

- run World 1 at 1x, 2x, 4x, 10x, 25x, 50x, or 100x
- choose watch mode or gate mode
- trigger unit tests, the phase gate, and an HTML render check
- inspect Route and Evidence as the primary workflow
- teach selected World 1 locations using player-facing names
- submit the batch to the latest session
- regenerate issues and proposals
- create Codex task packets for actionable issues

Use location names in the lab:

- Map
- 1-1
- 1-2
- 1-3
- Fortress
- 1-4
- Toad House
- Spade Panel
- Hammer Brother
- 1-5
- 1-6
- Airship
- King

Mario Route Lab intentionally hides backend route labels from the normal
workflow.
