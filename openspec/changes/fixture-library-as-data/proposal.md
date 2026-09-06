## Why

Every fixture type the system understands is a hardcoded dictionary in
`app/models/fixture.py`. Adding a model of lamp means editing Python, in a
project someone else has cloned, and redeploying.

For this installation that has been survivable - the kit is stable. It is the
single largest barrier to anyone else using the project, and it puts a code
change in the path of what is really a data entry task. Someone with a
different rig cannot get started without opening a source file.

It also means the fixture library cannot be shared, versioned or extended
independently of the software release cycle.

## What Changes

- Fixture type definitions move out of Python into a data file - the channel
  list for each type, with each channel's name, default value and whether it is
  shown in the editor.
- The application loads the library at startup and reports clearly if it is
  missing or malformed, rather than failing obscurely.
- A user can add a fixture type by editing that file, with no code change and
  no redeployment of the software.
- The definitions ship with the application, so an installation that adds
  nothing behaves exactly as it does today.
- Whether an operator's own additions live alongside the shipped library or in
  the operator data directory is a design decision this change has to make -
  the second allows a venue to add a lamp without touching the distribution,
  and follows the separation `separate-operator-data` establishes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `fixture-configuration`: the specification describes fixture types and their
  channel definitions as a property of the system. It gains requirements on
  where that library comes from, that it is extensible without modifying the
  software, and how an unusable library is reported.

## Impact

- Affected code: `app/models/fixture.py` (`FixtureType.TYPES` becomes loaded
  rather than literal), `app/views/setup.py` where fixture types are served to
  the editor.
- Affected data: a new library file shipped with the application. Existing
  configurations reference types by name and are unaffected as long as the
  shipped library keeps the current names.
- Not included: an editor for fixture types. The operator was explicit that
  making this part of the UI is not the goal - being able to change it at all,
  without editing code, is.
- Format choice (JSON or YAML) is a design decision. JSON needs no dependency
  and matches the rest of the project's storage; YAML is friendlier to
  hand-editing, which is the entire point of the change.
