# Design: secure authentication and debugger handling

## Context

The application is started by `start.sh` on a venue laptop, often by someone who
is not the developer. Any design that makes the secure path harder than the
insecure one will be worked around, so the goal is to make the safe
configuration the default and the unsafe one impossible to reach by accident.

The constraint that shapes everything: this must not turn a pre-show start into
a debugging session. A hard failure is acceptable **only** when it comes with a
message that says exactly what to do.

## Decisions

### Bind address determines strictness

Rather than a separate "production" flag that someone must remember to set, the
strictness follows from the bind address, which is already an explicit choice:

| Bind address | Credentials absent | Debug requested |
|---|---|---|
| loopback (`127.0.0.1`) | start with defaults + warning | allowed |
| anything else | refuse to start | refuse to start |

This means the developer workflow (`python app.py` on loopback) keeps working
with no environment setup, while the deployment path cannot silently run with a
public password.

The bind address moves out of the `app.run()` call into `DMXLIFE_HOST`,
defaulting to `127.0.0.1`. **This changes the current behaviour**, where the
default is `0.0.0.0`. `start.sh` sets `DMXLIFE_HOST=0.0.0.0` explicitly, so the
venue workflow is unchanged apart from needing credentials.

### Environment variables, not config.json

Credentials go in the environment rather than `config.json`, because
`config.json` is committed to git ([ADR-0001](../../../docs/adr/0001-json-file-as-system-of-record.md)
treats it as version-controlled state). Putting a password there recreates the
problem this change is fixing.

Variables:

- `DMXLIFE_USERNAME`, `DMXLIFE_PASSWORD` — credentials.
- `DMXLIFE_HOST` — bind address, default `127.0.0.1`.
- `DMXLIFE_DEBUG` — debugger, default off.

### Failure messages name the fix

A refusal prints the exact variable to set and an example invocation. A person
starting the show in fifteen minutes should not have to read source to recover.

## Risks

- **Someone hardcodes the values back into `start.sh` and commits it.** Mitigated
  by having `start.sh` read from the environment or a gitignored `.env`, and by
  adding `.env` to `.gitignore`.
- **The venue laptop loses its environment** (new shell, new user account) and
  the server refuses to start before an event. This is the main operational
  risk. Mitigated by a gitignored `.env` file that `start.sh` sources, so the
  credentials survive in one place on the machine without entering git.

## Open questions

- Should the existing `banana123` be treated as compromised and changed, given
  it is in public git history? Removing it from the working tree does not remove
  it from history. Recommendation: yes — pick a new password, since the old one
  is permanently public.
