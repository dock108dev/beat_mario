# Documentation index

Use the root [README](../README.md) to install, validate, and start the supported
flows. The documents below provide implementation and operating detail.

## Develop and modify

- [Development and repository structure](development.md): layout, entry points,
  environment, validation, and intentionally large files.
- [Single sources of truth](ssot.md): authoritative modules and retained paths.
- [Agent architecture](agent-architecture.md): component responsibilities.
- [Goal contracts](goal-contract.md): route composition and execution contract.
- [Route patch schema](route-patch-schema.md): reviewed change lifecycle.

## Run and operate

- [World 8 reliability gates](reliability-gate.md): authoritative and watchable
  runs, evidence, and failure behavior.
- [Mario Route Lab](mario-route-lab.md): local review UI and attempt workflow.
- [FCEUX harness](fceux-harness.md): low-level emulator runner and diagnostics.
- [Error handling and operations](error-handling.md): failure artifacts,
  response behavior, and incident checks.

## Product and evidence

- [Product direction](product-direction.md): current product boundary.
- [Route status](route-status.md): accepted route and evidence history.

## Security and local data

- [Security model](security.md): trust boundaries, implemented controls, and
  deferred security work.
- [Local Route Lab assets](local-assets.md): optional ignored UI images.

Historical build plans and duplicated validation checklists are intentionally
not retained. Current contracts, tests, source modules, and the canonical gate
describe how the repository works today.
