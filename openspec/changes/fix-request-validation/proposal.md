# Validate API request payloads

## Why

Several endpoints accept unvalidated input and crash with HTTP 500 instead of
returning a useful error. All of the following were reproduced against the
running application:

| Request | Expected | Actual |
|---|---|---|
| `DELETE /setup/api/config/scenes` with `{}` | 400, name required | **500** `KeyError: 'name'` |
| `POST /setup/api/config/scenes/test` with a channel value of `300` | 400 | **500** |
| `POST /setup/api/config/scenes/test` with a non-numeric channel | 400 | **500** |
| `POST /setup/api/config/network` with a non-numeric port | 400 | **500** |

The delete case is the clearest defect. The guard at `app/views/setup.py:113`
reads:

```python
if not data.get('name') not in data:
```

Python parses this as `not (data.get('name') not in data)` — it asks whether the
*scene name* is a *key* in the request payload, which is meaningless. For a
well-formed request it happens to evaluate falsy, so deletion works by accident.
For a payload with no name it also evaluates falsy, so execution falls through
to `data['name']` and raises `KeyError`. A guard that exists specifically to
catch the missing-name case does not catch it.

It would also refuse to delete a scene named `name`, since that string *is* a
key in the payload.

These are 500s, not data corruption — no request in this set damaged
`config.json`. The cost is diagnostic: a crash tells the operator nothing, and
in the current configuration it renders the Werkzeug debugger, complete with
source and a console prompt. That makes this change a partial mitigation for the
same exposure as `secure-auth-and-debug`, and the two should land together.

## What changes

- Replace the delete guard with a correct check that rejects a missing or empty
  name with 400.
- Validate that channel payloads are lists of integers in 0–255 before writing
  them to a DMX buffer, rejecting anything else with 400.
- Parse network settings defensively, returning 400 on non-numeric values rather
  than letting `int()` raise.
- Reject request bodies that are absent or not JSON objects with 400.

## Non-goals

- Introducing a validation framework or schema library. These are four
  endpoints; explicit checks are clearer than a dependency.
- Changing any success-path behaviour or response shape.
- Authentication and debugger changes — those are `secure-auth-and-debug`.

## Impact

- Affected specs: `scene-authoring`, `network-configuration`
- Affected code: `app/views/setup.py`, `app/dmx_controller.py`
- No client changes required; the frontend already handles
  `{success: false, message}` responses.
