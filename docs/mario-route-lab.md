# Mario Route Lab

Mario Route Lab is the local UI for reviewing, teaching, and validating the
World 1 route. It is not a dashboard. Its visible model is the experiment loop:

```text
run -> observe -> annotate -> patch -> validate -> promote
```

Every visible element should answer one of three questions:

- Where is Mario?
- What went wrong?
- What should he do next?

Run it with:

```bash
python -m smb3_agent lab ui --host 127.0.0.1 --port 8765
```

Render one HTML file for validation:

```bash
python -m smb3_agent lab ui-render --output artifacts/ui/latest.html
```

## Product Model

The primary object is evidence from the latest route attempt. The route path is
the index into that evidence. Notes, issues, variants, and Codex task packets
are secondary actions attached to the selected route location.

The operator should think:

- where Mario is in World 1
- which action failed or still needs validation
- what instruction or validation note should be attached before the next run

The operator should not think in dashboard metrics, tickets, or backend route
identifiers.

## Layout

Top:

- compact title: `Mario Route Lab`
- current session
- run button
- speed selector
- attempt selector
- last run result

Main:

- left route index: Map, 1-1, 1-2, 1-3, Fortress, 1-4, Toad House,
  Spade Panel, Hammer Brother, 1-5, 1-6, Airship, King
- center evidence viewer with latest screenshot/contact sheet when available
- right `Teach Mario` panel for the selected route location only

Bottom:

- Latest Attempt
- Active Problems
- Observation History

## Language Rule

The normal UI must speak in player-facing locations and objectives:

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
primary UI labels.

## Location Model

Mario Route Lab reads `data/worlds/world_1_locations.yaml`.

Each location defines:

- `id`
- `label`
- `type`
- `default_status`
- `objective`
- `guide_terms`

The model uses guide/player vocabulary such as Grass Land, World Map, Fortress,
Boom Boom, Super Leaf, Raccoon Mario, P-meter, Warp Whistle, Toad House, Spade
Panel, Hammer Brother, Airship, Koopaling, wand, and King.

## Teaching Notes

The teaching panel renders one add-observation form for the selected location.
It must not render a form for every route location. UI labels map to the
existing note severities:

- failure -> `bug`
- expected behavior -> `objective`
- route instruction -> `map_action`
- validation note -> `harden`
- positive evidence -> `guide_detail`

Existing observations are operable, not write-only. Each observation supports:

- edit
- delete
- mark resolved
- mark expected behavior
- convert to issue
- archive

Those controls are progressively disclosed. Default observation rows are compact
summaries with a `Review` link. Full controls appear only for the selected
observation in Review Notes mode.

Active issues support:

- mark resolved
- mark expected behavior / not a bug
- mark needs rerun
- create Codex task
- archive
- delete

Default issue rows are compact summaries with a `Review` link. Full controls
appear only for the selected issue in Fix Issue mode.

Examples:

```text
1-1: Mario jumps too late at the hole near 283 on the clock.
1-3: Whistle exit is expected; do not treat it as normal course completion.
Fortress: preserve P-meter before trying the above-ceiling flight route.
Map: after 1-3, move down, down, left.
Airship: verify boss transition and king restore.
```

## Evidence

The evidence viewer looks for screenshots/contact sheets in the latest session
or in artifact paths printed by the latest panel command. It renders the first
available image from those artifact roots and links to related files in the
attempt log.

If no image exists, the center pane shows:

```text
No screenshot captured yet
```

That empty state stays compact so it does not dominate the screen before real
evidence exists.

## Visual System

Cream is only the page background. Cards, inputs, and secondary buttons use
white or near-white surfaces so the panels read clearly on top of the grid.

The UI uses these roles:

- primary text: dark charcoal
- secondary text: muted slate
- cards: true white
- internal surfaces: near-white
- selected route and active review rows: blue-tinted background with a blue
  left rail
- active teaching mode: dark navy filled segment with white text
- failed state: red chip/text only
- learned state: green chip/text
- needs validation: amber chip/text

`Run World 1` is the only strong primary button. Other actions are secondary or
quiet controls. Destructive lifecycle actions remain small quiet buttons rather
than red blocks.

Render tests assert stable visual hooks instead of exact color values:

- `primary-button`
- `secondary-button`
- `segmented-control`
- `segment-active`
- `route-item-selected`
- `status-failed`
- `status-learned`
- `status-validation`

## Local Assets

Optional local-only UI art lives under:

```text
public/assets/local/
```

The directory is ignored by git except `.gitkeep`. Missing images render CSS
text fallbacks. See `docs/local-assets.md`.

## Validation

Required checks:

```bash
python -m pytest -q
python -m smb3_agent lab ui-render --output artifacts/ui/latest.html
```

The rendered HTML should contain:

- `Mario Route Lab`
- `Run World 1`
- `Route`
- `Evidence`
- `Teach Mario`
- `Active Problems`
- `Observation History`
- compact issue rows with `Review`
- compact observation rows with `Review`
- one selected detail area with lifecycle actions
- exactly one primary button: `Run World 1`
- visual hooks for primary, secondary, segmented-control, active segment,
  selected route, failed, learned, and validation states

The rendered HTML should not require old dashboard labels such as:

- `World 1 Control Panel`
- `World 1 Mission Control`
- `Run Controls`
- `World 1 Notes`
- `Route Health`
