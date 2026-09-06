## Context

DMX512 on the wire is RS-485 at 250 kbaud, 8 data bits, 2 stop bits. Each frame
is a BREAK of at least ~90µs, a mark-after-break of ~12µs, then a start code of
`0x00` followed by up to 512 channel bytes. At 11 bits per byte, 513 bytes take
about 22.6ms, which is why DMX tops out near 44 frames per second - and why
this application's refresh-rate setting is capped at 44.

The Pi's UART produces the byte stream in hardware and gets it exactly right.
It has no primitive for the BREAK. That single gap is the whole of the
difficulty in this change.

The Pi is a model 4. Its primary PL011 UART is claimed by Bluetooth by default
and its mini-UART derives its clock from the CPU frequency, so only the PL011 -
freed from Bluetooth - is usable for 250 kbaud.

`add-pluggable-dmx-backends` established the interface this plugs into, and
recorded a relevant judgement: the Open DMX USB backend was excluded because
"the host would own DMX-frame timing in Python with no onboard help - a
materially different risk profile from a documented-protocol backend". This
backend accepts that risk profile deliberately, and the reason it is acceptable
here is the subject of the next section.

## Goals / Non-Goals

**Goals:**
- A second physical output path available for the cost of a transceiver.
- No change to `DMXController`, the output thread, the crossfade, or the frame
  composition - a backend and nothing more.
- Honest about where this path is weaker than Art-Net, in the code and in the
  documentation, rather than presenting the two as equivalent.

**Non-Goals:** see proposal.md. In particular, no failure detection, no
automatic switching, no DMX input.

## Decisions

### Manual switching, permanently

The operator selects this backend in Network Setup when Art-Net has stopped
working. Nothing detects the failure and nothing switches automatically.

This is not a simplification to be revisited. Automatic failover would require
detecting that Art-Net has failed, and the failure that matters cannot be
detected. Art-Net is UDP: `sendto()` succeeds whether or not anything is
listening. On the venue network the Pi and the node share a subnet, so a
powered-off node can surface as a genuine socket error through failed ARP - but
a node that is powered, answering ARP, and simply not putting DMX on the wire
is indistinguishable from a healthy one.

ArtPoll/ArtPollReply is the protocol's own answer, and it was explicitly
excluded as a non-goal by `add-pluggable-dmx-backends`. It would tell us that
a node is present and answering, which is still not the same as fixtures
receiving light levels.

The operator, meanwhile, has a detector no software can match: the lights
stopped. Manual switching routes the decision to where the information actually
is.

### Break generation: start with the cheapest method that works

Three candidates, in the order they should be tried:

1. **Serial break condition.** `pyserial` can assert a break on the line;
   deasserting it after a Python-timed interval yields a break of milliseconds
   rather than the ~90µs of the spec. Receivers tolerate long breaks - the cost
   is frame rate, perhaps 10-20fps rather than 40.
2. **Baud-rate switch.** Drop to a lower baud, send `0x00` so that its start
   bit and eight zero data bits form a low period of roughly the right length,
   then switch back. Closer to spec, at the cost of two baud changes per frame.
3. **DMA waveform** via `pigpio`, which is supported on the Pi 4. This produces
   the break with genuine microsecond accuracy, immune to scheduler jitter,
   and is the only method that would be defensible for a primary output path.

The change should start at (1) and escalate only on evidence. A fallback path
running at 15fps with no new dependency is a better trade than a daemon and a C
library added for hardware that may never be used in anger. Held scenes and
three-second crossfades do not show a reduced frame rate; DMX receivers hold
their last valid frame, so a late frame is invisible rather than a flicker.

What would justify escalating to (3): visible stepping during a crossfade, or
fixtures dropping to black between frames, observed on the actual rig. Those
are observations, not predictions - the design should not pre-emptively take on
the dependency.

### Transmit only, driver-enable tied on in hardware

The RS-485 transceiver's driver-enable and receiver-enable are strapped in
hardware rather than driven from a GPIO. DMX output is unidirectional here -
there is no RDM and no DMX input - so there is nothing for the software to
toggle, and one less thing to get wrong at 19:00 on a Sunday.

### Two places this backend is weaker than the interface implies

Both belong in the documentation and in the code comments, not discovered
during an event:

**An unplugged DMX cable is undetectable.** The UART writes into the
transceiver whether or not anything is connected, exactly as UDP writes into
the network whether or not a node is listening. `dmx-output`'s "Output survives
an unreachable node" requirement is satisfied in the sense that the output
thread keeps running, but this backend cannot report the cable as disconnected.
Its connection status reflects whether the serial port is open, nothing more.

**Punctuality is not guaranteed under load.** `dmx-hardware-backends` requires
that crossfade timing does not vary by backend. That holds: `_update_transition`
interpolates from wall-clock time, so the composed frames are identical
whichever backend is active. What can vary is whether those frames reach the
wire on time when the Pi is busy. The requirement's own wording - "only the
physical transport of the output differs" - covers this, but it is worth saying
plainly that this transport has a jitter budget the others do not.

### Configuration shape

A `pi_uart` settings object alongside the existing ones, holding at minimum the
serial device path. Whether the break method is a setting or a constant is left
to implementation: making it configurable is useful while establishing which
method works, and is dead weight afterwards.

Following the existing pattern, all backends' settings persist regardless of
which is active, so switching to this backend and back does not discard the
Art-Net configuration - which matters especially here, since switching back is
the expected end state of any use of this path.

## Risks / Trade-offs

- **The OS change cannot be made during an event.** Freeing the UART from the
  serial console and Bluetooth is a boot-configuration change requiring a
  reboot. A fallback path that needs a reboot to become available is not a
  fallback. → The Pi must be configured, wired and *tested* well before it is
  needed, and the change is not complete until a scene has been driven through
  it on the real rig.
- **Untested fallbacks do not work.** This path will sit unused for months
  between uses, which is exactly how a backup rots - a kernel update reclaims
  the UART, the transceiver comes loose, the device path changes. → Worth
  exercising deliberately at intervals rather than trusting it.
- **Electrical risk without isolation.** A non-isolated transceiver places a
  direct electrical path between stage metalwork and the Pi's GPIO header. →
  Use an opto-isolated transceiver; the saving is a few euros against the Pi
  and the show.
- **Physical topology becomes a dependency.** Art-Net reaches the rig over the
  network from anywhere; this requires the Pi to stay within DMX cable reach of
  the first fixture. Moving the Pi silently removes the fallback. → Document
  it as a placement constraint, not merely a wiring note.

## Open Questions

- Which break method survives contact with the real fixtures. The design says
  start at the cheapest; only measurement on the actual rig settles it.
- Whether the achievable frame rate with method (1) is acceptable in practice.
  It should be, given held scenes, but "should be" is a prediction and the rig
  is the authority.
- Whether the house-lighting expansion - planned over Art-Net - ever shares a
  universe with the stage rig. If it does, this fallback covers only part of
  the installation, and that is worth knowing before relying on it.
