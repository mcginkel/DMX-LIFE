# Tasks: bring the existing documentation up to date

## 1. README.md

- [x] 1.1 Replace "Create up to 10 lighting scenes" with the configurable limit.
      Phrased generically ("a configurable number") rather than naming a
      specific number, so this doesn't go stale again the next time
      MAX_SCENES changes.
- [x] 1.2 Rewrite the scene sections to describe layering, groups, and toggling
      rather than single-scene activation. Also trimmed the "Code
      Architecture" section, which duplicated a now-superseded description
      of SceneManager ("tracks active scene" singular) - pointed it at the
      rewritten `design/ARCHITECTURE.md` instead of re-describing components
      a third place.
- [x] 1.3 Remove the published credentials; document how they are configured.
      Already done as part of `secure-auth-and-debug`'s own task 3.4 -
      verified still correct, no further change needed here.
- [x] 1.4 Add a short "Documentation" section pointing at `docs/adr/` and
      `openspec/specs/`. Replaced the old "Key Design Decisions" bullet list
      (a third copy of content now properly homed in the ADRs) with this
      section, rather than leaving both.
- [x] 1.5 Update the project structure tree — it omits `docs/` and `openspec/`,
      and lists files that the `remove-dead-code` change deletes. On
      inspection the tree didn't actually list any already-deleted files;
      added `docs/adr/` and `openspec/`.

      Found something unrelated while checking the real directory tree:
      `app/dmx_interfaces/` exists on disk with only stale `__pycache__`
      files (no source) - it belongs to a separate `nodejs-versie` branch's
      Python analog, left over from a branch switch. Gitignored, untracked,
      not part of the current codebase - left out of the tree and not
      touched (cleanup is outside this change's scope), flagging to the user.

## 2. design/ARCHITECTURE.md

Rewrote the document rather than patching it in place — once the buffer
algorithm, the design-decisions list, and the code snippets were all stale or
duplicated elsewhere, there wasn't a coherent "patch" left; see the reply to
the user's question about document size for the reasoning. 570 lines → 147.

- [x] 2.1 Replace the `build_dmx_buffer()` documentation with `toggle_scene()`
      and the layer-set model.
- [x] 2.2 Rewrite the "Buffer Building Algorithm" section — it describes
      starting from current DMX values, which is the superseded behaviour.
      Replaced with the current toggle/rebuild description; the old
      code-snippet style is gone entirely (embedded code drifts from source,
      which is exactly how this document went stale in the first place).
- [x] 2.3 Correct `MAX_SCENES`. No longer states a specific number in prose
      (it's configurable) - points at `app/__init__.py` instead of
      hardcoding a value that will just go stale again.
- [x] 2.4 Update the SceneManager method list to match the class. Verified
      against the actual current method names in scene_manager.py,
      dmx_controller.py, dmx_controller_class.py, config_manager.py, and the
      real route lists in main.py/setup.py before writing anything.
- [x] 2.5 Replace the "Key Design Decisions" section with links into
      `docs/adr/`, rather than a second copy of the rationale.
- [x] 2.6 Note the known thread-safety gap, or remove the claim that buffer
      access is thread-safe, until `thread-safe-dmx-buffers` lands.
      **Superseded**: that change landed and was archived earlier in this
      session, so the gap no longer exists. Documented the actual current
      locking behaviour (single lock, snapshot-then-send-outside-lock)
      instead of a stale caveat.

## 3. design/SUMMARY.md

- [x] 3.1 Move "Scene grouping and categories" out of future improvements.
- [x] 3.2 Correct the "monkey patching" description of the Art-Net integration.
      Both occurrences (Key Technologies and Design Patterns) - it wasn't
      just the "future improvements" line that was wrong.
- [x] 3.3 Remove the published credentials. Both occurrences (Key
      Technologies bullet and the "Running the Application" section).
      Kept this file's edits surgical per the proposal's own non-goal
      ("not rewriting wholesale") - didn't apply the same shrink treatment
      here that ARCHITECTURE.md got.

## 4. .github/copilot-instructions.md

- [x] 4.1 Rewrite the scene activation section for the layered model. Went
      beyond this one section: also fixed the SceneManager method list
      (`build_dmx_buffer` → `toggle_scene`/`get_active_scenes`), the fixture
      linking description (index → name), the DMX thread section (now
      documents the actual lock instead of a vague "thread-safe" claim), the
      config schema example, and the API response shapes - all now-wrong
      because of work landed this session, not because the original task
      list under-scoped them.
- [x] 4.2 Correct `MAX_SCENES`. Phrased to point at the source rather than
      hardcode 40, so it can't go stale the same way again.
- [x] 4.3 Fix the "don't modify" list: drop `app/views/` from it, drop the
      non-existent `routes/`, and drop `lib/` once it is deleted. Already
      done as part of `remove-dead-code`'s own implementation - verified
      still correct.
- [x] 4.4 Add a pointer to `docs/adr/` and `openspec/specs/` as the authoritative
      sources. Added both an inline mention near the top and a dedicated
      "Authoritative Documentation" section at the end, matching the
      pattern used in `README.md`.

Also corrected two entries this session's other changes made wrong, beyond
the four listed tasks: the "Thread safety" pitfall said "only modify
target_values from main thread," which predates the lock entirely and is
now both inaccurate and the wrong rule (the real rule is "go through the
locked methods"); and "Fixture index shifts" described exactly the manual
index-fixup burden that `fix-fixture-link-references` eliminated. Following
either as written would now actively mislead a future assistant.

## 5. Verify

- [x] 5.1 Every code reference in the four documents names something that
      actually exists. Grepped all four for every stale name/claim found
      during editing (`build_dmx_buffer`, `get_active_scene()`, `MAX_SCENES
      = 10`, "monkey"), confirmed zero remain; confirmed every file/directory
      path referenced (including the new `docs/adr/`, `openspec/specs/`,
      `openspec/changes/` pointers) actually exists on disk.
- [x] 5.2 No document publishes credentials. One `banana123` reference
      remains, in README's installation steps - verified it's the
      intentional, source-visible loopback-only dev fallback
      (`_DEV_USERNAME`/`_DEV_PASSWORD` in `app/__init__.py`), not a leaked
      production secret. Documenting it accurately matches source; that's
      the fix, not a violation.
- [x] 5.3 Numbers quoted for limits and durations match the source.
      `MAX_SCENES=40` and `TRANSITION_DURATION=3.0` confirmed against
      `app/__init__.py`/`app/dmx_controller_class.py`; the two remaining
      "2 seconds" mentions are correctly framed as historical
      spec-vs-implementation notes, not current-behaviour claims.
- [x] 5.4 Someone unfamiliar with the project can follow `README.md` from clone
      to a running server. Read the full Installation section end-to-end;
      confirmed `.env.example` exists and matches exactly what step 4
      describes, and `requirements.txt` exists.
