# Nice to have

Ideas captured as OpenSpec changes but **not planned work**. They sit here
rather than in `../changes/` so that everything under `changes/` means "we
intend to build this", and `openspec list` shows what is actually in flight.

The `openspec` CLI does not see these. It treats every directory under
`changes/` as a change, so a `someday/` folder in there would appear as a
phantom change and hide the real ones - which is why this lives alongside
`changes/` instead of inside it.

## Promoting one back

Move it and it becomes a normal change again - the artifacts and
`.openspec.yaml` travel with it:

```bash
mv openspec/nice-to-have/<name> openspec/changes/<name>
openspec status --change "<name>" --json
```

Most of these have only a proposal. Completing the remaining artifacts is part
of promoting them, not something to do while they sit here.

## What's parked, and why

| Change | Why it is not planned |
|---|---|
| [add-pi-native-dmx-backend](add-pi-native-dmx-backend/proposal.md) | A backup DMX path driven from the Pi's own UART, for when Art-Net fails. Needs hardware wiring - an RS-485 transceiver - and a boot-configuration change before it is usable, and Art-Net is both preferred and expected to grow to carry house lighting. Worth doing before it is needed rather than during an event, but nothing is broken without it. |
| [sync-show-data-via-git](sync-show-data-via-git/proposal.md) | Replicating operator data between the venue Pi and the laptop over git. Blocked on `separate-operator-data`, which does not exist yet - there is no self-contained data directory to sync. Revisit once that has landed and has been lived with. |
| [per-scene-files](per-scene-files/proposal.md) | One file per scene, so git merges cleanly per scene. Its own proposal argues against building it yet: with the venue on its own branch and merges done on the laptop, a bad merge cannot reach a show, so this is merge ergonomics rather than correctness. Decide after real merges provide evidence about how often unrelated edits actually collide. |

Two of the three are downstream of `separate-operator-data`. If that lands and
the sync workflow gets used in anger, both become concrete rather than
speculative - that is the moment to look at this folder again.
