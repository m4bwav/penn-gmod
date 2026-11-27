# HANDOFF: gm_penn_station

Status: in progress
Updated: 2026-11-27 (session 21)

- Prompt: plans/2026-11-25-penn-gmod-60x-continue-prompt.md
- Chain: session 21 of 60 (started 2026-11-26)
- Plan: plans/penn-gmod-plan.md. Era: 1910 station (decisions/2026-11-26-era-1910.md).
- Garry's Mod: D:/SteamLibrary/steamapps/common/GarrysMod (vbsp, vvis, vrad, bspzip, gmad, gmpublish, studiomdl, vbspinfo in bin/).
- Budget 2026-11-27 (session 21): 6,263/65,536 verts, 4,139 faces, BSP 19.9 MB. 146 fps capped.
- Workshop ID: 3846546331 (public, 0.2.0). tools/package.sh defaults to it.
- Driver: the user-level chain_loop (C:/Users/m4bwa/.chainwright/penn-prompt.md, stop check penn_stop.py, log penn-chain.log, 60 sessions / 24 h) runs this chain. Sessions it starts never start another driver.

## Done
- Session 1: repo, ai-docs, plan, era ruling, GCT tooling copied and renamed.
- Session 2: 13 PD refs (refs/SOURCES.md), sourced dimensions (notes/2026-11-26-dimensions.md).
- Session 3: waiting-room blockout, playable, full compile clean, shots/20261126-2039. Layout: +x north, +y east; arcade stair opening centre of the east wall, concourse openings west wall. Stock HL2 textures.
- Session 4: first detail pass. tools/penn_textures.py (travertine ashlar, plain travertine, coffered vault, travertine floor), tools/penn_models.py (fluted Corinthian column MDL, prop_static on brush pedestals), pilaster piers behind the bay columns, Diocletian mullions + transom + sill in every lunette, compare.py pairs for from_sw / from_nw / stair_east. shots/20261126-2049 with compare.jpg. The 20 fps was the frame cap: UNCAP=1 gives 730-890 fps.

- Session 5: detail pass 2. Round-headed arches (30 ft wide, crown 60 ft) in a 4 ft face layer on every long-wall bay, archivolts and imposts; the stair opening is a 40 ft arch with a glass tympanum; pedestals 14 ft; piers 7 ft deep, columns 13 ft off the walls with the entablature breaking forward over each; travertine darkened to 122/112/98; vault coffers now round-in-octagon on a diagonal lattice. shots/20261126-2055 with compare.jpg.

- Session 6: lighting pass. Window glass and door glow are texture lights (src/lights.rad, passed to vrad with -lights); a no-falloff light_spot from each east lunette drops a warm sun pool on the floor; warm fill lowered; auto-exposure 0.6-1.6, bloom 0.25. -StaticPropLighting turned the column MDLs black, so it stays off. shots/20261126-2102.

