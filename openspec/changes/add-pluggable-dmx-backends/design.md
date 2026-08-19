## Context

See proposal.md - Why. Two constraints shape this design specifically:

1. `DMXController` already owns a lock-protected output thread
   ([ADR-0003](../../../docs/adr/0003-continuous-dmx-output-thread.md),
   [`thread-safe-dmx-buffers`](../../../openspec/changes/archive/2026-08-19-thread-safe-dmx-buffers/))
   that snapshots the frame under a lock and sends it outside the lock. That
   thread, its lock, and its timing model are correct and stay exactly as
   they are - this change only replaces what `_send_dmx_packet()` hands the
   frame to.
2. Both target protocols are publicly documented: Art-Net (the protocol
   itself, independent of StupidArtnet) and the Enttec DMX USB Pro's
   "Widget API 1.44". Neither backend requires reverse engineering, which is
   why this change is scoped the way it is (see proposal.md - Non-goals for
   what's excluded and why).

## Goals / Non-Goals

**Goals:**
- `DMXController` depends on an interface, not a concrete transport.
- Adding a future backend (once SUSHI-Z1 or Open DMX USB is ready) means
  implementing one class against `DMXBackend`, not touching `DMXController`.
- No behavior change for existing Art-Net users beyond the config file shape
  (migrated automatically).

**Non-Goals:**
- ArtPoll / node discovery. The current StupidArtnet-based implementation
  sends raw ArtDmx frames only (unicast or broadcast, operator-configured
  address) - no discovery protocol. `ArtNetBackend` matches that; adding
  discovery is future scope if ever needed.
- ArtSync. `self.artnet.if_sync` exists in the current code but nothing in
  `config.json` or the UI ever enables it - it's dead capability, not a used
  feature. Dropped, not reimplemented.

## Decisions

### `DMXBackend` interface shape

```python
class DMXBackend(ABC):
    def connect(self) -> None: ...
    def send(self, frame: bytes) -> None: ...   # len(frame) == 512, may raise DMXBackendError
    def disconnect(self) -> None: ...
    def get_connection_status(self) -> dict: ...  # {connected, last_error_time, error_message}
```

Four methods, matching exactly what `DMXController` already does today
(`self.artnet.*` calls collapse to these four operations). `send()` raises a
single `DMXBackendError` on any failure - see "Uniform error translation"
below - rather than the caller needing to know which underlying exception
type each transport can raise.

**Alternative considered:** a richer interface (e.g. separate
`is_connected()`/`last_error()` methods instead of one status dict).
Rejected - `DMXController.connection_status` already has this shape today
and every consumer (`GET /api/connection/status`) expects it; no reason to
change the shape while changing what produces it.

### Uniform error translation

Each backend wraps its own transport's exceptions in `DMXBackendError`:
`ArtNetBackend` catches `socket.error`, `EnttecUsbBackend` catches
`serial.SerialException`. `DMXController` catches only `DMXBackendError` in
its send path and drives `connection_status` from that - unchanged from
today's `except socket.error` handling, just widened to a backend-defined
exception instead of a transport-specific one.

### Factory + config shape

```json
"output": {
  "backend": "artnet",
  "artnet": {
    "ip": "192.168.3.170", "port": 6454,
    "universe": 1, "packet_size": 512
  },
  "enttec_usb": {
    "port": "/dev/tty.usbserial-XXXX"
  }
}
```

`create_backend(config)` reads `output.backend` and constructs the matching
class from its own sub-object. Both sub-objects can be present at once
(so switching backends in the UI doesn't lose the other's settings) - only
`output.backend` determines which is active.

**Migration:** existing top-level `artnet_ip`/`artnet_port`/`universe`/
`packet_size` keys move into `output.artnet`, with `output.backend` defaulted
to `"artnet"`. Same pattern as `fix-fixture-link-references`'s link migration
- `ConfigManager.read()` detects the old flat shape and migrates in memory,
logging what it did; the migrated shape is written back on the next save,
so an old config keeps loading correctly without a forced one-time script.

**Alternative considered:** a flat `output_backend` string plus prefixed keys
(`artnet_ip`, `usb_port`, ...) instead of nesting. Rejected - nesting keeps
each backend's settings from colliding by name and matches how a third
backend (SUSHI-Z1, later) would slot in without inventing new prefixes.

### `ArtNetBackend`

Sends raw ArtDmx packets (`"Art-Net\0"` header + OpOutput opcode + protocol
version + sequence/physical/universe/length + 512 data bytes) directly over
a UDP socket. This is close to what `_send_dmx_packet()` already builds today
via `self.artnet.packet_header` - the difference is owning packet
construction ourselves instead of reading it off a StupidArtnet instance, so
there's no other library object to reach into.

### `EnttecUsbBackend`

Frames each send as a Widget API "Output Only Send DMX Packet" message:
start delimiter `0x7E`, label `6`, little-endian data length, a DMX start
code (`0x00`) followed by the 512 channel bytes, end delimiter `0xE7`, over
`pyserial` at the Pro's fixed baud rate. The Pro's own microcontroller
generates the actual DMX-frame timing (break/mark-after-break) from this
packet - see proposal.md - Why for why this offloading is the reason USB
Pro was chosen over Open DMX for this change.

### `DMXController.reconfigure()` becomes backend-aware

Currently `reconfigure()` tears down and rebuilds a `StupidArtnet` instance
with new settings. It now needs to handle the same settings-only case *and*
a full backend switch (Art-Net → USB): stop the thread, call
`create_backend(new_config)` (which may return a different class entirely,
not just a reconfigured one), call `connect()`, restart the thread. The
stop/restart sequencing itself is unchanged from today.

## Risks / Trade-offs

- **Writing Art-Net ourselves risks subtle protocol bugs** (sequence
  wraparound, universe encoding) that StupidArtnet, despite its other
  problems, had already gotten right. → Mitigate with a focused unit test
  comparing our packet bytes against a known-good ArtDmx capture, before
  this is wired into `DMXController`.
- **Serial port access varies by OS** (macOS/Linux may need dialout group
  membership; Windows needs the right COM port driver). → Surface a clear
  connection-status error rather than a stack trace; document the OS-level
  prerequisite in README once the backend exists.
- **Config migration bugs** could silently misroute settings (same class of
  risk as the fixture-link migration). → Same mitigation that worked there:
  log a before/after summary on migration, and note the deployed
  `config.json.bak` (from `atomic-config-writes`) as the recovery path if a
  migration goes wrong.
- **`stupidartnet` removal is BREAKING** for anything depending on it
  directly. → Confirmed nothing else in this codebase does (proposal.md -
  Impact); `requirements.txt` drop is safe.

## Migration Plan

1. Land `DMXBackend`/`ArtNetBackend`/factory/config migration first, with
   `DMXController` switched over - this alone is a no-op for existing Art-Net
   users beyond the config shape change, and is independently testable
   against the real venue rig before USB hardware exists.
2. Land `EnttecUsbBackend` once the Pro is purchased and can be tested
   against real hardware - packet framing can be unit-tested against the
   published spec beforehand, but connection handling needs the real device.
3. Rollback: revert the commit(s). If a `config.json` has already been
   migrated to the `output` shape and saved, reverting code without also
   reverting the config file would break `ConfigManager.get_network_settings()`
   - keep a `config.json.bak` checkpoint before deploying this change, same
     practice used for every change that's touched `config.json` this
     session.

## Open Questions

- `refresh_rate` in the current config is passed to `StupidArtnet`'s
  constructor but never actually controls anything - `DMXController`'s
  output loop timing is the hardcoded `UPDATE_RATE = 0.033` class constant,
  not derived from config at all. This change could (a) finally wire
  `refresh_rate` to actually drive `UPDATE_RATE`, or (b) drop the setting
  since it's already vestigial. Either is a small, later change - doesn't
  affect the backend interface, the specs, or the task breakdown for this
  change either way.
