# World 1 Lab Guide

Use this guide when you want to watch the current World 1 route, add notes, and
turn those notes into the next route experiment.

## Setup

From the repo root:

```bash
source .venv/bin/activate
export SMB3_GAME_FILE=/path/to/local-game-file
```

FCEUX must be available on `PATH`.

## Watch A Route

Watch the current route at regular speed:

```bash
python -m smb3_agent lab start "show me the route at 1x" --attempts 1
```

Watch faster:

```bash
python -m smb3_agent lab start "show me the route at 4x" --attempts 1
python -m smb3_agent lab start "show me the route at 10x" --attempts 1
```

Run a reliability-style gate:

```bash
python -m smb3_agent lab start "run world 1 king gate 3 times" --attempts 3
```

Run the path at an explicit speed:

```bash
python -m smb3_agent lab start "run world 1 king gate 3 times at 4x" --attempts 3
python -m smb3_agent lab start "run world 1 king gate 1 times at 100x" --attempts 1
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
  --segment world_1_fortress_whistle \
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

## Propose A Variant

```bash
python -m smb3_agent lab propose-variant latest
```

This creates a YAML proposal under `data/variants/`. It does not edit the
baseline route.

## Validate A Variant

Use the variant id printed by the proposal command:

```bash
python -m smb3_agent lab run-variant world_1_1_harden_320_a --attempts 10
python -m smb3_agent lab compare-variant world_1_1_harden_320_a
```

The current first version validates the active route under the proposed variant
name and records the evidence. As the route editor gets smarter, this is where
actual route-file changes will be applied and compared.

## Promotion Guard

Promotion is intentionally guarded:

```bash
python -m smb3_agent lab promote-variant world_1_1_harden_320_a
```

The command refuses to promote unless the variant has a passing validation
artifact. When promotion succeeds, it writes baseline metadata and backs up the
previous baseline metadata under `data/variants/backups/`.

## Good World 1 Workflow

1. Run `lab start "show me the route at 1x" --attempts 1`.
2. Add notes while the issue is fresh.
3. Run `lab review latest`.
4. Run `lab propose-variant latest`.
5. Validate the variant with 3 attempts first.
6. If it looks promising, validate with 10 attempts.
7. Promote only if the gate passes and the review makes sense.

Example loop:

```bash
python -m smb3_agent lab start "show me the route at 4x" --attempts 1
python -m smb3_agent lab note latest "1-4 platform gap is inconsistent under watch speed"
python -m smb3_agent lab review latest
python -m smb3_agent lab propose-variant latest
python -m smb3_agent lab run-variant VARIANT_ID --attempts 3
python -m smb3_agent lab compare-variant VARIANT_ID
```

Replace `VARIANT_ID` with the id printed by `lab propose-variant`.