- Session 7: 0.1.0 released. Workshop 3846546331 public (title, description, 5 previews), README with Z-Image banner, level map (make_map.py rewritten for Penn's +x north axes), LICENSE, SECURITY.md, repo public, tag v0.1.0. FNaF overlay fixed: tools/lua/a_penn_nofnaf.lua sets VJ_FNAFSB_CACHED during shot runs. shots/20261126-2113.

- Session 8: area 1 polish. 4 ft niches behind every side arch up to the crown (NICHE in build_vmf.py; the wall sits back and filler brushes bring the face forward), so the arches read as openings. Shots no longer show the physgun: tools/lua/penn_shots_sv.lua (PlayerLoadout returns true) is installed by shots.sh for shot runs only; hiding the viewmodel was not enough. shots/20261126-2121, -2122. Not released; ships with 0.2.0.

- Session 9: area 2 blockout. arcade() in build_vmf.py: 45 x 225 ft at the landing level (z 192), y 1468-4168, five 45 ft groin bays (coffer texture), a 30 x 18 ft shopfront recess per bay on both sides (glow panels for now), 40 ft opening at the east end into a 40 ft vestibule with glowing street doors. The stair hall now opens straight into the arcade; the player starts at the Seventh Avenue end facing west. Cameras arcade_west/_east/_vault. shots/20261126-2126. Not released.

- Session 10: area 2 detail pass 1. Ref: Joseph Pennell's etching "The arcade, Pennsylvania Station" (PD, refs/SOURCES.md); it shows the stair-hall arch seen from the arcade: archivolt with keystone, mullioned lunette window above, pilasters with cornice blocks, lamp standards. Added a procedural bronze shopfront texture (sign band, transoms, three plate-glass panes; FACEUV maps one tile per 45 ft bay; low texlight in lights.rad), 3 ft pilasters at every bay line and a 2 ft impost cornice at the springing (func_detail). shots/20261126-2130. Not released.

- Session 11: area 2 detail 2a. The stair-hall end of the arcade after Pennell: a 2 ft architrave band round the 40 ft opening with a keystone, and the west lunette above it glazed (r 20 ft 6 in) with two mullions, a transom, a sill and an archivolt band. Camera arcade_stairarch. shots/20261126-2133. Not released.

- Session 12: arcade vaults in plain travertine with coffers only in the crown strips (groin() takes crown=). shots/20261126-2136. Not released.

- Session 13: arcade lamp standards. lamp MDL in tools/penn_models.py (bronze candelabrum, fluted post, four arms + finial, five unlit frosted globes; bronze/globe VMTs on debugwhite with $color2), 8 placed 5 ft in front of the pilasters at the inner bay lines, each with a small warm light at the globes. Camera arcade_lamp. shots/20261126-2140. Not released.

- Session 14: the Cassatt niche on the stair hall's north wall at the landing: 10 ft round-headed recess with imposts, travertine pedestal, cassatt.mdl (simplified 9 ft bronze standing figure in tools/penn_models.py) facing south, a small warm light. Camera cassatt_niche. shots/20261126-2145. Not released.
- Session 15: Seventh Avenue entrance colonnade: facade wall with the arcade opening, 12 Doric columns (doric.mdl, 35 ft), portico roof, cornice and attic, sidewalks, avenue, stand-in block opposite, open sky with light_environment. Cameras colonnade_street, colonnade_portico, arcade_to_street. shots/20261126-2158. Not released.
- Session 16: area 2 lighting. Sun turned to come from the east (yaw 250, pitch -35) onto the facade, brighter ambient, 10 warm lights under the portico soffit and colonnade, arcade and vestibule fills raised. shots/20261126-2304 (146 fps capped). Not released.
- Session 17: 0.2.0 released (area 2). README, Workshop description and previews, level map now draws both walking levels (make_map.py LAND) with labels for every area, gma uploaded, tag v0.2.0. shots/20261126-2307.
- Session 18: area 3 refs + blockout. 6 PD concourse refs (HABS Cervin Robinson x4, Popko roof detail, Pennell 'Hall of iron'; refs/SOURCES.md). concourse() in build_vmf.py: 314 x 200 ft west of the waiting room (y CY0..CY1), floor level 0, three glass groin bays (spring 45 ft, crown ~100 ft, penn/window_glass), 16 blockout lattice columns (metal/metalwall001a boxes), joined through the waiting room's three west passages (glow doors removed). Cameras conc_south, conc_east, conc_vault, wr_to_conc. shots/20261126-2317. Not released.
- Session 19: area 3 detail 1. lattice.mdl (tools/penn_models.py: four angle posts on a 3 ft square, zigzag lacing, base shoe, cap, four curved arch ribs flaring 16 ft out and 10 ft up) replaces the 16 box columns; steel.vmt. Roof glass is now penn/conc_glass (dark glazing grid on pale wired glass, texlight 70 in lights.rad). shots/20261126-2324. Not released.
- Session 20: concourse steel ribs. conc_diag.mdl (truss ribs on both groins of a bay, 3 placed) and conc_arch.mdl (transverse truss arch, at the two inner bay lines) in tools/penn_models.py, prop_static with disableshadows=1 (without it vrad's prop shadows blacked out the whole roof). shots/20261126-2332. Not released.
- Session 21: the "hanging line" was conc_arch lying along the hall: studiomdl turns SMD geometry 90 degrees about z, so the arch (built spanning y) stood along x and showed edge-on from the centre line, and the diagonal ribs missed the bay corners. Both rib props now stand at angles "0 90 0"; the conc_arch/conc_diag MDLs session 20 never committed are in src/models. shots/20261127-0002. Not released.

## Next
1. Area 3 detail: ribs on lattice.mdl could follow the groin curve upward instead of ending flat, travertine arcade of round arches on the east wall (photos), stairs down to the tracks with railings (refs: CONCOURSE_FROM_SOUTH), clock. Then lighting, then 0.3.0.
2. Optional leftovers: attic storey above the waiting-room side arches, coffered soffits on the cross arches, eagles/clock on the facade; the colonnade cornice still reads dark from the street.
3. Wiki: the GitHub wiki needs its first page created by hand in the browser before it can be pushed (as with GCT); draft pages can go in docs/wiki/ meanwhile.

## Waiting on Mark
- Nothing. (Flag: era ruled 1910 by default.)
