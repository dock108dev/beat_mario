# Mario Route Lab

Mario Route Lab is the local evidence-first route review surface. It answers:

- Where is Mario in the selected route?
- What is proved, bridged, planned, or failing?
- What should be observed or repaired next?

It is not a generic operations dashboard. The CLI, goal contract, catalog, and
artifact schemas remain the source of truth.

## Active route

The default selected goal is `world_8_double_whistle`. Route Lab loads its
declared segment catalog and renders exactly this contract order:

1. Fresh Start
2. 1-1
3. 1-2
4. 1-3 whistle
5. Fortress whistle
6. 1-5
7. 1-6
8. Airship / King
9. World 2 Map with both whistles
10. First Whistle (World 2)
11. Warp Zone 5 / 6 / 7
12. Second Whistle (Warp Zone)
13. Warp Zone World 8
14. World 8 Pipe
15. World 8 Map

World 1-4 is not rendered because it is not in the active contract. World 7 is
not a route destination; it appears only in the visible Warp Zone tier label.

Each route row uses player-facing language and displays its role:

- `goal milestone` for owner-required outcomes;
- `required path` for game traversal needed to reach the next milestone;
- truthful state such as Learned, Needs Validation, or Planned.

Planned steps never appear as learned or solved.

## Layout

The established layout remains:

- top run strip;
- Route index;
- Evidence viewer;
- Teach Mario panel;
- Latest Attempt, Active Problems, and Observation History.

The route correction changes content and source-of-truth plumbing, not the page
structure.

## Primary action

`Run World 8 Route` is the only strong primary button. The active goal is
currently planned, so attempting to run it returns an honest not-yet-executable
error. It does not run the World 1 king diagnostic.

Unit tests, phase gate, HTML render check, refresh, note, lifecycle, and Codex
task actions remain secondary or quiet controls.

## Evidence behavior

The selected route row drives the evidence and teaching panels. Evidence may
come from a screenshot, contact sheet, log, state trace, note, issue, or
proposal. Assisted evidence must remain labeled; a bridge screenshot cannot be
presented as normal gameplay proof.

The current live boundary is the post-Fortress World 1 route. World 2 and later
rows remain Planned until independent live observations exist.

## Route roles and observations

Notes and issues continue to use human locations while retaining segment ids in
artifacts. New active mappings include:

- `world_2_map_arrival_with_two_whistles` -> World 2 Map
- `world_2_first_whistle_use` -> First Whistle (World 2)
- `warp_zone_5_6_7_tier` -> Warp Zone 5 / 6 / 7
- `warp_zone_second_whistle_use` -> Second Whistle (Warp Zone)
- `warp_zone_world_8_tier` -> Warp Zone World 8
- `world_8_pipe_entry` -> World 8 Pipe
- `world_8_map_arrival` -> World 8 Map

## Commands

Render once:

```bash
python -m smb3_agent lab ui-render \
  --output artifacts/ui/world_8_double_whistle.html
```

Serve locally:

```bash
python -m smb3_agent lab ui --host 127.0.0.1 --port 8765
```

Inspect the contract independently:

```bash
python -m smb3_agent goal status world_8_double_whistle
```

## Visual contract

Keep the current warm off-white page, white panels, dark text, neutral borders,
blue selection, and restrained red/green/amber state treatments. Preserve the
semantic render hooks:

- `primary-button`
- `secondary-button`
- `segmented-control`
- `segment-active`
- `route-item-selected`
- `status-failed`
- `status-learned`
- `status-validation`

Tests assert these hooks and the exact contract-derived route, not color values.

## Diagnostic route

The bridge-assisted `world_1_king` route remains explicitly selectable from
the CLI under its diagnostic name. It is intentionally not the default Route
Lab route and its king marker is not a World 8 success state.
