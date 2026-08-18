# Secure authentication and disable the remote debugger

## Why

Two issues in the current deployment are more serious than anything else in the
codebase, and they compound each other.

**The operator credentials are committed to a public repository.**
`app/__init__.py` contains `ADMIN_USERNAME = "admin"` and
`ADMIN_PASSWORD = "banana123"` as module constants. Anyone who finds the GitHub
repository knows the password for every deployment that has not edited the
source. There is no way to change them without a code edit and redeploy.

**The Werkzeug debugger is exposed to the network.** `app.py` calls
`app.run(host='0.0.0.0', port=5050, debug=True)`. With `debug=True`, an
unhandled exception serves an interactive Python console. Bound to `0.0.0.0`,
that console is reachable from every device on the venue network. This is remote
code execution on the machine driving the lighting, and it is reachable by
anyone who can trigger an error path.

Together: a publicly known password guarding an interactive Python console on
the show machine.

## What changes

- Read credentials from environment variables at startup, falling back to the
  existing defaults **only** when the application is bound to loopback.
- Compare credentials with `secrets.compare_digest` instead of `==`.
- Remove the hardcoded password from source control.
- Drive `debug` from an environment variable, defaulting to off.
- Refuse to start with debug enabled while bound to a non-loopback interface.
- Document the required environment variables in `README.md`.

## Non-goals

- Multi-user accounts, roles, or a login UI. The single-operator model
  ([ADR-0013](../../../docs/adr/0013-http-basic-auth.md)) is unchanged.
- HTTPS. Basic Auth still transmits credentials in cleartext on the LAN; that is
  a separate decision with its own trade-offs (certificate warnings on every
  device).
- Rotating or hashing stored credentials. Out of proportion for one account.

## Impact

- Affected specs: `access-control`
- Affected code: `app/__init__.py`, `app.py`, `README.md`, `start.sh`
- **Operational:** after this change, starting the server on a network
  interface requires `DMXLIFE_USERNAME` and `DMXLIFE_PASSWORD` to be set. This
  is a deliberate breaking change — a silent fallback to a public password is
  the problem being fixed.
