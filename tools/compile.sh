#!/bin/sh
# Full compile of src/gm_penn_station.vmf, pack src/materials into the BSP, copy into Garry's Mod maps.
set -e
G="${GMOD:-D:/SteamLibrary/steamapps/common/GarrysMod}"
cd "$(dirname "$0")/.."
python tools/build_vmf.py
[ -f tools/penn_models.py ] && python tools/penn_models.py
mkdir -p "$G/garrysmod/materials/penn"
cp src/materials/penn/* "$G/garrysmod/materials/penn/"
# vbsp's exit code is lost in a pipe and it can fail while an old BSP stays on disk: remove it first
# and stop when vbsp reports a fatal error.
rm -f src/gm_penn_station.bsp
"$G/bin/vbsp.exe" -game "$G/garrysmod" src/gm_penn_station > src/vbsp.log 2>&1; tail -15 src/vbsp.log
if [ ! -f src/gm_penn_station.bsp ] || grep -q -i -E "bad normal|leaked|too many" src/vbsp.log; then echo "vbsp FAILED: see src/vbsp.log"; exit 1; fi
"$G/bin/vvis.exe" -game "$G/garrysmod" ${FAST:+-fast} src/gm_penn_station 2>&1 | tail -4
"$G/bin/vrad.exe" -game "$G/garrysmod" ${FAST:+-fast} -both src/gm_penn_station 2>&1 | tail -4
: > src/packlist.txt
for f in src/materials/penn/*; do printf 'materials/penn/%s\n%s\n' "$(basename "$f")" "$(cygpath -w "$PWD/$f" 2>/dev/null || echo "$PWD/$f")" >> src/packlist.txt; done
for f in src/materials/models/penn/* src/models/penn/*; do [ -e "$f" ] || continue; r="${f#src/}"; printf '%s\n%s\n' "$r" "$(cygpath -w "$PWD/$f" 2>/dev/null || echo "$PWD/$f")" >> src/packlist.txt; done
"$G/bin/bspzip.exe" -addlist src/gm_penn_station.bsp src/packlist.txt src/gm_penn_station.bsp 2>&1 | tail -2
cp src/gm_penn_station.bsp "$G/garrysmod/maps/"
ls -la src/gm_penn_station.bsp
