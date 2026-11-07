#!/usr/bin/env python3
"""Reproduce a submission: run its README's run commands in a throwaway container.

Usage: python3 tools/repro.py <github-url | local-path> [--timeout 180]

1. Copies the repo into a temp folder (a shallow clone for URLs).
2. Finds the first shell code block under a Run / Quickstart / Usage heading.
3. Picks an image from the stack (package.json -> node, requirements.txt or
   pyproject -> python, go.mod -> golang, otherwise debian).
4. Runs the commands with `docker run --rm` under CPU, memory, PID and time
   limits, with the copy mounted and nothing else from the host.
5. Prints JSON: verdict, commands, exit code, the last lines of output.

The submission's code never runs on the host. Standard library only.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HEADING_RE = re.compile(r"^#{1,4}\s*(run|running|quick ?start|getting started|usage|how to run)\b.*$", re.I | re.M)
BLOCK_RE = re.compile(r"```(?:bash|sh|shell|console|zsh)?\s*\n(.*?)```", re.S)
SETUP_HEADING_RE = re.compile(r"^#{1,4}\s*(setup|install|installation)\b.*$", re.I | re.M)

# Docker Desktop's credential helper lives in the app bundle, which agent
# shells often lack on PATH; without it `docker run` fails before pulling.
for _bin in ("/Applications/Docker.app/Contents/Resources/bin", os.path.expanduser("~/.docker/bin")):
    if os.path.isdir(_bin) and _bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = _bin + os.pathsep + os.environ.get("PATH", "")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from preflight import resolve, find_readme  # noqa: E402


def commands_from_readme(text):
    """Return the setup commands followed by the run commands."""
    def block_after(match):
        if not match:
            return []
        rest = text[match.end():]
        nxt = re.search(r"^#{1,4}\s", rest, re.M)
        section = rest[: nxt.start()] if nxt else rest
        b = BLOCK_RE.search(section)
        if not b:
            return []
        lines = []
        for line in b.group(1).splitlines():
            line = line.strip()
            if line.startswith("$ "):
                line = line[2:]
            if line and not line.startswith("#"):
                lines.append(line)
        return lines

    setup = block_after(SETUP_HEADING_RE.search(text))
    run = block_after(HEADING_RE.search(text))
    seen, out = set(), []
    for c in setup + run:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def pick_image(path):
    if os.path.exists(os.path.join(path, "package.json")):
        return "node:20-slim"
    if any(os.path.exists(os.path.join(path, f)) for f in ("requirements.txt", "pyproject.toml", "setup.py")):
        return "python:3.12-slim"
    if os.path.exists(os.path.join(path, "go.mod")):
        return "golang:1.22"
    if any(f.endswith(".py") for f in os.listdir(path)):
        return "python:3.12-slim"
    return "debian:bookworm-slim"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    timeout = 180
    if "--timeout" in sys.argv:
        timeout = int(sys.argv[sys.argv.index("--timeout") + 1])
        args = [a for a in args if a != str(timeout)]
    if not args:
        print(__doc__)
        sys.exit(2)

    if subprocess.run(["docker", "info"], capture_output=True).returncode != 0:
        print(json.dumps({"verdict": "ERROR", "reason": "Docker is not running on the reproducer's machine."}))
        sys.exit(1)

    path, cleanup, label = resolve(args[0])
    work = tempfile.mkdtemp(prefix="shortlist-run-")
    try:
        shutil.copytree(path, os.path.join(work, "src"), ignore=shutil.ignore_patterns(".git", "node_modules"))
        src = os.path.join(work, "src")
        readme = find_readme(src)
        text = open(readme, encoding="utf-8", errors="replace").read() if readme else ""
        cmds = commands_from_readme(text)
        report = {"target": label, "commands": cmds}
        if not cmds:
            report.update(verdict="FAIL", reason="No runnable commands found under a Run/Quickstart/Usage heading.")
            print(json.dumps(report, indent=2))
            return

        image = pick_image(src)
        script = "set -e\n" + "\n".join(cmds) + "\n"
        with open(os.path.join(work, "run.sh"), "w") as f:
            f.write(script)
        name = "shortlist-%d" % int(time.time() * 1000)
        docker = [
            "docker", "run", "--rm", "--name", name,
            "--cpus", "1", "--memory", "1g", "--pids-limit", "256",
            "--security-opt", "no-new-privileges",
            "-v", "%s:/work" % work, "-w", "/work/src",
            "-e", "CI=1", image, "sh", "/work/run.sh",
        ]
        started = time.time()
        try:
            r = subprocess.run(docker, capture_output=True, text=True, timeout=timeout)
            code, out = r.returncode, (r.stdout + r.stderr)
            timed_out = False
        except subprocess.TimeoutExpired as e:
            subprocess.run(["docker", "kill", name], capture_output=True)
            code = 124
            out = ((e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or ""))
            timed_out = True
        tail = [l for l in out.strip().splitlines() if l.strip()][-15:]
        if code == 0:
            verdict = "PASS"
        elif timed_out:
            verdict = "PARTIAL"
        else:
            verdict = "FAIL"
        report.update(
            verdict=verdict,
            image=image,
            exit_code=code,
            timed_out=timed_out,
            seconds=round(time.time() - started, 1),
            output_tail=tail,
        )
        print(json.dumps(report, indent=2))
    finally:
        shutil.rmtree(work, ignore_errors=True)
        if cleanup:
            shutil.rmtree(cleanup, ignore_errors=True)


if __name__ == "__main__":
    main()
