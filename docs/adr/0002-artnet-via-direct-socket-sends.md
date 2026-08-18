# ADR-0002: Art-Net output via direct socket sends

- **Status:** Accepted
- **Date:** 2026-08-18 (documented retroactively)

## Context

DMX Life speaks Art-Net (DMX over UDP, port 6454) using the `stupidartnet`
library. The library offers a high-level API: `start()` spawns its own output
thread, and `show()` sends the current frame.

Two problems surfaced in use:

1. `show()` prints `ERROR: Socket error` directly to stdout whenever the
   Art-Net node is unreachable. During a show with a flaky network this floods
   `nohup.out` with thousands of lines, and there is no library-level way to
   suppress it.
2. `show()` swallows the outcome. The application cannot tell whether a frame
   actually left the machine, so it cannot report Art-Net connectivity to the
   operator — which is exactly what an operator needs to know when the lights
   are not responding.

## Decision

Use `stupidartnet` only for Art-Net packet construction (header building,
sequence numbering, net/subnet configuration). Do not use its threading or its
`show()` method.

Instead, `DMXController._send_dmx_packet()` builds the packet from
`artnet.packet_header` plus the 512-byte payload and calls
`artnet.socket_client.sendto()` directly, wrapped in our own `try/except
socket.error`. The exception handler updates a `connection_status` dictionary
and logs only on state *transitions* — once when the link drops, once when it
recovers.

## Consequences

**Good:**

- Log output stays readable. A disconnected node produces one warning, not a
  stream.
- Real connection status is available to the UI (`GET /api/connection/status`),
  which drives the indicator in the page header.
- Full control over error policy: ArtSync failures are silently ignored, while
  data-send failures are tracked.

**Bad:**

- **We depend on `stupidartnet` internals** — `packet_header`, `socket_client`,
  `target_ip`, `port`, `if_sync`, `sequence`, `make_artsync_header()`. None of
  these are part of a documented public API. A library upgrade can break DMX
  output, and the failure would be silent until someone runs a show.
- Sequence-number maintenance is now our responsibility (`sequence = (sequence
  + 1) % 256` in a `finally` block).
- The version in `requirements.txt` is pinned (`stupidartnet==1.6.0`) largely
  because of this coupling.

## Alternatives considered

- **Use `show()` and redirect stdout.** Suppresses the spam but still yields no
  connection status, and hijacking stdout process-wide is worse than reaching
  into one object.
- **Fork or vendor `stupidartnet`.** More control, but takes on maintenance of
  protocol code that currently works.
- **Write the Art-Net packet from scratch.** The protocol header is simple and
  this would remove the dependency entirely. A reasonable future move; not done
  because the current approach works and the library still handles the fiddly
  net/subnet/universe encoding.
