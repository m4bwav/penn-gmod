All scripts live in `tools/` in the repository.

| Script | What it does |
|---|---|
| `build_vmf.py` | Writes `src/gm_penn_station.vmf`: every room, the outside, lights, spawns and cubemaps |
| `vmf_lib.py` | Brush helpers lifted from the Grand Central map |
| `penn_textures.py` | Procedural materials: travertine ashlar, coffered vaults, floors, window glass, bronze shopfronts, paving, oak and plaster for the dining rooms |
| `penn_models.py` | Props built as MDL: Corinthian and Doric columns, lamp standards, the Cassatt statue, steel lattice columns and roof ribs, clocks, the clock group with its figures and eagles, coaches and DD1 electrics, chandeliers, tables and stools |
| `make_models.py` | The SMD + QC writer and studiomdl driver that `penn_models.py` uses |
| `compile.sh` | Builds the VMF, textures and models, runs vbsp, vvis and vrad, packs materials and copies the BSP into Garry's Mod |
| `cubemaps.sh` | Builds the reflections with `-buildcubemaps` |
| `nav.sh` | Generates the nav mesh |
| `shots.sh` and `lua/penn_shots.lua` | Launch the game and capture fixed camera views and fps into `shots/` |
| `compare.py` | Puts each shot beside the reference photo from the same viewpoint |
| `make_map.py` | Draws the top-down level map, `docs/level-map.png` |
| `fetch_refs.py` | Downloads reference photos and logs them in `refs/SOURCES.md` |
| `texsheet.py` | Contact sheet of stock Half-Life 2 materials |
| `package.sh` | Packs the `.gma` and updates the Workshop item |
| `workshop_update.py` | Sets the Workshop title, description and preview images |
| `gmod_lock.sh` | The lock that lets several projects share one Garry's Mod install |

Models don't count toward vbsp's vertex limit, so round and repeated ornament (columns, capitals, lamps, eagles) is built as models, and brushes keep to walls, floors and vaults.
