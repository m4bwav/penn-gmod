# HANDOFF: gm_penn_station

Status: in progress
Updated: 2026-11-26 (session 6)

- Prompt: plans/2026-11-25-penn-gmod-60x-continue-prompt.md
- Chain: session 6 of 60 (started 2026-11-26)
- Plan: plans/penn-gmod-plan.md. Era: 1910 station (decisions/2026-11-26-era-1910.md).
- Garry's Mod: D:/SteamLibrary/steamapps/common/GarrysMod (vbsp, vvis, vrad, bspzip, gmad, gmpublish, studiomdl, vbspinfo in bin/).
- Budget 2026-11-26 (session 6): 2,488/65,536 verts, 1,513 faces, BSP 7.6 MB. 770-860 fps uncapped.
- Workshop ID: none yet (first upload at 0.1.0 with gmpublish create).
- Driver: the user-level chain_loop (C:/Users/m4bwa/.chainwright/penn-prompt.md, stop check penn_stop.py, log penn-chain.log, 60 sessions / 24 h) runs this chain. Sessions it starts never start another driver.

## Done
- Session 1: repo, ai-docs, plan, era ruling, GCT tooling copied and renamed.
- Session 2: 13 PD refs (refs/SOURCES.md), sourced dimensions (notes/2026-11-26-dimensions.md).
- Session 3: waiting-room blockout, playable, full compile clean, shots/20261126-2039. Layout: +x north, +y east; arcade stair opening centre of the east wall, concourse openings west wall. Stock HL2 textures.
- Session 4: first detail pass. tools/penn_textures.py (travertine ashlar, plain travertine, coffered vault, travertine floor), tools/penn_models.py (fluted Corinthian column MDL, prop_static on brush pedestals), pilaster piers behind the bay columns, Diocletian mullions + transom + sill in every lunette, compare.py pairs for from_sw / from_nw / stair_east. shots/20261126-2049 with compare.jpg. The 20 fps was the frame cap: UNCAP=1 gives 730-890 fps.

- Session 5: detail pass 2. Round-headed arches (30 ft wide, crown 60 ft) in a 4 ft face layer on every long-wall bay, archivolts and imposts; the stair opening is a 40 ft arch with a glass tympanum; pedestals 14 ft; piers 7 ft deep, columns 13 ft off the walls with the entablature breaking forward over each; travertine darkened to 122/112/98; vault coffers now round-in-octagon on a diagonal lattice. shots/20261126-2055 with compare.jpg.

- Session 6: lighting pass. Window glass and door glow are texture lights (src/lights.rad, passed to vrad with -lights); a no-falloff light_spot from each east lunette drops a warm sun pool on the floor; warm fill lowered; auto-exposure 0.6-1.6, bloom 0.25. -StaticPropLighting turned the column MDLs black, so it stays off. shots/20261126-2102.

## Next
1. 0.1.0 release: first Workshop upload (gmpublish create), README, level map, licence audit before going public.
2. Still missing from the photos (can follow 0.1.0): attic storey with clerestory windows above the entablature over the side arches, coffered soffits on the cross arches, a darker recess behind the arches (they read as niches, the real ones open into side passages), stair hall grand stair width.
3. Shot overlay: "FNaF SB Models are Pre-Caching" still prints with +cl_drawhud 0; it is a local addon. Disable it in garrysmod/addons for shot runs (find it by name, move it out and back).

## Waiting on Mark
- Nothing. (Flag: era ruled 1910 by default.)
