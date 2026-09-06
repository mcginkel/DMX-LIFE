## Why

Two small frictions in the scene editor, both noticed in real use.

Scenes are listed in the order they happen to sit in storage. The main page
groups them - Main, Achtergrond, Sfeer, Alles Aan/Uit, Extra - but the editor's
list ignores grouping entirely and offers no alphabetical fallback. With
eighteen scenes and rising, finding the one to edit means reading the whole
list. The editor and the page the operator actually uses during a show present
the same scenes in two different orders.

Creating a new scene starts with the rig dark and stays dark until a control is
touched. Opening an *existing* scene previews it immediately, and moving any
slider or toggling any fixture previews too - so the preview behaviour is
inconsistent in exactly the case where the operator is building something from
nothing and most wants to see it.

Neither is a defect. Both are the kind of friction that makes a tool feel worse
than it is.

## What Changes

- The editor's scene list is ordered by group, in the same order the main page
  presents groups, and alphabetically within each group.
- The list makes the grouping visible, so the operator can see which group a
  scene belongs to without opening it.
- Entering the editor to create a new scene begins previewing immediately, so
  the rig reflects what is being built from the first moment rather than from
  the first interaction.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `scene-authoring`: "Scene preview" requires an immediate preview path for
  judging a scene while editing, but does not say when previewing begins. It
  gains the requirement that editing a scene - including a new one - previews
  from the start. Presentation order of the scene list also becomes a stated
  requirement rather than an accident of storage order.

## Impact

- Affected code: `app/static/js/scenes.js` (list ordering and rendering, and
  the preview call on entering create mode).
- Consideration for the design: previewing a new scene means transmitting a
  frame of all zeros the moment the operator clicks "Create New Scene", which
  blacks out the rig. That is arguably correct - it is what the scene currently
  contains - but it is abrupt if a look is live. Whether creating a scene should
  preview immediately or preview from the current output needs deciding rather
  than assuming.
- No change to stored data, scene composition, or the API.
