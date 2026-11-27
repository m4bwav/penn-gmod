# gm_penn_station

Garry's Mod map of the 1910 Pennsylvania Station, New York (McKim, Mead & White), generated from Python.

- Start here: ai-docs/HANDOFF.md (state), ai-docs/plans/penn-gmod-plan.md (scope, scale, area order, budgets), ai-docs/log.md.
- Chain prompt: ai-docs/plans/2026-11-25-penn-gmod-60x-continue-prompt.md. One worktree per session; merge through PRs.
- Tooling is adapted from m4bwav/gcs-gmod (gm_grand_central). tools/gct_build_vmf.py is the GCT generator kept as a helper reference; the Penn generator is tools/build_vmf.py.
- Never edit the VMF by hand. Repo text is LF (write from Python with newline='').
- Never run two compiles or two GMod launches at once. Kill GMod by PID only.
- Assets: public domain or CC only, each logged in refs/SOURCES.md. No Krea 2 images.
