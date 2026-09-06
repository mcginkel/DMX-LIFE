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
- **`nice-to-have/`** — ideas captured as changes but not planned work. Kept
  outside `changes/` so that everything in there means "we intend to build
  this". See [its README](nice-to-have/README.md) for what is parked and how to
  promote one back.

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

Proposals, none implemented. `kind` says what sort of work it is, `when` says
how committed it is - `next` is ordered, `soon` is intended but unscheduled.

| Change | Kind | When | Why it matters |
|---|---|---|---|
| [separate-operator-data](changes/separate-operator-data/proposal.md) | capability | next | Operator data lives in the repo working tree, so `git checkout` deployment and saving a scene are in each other's way. Precondition for backup, sync and multi-show. Fully specced, ready to implement |
| [per-channel-participation](changes/per-channel-participation/proposal.md) | bug | next | Opening `extraLampSpreker` in the editor and saving it silently widens it from 5 claimed channels to 26. A working scene can be destroyed with no warning |
| [migrate-scenes-on-repatch](changes/migrate-scenes-on-repatch/proposal.md) | capability | soon | Scenes address the rig by DMX channel, so moving a fixture silently points them at the wrong lamps. Same failure ADR-0010 fixed for fixture links, one level up |
| [scene-editor-ergonomics](changes/scene-editor-ergonomics/proposal.md) | polish | soon | The editor lists scenes in storage order, ignoring the grouping the main page uses, and a new scene does not preview until a control is touched |
| [propagate-scene-state](changes/propagate-scene-state/proposal.md) | capability | soon | Two browsers controlling the rig show different pictures of what is live until one is reloaded |
| [fixture-library-as-data](changes/fixture-library-as-data/proposal.md) | capability | soon | Fixture types are hardcoded in Python, so adding a lamp means editing source. The largest barrier to anyone else using this |
| [add-test-suite](changes/add-test-suite/proposal.md) | capability | soon | Nothing is tested automatically. Note two of its tasks target composition rules that `compact-scene-storage` removed, and its crossfade tests need a clock seam that does not exist |

Parked in [`nice-to-have/`](nice-to-have/README.md): `add-pi-native-dmx-backend`,
`sync-show-data-via-git`, `per-scene-files`.

## Completed

| Change | Landed |
|---|---|
| [refresh-dark-theme](changes/archive/2026-09-06-refresh-dark-theme/proposal.md) | 2026-09-06 — the surface ladder widened from ~20 to ~55 luminance units, and scene states stopped depending on hue alone: active is a solid bright fill, off scenes are recessed below the idle surface, active states carry an edge bar, and the disconnected indicator is a triangle. Prompted by three palette variants reading as identical to a slightly colourblind operator. Archived with the dark-room check at the venue still outstanding |
| [add-pluggable-dmx-backends](changes/archive/2026-09-01-add-pluggable-dmx-backends/proposal.md) | 2026-09-01 — DMX output goes through a `DMXBackend` interface; StupidArtnet removed, Art-Net re-implemented byte-identically and verified against a pre-change capture, Enttec DMX USB Pro backend added. Archived at 24/28: the remaining tasks need an Enttec Pro that is no longer being bought, and rig access to confirm output. New `dmx-hardware-backends` capability |
| [compact-scene-storage](changes/archive/2026-08-30-compact-scene-storage/proposal.md) | 2026-08-30 — scenes store a sparse `{channel: value}` map instead of a 512-entry array; `enabledFixtures` retired (ADR-0007) with its two composition rules collapsed into one, and the editor's per-fixture selection now derived from which channels a scene claims. config.json 186→27 KB; 1217 layer combinations verified byte-identical to the old composition |
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
