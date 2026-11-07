# Standup Relay

Async standups for teams spread across time zones. People post their update in
a Switch room. A **summariser** agent writes one digest per region at 9:00
local time, and a **blocker-hunter** agent pings the person who can unblock
anyone who is stuck.

## Who it's for
Distributed engineering teams (we built it for our IST, GMT and PST squad)
whose standup calls always land at midnight for somebody.

## How Switch is used
- `standup.template.yaml` creates the room, **both agents** (`summariser`,
  `blocker-hunter`), the `summariser` (exclusive) and `blocker-hunter` (shared)
  roles, the standup format as room instructions, and the `digest` room
  document.
- The summariser runs `relay.py digest` and rewrites the `digest` document.
- The blocker-hunter runs `relay.py blockers` and @-mentions each owner in the room.

## Run

```bash
python3 relay.py --selftest
```

`python3 relay.py digest updates.json` prints today's digest grouped by region;
`python3 relay.py blockers updates.json` prints the pings.

## License
MIT
