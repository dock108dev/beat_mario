# World 1 Control Panel Plan

The control panel is the operator surface for watching World 1, adding notes,
triggering runs, and turning observations into the next controlled experiment.
It must use player-facing guide vocabulary, not backend route identifiers.

Run it with:

```bash
python -m smb3_agent lab ui --host 127.0.0.1 --port 8765
```

Render one HTML file for validation:

```bash
python -m smb3_agent lab ui-render --output artifacts/ui/latest.html
```

## Language Rule

The normal UI must speak in locations and objectives:

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

Backend route ids, script ids, detector ids, and implementation labels are
plumbing. They can exist in artifact files and code, but they should not be the
primary labels in the control panel.

## Location Model

The control panel reads `data/worlds/world_1_locations.yaml`.

Each location defines:

- `id`
- `label`
- `type`
- `default_status`
- `objective`
- `guide_terms`

The model is guide/player vocabulary. The first World 1 model uses common SMB3
walkthrough concepts such as Grass Land, World Map, Fortress, Boom Boom, Super
Leaf, Raccoon Mario, P-meter, Warp Whistle, Toad House, Spade Panel, Hammer
Brother, Airship, Koopaling, wand, and King.

Guide references used for vocabulary:

- StrategyWiki Super Mario Bros. 3 walkthrough:
  <https://strategywiki.org/wiki/Super_Mario_Bros._3/Walkthrough>
- StrategyWiki World 1 page:
  <https://strategywiki.org/wiki/Super_Mario_Bros._3/World_1>
- Super Mario Wiki Super Mario Bros. 3 overview:
  <https://www.mariowiki.com/Super_Mario_Bros._3>
- Super Mario Wiki Super Leaf page:
  <https://www.mariowiki.com/Super_Leaf>
- Super Mario Wiki P-Wing page:
  <https://www.mariowiki.com/P-Wing>

## First Screen

The first screen has four areas:

```text
World 1 Control Panel
-> Run Controls
-> Guide Logic
-> World 1 Notes
-> Open Issues / Recent Notes
```

Run Controls:

- speed selector: `1x`, `2x`, `4x`, `10x`, `25x`, `50x`, `100x`
- attempts selector: `1`, `3`, `5`, `10`
- mode selector: watch route or gate run
- Run World 1
- Unit Tests
- Phase Gate
- Render Check

World 1 Notes:

- one card per location
- status badge
- objective text
- note count
- open issue count
- variant count
- free-form note textarea
- note type selector
- optional anchor selector

## Note Types

The note form supports:

- `note`
- `harden`
- `bug`
- `objective`
- `map action`
- `guide detail`

Examples:

```text
1-1: falls into hole at 283 on clock
1-3: getting the whistle is expected, do not treat it as normal completion
Fortress: needs Raccoon flight, not fire form
Map: after 1-3, move down, down, left
Airship: verify boss transition and king restore
```

## Review Loop

The intended loop is:

1. Run World 1 from the panel.
2. Watch at a useful speed.
3. Add notes to each affected location.
4. Submit notes.
5. Refresh review artifacts.
6. Pick the highest-value issue.
7. Create a Codex task packet.
8. Patch one controlled experiment.
9. Re-run at the selected speed.
10. Promote only after validation evidence exists.

## Current Non-Goals

- Do not turn the UI into a visual route editor yet.
- Do not edit route files directly from textareas.
- Do not promote variants without evidence.
- Do not make World 8 planning depend on perfect World 1 UI polish.

## Validation

Required checks:

```bash
python -m pytest -q
python -m smb3_agent lab ui-render --output artifacts/ui/latest.html
```

The rendered HTML should contain:

- `World 1 Control Panel`
- `Run Controls`
- `World 1 Notes`
- `1-1`
- `1-3`
- `Fortress`
- `Airship`
- `Unit Tests`
- `Phase Gate`
