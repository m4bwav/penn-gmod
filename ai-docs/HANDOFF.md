# HANDOFF: gm_penn_station

Status: in progress
Updated: 2026-11-26 (session 3)

- Prompt: plans/2026-11-25-penn-gmod-60x-continue-prompt.md
- Chain: session 3 of 60 (started 2026-11-26)
- Plan: plans/penn-gmod-plan.md. Era: 1910 station (decisions/2026-11-26-era-1910.md).
- Garry's Mod: D:/SteamLibrary/steamapps/common/GarrysMod (vbsp, vvis, vrad, bspzip, gmad, gmpublish, studiomdl, vbspinfo in bin/).
- Budget 2026-11-26 (session 3): 1,537/65,536 verts, 975 faces, BSP 3.6 MB.
- Workshop ID: none yet (first upload at 0.1.0 with gmpublish create).
- Driver: chain_loop.py started 2026-11-26 after session 3 (--max-sessions 57 --max-hours 24 --limit-wait 1800 --max-waits 12, stop check tools/chain_stop.py), log ai-docs/chain-loop.log. Never start a second one.

## Done
- Session 1: repo, ai-docs, plan, era ruling, GCT tooling copied and renamed.
- Session 2: 13 PD refs (refs/SOURCES.md), sourced dimensions (notes/2026-11-26-dimensions.md).
- Session 3: waiting-room blockout, playable, full compile clean, shots/20261126-2039. Layout: +x north, +y east; arcade stair opening centre of the east wall, concourse openings west wall. Stock HL2 textures.

## Next
1. Waiting-room detail against the HABS photos (refs/photos/WAITING_ROOM_FROM_SOUTHWEST..., NORTHWEST): set up compare.py pairs for from_sw / from_nw; real proportions of the column screen (columns stand in front of piers with arched openings between, side aisles under lower coffered vaults), coffered vault texture, travertine wall texture, thermal-window mullion pattern (Diocletian three-light), MDL Corinthian columns via make_models.py (tools/penn_models.py).
2. Lighting pass, then 0.1.0 release: first Workshop upload (gmpublish create), README, level map, licence audit before going public.
3. Check fps with UNCAP=1 (session 3 logged a flat 20 fps).

## Waiting on Mark
- Nothing. (Flag: era ruled 1910 by default.)
