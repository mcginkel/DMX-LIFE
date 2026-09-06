## Why

The venue Raspberry Pi and the operator's laptop both run the application and
both are edited: operators change scenes on Sunday, the operator adjusts them
during the week at home. Today those two copies have no relationship. There is
no way to see what changed at the venue, no way to get home changes to the
venue except by carrying the Pi, and no backup of either.

The Pi has full internet at the venue, and the project already uses git for
everything else. Git is the right tool for the actual problem - two replicas
of the same data, edited independently, reconciled when convenient - and it
brings the thing the operator explicitly wants: a readable history of what
changed at the venue, which doubles as the record of what operators actually
did on a Sunday.

The dangerous part of git here is merging. A conflict resolved badly, or left
unresolved, must never reach a venue on a Sunday evening.

## What Changes

- The operator data directory becomes its own git repository, separate from
  the code repository. Code deploys one way; show data syncs both ways. Each
  gets the tool it needs and neither is in the other's path.
- The venue installation commits and pushes to its own branch, never to the
  main line. Reconciliation happens on the operator's laptop, where there are
  tools and time.
- Committing and pushing is performed by a scheduled sidecar, not by the
  application. The application only writes files. A slow push, an expired
  credential or an unreachable remote can therefore never make saving a scene
  fail during a show.
- The venue installation starts each session from the reconciled main line, so
  the operator's week of changes is in effect on Sunday without anyone at the
  venue doing anything.
- Divergence that has not reached the remote is preserved rather than
  discarded, so a network failure mid-session cannot cost an operator their
  work.

## Capabilities

### New Capabilities

- `show-data-sync`: how operator data is replicated between installations -
  what is guaranteed to reach the venue before a session, what is captured
  from it afterwards, how a failure to reach the remote is handled, and the
  rule that reconciliation never happens on the venue installation.

### Modified Capabilities

None. This adds a capability around operator data rather than changing how the
application behaves with it.

## Impact

- Affected code: none in the application, by design. The work is a data
  repository, a scheduled unit on the Pi, a start-of-session routine, and
  documentation.
- Depends on `separate-operator-data`: there is no self-contained directory to
  sync until that lands.
- Does not depend on `per-scene-files`. That change makes merges cleaner but
  is not required - the branch model already keeps conflicts away from the
  venue.
- Operational surface this introduces: credentials on the venue Pi, a
  scheduled job that can fail silently, and a branch that must actually be
  merged rather than accumulating forever. The specification needs to say what
  happens when each of those goes wrong.
- Deliberately excluded: any conflict resolution on the venue installation.
  If reconciliation is ever needed there, the correct behaviour is to refuse
  and report, not to guess.
