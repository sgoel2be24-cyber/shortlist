"""Standup Relay: groups standup updates into a digest (the logic the summariser agent calls)."""
import sys

UPDATES = [
    ("asha", "IST", "Shipped login page", "none"),
    ("ben", "GMT", "Reviewing PR #42", "waiting on API keys from ops"),
    ("chen", "PST", "Fixing flaky test", "none"),
]


def digest(updates):
    lines = ["# Daily digest"]
    blockers = [u for u in updates if u[3] != "none"]
    for who, tz, did, _ in updates:
        lines.append("- %s (%s): %s" % (who, tz, did))
    if blockers:
        lines.append("## Blockers")
        lines += ["- %s: %s" % (b[0], b[3]) for b in blockers]
    return "\n".join(lines)


if __name__ == "__main__":
    out = digest(UPDATES)
    print(out)
    if "--selftest" in sys.argv:
        assert "ben: waiting on API keys" in out, "blocker missing"
        print("selftest: OK (3 updates, 1 blocker)")
