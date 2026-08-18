# Tasks: secure authentication and disable the remote debugger

## 1. Credentials from the environment

- [x] 1.1 Read `DMXLIFE_USERNAME` and `DMXLIFE_PASSWORD` in `app/__init__.py`
      instead of using module constants.
- [x] 1.2 Replace the `==` comparison in `verify_password` with
      `secrets.compare_digest` on both username and password.
- [x] 1.3 Remove the hardcoded `admin` / `banana123` constants from source.
      (Kept as clearly-labeled `_DEV_USERNAME`/`_DEV_PASSWORD` fallback,
      gated to loopback-only per 1.4 — see note below.)
- [x] 1.4 Fall back to development defaults only when the bind address is
      loopback, logging a warning that development credentials are in use.
- [x] 1.5 Refuse to start with a clear message naming the missing variables when
      bound to a non-loopback address without credentials.

## 2. Debugger handling

- [x] 2.1 Move the bind address into `DMXLIFE_HOST`, defaulting to `127.0.0.1`.
- [x] 2.2 Drive `debug` from `DMXLIFE_DEBUG`, defaulting to off.
- [x] 2.3 Refuse to start when debug is enabled and the bind address is not
      loopback, explaining the risk.

## 3. Deployment

- [x] 3.1 Have `start.sh` source a gitignored `.env` if present and set
      `DMXLIFE_HOST=0.0.0.0`. Also added a post-start liveness check (not
      explicitly listed) since a refused start would otherwise still print
      "started successfully" — see summary.
- [x] 3.2 Add `.env` to `.gitignore`. Already present (Python boilerplate,
      line 131) — verified, not duplicated.
- [x] 3.3 Add a `.env.example` documenting the variables with placeholder values.
- [x] 3.4 Update `README.md`: replace the published default credentials with
      setup instructions.

## 4. Verification

- [x] 4.1 Unauthenticated request to `/` returns 401.
- [x] 4.2 Request with environment-supplied credentials succeeds.
- [x] 4.3 Request with the old `admin` / `banana123` credentials is rejected
      (verified against a real deployment with configured credentials).
- [x] 4.4 Start bound to `0.0.0.0` without credentials refuses, and the message
      names the variables. Verified via `start.sh` itself, which now detects
      the refusal instead of reporting false success.
- [x] 4.5 Start bound to `0.0.0.0` with `DMXLIFE_DEBUG` enabled refuses.
- [x] 4.6 Start on loopback without credentials works and warns; old
      `admin`/`banana123` succeeds there (dev fallback), wrong password 401s.
- [x] 4.7 `start.sh` still produces a working server reachable on the network,
      with real credentials from `.env` — confirmed against 127.0.0.1 as a
      stand-in for a LAN device, config.json unaffected (18 scenes, byte
      diff clean before/after).

## 5. Follow-up

- [ ] 5.1 Choose a new password; treat `banana123` as permanently compromised
      because it remains in public git history. **Not done as part of this
      implementation** — it's an operational choice for the venue, not
      something to pick on their behalf. `.env.example` prompts for it.
