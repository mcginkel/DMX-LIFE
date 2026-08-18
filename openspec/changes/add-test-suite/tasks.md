# Tasks: add an automated test suite

## 1. Scaffolding

- [ ] 1.1 Add `requirements-dev.txt` with `pytest`.
- [ ] 1.2 Create `tests/` with a `conftest.py` providing a representative
      fixture patch and scene set, including fixtures with adjacent addresses
      and one sparse overlay scene.
- [ ] 1.3 Add a fake config manager exposing `get_scenes()`, `get_fixtures()`
      and `get_scene_by_name()`.
- [ ] 1.4 Add `.pytest_cache/` to `.gitignore`.

## 2. SceneManager — scene composition

Mirrors `openspec/specs/scene-control/spec.md`.

- [ ] 2.1 Toggling an inactive scene activates it; toggling it again
      deactivates it.
- [ ] 2.2 Activating in an exclusive group replaces that group's active member.
- [ ] 2.3 Activating across groups accumulates layers.
- [ ] 2.4 An additive scene neither displaces nor is displaced.
- [ ] 2.5 Removing a layer restores the value from the layer underneath.
- [ ] 2.6 Removing the only claimant of a channel returns it to 0.
- [ ] 2.7 Later-activated layers win contested channels.
- [ ] 2.8 A fixture-scoped scene writes zeros within its own fixtures.
- [ ] 2.9 A sparse overlay writes only non-zero channels and leaves the rest of
      an overlapping fixture intact.
- [ ] 2.10 An unknown scene name is rejected and leaves the active set
      unchanged.

## 3. ConfigManager

- [ ] 3.1 Round-trip read/write against `tmp_path`.
- [ ] 3.2 A missing config file produces the documented defaults.
- [ ] 3.3 Saving a scene adds it; saving under an existing name replaces it.
- [ ] 3.4 Deleting a scene removes it.
- [ ] 3.5 The `group` field survives a round trip.

## 4. DMXController

- [ ] 4.1 Interpolation moves values toward the target.
- [ ] 4.2 At completion every channel equals its target exactly.
- [ ] 4.3 `set_immediate` cancels an active transition.
- [ ] 4.4 A buffer that is not 512 bytes is rejected.
- [ ] 4.5 Connection status flips on send failure and recovers on success.

## 5. API

- [ ] 5.1 Every endpoint returns 401 without credentials.
- [ ] 5.2 `GET /setup/api/config` includes `MAX_SCENES`.
- [ ] 5.3 `POST /api/scenes/activate` returns the full active list.
- [ ] 5.4 Activating an unknown scene fails without a 500.
- [ ] 5.5 The documented rejection cases return 400, not 500 (after
      `fix-request-validation`).
- [ ] 5.6 The scene limit is enforced for new scenes but not for edits.

## 6. Verify

- [ ] 6.1 `pytest` passes from a clean checkout.
- [ ] 6.2 No test touches the real `app/config.json`.
- [ ] 6.3 No test opens a real socket or starts the DMX thread.
- [ ] 6.4 The suite runs in a few seconds and contains no `sleep`.
- [ ] 6.5 Document how to run it in `README.md`.
