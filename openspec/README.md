# OpenSpec

Behavioural specifications for DMX Life, in [OpenSpec](https://github.com/Fission-AI/OpenSpec)
format. Specs say **what the system does**, in scenarios concrete enough to test
against. The reasoning behind the design lives in [`docs/adr/`](../docs/adr/).

## Layout

- **`specs/`** — the current system, as built. One directory per capability.
- **`changes/`** — proposed work not yet implemented. Each change holds a
  `proposal.md` (why), `specs/` deltas (what changes), sometimes a `design.md`
  (how), and `tasks.md` (the steps).
- **`changes/archive/`** — completed changes, filed after implementation.

A change's spec files are *deltas* — `## ADDED` / `## MODIFIED` / `## REMOVED`
sections — that get merged into `specs/` once the work lands.

## Capabilities

| Capability | Covers |
|---|---|
| [scene-control](specs/scene-control/spec.md) | Toggling scenes, layering, groups, frame composition |
| [scene-authoring](specs/scene-authoring/spec.md) | Creating, editing, previewing and deleting scenes |
| [configuration-persistence](specs/configuration-persistence/spec.md) | Durable, atomic storage of fixtures/scenes/network settings |
| [fixture-configuration](specs/fixture-configuration/spec.md) | The fixture patch, types, linking, the address map |
| [dmx-output](specs/dmx-output/spec.md) | Art-Net output, crossfades, connection tracking |
| [network-configuration](specs/network-configuration/spec.md) | Art-Net destination, universe, refresh rate |
| [system-monitoring](specs/system-monitoring/spec.md) | Connection indicator, DMX value monitor |
| [access-control](specs/access-control/spec.md) | Authentication |
| [version-display](specs/version-display/spec.md) | Shows the running app's version on every page |

## Open changes

Proposals, none implemented. Roughly in priority order:

| Change | Why it matters |
|---|---|
| [add-pluggable-dmx-backends](changes/add-pluggable-dmx-backends/proposal.md) | Replaces StupidArtnet with our own Art-Net sender behind a `DMXBackend` interface, plus an Enttec DMX USB Pro backend — DMX output becomes configurable per installation instead of Art-Net-only |
| [compact-scene-storage](changes/compact-scene-storage/proposal.md) | Scenes stored as a sparse `{channel: value}` map instead of a 512-entry array — config.json projected 186→61 KB, and retires the `enabledFixtures` dual-meaning wart (ADR-0007) in the same move |
| [add-test-suite](changes/add-test-suite/proposal.md) | Nothing is tested automatically |

## Completed

| Change | Landed |
|---|---|
| [add-daily-config-backup](changes/archive/2026-08-20-add-daily-config-backup/proposal.md) | 2026-08-20 — `ConfigManager.write()` now snapshots config.json to `backups/config-<date>.json` before the first write of each day; every day's snapshot is kept forever, no restore functionality |
| [add-version-display](changes/archive/2026-08-20-add-version-display/proposal.md) | 2026-08-20 — a hand-edited `VERSION` file is read at startup and shown in the footer of every page; falls back to "unknown" if missing; PyInstaller build check left for the next real release |
| [refresh-architecture-docs](changes/archive/2026-08-19-refresh-architecture-docs/proposal.md) | 2026-08-19 — README/ARCHITECTURE.md/SUMMARY.md/copilot-instructions.md corrected; ARCHITECTURE.md shrunk 570→147 lines to an orientation doc pointing at docs/adr/ and openspec/specs/ |
| [thread-safe-dmx-buffers](changes/archive/2026-08-19-thread-safe-dmx-buffers/proposal.md) | 2026-08-19 — a single lock now guards the DMX buffers so every transmitted frame is one composition, never a mixture of two |
| [fix-fixture-link-references](changes/archive/2026-08-19-fix-fixture-link-references/proposal.md) | 2026-08-19 — fixture links now identify their master by name instead of array position; repaired the off-by-one data and added server-side validation |
| [atomic-config-writes](changes/archive/2026-08-19-atomic-config-writes/proposal.md) | 2026-08-19 — config.json is written via a temp file + atomic rename instead of truncate-in-place; new configuration-persistence capability |
| [remove-dead-code](changes/archive/2026-08-19-remove-dead-code/proposal.md) | 2026-08-19 — deleted a 433-line superseded module, duplicate utils, an unused import, and untracked .DS_Store |
| [secure-auth-and-debug](changes/archive/2026-08-19-secure-auth-and-debug/proposal.md) | 2026-08-19 — credentials and the debugger now come from the environment, with a bind-address-based safety check |
| [fix-request-validation](changes/archive/2026-08-19-fix-request-validation/proposal.md) | 2026-08-19 — four endpoints returned 500 on bad input; the scene-delete guard never worked |

## Using the CLI

Installed via `npx` (a global install needs root on this machine):

```bash
npx @fission-ai/openspec@latest list
```

Other useful commands — `validate --all --strict`, `show <name>`,
`status --change <name>`. In Claude Code, `/opsx:apply <change>` works through a
change's tasks, and `/opsx:archive <change>` files it once done.
