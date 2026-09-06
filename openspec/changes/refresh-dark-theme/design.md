## Context

The dark theme was tuned for one thing: preserving dark adaptation while
operating in a blacked-out room. It succeeded at that and overshot into an
interface that reads as murky rather than calm.

Two measurable causes, both visible in the token block rather than in any
individual rule.

**The surface ladder is compressed.** The five surfaces span a very narrow
range, so nothing appears to sit on top of anything else:

```
  --chrome-color   #060504   ▏
  --bg-color       #0b0a08   ▏▏          five steps inside a
  --surface-color  #14120e   ▏▏▏         very small luminance band
  --surface-raised #1a1610   ▏▏▏▏
  --surface-hover  #221d15   ▏▏▏▏▏
```

A card at `#14120e` on a page at `#0b0a08` is a difference of a few units.
The eye reads that as one flat field, so the interface loses its structure and
the panels stop looking like panels.

**It is effectively monochrome.** Everything is one warm hue - amber accent,
brown-black surfaces, brown-grey text - with red as the only other colour, and
red is reserved for the kill scenes. When every element shares a hue, nothing
can stand out by hue, so the accent has to do all the work of separating
"live" from "not live" from "structural".

The constraint that produced this is still real and is not being relaxed:
large areas of blue light in a dark room cost dark adaptation, and the screen
should not get generally brighter.

## Goals / Non-Goals

**Goals:**
- Panels visibly sit above the page, so the layout has structure again.
- Amber means "this is live" rather than being the colour of the whole
  interface.
- Overall screen luminance does not meaningfully increase.

**Non-Goals:**
- A light theme, or a theme toggle. Still one theme.
- Changing the *meanings* already established: amber for the active scene,
  red for the kill scenes, yellow for the Extra group's active state, green
  for a healthy connection. Only the ground they sit on changes.
- Changing any layout, spacing or density. `compact-scene-storage`'s
  condensed grid stays exactly as it is.
- Changing markup or behaviour. This change touches the token block and
  little else.

## Decisions

### Widen the ladder rather than raise the floor

The page stays essentially where it is; the surfaces above it move up. The
brightest element on screen is already the amber accent, and the eye adapts to
the brightest element - so lifting a card from `#14120e` toward something
clearly distinguishable costs nothing in dark adaptation while restoring the
sense that a panel is a panel.

**Alternative considered:** keeping the surfaces and adding borders to separate
panels instead. Rejected - the theme already has borders, and adding more
weight to them makes a dense scene grid look like a spreadsheet. Separation by
surface is quieter than separation by line.

### One cool hue, for structure only

A second hue is introduced for the things that are neither live nor dangerous:
borders, group labels, muted text, inactive chrome. Amber is then free to mean
exactly one thing.

The cool hue must be desaturated and dark enough that it never occupies a large
bright area - it is for hairlines and small text, not for fills. A cool *tint*
in the structural greys is enough to make the warm accent read as warm again;
a saturated blue would defeat the reason the theme is warm in the first place.

**Alternative considered:** a second warm hue instead - a deeper orange or a
yellow for structure. Rejected: too close to the accent to create separation,
which is the entire point.

### The palette is chosen by eye, from rendered variants

This is the part that cannot be decided in a design document. The approach
above admits several palettes, and the difference between a good one and a
drab one is not something the reasoning predicts.

The process is the one used when the theme was introduced: render two or three
complete variants against the real scene grid, with real scene names and real
active states, and choose. What is decided here is the *shape* of the change -
wider ladder, one cool structural hue, unchanged meanings - not the hex values.

### Verify in the room, not at the desk

The previous palette looked correct on a bright desk display and drab in situ.
The variant chosen from samples should be looked at on the venue machine, in
the dark, before the change is considered done. A palette that reads well in
daylight is not evidence.

## Risks / Trade-offs

- **"Fresh" is easily achieved by getting brighter**, which would quietly
  undo the theme's purpose. → The page background is a fixed point; only the
  surfaces above it move, and the result is checked in a dark room.
- **The cool hue creeps.** A structural hue is easy to start using for fills
  and states, at which point the theme has two accents and neither means
  anything. → The token names should say what they are for, and the hue stays
  out of anything that signals state.
- **Subjective verification does not survive time.** A palette chosen in one
  sitting can look wrong a month later. → The token block is small and
  entirely centralised; changing it again is cheap. This is not a decision
  that needs to be right forever.

## Decision recorded: signals differ by more than hue

Chosen after rendering variants: **strong lightness separation plus a
non-colour marker**, not a hue-only palette.

The first round of samples varied the *temperature of the greys* between
variants and the operator could not tell them apart - he is slightly
colourblind. That is useful evidence beyond the immediate choice: a palette
whose states are distinguished by hue alone is not reliable here, and the
whole first approach was aimed at the wrong axis.

Red versus green turned out to be fine for him, so the signal hues
themselves - amber for active, red for the kill scenes, green for a healthy
connection - are not the problem and are kept. What changes is that they stop
being the *only* difference:

- An active scene is markedly brighter than an idle one, not tinted.
- An off scene is markedly darker - recessed rather than merely coloured.
- Active states carry a solid edge bar, so the state survives with colour
  removed entirely.
- The connection indicator differs in shape as well as colour. Not needed for
  this operator's vision, but preferred on sight and free to keep.

The red kill-scene treatment established earlier is retained rather than
replaced with the sample's neutral version: it was a deliberate choice, it is
legible to this operator, and the lightness and marker changes make it robust
without discarding it.

## Open Questions

- Whether solid bright fills for active scenes are too bright in a blacked-out
  room when four or five scenes are live at once. The whole point is that
  active reads at a glance, but this is the change most likely to need pulling
  back after seeing it in situ.
- Whether the `--surface-hover` step is still needed once the ladder is
  widened, or whether hover can be expressed by border rather than fill. Worth
  seeing in the samples.
