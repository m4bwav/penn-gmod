# Plan: gm_penn_station

Updated 2026-11-26 (session 1). Era ruling: [decisions/2026-11-26-era-1910.md](../decisions/2026-11-26-era-1910.md).

## Scope
The 1910 Pennsylvania Station, one map, true scale (1 ft = 12 units, as gm_grand_central). Walkable from Seventh Avenue through the arcade to the waiting room, the concourse and down to the platforms.

## Scale (to verify against HABS drawings in the refs session; figures below are the commonly cited ones)
- Building footprint about 780 x 430 ft (two blocks, 31st to 33rd St, Seventh to Eighth Ave).
- Main waiting room about 314 x 108 ft, about 150 ft to the vault crown; three groin-vault bays over Corinthian columns, thermal (Diocletian) windows in the lunettes.
- Concourse: steel lattice columns and glass groin vaults, roughly 340 x 210 ft.
- Platforms about 45 ft below street.
A 314 ft room is about 3,770 units; the whole station fits inside the 32,768 u Source grid but the platforms need care.

## Area order
1. Main waiting room. Ships as 0.1.0 (first Workshop upload, pre-approved).
2. Arcade and shopping corridor from Seventh Avenue, plus the main entrance colonnade.
3. Train concourse (steel lattice, glass vaults), stairs down to the platforms.
4. Track platforms and a train (train as MDL).
5. Exterior: Seventh Avenue colonnade, eagles, street.
6. Extras: dining room, lunch room, Moynihan Train Hall, nav mesh.

## Per area
refs (PD/CC, refs/SOURCES.md) -> blockout -> playable compile joined through a real opening -> detail against photos (compare.jpg) -> lighting -> release (README, level map, wiki, Workshop, tag).

## Budgets (vbsp hard caps, lessons from GCT)
- 65,536 unique verts (GCT ended at 49,703 with nine chambers). Target: waiting room <= 12k, arcade <= 6k, concourse <= 14k, platforms <= 8k, exterior <= 12k, extras the rest.
- Columns, capitals, coffers if repeated, eagles, benches, lamps: MDL models from day one (tools/make_models.py).
- Grids, lattices, lettering: alpha-tested textures. Concourse steel lattice is the big risk: plan it as textured planes plus MDL column shafts.
- One func_brush per area for decor. vbspinfo after every compile.
- 150 MB files, 60 fps mid-range.

## Tooling (from gcs-gmod)
compile.sh, shots.sh + lua/penn_shots.lua, nav.sh + lua/penn_nav.lua, compare.py, make_models.py, make_map.py, make_walls.py, make_floor.py, texsheet.py, fetch_refs.py, package.sh, workshop_update.py, chain_stop.py. tools/gct_build_vmf.py holds the GCT helpers (prism, xprism, yprism, groin, _slab, arcade_bay, ent) to lift into tools/build_vmf.py. Workshop ID is set after the first `gmpublish create`.
