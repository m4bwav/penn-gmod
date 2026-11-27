## What you need

- Garry's Mod. The scripts look in `D:/SteamLibrary/steamapps/common/GarrysMod`; set `GMOD` if yours is elsewhere. vbsp, vvis, vrad, bspzip, studiomdl, vbspinfo, gmad and gmpublish all come from its `bin/` folder.
- Python 3 with Pillow.
- Git Bash (the build scripts are POSIX sh).

## Compile

```sh
sh tools/compile.sh      # VMF, textures, models, vbsp/vvis/vrad, pack, copy to garrysmod/maps
sh tools/cubemaps.sh     # build the env_cubemap reflections into the copied BSP
sh tools/nav.sh          # nav mesh for NPCs and nextbots (after any change to a walkable floor)
```

`compile.sh` runs `vbspinfo` at the end. Check the vertex count every time: vbsp stops at 65,536 unique vertices, and 0.7.1 uses about 26,300.

## Load it

Start Garry's Mod and type in the console:

```
map gm_penn_station
```

You spawn at the Seventh Avenue end of the arcade, facing west toward the waiting room.

## Screenshots and comparisons

```sh
UNCAP=1 sh tools/shots.sh                # fixed camera views and fps into shots/<stamp>/
python tools/compare.py shots/<stamp>    # compare.jpg: each shot beside its reference photo
python tools/make_map.py                 # docs/level-map.png
```

## Shared install

The build scripts take a lock file (`tools/gmod_lock.sh`) before they write into `garrysmod/` or start the game, because more than one project can share one Garry's Mod install. If a script prints `gmod.lock: waiting for ...`, let it wait.

## Packaging

`sh tools/package.sh` packs the BSP into a `.gma` and updates the Workshop item. Copy the cubemapped BSP from `garrysmod/maps` to `src/` first. Only the item's owner can update it.
