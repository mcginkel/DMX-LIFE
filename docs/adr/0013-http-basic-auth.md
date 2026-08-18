# ADR-0013: HTTP Basic Auth with hardcoded credentials

- **Status:** Accepted (known risk)
- **Date:** 2026-08-18 (documented retroactively)

## Context

DMX Life runs on a laptop on the venue's local network and controls the room's
lighting. The threat model is modest: the main concern is a guest on the same
Wi-Fi stumbling onto the page and blacking out the room mid-event, not a
targeted attack.

Some access control is nonetheless needed, because the server binds
`0.0.0.0:5050` and is therefore reachable from every device on the network.

## Decision

Protect every route with HTTP Basic Auth via `flask-httpauth`, using a single
username and password defined as module constants in `app/__init__.py`:

```python
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "banana123"
```

Every view carries `@auth.login_required`. There is one account and no
password-change mechanism.

## Consequences

**Good:**

- Every endpoint is covered by default; a new route without the decorator is a
  visible omission rather than a silent hole.
- Browsers cache the credentials for the session, so the operator authenticates
  once per boot.
- Zero configuration on a show night.

**Bad — and these are real:**

- **The credentials are committed to a public GitHub repository.** Anyone who
  finds the repo knows the password for every deployment that has not changed
  it. This is the single most serious issue in the codebase.
- **Basic Auth over plain HTTP transmits the password in base64 on every
  request**, readable by anyone on the same network — which is precisely the
  population the auth is meant to exclude.
- **Credentials cannot be changed without editing source and redeploying.**
  There is no environment variable, no config entry, no UI.
- **Password comparison is a plain `==`**, which is timing-attack-sensitive.
  Marginal in this threat model, but free to fix with `secrets.compare_digest`.
- Separately, `app.py` runs with `debug=True` while bound to `0.0.0.0`. The
  Werkzeug debugger offers an interactive console on unhandled exceptions,
  which is remote code execution for anyone who can reach it and get past — or
  around — the auth. **This combination is more dangerous than the weak
  password itself.**

## Status rationale

This is recorded as *Accepted (known risk)* rather than *Accepted* because the
decision to use Basic Auth is defensible for the threat model, but the specific
implementation is not. The credential handling and the debug flag should change;
see the `secure-auth-and-debug` change proposal in `openspec/changes/`.

## Alternatives considered

- **Credentials from environment variables** with a hashed default and
  `secrets.compare_digest`. Small change, removes the secret from git, keeps
  everything else. The recommended immediate fix.
- **No authentication at all**, relying on network isolation. Honest about the
  threat model and removes the false sense of security, but leaves the room
  one curious guest away from a blackout.
- **Session-based login with a user table.** Proper, and unnecessary for a
  single-operator tool.
- **HTTPS with a self-signed certificate.** Would protect the password in
  transit, at the cost of browser warnings on every device. Worth it only if
  the app ever leaves a trusted LAN.
