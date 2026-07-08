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
- right teaching panel for notes attached to route locations

Bottom:

- timeline / attempt log
- Things Mario Still Gets Wrong
- Recent Observations

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

The teaching panel saves notes to the latest session. UI labels map to the
existing note severities:

- failure -> `bug`
- expected behavior -> `objective`
- route instruction -> `map_action`
- validation note -> `harden`
- positive evidence -> `guide_detail`

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
Run World 1 to capture evidence
```

That empty state is acceptable only before evidence exists.

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
- `Teach This Section`
- `Things Mario Still Gets Wrong`
- `Recent Observations`

The rendered HTML should not require old dashboard labels such as:

- `World 1 Control Panel`
- `World 1 Mission Control`
- `Run Controls`
- `World 1 Notes`
- `Route Health`
