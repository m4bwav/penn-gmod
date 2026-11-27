![gm_penn_station](docs/banner.jpg)

# gm_penn_station

**Play it:** [Steam Workshop: Penn Station 1910 (gm_penn_station)](https://steamcommunity.com/sharedfiles/filedetails/?id=3846546331)

A Garry's Mod map of the 1910 Pennsylvania Station in New York (McKim, Mead & White), built at true scale (1 ft = 12 units). The station was torn down in 1963; this map rebuilds it from public-domain photographs and plans.

Release 0.7.2 puts 16 double-sided oak benches in the waiting room's end bays, leaving the middle bay clear from the arcade stair to the concourse, and rebuilds the nav mesh around them. Release 0.7.1 adds an attic storey over the waiting room's columns and coffered cross arches between its vault bays, and closes a gap of sky that had opened in the crown of every waiting-room vault since 0.5.0. Release 0.7.0 cuts the Seventh Avenue front to its real 430 ft, gives the reclining figures of the clock group limbs and turns the clock face to the avenue, and rebuilds the nav mesh. Release 0.6.0 added the dining room and lunch room off the stair hall, after the 1910 booklet photos: oak wainscot and pilasters, cream plaster, square-coffered ceilings, round-headed windows, chandeliers over laid tables, marble lunch counters with stools, a mirrored wall, and a nav mesh for NPCs and nextbots. Release 0.5.0 added the outside of the station: the full Seventh Avenue front with 32 Doric columns between corner pavilions, the raised central pavilion with its clock group and stone eagles, and the 31st and 33rd Street fronts with pilastered walls, carriage drives behind Doric colonnades and arched gables over thermal windows, lit by street lamps. Release 0.4.0 added the track level: six island platforms with stone coping, steel columns and hanging lamps under the concourse, seven tracks running west to the tunnel portals, and two trains of Tuscan red coaches behind DD1 electrics lettered PENNSYLVANIA. Release 0.3.0 added the train concourse: three glass groin vaults about 100 ft high on branching steel lattice columns and truss ribs, a travertine arcade and clock on the east wall, and six stairs down toward the tracks. Release 0.2.0 added the Seventh Avenue front: the Doric colonnade on the street, the entrance vestibule and the 225 ft shopping arcade with bronze shopfronts, groin vaults and lamp standards, down to the Cassatt statue niche at the head of the grand stair. Release 0.1.0 had the main waiting room: three groin-vaulted bays 150 ft to the crown, coffered vaults, Corinthian columns on tall pedestals, thermal windows in every lunette with morning sun on the floor. Moynihan Train Hall may come later if the budget allows (see the [plan](ai-docs/plans/penn-gmod-plan.md)).

The map is written as VMF text by a Python script, not drawn in Hammer. The textures (travertine, coffers, floor, window glass, shopfronts, paving) and the models (columns, lamps, statue, steel lattice columns and roof ribs, clock, train) are made by scripts in `tools/`.

Screenshots from release 0.7.2:

| | |
|---|---|
| ![Waiting room vaults and cross arches](docs/vault_up.jpg) | ![Waiting room](docs/from_sw.jpg) |
| ![Dining room](docs/dining_in.jpg) | ![Lunch room](docs/lunch_in.jpg) |
| ![Seventh Avenue front](docs/front_centre.jpg) | ![Clock group and eagles](docs/front_attic.jpg) |
| ![Carriage drive on the side street](docs/side_carriage.jpg) | ![Corner pavilion](docs/front_south.jpg) |
| ![Train at the platform](docs/train_side.jpg) | ![DD1 electric](docs/train_nose.jpg) |
| ![Along a platform](docs/plat_long.jpg) | ![Across the tracks](docs/plat_tracks.jpg) |
| ![Concourse from the south](docs/conc_south.jpg) | ![Concourse looking east](docs/conc_east.jpg) |
| ![Concourse glass vault](docs/conc_vault.jpg) | ![Concourse clock](docs/conc_clock.jpg) |
| ![Seventh Avenue colonnade](docs/colonnade_street.jpg) | ![Under the portico](docs/colonnade_portico.jpg) |
| ![The arcade](docs/arcade_west.jpg) | ![Arcade shopfront and lamp](docs/arcade_lamp.jpg) |
| ![Cassatt niche](docs/cassatt_niche.jpg) | ![Benches in the waiting room](docs/wr_benches.jpg) |
| ![The vault](docs/vault_up.jpg) | ![Stair to the arcade](docs/stair_east.jpg) |

### Level map

![Level map](docs/level-map.png)

## Build

Needs Garry's Mod (set `GMOD` if it is not in `D:/SteamLibrary/steamapps/common/GarrysMod`), Python 3 with Pillow, and Git Bash.

```sh
sh tools/compile.sh          # VMF, textures, models, vbsp/vvis/vrad, pack, copy to garrysmod/maps
UNCAP=1 sh tools/shots.sh    # screenshots and fps into shots/
python tools/make_map.py     # docs/level-map.png
```

## Credits and licence

- Reference photos and plans: public domain, from Wikimedia Commons and the Library of Congress (list in [refs/SOURCES.md](refs/SOURCES.md)). Used for proportions and colour only.
- Stock Half-Life 2 materials ship with Garry's Mod and are not bundled.
- The banner above was made with the Z-Image Turbo model (Apache-2.0) and is AI art, not a screenshot. No AI images are in the map.
- Tools: MIT ([LICENSE](LICENSE)). Map source and textures: CC BY-SA 4.0.
