## 1. Backend interface

- [ ] 1.1 Create `app/dmx_backends/base.py`: `DMXBackend` ABC with
      `connect()`, `send(frame)`, `disconnect()`, `get_connection_status()`.
- [ ] 1.2 Define `DMXBackendError` in the same module - the single exception
      type `DMXController` catches, regardless of which backend raised it.

## 2. Art-Net backend

- [ ] 2.1 Create `app/dmx_backends/artnet.py`: `ArtNetBackend` implementing
      `DMXBackend` - own ArtDmx packet construction (header, opcode, protocol
      version, sequence/physical/universe/length, 512 data bytes) over a UDP
      socket, matching the byte layout `_send_dmx_packet()` currently builds
      via StupidArtnet.
- [ ] 2.2 Translate `socket.error` to `DMXBackendError` in `send()`.
- [ ] 2.3 Unit test: compare constructed packet bytes against a known-good
      ArtDmx capture (design.md - Risks).

## 3. Config migration

- [ ] 3.1 In `ConfigManager.read()`, detect the legacy flat shape
      (`artnet_ip`/`artnet_port`/`universe`/`packet_size` at the top level)
      and migrate it into `output.artnet`, defaulting `output.backend` to
      `"artnet"`.
- [ ] 3.2 Log a before/after summary of the migration, same pattern as
      `_migrate_fixture_links`.
- [ ] 3.3 Accept the new `output` shape unchanged on read (idempotent -
      already-migrated configs aren't touched again).
- [ ] 3.4 Add a `create_backend(config)` factory in
      `app/dmx_backends/factory.py` that reads `output.backend` and
      constructs the matching backend from its own sub-object.

## 4. Wire DMXController to the backend interface

- [ ] 4.1 `DMXController.__init__` takes a `DMXBackend` (via the factory)
      instead of constructing a `StupidArtnet` directly.
- [ ] 4.2 Replace `_send_dmx_packet()`'s StupidArtnet-specific body with
      `self.backend.send(frame)`, catching `DMXBackendError` and driving
      `connection_status` exactly as the current `except socket.error`
      block does.
- [ ] 4.3 Update `reconfigure()` to construct a new backend via the factory
      (which may be a different class, not just reconfigured settings) and
      swap it in during the existing stop/restart sequence.
- [ ] 4.4 Confirm the output thread, its lock, and `_update_transition()`
      are untouched - only what receives the frame changes.

## 5. Enttec USB Pro backend

- [ ] 5.1 Create `app/dmx_backends/enttec_usb.py`: `EnttecUsbBackend`
      implementing `DMXBackend` - Widget API 1.44 "Output Only Send DMX
      Packet" framing (`0x7E`, label `6`, length, start code `0x00` + 512
      channel bytes, `0xE7`) over `pyserial`.
- [ ] 5.2 Translate `serial.SerialException` to `DMXBackendError`.
- [ ] 5.3 `connect()`/`disconnect()` open and close the serial port at the
      Pro's fixed baud rate.
- [ ] 5.4 Unit test the packet framing against the published spec (no
      hardware required for this part).
- [ ] 5.5 Add `pyserial` to `requirements.txt`; remove `stupidartnet`.

## 6. Setup UI

- [ ] 6.1 Network Setup page: add backend selection (Art-Net / Enttec USB
      Pro) as a setting distinct from each backend's own connection fields.
- [ ] 6.2 Show only the active backend's own settings fields, per selection.
- [ ] 6.3 Server-side validation in `update_network_config` (or a renamed
      equivalent) validates each backend's settings independently -
      numeric Art-Net fields, a serial device path for USB - per
      `network-configuration`'s "Per-backend settings" requirement.

## 7. Verify

- [ ] 7.1 Existing Art-Net setup: activate a scene, confirm output reaches
      the real venue rig exactly as before this change.
- [ ] 7.2 An old-shape `config.json` (flat `artnet_ip` etc.) loads correctly
      and migrates; a fresh default config still starts successfully.
- [ ] 7.3 Switching backend in Network Setup takes effect without an app
      restart (per the modified "Runtime network reconfiguration"
      requirement).
- [ ] 7.4 Connection status reporting works identically for a deliberately
      unreachable Art-Net target (already testable) and, once hardware is
      available, a disconnected Enttec Pro.
- [ ] 7.5 Once the Enttec DMX USB Pro is in hand: connect it, select it as
      the active backend, confirm real DMX output reaches a fixture.
- [ ] 7.6 Crossfade duration and behavior are unaffected by which backend
      is active (design.md Goals).

## 8. Follow-up

- [ ] 8.1 Decide `refresh_rate`'s fate (design.md - Open Questions): wire it
      to actually drive `UPDATE_RATE`, or remove it as vestigial. Separate,
      small follow-up - not blocking for this change.
