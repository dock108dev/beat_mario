# Single sources of truth

This repository keeps policy in the narrowest domain owner and routes CLI,
Route Lab, tests, and documentation through that owner.

## Goal identity, composition, and display

Domain: routing, product-goal configuration, and Route Lab goal metadata.

SSOT module/file: `data/goals/*.yaml`, loaded by `smb3_agent.goals`.

Why this is authoritative: contracts declare goal identity, prefix composition,
route steps, execution state, runner preset, success metrics, and display text.

Known callers: goal CLI, command runner, segment validation, reliability,
Route Lab, recovery, and attempt lab

`load_product_goal_contracts()` discovers executable product contracts and
orders them by resolved route length. Route Lab does not maintain a second goal
id, label, or subtitle registry. Adding a product goal without a matching
reliability acceptance profile fails the SSOT drift test.

## Preset execution policy

Domain: preset-to-environment execution policy.

SSOT module/file: `src/smb3_agent/presets.py`.

Why this is authoritative: `PRESET_ENV` is the only mapping from a contract's
preset name to fixed FCEUX environment settings.

Known callers: `run_goal_contract()` and tests that verify every contract
preset is represented exactly once

Goal validation derives its supported executable presets from this mapping.
Diagnostic bridge permission derives from `DIAGNOSTIC_PRESETS`; callers do not
repeat a preset switch. Goal-local `runner.env` is rejected so a contract cannot
silently shadow the preset policy.

## Product acceptance

Domain: fresh-run counts, boundaries, focused evidence, timeouts, and
byte-identity requirements.

SSOT module/file: `src/smb3_agent/reliability.py` (`RELIABILITY_PROFILES`).

Why this is authoritative: these are acceptance rules, distinct from the goal's
route definition and the Lua executor's behavior.

Known callers: `reliability run`, `reliability watch`, route-patch validation,
and reliability tests

The profile keys must equal the product-goal contract ids. This guard prevents
either catalog from silently gaining a product path the other does not know.

## Route changes and promotion

Domain: reviewed code changes, isolated validation, promotion, and rollback.

SSOT module/file: `src/smb3_agent/route_patch.py`.

Why this is authoritative: it enforces the normalized schema, provenance,
allowlists, hashes, detached worktree, validation profile, exact promotion, and
inverse rollback contract.

Known callers: `lab patch` CLI, Route Lab patch actions, and Codex task packets

`lab propose-variants latest` may create descriptive work proposals, but they
cannot execute, compare, or promote. The former metadata-only execution and
promotion commands were removed instead of retained as failing compatibility
paths.

## Rendering and local administration

Domain: Route Lab HTTP behavior and rendering.

SSOT module/file: `src/smb3_agent/lab_ui.py`.

Why this is authoritative: one handler owns supported GET/POST routes, browser
security policy, form validation, CSRF, artifact serving, and rendering.

Known callers: `lab ui`, `lab ui-render`, the canonical gate, and HTTP tests

The static HTML renderer intentionally has no live CSRF token and is not an
interactive server artifact. The hosted server injects one token into every
POST form.

## Retained supported paths

- `goal run world_1_king` remains the explicit legacy diagnostic. Its duplicate
  `task fceux-world-1-king` wrapper was removed.
- `task fceux-1-1` remains a low-level harness diagnostic because it exposes
  direct runner controls not represented by a goal contract; it is not product
  acceptance.
- Mednafen remains a macOS-only diagnostic adapter. It is separate from the
  FCEUX product runner and fails explicitly on unsupported hosts.
- User-command aliases remain supported input normalization; execution still
  resolves to a goal contract and `run_goal_contract()`.

## Removed compatibility paths

- `lab propose-variant latest`; use `lab propose-variants latest`.
- `lab run-variant`, `lab compare-variant`, and `lab promote-variant`; use the
  `lab patch` lifecycle.
- `task fceux-world-1-king`; use `goal run world_1_king`.

The canonical tests contain a static guard preventing these parser entries and
lab functions from returning.
