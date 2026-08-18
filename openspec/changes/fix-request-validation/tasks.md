# Tasks: validate API request payloads

## 1. Shared helpers

- [ ] 1.1 Add a helper that returns the request body as a dict or `None` when it
      is absent or not a JSON object.
- [ ] 1.2 Add a helper that validates a channel list: every entry an integer in
      0–255, returning the offending index on failure.

## 2. Scene endpoints

- [ ] 2.1 Replace the guard in `delete_scene_endpoint` with a correct check for
      a present, non-empty `name`, returning 400 when it is missing.
- [ ] 2.2 Validate the channel payload in `test_scene_endpoint` before calling
      `test_scene`, returning 400 with the offending index.
- [ ] 2.3 Validate the channel payload in `save_scene_endpoint` on the same
      terms.
- [ ] 2.4 Guard `test_scene()` in `app/dmx_controller.py` so it cannot raise on
      out-of-range values even if reached directly.

## 3. Network endpoint

- [ ] 3.1 Parse port, universe and refresh rate defensively in
      `update_network_config`, returning 400 naming the offending setting.
- [ ] 3.2 Leave stored configuration untouched when validation fails.

## 4. Verify

- [ ] 4.1 `DELETE /setup/api/config/scenes` with `{}` returns 400, not 500.
- [ ] 4.2 `DELETE` with a valid name still deletes the scene.
- [ ] 4.3 A scene named `name` can be deleted.
- [ ] 4.4 `POST .../scenes/test` with a value of 300 returns 400.
- [ ] 4.5 `POST .../scenes/test` with a non-numeric value returns 400.
- [ ] 4.6 `POST .../scenes/test` with valid values still previews correctly.
- [ ] 4.7 `POST .../config/network` with a non-numeric port returns 400 and
      leaves `config.json` unchanged.
- [ ] 4.8 Saving valid network settings still works and takes effect.
- [ ] 4.9 The scene editor's save, test and delete buttons all still work from
      the UI.

## 5. Notes

- [ ] 5.1 Test against a copy of `config.json`, or commit first — earlier
      exploratory testing of the delete endpoint removed a real scene.
