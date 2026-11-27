"""Stop check for chainwright's chain_loop.py when sessions work in worktrees and merge
through PRs: progress is origin/main moving, and the run ends on `Status: finished`
in origin/main's HANDOFF.md. Prints {may_stop, why, waiting_on, fingerprint}."""
import json, re, subprocess

def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, encoding="utf-8").stdout

git("fetch", "-q", "origin", "main")
head = git("rev-parse", "origin/main").strip()
handoff = git("show", "origin/main:ai-docs/HANDOFF.md")
done = bool(re.search(r"^Status:\s*finished\b", handoff, re.I | re.M))
print(json.dumps({"may_stop": done, "why": ["origin/main HANDOFF.md: Status: finished"] if done else [],
                  "waiting_on": [], "fingerprint": head}))
