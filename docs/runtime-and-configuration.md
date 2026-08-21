# Runtime, configuration, and data

This repository is a local Python command-line application with two emulator
adapters and a loopback-only review UI. It has no database, migrations,
long-running worker, scheduler, cloud API, or production deployment target.

## Runtime components

The `smb3_agent` CLI in `src/smb3_agent/cli.py` is the public entry point. Its
commands call five main parts:

1. Goal and segment loaders read tracked YAML contracts under `data/goals/`
   and `data/segments/`.
2. Reliability and goal runs launch a new FCEUX process with
   `scripts/fceux_1_1_agent.lua`, then parse its event log and write an
   inspection report.
3. Attempt Lab records runs, notes, reviews, issue ledgers, and task packets as
   local files.
4. Route Lab serves the same records through Python's threaded HTTP server.
   It binds only to `127.0.0.1`, `::1`, or `localhost` and runs until stopped.
5. Route-patch commands use Git and detached temporary worktrees to preview,
   validate, compare, promote, reject, or roll back an exact reviewed change.

The legacy Mednafen adapter is a separate macOS diagnostic path. It starts the
local `mednafen` executable, uses AppleScript to focus it, Quartz to locate and
capture its window, and `pyautogui` for input. It is not used by the product
reliability gate.

There are no background jobs. An operator starts each CLI, emulator, or Route
Lab process directly. Stopping Route Lab stops the only persistent server
process.

## Operator configuration

The application does not load `.env` files and does not need a sample env file.
There are no credentials or network service endpoints to configure.

| Setting | Used by | Behavior |
| --- | --- | --- |
| `SMB3_GAME_FILE` | Live goal, reliability, task, and Route Lab actions | Absolute or repository-relative path to the operator's local game file. An explicit `--game-file` wins where the command exposes that option. |
| `PYTHON` | `scripts/validate_phase0.sh` | Interpreter used by the repository gate; defaults to `python`. This is a development-script setting, not application configuration. |

Authoritative reliability runs sanitize inherited variables whose names begin
with `SMB3_`, then apply the selected preset from
`src/smb3_agent/presets.py`. The many `SMB3_*` reads in the Lua runner are an
internal Python-to-FCEUX protocol and diagnostic tuning surface. They are not a
supported production configuration API. Low-level diagnostic commands may
accept explicit `--set-env NAME=VALUE` overrides; their output is not accepted
product reliability evidence.

Other behavior is selected through CLI arguments and tracked configuration:

- goal composition and run policy: `data/goals/*.yaml`;
- segment acceptance events: `data/segments/*.yaml`;
- executable preset environment: `src/smb3_agent/presets.py`;
- structured diagnostic input: `data/routes/scripts/*.yaml`;
- Route Lab location labels: `data/worlds/world_1_locations.yaml`.

Use `python -m smb3_agent COMMAND --help` and subcommand help for current CLI
arguments. Goal identifiers can be passed in place of paths to goal commands.

## Local executables and integrations

- FCEUX must be on `PATH` for live FCEUX runs. Python launches it as a local
  subprocess with the tracked Lua script and the operator's game-file path.
- Git must be available for source-state evidence and route-patch worktrees.
- Mednafen, AppleScript, Accessibility permission, screen-capture permission,
  and a visible desktop session are required only by the optional macOS
  diagnostic adapter.
- The standard-library web server and optional default-browser launch are the
  only Route Lab integrations. Route Lab makes no cloud or external HTTP calls.

Python dependencies and the supported Python version are declared in
`pyproject.toml`; the locked local resolution is in `uv.lock`. GitHub Actions
installs the declared development extra on Python 3.11 and runs the ROM-free
gate.

## Persistence and data ownership

Tracked YAML files under `data/goals/`, `data/segments/`, `data/routes/`, and
`data/worlds/` are repository inputs. Tests also use tracked PNG fixtures under
`data/fixtures/`. There is no relational or remote data store.

Generated state is filesystem-only and ignored by Git:

| Path | Contents |
| --- | --- |
| `artifacts/reliability/<goal>/` | Timestamped authoritative batch logs, execution metadata, and reports. |
| `artifacts/review/<goal>/` | Timestamped throttled watch playback and review images. |
| `artifacts/sessions/` | Attempt Lab sessions; `latest.txt` points to the latest local session. |
| `artifacts/route-patches/<patch-id>/` | Imported patch contract, state, diffs, validation output, comparison evidence, and audit records. |
| `artifacts/ui/last_command.yaml` | Most recent Route Lab command result for local display. |
| `public/assets/local/` | Optional ignored local artwork used by Route Lab. |

Treat `artifacts/` as local evidence, not as a durable shared store. Back it up
separately if a run must be retained. Never commit game files, savestates,
screenshots, logs, generated evidence, or copyrighted local UI assets.

## Deployment and operations boundary

There is no production service deployment, container image, package registry
release, database bootstrap, health endpoint, or service-manager definition.
The supported operating model is a repository checkout on an engineer's
machine. Route Lab is an operator convenience surface, not a deployable web
application: it has no TLS, user accounts, or remote-access authentication and
must remain on loopback.

For routine operation, run the canonical ROM-free gate before a change. For a
live route change, also run the selected goal's authoritative reliability
profile and a separate watch playback as described in
[World 8 reliability gates](reliability-gate.md). Preserve the resulting local
evidence directory and record its exact path when reporting acceptance.
