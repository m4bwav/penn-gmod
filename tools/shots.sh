#!/bin/sh
# Launch GMod on gm_penn_station, let tools/lua/penn_shots.lua capture the cameras,
# copy the JPGs into shots/. CAMS="a b" limits the run to those cameras. UNCAP=1 lifts the frame cap (fps_max 0, vsync off) for the fps log. The Lua quits the game; fallback kill is by PID only.
G="${GMOD:-D:/SteamLibrary/steamapps/common/GarrysMod}"
QW="C:/Users/m4bwa/.claude/plugins/cache/mark-local/quirkwright/0.2.1/skills/quirkwright/scripts/qw.py"
cd "$(dirname "$0")/.."
D="$G/garrysmod/data"
echo 4000 > "$G/steam_appid.txt"
cp tools/lua/penn_shots.lua "$G/garrysmod/lua/autorun/client/penn_shots.lua"
EXTRA=""; [ -n "$UNCAP" ] && EXTRA="+fps_max 0 +mat_vsync 0" ; EXTRA="$EXTRA $GARGS"   # GARGS: extra launch args, e.g. "+sv_cheats 1 +mat_fullbright 1"
mkdir -p "$D"; rm -rf "$D/penn_shots"; echo "${CAMS:-go}" > "$D/penn_shots_go.txt"
"$G/gmod.exe" -windowed -w 1600 -h 900 -novid -nojoy -condebug +sv_cheats 1 $EXTRA +map gm_penn_station &
for n in $(seq 1 ${WAIT:-180}); do [ -f "$D/penn_shots/done.txt" ] && break; sleep 5; done
sleep 5
# Every gmod.exe by PID (Lua quit is blocked in this GMod build; qw pid matched a helper process, not the game).
for PID in $(tasklist //FI "IMAGENAME eq gmod.exe" //FO CSV //NH | cut -d'"' -f4); do taskkill //PID "$PID" //F >/dev/null 2>&1; done
rm -f "$G/garrysmod/lua/autorun/client/penn_shots.lua" "$D/penn_shots_go.txt"
stamp=$(date +%Y%m%d-%H%M); mkdir -p "shots/$stamp"
cp "$D"/penn_shots/*.jpg "$D"/penn_shots/fps.txt "shots/$stamp/" 2>/dev/null; ls "shots/$stamp"
cat "shots/$stamp/fps.txt" 2>/dev/null
