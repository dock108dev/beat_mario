# Lab UI Plan

The lab UI is a thin front end over attempt-lab artifacts. It is not a separate
source of truth.

Run it with:

```bash
python -m smb3_agent lab ui --host 127.0.0.1 --port 8765
```

Render one HTML file for validation:

```bash
python -m smb3_agent lab ui-render --output artifacts/ui/latest.html
```

## First Screen

World 1 route map:

```text
Start -> 1-1 -> 1-2 -> 1-3 Whistle -> Fortress Whistle -> 1-4 -> 1-5 -> 1-6 -> Castle
```

Each segment should show:

- current route status
- latest note count
- open issue count
- highest priority issue
- proposal count
- latest validation result

## Note Entry

The user should be able to add multiple notes before submitting:

```text
1-1: falls into hole at 283 clock
1-2: good
1-3: whistle exit expected
fortress: dies first try, then carry-over inputs send map toward 1-4
```

The UI writes the same note schema used by `lab note latest`. On submission it
also regenerates `issues.yaml` and `variant_proposals.yaml`.

## Issue Review

After submission, the UI should show grouped issues:

- actionable route hardening
- recovery bugs
- wrong route state
- expected behavior
- positive evidence

Only actionable issues should offer route proposal generation.

## Codex Integration

The UI exposes a button such as:

```text
Create Codex task for this issue
```

That uses the same command path as the CLI:

```bash
python -m smb3_agent lab codex-task latest --issue ISSUE_ID
```

Codex should receive an evidence packet, not a vague chat summary.

## Non-Goals

- Do not control the emulator from the UI first.
- Do not hide validation gates.
- Do not let UI edits bypass the lab artifact schema.
- Do not make route changes without a variant and validation artifact.
