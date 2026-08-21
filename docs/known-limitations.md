# Known limitations

These boundaries are implemented or directly implied by the current runtime;
they are not unverified product promises.

## Live validation requires local assets

The repository does not contain or download a game file. ROM-free tests verify
contracts, parsers, reports, security controls, and deterministic rendering,
but they cannot prove emulator startup, route timing, gameplay success, or the
game-owned ending. That proof requires an operator-supplied game file, FCEUX,
and the goal-specific fresh-run gate.

Ignored gameplay artifacts are local-only. They are neither uploaded nor
replicated, so another checkout cannot reproduce an acceptance claim without
the recorded source revision, compatible local runtime, and a fresh run.

## Platform support

FCEUX is the supported live product adapter. The older Mednafen diagnostic
adapter is macOS-only and depends on a visible desktop plus Accessibility and
screen-capture permissions. Headless Mednafen operation and non-macOS Mednafen
control are unsupported.

The ROM-free CI job runs on Linux and intentionally does not install or start
either emulator.

## Route Lab is local-only

Route Lab accepts only loopback bind hosts. It is not designed for LAN,
internet, multi-user, or unattended deployment. It has request-size limits,
CSRF protection, safe artifact serving, and serialized mutation actions, but
it does not provide TLS, accounts, durable sessions, backups, or an availability
guarantee. Local artifact files remain the source of its displayed state.

## No autonomous service operation

There is no scheduler, queue, worker, daemon, retry service, telemetry backend,
or alerting integration. Commands run synchronously under operator control.
Failures are written into local reports where the command supports them; an
engineer must inspect and respond to those reports.

## Maintenance follow-ups

- Splitting the large FCEUX Lua runner requires a loader/module design and live
  regression evidence; line-count-only extraction is unsafe.
- Extracting Route Lab's embedded HTML and CSS would improve maintainability,
  but needs snapshot or browser-level coverage before changing its rendering
  boundary.
- A production web deployment, shared evidence store, or remote orchestration
  model would require explicit product and security design. None should be
  inferred from the local UI.
- The CI dependency installation uses the declared version ranges rather than
  the `uv.lock` resolution. Changing CI to enforce the lock is a separate build
  reproducibility decision.
