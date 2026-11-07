"""Standup Relay: the logic the Switch agents call.

  relay.py digest   <updates.json>  -> markdown digest per region (summariser agent)
  relay.py blockers <updates.json>  -> one @-mention per blocker (blocker-hunter agent)
  relay.py --selftest               -> runs the checks below on the bundled updates.json
"""
import json
import os
import sys

# 9:00 local, expressed in UTC, per region (no DST handling needed for the demo regions).
DIGEST_UTC = {"IST": "03:30", "GMT": "09:00", "PST": "17:00"}
REQUIRED = {"who", "region", "did", "next"}


class BadUpdate(ValueError):
    pass


def load(path):
    try:
        with open(path) as f:
            items = json.load(f)
    except (OSError, ValueError) as e:
        raise BadUpdate("cannot read %s: %s" % (path, e))
    for i, u in enumerate(items):
        missing = REQUIRED - set(u)
        if missing:
            raise BadUpdate("update %d is missing %s" % (i, ", ".join(sorted(missing))))
        if u["region"] not in DIGEST_UTC:
            raise BadUpdate("update %d has unknown region %r" % (i, u["region"]))
    return items


def digest(updates):
    out = []
    for region in sorted(DIGEST_UTC, key=lambda r: DIGEST_UTC[r]):
        rows = [u for u in updates if u["region"] == region]
        if not rows:
            continue
        out.append("## %s digest (posts %s UTC)" % (region, DIGEST_UTC[region]))
        for u in rows:
            flag = " ⛔" if u.get("blocker") else ""
            out.append("- **%s**: %s → next: %s%s" % (u["who"], u["did"], u["next"], flag))
    return "\n".join(out)


def blockers(updates):
    return [
        "@%s %s is blocked on you: %s" % (u["blocker"]["waiting_on"], u["who"], u["blocker"]["what"])
        for u in updates if u.get("blocker")
    ]


def selftest():
    here = os.path.dirname(os.path.abspath(__file__))
    ups = load(os.path.join(here, "updates.json"))
    d = digest(ups)
    print(d)
    pings = blockers(ups)
    print("\n".join(pings))
    assert d.index("## IST") < d.index("## GMT") < d.index("## PST"), "regions out of order"
    assert pings == ["@priya ben is blocked on you: API keys from ops",
                     "@chen dev is blocked on you: staging DB access"], pings
    try:
        load(os.path.join(here, "README.md"))
        raise AssertionError("bad input accepted")
    except BadUpdate:
        pass
    print("selftest: OK (4 updates, 3 regions, 2 blockers, bad input rejected)")


if __name__ == "__main__":
    args = sys.argv[1:]
    try:
        if args[:1] == ["--selftest"]:
            selftest()
        elif len(args) == 2 and args[0] in ("digest", "blockers"):
            ups = load(args[1])
            print(digest(ups) if args[0] == "digest" else "\n".join(blockers(ups)))
        else:
            print(__doc__)
            sys.exit(2)
    except BadUpdate as e:
        print("error:", e, file=sys.stderr)
        sys.exit(1)
