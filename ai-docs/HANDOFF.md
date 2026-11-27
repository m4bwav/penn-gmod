# HANDOFF: gm_penn_station

Status: in progress
Updated: 2026-11-26 (session 4)

- Prompt: plans/2026-11-25-penn-gmod-60x-continue-prompt.md
- Chain: session 4 of 60 (started 2026-11-26)
- Plan: plans/penn-gmod-plan.md. Era: 1910 station (decisions/2026-11-26-era-1910.md).
- Garry's Mod: D:/SteamLibrary/steamapps/common/GarrysMod (vbsp, vvis, vrad, bspzip, gmad, gmpublish, studiomdl, vbspinfo in bin/).
- Budget 2026-11-26 (session 4): 1,741/65,536 verts, 1,043 faces, BSP 7.1 MB (procedural textures packed). 730-890 fps uncapped.
- Workshop ID: none yet (first upload at 0.1.0 with gmpublish create).
- Driver: the user-level chain_loop (C:/Users/m4bwa/.chainwright/penn-prompt.md, stop check penn_stop.py, log penn-chain.log, 60 sessions / 24 h) runs this chain. Sessions it starts never start another driver.

## Done
- Session 1: repo, ai-docs, plan, era ruling, GCT tooling copied and renamed.
- Session 2: 13 PD refs (refs/SOURCES.md), sourced dimensions (notes/2026-11-26-dimensions.md).
- Session 3: waiting-room blockout, playable, full compile clean, shots/20261126-2039. Layout: +x north, +y east; arcade stair opening centre of the east wall, concourse openings west wall. Stock HL2 textures.
- Session 4: first detail pass. tools/penn_textures.py (travertine ashlar, plain travertine, coffered vault, travertine floor), tools/penn_models.py (fluted Corinthian column MDL, prop_static on brush pedestals), pilaster piers behind the bay columns, Diocletian mullions + transom + sill in every lunette, compare.py pairs for from_sw / from_nw / stair_east. shots/20261126-2049 with compare.jpg. The 20 fps was the frame cap: UNCAP=1 gives 730-890 fps.

## Next
1. Waiting-room detail, round two (see shots/20261126-2049/compare.jpg): the long walls need the big round-headed arches (about 30 ft wide, 60 ft tall) between the bay piers, the east stair opening as a tall arch, an attic storey above the entablature with the clerestory windows over the side arches, taller pedestals, walls darker (photo travertine reads mid-grey), coffers as round/octagonal coffers in diagonal rows, coffered soffits on the cross arches.
2. Lighting pass, then 0.1.0 release: first Workshop upload (gmpublish create), README, level map, licence audit before going public.
3. Shot cameras: an addon in the local GMod prints "FNaF SB Models are Pre-Caching" over every shot; disable that addon for the shot run or hide the HUD (cl_drawhud 0) and the viewmodel (r_drawviewmodel 0) via GARGS.

## Waiting on Mark
- Nothing. (Flag: era ruled 1910 by default.)
