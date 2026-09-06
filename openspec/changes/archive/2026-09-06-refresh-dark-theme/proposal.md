## Why

The dark theme works but has gone flat. It was tuned hard for one thing -
preserving night vision in a darkened room - and overshot into a single
low-contrast brown-black field that reads as drab rather than calm.

Two specific causes. The surface ladder is compressed: the page, card, control
and hover surfaces sit within a very narrow luminance range, so panels do not
lift off the background and the interface has no visible structure. And it is
effectively monochromatic - one amber accent on warm near-black, with red as
the only other hue - so nothing has anywhere to stand out against.

The constraint that produced it is still valid. This is operated in a dark room
during performances, screen brightness matters, and the theme should not be
made "fresh" by getting brighter or bluer overall.

## What Changes

- The surface ladder is widened so cards and controls are distinguishable from
  the page behind them, without raising overall screen brightness meaningfully -
  the eye adapts to the brightest element, which is already the accent.
- A second, cooler hue is introduced for neutral and structural elements -
  borders, group labels, inactive states - so that amber can mean "this is
  live" rather than being the colour of everything.
- The active-scene and kill-scene treatments keep their current meanings. What
  changes is the ground they sit on, not the signals themselves.
- Still a single dark theme with no toggle, and still no significant blue light
  in large areas.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. This changes the appearance of the interface, not any stated behaviour.
The change sets `skip_specs: true`.

## Impact

- Affected code: `app/static/css/style.css`, principally the token block. The
  theme is fully tokenised, so the work is concentrated in the variable
  definitions rather than spread through the rules.
- No change to markup, behaviour, or stored data.
- Verification is visual and subjective, so it needs the operator's eye: the
  intended process is to produce two or three palette variants rendered against
  the real scene grid and choose between them, as was done when the dark theme
  was introduced.
- Worth checking in the room it is used in, not only on a desk - the previous
  palette looked right on a bright screen and drab in situ.
