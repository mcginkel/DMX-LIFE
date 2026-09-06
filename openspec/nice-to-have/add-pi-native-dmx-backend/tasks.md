## 0. Hardware and OS prerequisites

These are physical and cannot be done during an event. Everything below
depends on them.

- [ ] 0.1 Wire an RS-485 transceiver to the Pi's UART TX (GPIO14) and to a DMX
      output connector, with driver-enable strapped for transmit. Prefer an
      opto-isolated transceiver.
- [ ] 0.2 Free the Pi's primary PL011 UART: remove the serial console from it
      and release it from Bluetooth, then reboot.
- [ ] 0.3 Confirm the UART is present and that the application's user may open
      it, without running as root.
- [ ] 0.4 Verify the line carries a 250 kbaud byte stream before any
      application code is involved - a scope, a logic analyser, or a known-good
      DMX receiver. Debugging protocol code over unverified wiring is not worth
      the time it costs.

## 1. The backend

- [ ] 1.1 Create `app/dmx_backends/pi_uart.py` implementing `DMXBackend`:
      `connect()`, `send(frame)`, `disconnect()`, `get_connection_status()`.
- [ ] 1.2 Open the serial device at 250000 baud, 8 data bits, no parity, 2 stop
      bits.
- [ ] 1.3 Build the frame payload: start code `0x00` followed by the 512
      channel bytes, exposed separately from transmission so the bytes can be
      asserted on without a serial port present - same shape as the Art-Net and
      Enttec backends.
- [ ] 1.4 Generate the BREAK and mark-after-break before each frame, using the
      serial break condition as the first method (design.md - Break
      generation).
- [ ] 1.5 Translate serial and OS errors into `DMXBackendError`, so the
      controller's existing handling applies unchanged.
- [ ] 1.6 Reject a frame that is not exactly 512 bytes, consistent with the
      other backends.
- [ ] 1.7 Unit test the frame payload: start code present, channel values
      carried verbatim, wrong-sized frames rejected. No hardware required.

## 2. Selection and configuration

- [ ] 2.1 Add the backend to `create_backend()` in
      `app/dmx_backends/factory.py`, constructed from an `output.pi_uart`
      settings object.
- [ ] 2.2 Add it to the supported-backends list so it appears in Network Setup.
- [ ] 2.3 Add its settings fields to the Network Setup page, shown only when it
      is the selected backend.
- [ ] 2.4 Validate its settings server-side on their own terms - a device path,
      not a numeric field - per the existing per-backend validation.
- [ ] 2.5 Confirm switching to it and back leaves the Art-Net settings intact,
      since switching back is the expected end state of any use of this path.

## 3. Measure the break method

- [ ] 3.1 With the backend selected, measure the achieved frame rate on the
      real rig.
- [ ] 3.2 Judge a crossfade by eye on the actual fixtures: stepping, or
      fixtures dropping toward black between frames, is the signal to escalate.
- [ ] 3.3 If the serial break condition is inadequate, try the baud-rate switch
      method and measure again.
- [ ] 3.4 Only if both are inadequate, evaluate the `pigpio` DMA waveform, and
      record in design.md what evidence justified taking on the dependency.
- [ ] 3.5 Record the method chosen and the frame rate achieved, so a future
      reader knows what was measured rather than assumed.

## 4. Documentation

- [ ] 4.1 Document the wiring in `README.md`: transceiver, GPIO pin, DMX
      connector, and the recommendation for isolation.
- [ ] 4.2 Document the boot-configuration change and that it needs a reboot -
      therefore that this path must be prepared in advance, not improvised.
- [ ] 4.3 Document the placement constraint: the Pi must stay within DMX cable
      reach of the first fixture, or this fallback silently ceases to exist.
- [ ] 4.4 State plainly that this backend cannot detect a disconnected DMX
      cable, and that its connection status reflects only whether the serial
      port is open.

## 5. Verify

- [ ] 5.1 Select the backend in Network Setup and confirm real DMX output
      reaches a fixture.
- [ ] 5.2 Confirm the switch takes effect without restarting the application,
      per the existing runtime-reconfiguration requirement.
- [ ] 5.3 Confirm scene composition and layering are identical to Art-Net -
      activate the same combination on both backends and compare the fixtures.
- [ ] 5.4 Confirm a crossfade completes and settles on its target values.
- [ ] 5.5 Confirm an unopenable serial device surfaces as a connection-status
      error rather than preventing the application from starting.
- [ ] 5.6 Switch back to Art-Net and confirm normal operation resumes.
- [ ] 5.7 Rehearse the actual fallback: with Art-Net deliberately broken, time
      how long it takes to switch over. If that is slow or fiddly, the
      documentation - or the interface - needs work.
