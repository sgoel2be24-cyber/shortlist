#!/usr/bin/env python3
"""Preflight check for a hackathon submission.

Usage: python3 tools/preflight.py <github-url | local-path> [--platform switch]

Clones the repo (shallow) or reads a local folder, then checks the things
judges always ask for, and prints a JSON report. Nothing from the submission
is executed. Standard library only (Python 3.9+).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

VIDEO_RE = re.compile(
    r"https?://(www\.)?(youtube\.com|youtu\.be|loom\.com|vimeo\.com|drive\.google\.com)/\S+",
    re.I,
)
RUN_HEADING_RE = re.compile(
    r"^#{1,4}\s*(run|running|quick ?start|getting started|setup|install|usage|how to run)\b",
    re.I | re.M,
)
CODE_EXT = {".py", ".js", ".ts", ".tsx", ".go", ".rs", ".java", ".rb", ".sh", ".mjs", ".yaml", ".yml"}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build"}


def resolve(target):
    """Return (local_path, cleanup_dir_or_None, source_label)."""
    if os.path.isdir(target):
        return os.path.abspath(target), None, target
    m = re.match(r"https://github\.com/([^/]+)/([^/#?]+)(?:/tree/([^/]+)/(.+))?", target)
    if not m:
        raise SystemExit(json.dumps({"error": "not a local folder or GitHub URL", "target": target}))
    owner, repo, branch, sub = m.groups()
    repo = repo[:-4] if repo.endswith(".git") else repo
    tmp = tempfile.mkdtemp(prefix="shortlist-")
    cmd = ["git", "clone", "--depth", "1", "--quiet"]
    if branch:
        cmd += ["--branch", branch]
    cmd += ["https://github.com/%s/%s.git" % (owner, repo), tmp]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        shutil.rmtree(tmp, ignore_errors=True)
        raise SystemExit(json.dumps({"error": "clone failed", "detail": r.stderr.strip()[-400:]}))
    path = os.path.join(tmp, sub) if sub else tmp
    return path, tmp, target


def walk_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            yield os.path.join(dirpath, f)


def find_readme(root):
    for name in os.listdir(root):
        if name.lower().startswith("readme"):
            return os.path.join(root, name)
    return None


def check(path, platform):
    files = list(walk_files(path))
    rel = [os.path.relpath(f, path) for f in files]
    readme_path = find_readme(path)
    readme = open(readme_path, encoding="utf-8", errors="replace").read() if readme_path else ""
    code_files = [f for f in files if os.path.splitext(f)[1] in CODE_EXT]

    platform_hits_code = 0
    for f in code_files[:400]:
        try:
            if platform.lower() in open(f, encoding="utf-8", errors="ignore").read().lower():
                platform_hits_code += 1
        except OSError:
            pass
    templates = [r for r in rel if r.endswith((".template.yaml", ".template.yml"))]

    checks = {
        "readme": bool(readme_path),
        "run_instructions": bool(RUN_HEADING_RE.search(readme)) and "```" in readme,
        "demo_video": bool(VIDEO_RE.search(readme)),
        "license": any(os.path.basename(r).upper().startswith(("LICENSE", "LICENCE", "COPYING")) for r in rel),
        "mentions_platform_in_readme": platform.lower() in readme.lower(),
        "platform_used_in_code": platform_hits_code > 0 or bool(templates),
        "has_code": len(code_files) > 0,
    }
    passed = sum(checks.values())
    fixes = {
        "readme": "Add a README.md.",
        "run_instructions": "Add a '## Run' section with the commands in a code block.",
        "demo_video": "Link your demo video (YouTube, Loom, Vimeo or Drive) in the README.",
        "license": "Add a LICENSE file.",
        "mentions_platform_in_readme": "Explain in the README how %s is used." % platform,
        "platform_used_in_code": "No %s config or code found. Judges weight platform use at 30%%." % platform,
        "has_code": "No source files found.",
    }
    return {
        "checks": checks,
        "score": "%d/%d" % (passed, len(checks)),
        "to_fix": [fixes[k] for k, ok in checks.items() if not ok],
        "facts": {
            "files": len(files),
            "code_files": len(code_files),
            "readme_words": len(readme.split()),
            "platform_templates": templates[:5],
            "platform_mentions_in_code_files": platform_hits_code,
            "video_link": (VIDEO_RE.search(readme).group(0) if VIDEO_RE.search(readme) else None),
        },
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    platform = "switch"
    if "--platform" in sys.argv:
        platform = sys.argv[sys.argv.index("--platform") + 1]
        args = [a for a in args if a != platform]
    if not args:
        print(__doc__)
        sys.exit(2)
    path, cleanup, label = resolve(args[0])
    try:
        report = {"target": label, "platform": platform}
        report.update(check(path, platform))
        print(json.dumps(report, indent=2))
    finally:
        if cleanup:
            shutil.rmtree(cleanup, ignore_errors=True)


if __name__ == "__main__":
    main()
