# Bring the existing documentation up to date

## Why

Four documents describe the system, and all four now contain statements that are
false. They predate both the scene-layering rework and the ADRs, and they are
the first thing a new reader — human or AI assistant — encounters.

| Document | What is wrong |
|---|---|
| `README.md` | "Create up to 10 lighting scenes" (the limit is 40, and 18 exist). Publishes the admin password. Describes single-scene activation with no mention of layering or groups. |
| `design/ARCHITECTURE.md` | Documents `SceneManager.build_dmx_buffer()` and `get_active_scene()` as the core API; `build_dmx_buffer` no longer exists, replaced by `toggle_scene()`. States `MAX_SCENES` is 10. Describes the buffer algorithm as "start with current DMX values", which is precisely the behaviour [ADR-0005](../../../docs/adr/0005-layered-scene-state.md) replaced. |
| `design/SUMMARY.md` | Lists "Scene grouping and categories" as a future improvement; it shipped. Describes `StupidArtnet` as "monkey-patched", which is not what the code does — it bypasses the library's methods rather than patching them ([ADR-0002](../../../docs/adr/0002-artnet-via-direct-socket-sends.md)). |
| `.github/copilot-instructions.md` | Documents the pre-layering scene model as current. Says `MAX_SCENES = 10`. Tells assistants not to modify `lib/`, `routes/` and `views/` as "legacy" — but `app/views/` is live code, and `routes/` does not exist. |

The `views/` instruction is the most damaging: it steers assistants away from
one of the most frequently edited directories in the project.

## What changes

- Correct the factual errors in all four documents.
- Point `ARCHITECTURE.md` and `SUMMARY.md` at `docs/adr/` for rationale rather
  than duplicating it, keeping them as orientation documents.
- Rewrite the scene-model sections to describe layering, groups, and toggling.
- Remove the published credentials from `README.md`, replacing them with setup
  instructions.
- Fix the misleading "do not modify" list in the Copilot instructions.
- Add a short section to `README.md` describing `docs/adr/` and `openspec/`.

## Non-goals

- Rewriting the documents wholesale. They are largely accurate and worth
  keeping; this corrects them.
- Deleting `design/prompt.txt`. It is a historical record of the original brief
  and should stay as-is, including its 2-second fade specification that
  [ADR-0004](../../../docs/adr/0004-fixed-linear-crossfade.md) explains was
  changed.
- Documenting behaviour that the change proposals have not yet implemented.

## Impact

- Affected specs: none — documentation only.
- Affected code: `README.md`, `design/ARCHITECTURE.md`, `design/SUMMARY.md`,
  `.github/copilot-instructions.md`.
- Depends on `secure-auth-and-debug` for the credential section; if that lands
  first, document the environment variables instead of a password.
