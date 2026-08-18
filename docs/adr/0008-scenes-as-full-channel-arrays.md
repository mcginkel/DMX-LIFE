# ADR-0008: Scenes stored as full 512-value arrays

- **Status:** Accepted (known risk)
- **Date:** 2026-08-18 (documented retroactively)

## Context

A scene needs to record DMX values. A universe has 512 channels, but a typical
scene touches far fewer — the current rig patches 128 channels, and a
background-colour scene meaningfully sets 12 of them.

The scene editor works by rendering a slider per channel for each enabled
fixture and reading their values back on save.

## Decision

Persist each scene's `channels` as a flat JSON array of integers indexed by
channel, with index 0 corresponding to DMX channel 1. Unused channels are
stored as `0`.

The array is not required to be exactly 512 long; application code guards with
`channel < len(channel_values)`, and older scenes in `config.json` are various
lengths (664, 1203, 2275 entries) depending on how they were produced.

## Consequences

**Good:**

- Applying a scene is a direct index lookup — no sparse-map decoding, no
  key parsing.
- The editor's slider-per-channel model maps one-to-one onto the storage
  format.
- Generating scenes programmatically is trivial: build a 512-entry list and
  write it. This is how the Daslight-derived scenes were imported.

**Bad:**

- **The config file is dominated by zeros.** `app/config.json` is roughly
  200 KB, the overwhelming majority of it `0,` lines from `indent=4`
  serialisation. Combined with [ADR-0001](0001-json-file-as-system-of-record.md)'s
  full-file rewrites, every scene save rewrites all of it.
- **Diffs are unreadable.** Changing one channel produces a diff buried in
  thousands of unchanged lines, which defeats the "state is in git" benefit
  ADR-0001 was aiming at.
- **Inconsistent array lengths.** Some stored arrays exceed 512 entries, which
  is meaningless for a single universe. Nothing validates or normalises this;
  the extra entries are simply ignored on read.
- The format assumes exactly one universe. Supporting a second would require
  either a second array or a rethink.

## Alternatives considered

- **Sparse channel map** (`{"111": 255, "112": 130}`). Would shrink the file by
  more than an order of magnitude and make diffs legible. JSON object keys must
  be strings, so it needs conversion on both sides, and it interacts with
  [ADR-0007](0007-sparse-overlay-via-empty-enabled-fixtures.md) — a sparse map
  makes "claimed" explicit, which would let that overload be retired. The
  strongest candidate for a future schema change.
- **Per-fixture nested values** (`{"Perf1": [255, 200, ...]}`). Reads well and
  survives re-patching a fixture to a different address. Bigger rewrite of both
  the editor and the buffer builder.
- **Compact serialisation** (`indent=None`, or base64). Shrinks the file
  without changing the schema, but makes it unreadable by hand — losing the
  main benefit of ADR-0001.
