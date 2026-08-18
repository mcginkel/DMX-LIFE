# Tasks: secure authentication and disable the remote debugger

## 1. Credentials from the environment

- [ ] 1.1 Read `DMXLIFE_USERNAME` and `DMXLIFE_PASSWORD` in `app/__init__.py`
      instead of using module constants.
- [ ] 1.2 Replace the `==` comparison in `verify_password` with
      `secrets.compare_digest` on both username and password.
- [ ] 1.3 Remove the hardcoded `admin` / `banana123` constants from source.
- [ ] 1.4 Fall back to development defaults only when the bind address is
      loopback, logging a warning that development credentials are in use.
- [ ] 1.5 Refuse to start with a clear message naming the missing variables when
      bound to a non-loopback address without credentials.

## 2. Debugger handling

- [ ] 2.1 Move the bind address into `DMXLIFE_HOST`, defaulting to `127.0.0.1`.
- [ ] 2.2 Drive `debug` from `DMXLIFE_DEBUG`, defaulting to off.
- [ ] 2.3 Refuse to start when debug is enabled and the bind address is not
      loopback, explaining the risk.

## 3. Deployment

- [ ] 3.1 Have `start.sh` source a gitignored `.env` if present and set
      `DMXLIFE_HOST=0.0.0.0`.
- [ ] 3.2 Add `.env` to `.gitignore`.
- [ ] 3.3 Add a `.env.example` documenting the variables with placeholder values.
- [ ] 3.4 Update `README.md`: replace the published default credentials with
      setup instructions.

## 4. Verification

- [ ] 4.1 Unauthenticated request to `/` returns 401.
- [ ] 4.2 Request with environment-supplied credentials succeeds.
- [ ] 4.3 Request with the old `admin` / `banana123` credentials is rejected.
- [ ] 4.4 Start bound to `0.0.0.0` without credentials refuses, and the message
      names the variables.
- [ ] 4.5 Start bound to `0.0.0.0` with `DMXLIFE_DEBUG` enabled refuses.
- [ ] 4.6 Start on loopback without credentials works and warns.
- [ ] 4.7 `start.sh` still produces a working server reachable from another
      device on the LAN.

## 5. Follow-up

- [ ] 5.1 Choose a new password; treat `banana123` as permanently compromised
      because it remains in public git history.
