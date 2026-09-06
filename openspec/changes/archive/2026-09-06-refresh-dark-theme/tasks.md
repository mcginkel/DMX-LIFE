## 1. Choose the palette

- [x] 1.1 Render two or three complete variants against the real scene grid -
      real scene names, real groups, an active scene, an active kill scene -
      so the choice is made on the actual interface rather than on swatches.
- [x] 1.2 Each variant applies the same shape: a widened surface ladder and
      one cool structural hue, with the established meanings unchanged.
- [x] 1.3 Choose one. Record which, and why, in design.md so a later reader
      knows it was a decision rather than an accident.

## 2. Apply the palette

- [x] 2.1 Update the surface tokens so a card is clearly distinguishable from
      the page behind it, leaving the page background essentially where it is.
- [x] 2.2 Introduce the cool structural hue as its own token, named for what
      it is for, and apply it to borders, group titles and muted text.
- [x] 2.3 Leave `--primary-color`, `--danger-*`, `--warning-*` and
      `--success-color` meaning exactly what they mean today.
- [x] 2.4 Decide whether `--surface-hover` survives the wider ladder or
      whether hover is better expressed another way (design.md - Open
      Questions), and act on the decision.

## 3. Verify

- [x] 3.1 Main page: groups, an active scene, an active kill scene, the Extra
      group's warning state, and the connection indicator all still read
      correctly and distinctly.
- [x] 3.2 Setup pages: forms, selects, sliders, the fixture list and the
      channel badges are all legible on the new surfaces.
- [x] 3.3 The DMX monitor's grid, bars and its blackout and error overlays are
      legible.
- [x] 3.4 Nothing reverted to a light surface anywhere - no rule was relying
      on a token that changed meaning.
- [x] 3.5 All 18 scenes still fit one page without scrolling at 1440x830 and
      at 1024x768. The theme change must not cost the density work.
- [ ] 3.6 Look at it on the venue machine, in the dark, before calling it
      done. A palette that reads well in daylight is not evidence.
      DEFERRED at archive time: verified only on the operator's laptop. The
      open question in design.md stands - whether four or five solid bright
      fills at once are too much in a blacked-out room. Pulling back is a
      one-line change to --primary-color if so.
