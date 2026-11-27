#!/bin/sh
# Build the env_cubemap reflections into the compiled map: launch GMod with -buildcubemaps, wait until
# it rewrites garrysmod/maps/gm_penn_station.bsp, kill only our gmod.exe, copy the BSP back to src/.
# Run after tools/compile.sh (compile.sh's BSP has no cubemaps, so mirrors and glass read flat grey).
G="${GMOD:-D:/SteamLibrary/steamapps/common/GarrysMod}"
cd "$(dirname "$0")/.."
. tools/gmod_lock.sh; gmod_lock_take   # shared GMod lock, released on exit
M="$G/garrysmod/maps/gm_penn_station.bsp"
before=$(date -r "$M" +%s); size0=$(stat -c %s "$M")
echo 4000 > "$G/steam_appid.txt"
gmod_snapshot
"$G/gmod.exe" -windowed -w 1280 -h 720 -novid -nojoy -condebug +sv_cheats 1 +mat_specular 1 +mat_hdr_level 2 -buildcubemaps +map gm_penn_station &
ok=""
for n in $(seq 1 ${WAIT:-100}); do
	sleep 5
	now=$(date -r "$M" +%s)
	if [ "$now" -gt "$before" ]; then sleep 10; ok=1; break; fi
done
gmod_kill_own
[ -z "$ok" ] && { echo "cubemaps: BSP not rewritten, see garrysmod/console.log"; exit 1; }
cp "$M" src/gm_penn_station.bsp
echo "cubemaps: $size0 -> $(stat -c %s "$M") bytes"
