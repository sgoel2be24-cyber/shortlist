# Standup Relay

Async standups for teams spread across time zones. A Switch room collects each
person's update, a summariser agent posts a digest at 9:00 local time for every
region, and a blocker-hunter agent pings owners when someone is stuck.

Demo video: https://youtu.be/standup-relay-demo

## How Switch is used
- `standup.template.yaml` creates the room, the `summariser` and `blocker-hunter` roles, and both agents.
- Room instructions hold the team's standup format.
- The `digest` room document is rewritten by the summariser every day.

## Run

```bash
python3 relay.py --selftest
```

## License
MIT
