## Why

DMX output is hardwired to Art-Net via StupidArtnet. `DMXController` doesn't
use the library as a clean abstraction, either — it reaches directly into
`StupidArtnet`'s internals (`self.artnet.packet_header`, `.socket_client`,
`.target_ip`, `.sequence`, ...) because the library's own `show()`/threading
couldn't be worked around any other way ([ADR-0002](../../../docs/adr/0002-artnet-via-direct-socket-sends.md)).
That coupling means there is currently no way to drive a fixture over USB, and
no seam to add one without another StupidArtnet-shaped workaround.

The venue rig needs a USB-DMX path (an Enttec DMX USB Pro or Open DMX USB is
being purchased) alongside the existing Art-Net path, selected per
installation. Since Art-Net is already effectively hand-rolled below
StupidArtnet's abstraction, and the Enttec Pro Widget API is a public,
documented protocol (same shape of work as Art-Net), this is the point to
replace StupidArtnet with our own output backends rather than bolt USB
support onto the existing workaround.

## What Changes

- Introduce a `DMXBackend` interface: `connect()`, `send(frame)`,
  `disconnect()`, connection status - one method per concern, matching what
  `DMXController` already needs from `_send_dmx_packet()` today.
- Implement `ArtNetBackend`: our own Art-Net UDP sender, replacing
  StupidArtnet entirely. **BREAKING**: removes the `stupidartnet` dependency.
- Implement `EnttecUsbBackend`: DMX USB Pro Widget API 1.44 framing over a
  serial connection (`pyserial`). Open DMX USB (bare FTDI, host-timed) is
  explicitly out of scope for this change - see Non-goals.
- Add a backend factory that constructs the configured backend from
  `config.json`.
- `DMXController` holds a `DMXBackend` instead of a `StupidArtnet` instance;
  the lock, the transition math, the output thread, and the timing model are
  all unchanged - only what `_run()` hands its frame to changes.
- Extend `config.json` with an `output` section: which backend is active,
  plus that backend's own settings. Existing `artnet_ip`/`artnet_port`/
  `universe`/`packet_size` are migrated into it.
- One backend active per installation, selected in Network Setup - not
  simultaneous multi-backend output.

## Non-goals

- **SUSHI-Z1 support.** Its USB protocol is proprietary and undocumented
  (Nicolaudie's own driver/DLL only); a backend for it depends on reverse-
  engineering a USB capture against the real hardware, which is separate,
  unscoped work.
- **Open DMX USB support.** Feasible, but the host would own DMX-frame
  timing (break/mark-after-break) in Python with no onboard help - a
  materially different risk profile from a documented-protocol backend. Not
  ruled out for later; not part of this change.
- **Simultaneous multi-backend output** (e.g. Art-Net to some fixtures, USB
  to others). Config supports exactly one active backend.
- **Changing the scene/fixture data model.** Backends consume the same
  512-byte frame `SceneManager` already produces; nothing about scene
  composition or fixture configuration changes.
- **The config-bloat problem** (scenes stored as near-entirely-zero 512-value
  arrays). Real, and related in that this change also touches `config.json`,
  but a separate concern - not conflated here.

## Capabilities

### New Capabilities
- `dmx-hardware-backends`: the pluggable backend interface itself - what a
  backend must provide, how one is selected and constructed, and the
  guarantees `DMXController` can rely on regardless of which is active.

### Modified Capabilities
- `dmx-output`: requirements currently describe Art-Net specifically
  ("Continuous Art-Net output", scenarios naming "the Art-Net node"). These
  generalize to backend-agnostic output, with Art-Net becoming one backend
  among others rather than the only one.
- `network-configuration`: "Art-Net settings" becomes backend selection plus
  per-backend settings; existing Art-Net-specific scenarios remain valid for
  when Art-Net is the active backend.

## Impact

- Affected code: `app/dmx_controller_class.py` (holds a backend instead of
  StupidArtnet), new `app/dmx_backends/` package (`base.py`, `factory.py`,
  `artnet.py`, `enttec_usb.py`), `app/config_manager.py` (config migration
  for the new `output` section), `app/views/setup.py` and
  `app/static/js/network.js` (backend selection in Network Setup),
  `requirements.txt` (drop `stupidartnet`, add `pyserial`).
- **BREAKING**: `stupidartnet` dependency removed. Any external code
  depending on `DMXController.artnet` (none known within this codebase -
  confirmed by the same audit that shaped ADR-0002) would break.
- Migration: existing `artnet_ip`/`artnet_port`/`universe`/`packet_size` keys
  need a compatibility path into the new `output` section - detailed in
  design.md.
