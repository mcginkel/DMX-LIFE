# Tasks: bring the existing documentation up to date

## 1. README.md

- [ ] 1.1 Replace "Create up to 10 lighting scenes" with the configurable limit.
- [ ] 1.2 Rewrite the scene sections to describe layering, groups, and toggling
      rather than single-scene activation.
- [ ] 1.3 Remove the published credentials; document how they are configured.
- [ ] 1.4 Add a short "Documentation" section pointing at `docs/adr/` and
      `openspec/specs/`.
- [ ] 1.5 Update the project structure tree — it omits `docs/` and `openspec/`,
      and lists files that the `remove-dead-code` change deletes.

## 2. design/ARCHITECTURE.md

- [ ] 2.1 Replace the `build_dmx_buffer()` documentation with `toggle_scene()`
      and the layer-set model.
- [ ] 2.2 Rewrite the "Buffer Building Algorithm" section — it describes
      starting from current DMX values, which is the superseded behaviour.
- [ ] 2.3 Correct `MAX_SCENES`.
- [ ] 2.4 Update the SceneManager method list to match the class.
- [ ] 2.5 Replace the "Key Design Decisions" section with links into
      `docs/adr/`, rather than a second copy of the rationale.
- [ ] 2.6 Note the known thread-safety gap, or remove the claim that buffer
      access is thread-safe, until `thread-safe-dmx-buffers` lands.

## 3. design/SUMMARY.md

- [ ] 3.1 Move "Scene grouping and categories" out of future improvements.
- [ ] 3.2 Correct the "monkey patching" description of the Art-Net integration.
- [ ] 3.3 Remove the published credentials.

## 4. .github/copilot-instructions.md

- [ ] 4.1 Rewrite the scene activation section for the layered model.
- [ ] 4.2 Correct `MAX_SCENES`.
- [ ] 4.3 Fix the "don't modify" list: drop `app/views/` from it, drop the
      non-existent `routes/`, and drop `lib/` once it is deleted.
- [ ] 4.4 Add a pointer to `docs/adr/` and `openspec/specs/` as the authoritative
      sources.

## 5. Verify

- [ ] 5.1 Every code reference in the four documents names something that
      actually exists.
- [ ] 5.2 No document publishes credentials.
- [ ] 5.3 Numbers quoted for limits and durations match the source.
- [ ] 5.4 Someone unfamiliar with the project can follow `README.md` from clone
      to a running server.
