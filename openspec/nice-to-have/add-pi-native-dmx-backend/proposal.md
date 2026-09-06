## Why

Art-Net is and remains the primary output path. It reaches the rig over the
venue network, it will grow to carry the house lighting as well, and it needs
no cable moved. Nothing here changes that.

What it lacks is a fallback. If the Art-Net node stops working mid-event there
is no second way to get DMX to the fixtures, and the show stops. The Enttec DMX
USB Pro was the intended answer, but its price is hard to justify for hardware
whose entire purpose is to sit unused.

The Raspberry Pi already running the application has a UART capable of DMX's
250 kbaud, the DMX cable is within reach of it, and an RS-485 transceiver costs
a few euros. That makes a second output path available for roughly the price of
a cable, using hardware already in the room.

The backend interface introduced by `add-pluggable-dmx-backends` means this is
an additional class, not a change to how output works.

## What Changes

- A new output backend drives DMX directly from the Pi's UART through an
  RS-485 transceiver, generating the DMX break, start code and 512 channel
  bytes itself.
- It is selectable in Network Setup alongside Art-Net and the Enttec USB Pro,
  with its own settings, exactly like the existing backends.
- Switching to it is **manual and deliberate**. There is no failure detection
  and no automatic failover: the operator notices the lights have stopped and
  changes the active backend. This is a decision, not a limitation to be lifted
  later - see design.
- The hardware and operating-system prerequisites are documented: the
  transceiver and its wiring, freeing the Pi's primary UART from the serial
  console and from Bluetooth, and the fact that this is transmit-only.
- Art-Net remains the configured default and the primary path.

## Non-goals

- **Automatic failover.** Detecting that Art-Net has failed is not possible in
  the way that matters - see design. Manual switching is the whole design, not
  a first step toward automatic switching.
- **Removing or replacing the Art-Net backend.** Art-Net is preferred and is
  expected to grow to carry house lighting.
- **Removing the Enttec USB Pro backend.** It stays as an implemented and
  tested option even though the hardware is no longer being purchased.
- **DMX input, RDM, or bidirectional operation.** Transmit only. The
  transceiver's driver-enable is tied on in hardware.
- **Simultaneous output through more than one backend.** Unchanged from
  `dmx-hardware-backends`: exactly one is active.

## Capabilities

### New Capabilities

None. The backend contract, the selection mechanism and the per-backend
settings model all exist already.

### Modified Capabilities

None. `dmx-hardware-backends` requires that the active backend is determined
by configuration "without requiring a code change to select among
already-implemented backend types" - implementing another backend is the case
that capability was written to accommodate, and `network-configuration`'s
per-backend settings requirement already covers a backend defining settings of
its own shape.

This change therefore sets `skip_specs: true`. No externally visible behaviour
changes; a third value becomes available for an existing setting.

## Impact

- Affected code: new `app/dmx_backends/pi_uart.py`, one branch in
  `app/dmx_backends/factory.py`, a third option and settings field in the
  Network Setup page and its JavaScript, and per-backend validation in
  `app/views/setup.py`.
- Affected hardware: an RS-485 transceiver wired to the Pi's UART TX and to a
  DMX connector. An opto-isolated transceiver is strongly preferred - the DMX
  line runs to metalwork on a stage, and the alternative is a direct electrical
  path from there into the Pi.
- Affected configuration: a new `output.pi_uart` settings object. Existing
  configurations are unaffected; the backend is only used when selected.
- Affected operating system: the Pi's primary UART must be released from the
  serial console and from Bluetooth. This is a one-time change to the Pi's
  boot configuration and requires a reboot, so it cannot be done during an
  event.
- Dependencies: intended to add none. Whether accurate break timing requires a
  DMA library is the change's main open question - see design.
- Applies to the venue Raspberry Pi 4 only. The operator's laptop has no UART
  or transceiver, so this backend is not selectable in any useful sense there.
