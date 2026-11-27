# Penn Station map for Garry's Mod, 60-session chain

Goal: `gm_penn_station`, a Garry's Mod map of New York's Penn Station, built the way `gm_grand_central` was (repo m4bwav/gcs-gmod) and published on the Steam Workshop. Before the first session, decide which era to build and log the ruling. The default is the original 1910 McKim, Mead & White station (waiting room after the Baths of Caracalla, steel-and-glass train concourse), since public-domain photos and HABS drawings exist. The present-day station plus Moynihan Train Hall is a later extra if the budget allows.

## First session only (if `D:/m4bwa/Claude/Projects/Ai/penn-gmod` doesn't exist)
- Create the private repo m4bwav/penn-gmod and clone it to that path. Set up ai-docs (everlast-setup) with HANDOFF.md, log.md and plans/penn-gmod-plan.md (scope, scale, era, area order, budgets). Copy this prompt into its `ai-docs/plans/` and print the start command from there from then on.
- Reuse the GCT tooling by copying and adapting it, not by hand-editing it: build_vmf.py patterns, compile.sh, shots.sh + gcs_shots.lua, compare.py, make_models.py (MDL route), package.sh, workshop_update.py, make_map.py. Read `gcs-gmod/notes/lessons-for-penn.md` and the GCT HANDOFF budget notes first.
- Make the repo public (README with a ComfyUI banner (no Krea 2), LICENSE, SECURITY.md, wiki) once its assets pass a licence audit, as GCT did. First Workshop upload when the first area is playable (pre-approved).

## Area order (refine in the plan)
1. Main waiting room (full scale, coffered vaults, Corinthian columns, thermal windows). Ships as 0.1.0.
2. Arcade and shopping corridor from Seventh Avenue, plus the main entrance colonnade.
3. Train concourse (steel lattice, glass vaults), stairs down to the platforms.
4. Track platforms and a train.
5. Exterior: Seventh Avenue colonnade, eagles, street.
6. Extras: dining room, lunch room, Moynihan Train Hall, nav mesh.

## Keep going (read first)
A "session" is one unit of work, not the end of the conversation. When an item finishes, bump the session number and start the next item in the same conversation. Hand over only at a stop point or when context runs low. In an interactive session, then start chainwright's driver (`chain_loop.py --go`, bounds in HANDOFF.md). A session started by the driver (headless `claude -p`, or a `chain_loop.py` process is running) never starts another driver: it finishes its item, updates HANDOFF.md and ends.

## Unattended runs
A headless session ends when its turn ends, and background jobs die with it. Run compiles, nav, shots and packaging in the foreground (under the 10-minute tool timeout; split long chains), never in the background, and don't end the turn while one runs. Before finishing, commit and push your branch even if the work is unfinished, and name it in HANDOFF.md. A leftover worktree from an earlier session means resume it, unless a gmod/vbsp/vrad process is actually running. Never run two compile or shots jobs at once.

## Budget rules from GCT (vbsp's hard caps)
65,536 unique vertices is the limit you hit first. Use textures for grids and lettering, MDL models for props and repeated ornament (capitals, coffers if needed, eagles), one func_brush per area for decor, and vbspinfo after every compile. Plan for the waiting room's columns and coffers to be models from day one. 150 MB file budget, 60 fps on a mid-range PC.

## Each session
1. `git fetch`, then read HANDOFF.md, the log tail and the plan from origin/main. Work in your own worktree. Skills: modwright, polywright, comfyui-gen (never Krea 2), artwright/-judge, photowright, historywright (era facts, sources), askwright, quirkwright, labwright, releasewright, grindwright.
2. Read and consume answered askwright sets.
3. Bump `Chain: session N of 60`. Take the next item: refs (licensed or public domain, logged in refs/SOURCES.md), blockout, playable compile joined through a real opening, detail matched against photos with compare.jpg, then lighting. Every map change ends in a full compile that loads, shots, and vbspinfo numbers.
4. After each area: update the README, level map, wiki and Workshop, bump the version, tag and release (pre-approved).
5. Stop before paid or ripped assets, a scope change, or a level split (askwright page). Decide small rulings and flag them.
6. Stop early if `Status: finished` or nothing can move without Mark; say what waits on Mark (listed under "Waiting on Mark" in HANDOFF.md).

## Hand-over
Run evergreen-wrapup (if it's installed), update the log and HANDOFF.md, and only then print the start command:
`Execute D:/m4bwa/Claude/Projects/Ai/penn-gmod/ai-docs/plans/2026-11-25-penn-gmod-60x-continue-prompt.md`
(For the first session only, before the repo exists, run it from `D:/m4bwa/Claude/Projects/Ai/gcs-gmod/ai-docs/plans/`.) State lives in HANDOFF.md, never in this file.
