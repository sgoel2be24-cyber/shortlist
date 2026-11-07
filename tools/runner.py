#!/usr/bin/env python3
"""Shortlist sandbox runner: the only process that executes submission code.

Usage: python3 tools/runner.py [--watch ~/.switch/agents] [--interval 3]

Agents never run submission code themselves. The reproducer agent files a job
by writing `shortlist-queue/<case>.request.json` in its working directory:

    {"case": "S-1", "target": "https://github.com/owner/repo"}

This runner finds new requests under the watched folder, runs tools/repro.py
on the target (which runs the README's commands in a locked-down Docker
container), and writes `shortlist-queue/<case>.result.json` next to the
request. The agent reads the result and reports it in the room.

Splitting things this way keeps a hard line between the agent, which reads
untrusted text, and the executor, which runs untrusted code. A human starts
the runner, and it can be stopped at any time with Ctrl-C.
"""
import glob
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET_RE = re.compile(r"^https://github\.com/[\w.-]+/[\w.-]+(/tree/[\w./-]+)?/?$")
CASE_RE = re.compile(r"^[A-Za-z0-9_-]{1,32}$")


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def handle(req_path):
    base = req_path[: -len(".request.json")]
    res_path = base + ".result.json"
    running = base + ".running"
    os.rename(req_path, running)
    try:
        job = json.load(open(running))
        case, target = str(job.get("case", "")), str(job.get("target", ""))
        if not CASE_RE.match(case) or not TARGET_RE.match(target):
            result = {"case": case, "verdict": "ERROR", "reason": "Rejected: target must be a public GitHub URL."}
        else:
            log("▶ %s  %s" % (case, target))
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "repro.py"), target],
                capture_output=True, text=True, timeout=600,
            )
            try:
                result = json.loads(r.stdout)
            except ValueError:
                result = {"verdict": "ERROR", "reason": (r.stdout + r.stderr)[-800:]}
            result["case"] = case
        result["runner"] = "shortlist sandbox runner"
        tmp = res_path + ".tmp"
        json.dump(result, open(tmp, "w"), indent=2)
        os.rename(tmp, res_path)
        log("■ %s  %s (exit %s)" % (case, result.get("verdict"), result.get("exit_code")))
    finally:
        if os.path.exists(running):
            os.remove(running)


def main():
    watch = os.path.expanduser("~/.switch/agents")
    interval = 3.0
    if "--watch" in sys.argv:
        watch = os.path.expanduser(sys.argv[sys.argv.index("--watch") + 1])
    if "--interval" in sys.argv:
        interval = float(sys.argv[sys.argv.index("--interval") + 1])
    patterns = [
        os.path.join(watch, "shortlist-queue", "*.request.json"),
        os.path.join(watch, "*", "shortlist-queue", "*.request.json"),
        os.path.join(watch, "*", "*", "shortlist-queue", "*.request.json"),
    ]
    log("Shortlist sandbox runner watching %s (Ctrl-C to stop)" % watch)
    while True:
        for pattern in patterns:
            for req in sorted(glob.glob(pattern)):
                try:
                    handle(req)
                except Exception as e:  # keep serving other jobs
                    log("! %s: %s" % (req, e))
        time.sleep(interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("runner stopped")
