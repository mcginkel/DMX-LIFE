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
| [fixture-configuration](specs/fixture-configuration/spec.md) | The fixture patch, types, linking, the address map |
| [dmx-output](specs/dmx-output/spec.md) | Art-Net output, crossfades, connection tracking |
| [network-configuration](specs/network-configuration/spec.md) | Art-Net destination, universe, refresh rate |
| [system-monitoring](specs/system-monitoring/spec.md) | Connection indicator, DMX value monitor |
| [access-control](specs/access-control/spec.md) | Authentication |

## Open changes

Proposals, none implemented. Roughly in priority order:

| Change | Why it matters |
|---|---|
| [atomic-config-writes](changes/atomic-config-writes/proposal.md) | An interrupted write can leave the whole show configuration unparseable |
| [fix-fixture-link-references](changes/fix-fixture-link-references/proposal.md) | Stored fixture links are off by one, including two self-references |
| [thread-safe-dmx-buffers](changes/thread-safe-dmx-buffers/proposal.md) | Buffers are shared between threads with no synchronisation |
| [add-test-suite](changes/add-test-suite/proposal.md) | Nothing is tested automatically |
| [refresh-architecture-docs](changes/refresh-architecture-docs/proposal.md) | README and ARCHITECTURE.md describe behaviour that no longer exists |

## Completed

| Change | Landed |
|---|---|
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
