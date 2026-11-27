-- gm_penn_station screenshot rig. Runs only when data/penn_shots_go.txt exists
-- (tools/shots.sh writes it); captures each camera to data/penn_shots/, then quits.
if SERVER then return end
if not file.Exists("penn_shots_go.txt", "DATA") then return end
if game.GetMap() ~= "gm_penn_station" then return end
-- The go file may list camera names (one line, spaces); "go" means all.
local want = string.Trim(file.Read("penn_shots_go.txt", "DATA") or "go")
file.Delete("penn_shots_go.txt")
file.CreateDir("penn_shots")

local CAMS = {
  { "from_sw",    Vector(-1560, -440, 420), Angle(6, 28, 0) },
  { "from_nw",    Vector(1560, -440, 420), Angle(6, 152, 0) },
  { "nave_north", Vector(-1600, 0, 72), Angle(-12, 0, 0) },
  { "vault_up",   Vector(-600, 0, 72), Angle(-70, 0, 0) },
  { "stair_east", Vector(0, -400, 72), Angle(-8, 90, 0) },
  { "west_wall",  Vector(0, 450, 72), Angle(-10, -90, 0) },
  { "stair_down", Vector(0, 1300, 220), Angle(10, -90, 0) },
  { "conc_south", Vector(-1700, -2068, 72), Angle(-12, 0, 0) },
  { "conc_east", Vector(0, -3100, 72), Angle(-10, 90, 0) },
  { "conc_vault", Vector(0, -2068, 72), Angle(-70, 0, 0) },
  { "conc_stairs", Vector(-628, -2450, 110), Angle(22, -115, 0) },
  { "conc_stairwell", Vector(-300, -2700, 40), Angle(18, -90, 0) },
  { "conc_landing", Vector(-300, -3160, -170), Angle(5, -90, 0) },
  { "plat_stairfoot", Vector(-300, -3400, -170), Angle(5, 75, 0) },
  { "plat_long", Vector(-300, -4200, -175), Angle(2, -90, 0) },
  { "plat_tracks", Vector(-628, -5200, -150), Angle(12, 180, 0) },
  { "conc_clock", Vector(0, -1900, 200), Angle(-25, 90, 0) },
  { "wr_to_conc", Vector(0, 300, 72), Angle(-4, -90, 0) },
  { "arcade_west", Vector(0, 4000, 264), Angle(-4, -90, 0) },
  { "arcade_east", Vector(0, 1600, 264), Angle(-4, 90, 0) },
  { "arcade_vault", Vector(0, 2800, 264), Angle(-60, 90, 0) },
  { "arcade_stairarch", Vector(0, 2500, 264), Angle(-18, -90, 0) },
  { "arcade_lamp", Vector(-60, 2280, 300), Angle(4, 160, 0) },
  { "cassatt_niche", Vector(-160, 1300, 320), Angle(6, 0, 0) },
  { "colonnade_street", Vector(700, 5950, 262), Angle(-14, 245, 0) },
  { "colonnade_portico", Vector(-900, 4990, 260), Angle(-4, 15, 0) },
  { "arcade_to_street", Vector(0, 3900, 290), Angle(0, 90, 0) },
}
if want ~= "go" then
  local keep, set = {}, {}
  for n in string.gmatch(want, "%S+") do set[n] = true end
  for _, c in ipairs(CAMS) do if set[c[1]] then keep[#keep + 1] = c end end
  CAMS = keep
end
local i, cam, frames = 0, nil, 0
-- The view moves by CalcView but the server sends entities by the player's PVS: move the player
-- to each camera (setpos needs sv_cheats, shots.sh sets it), else brush entities in rooms out of
-- sight of the spawn (tm_decor, hy_decor) are never networked and never drawn.
local function goto_cam()
  if cam then RunConsoleCommand("setpos", cam[2].x, cam[2].y, cam[2].z - 64) end
end
local ft, fpslog = 0, {}  -- frame time summed over frames 31-89, one fps line per camera

hook.Add("CalcView", "penn_shots", function()
  if cam then return { origin = cam[2], angles = cam[3], fov = 90, drawviewer = false } end
end)
hook.Add("HUDShouldDraw", "penn_shots", function() if cam then return false end end)
-- Hide the held weapon (the physgun glowed at the right edge of every shot).
hook.Add("PreDrawViewModel", "penn_shots", function() if cam then return true end end)
hook.Add("PostRender", "penn_shots", function()
  if not cam then return end
  frames = frames + 1
  if frames > 30 then ft = ft + RealFrameTime() end
  if frames < 90 then return end
  fpslog[#fpslog + 1] = string.format("%-14s %4.0f fps%s", cam[1], 59 / math.max(ft, 1e-4),
    bit.band(util.PointContents(cam[2]), CONTENTS_SOLID) ~= 0 and "  CAMERA IN SOLID" or "")
  ft = 0
  local data = render.Capture({ format = "jpg", quality = 92, x = 0, y = 0, w = ScrW(), h = ScrH() })
  file.Write("penn_shots/" .. cam[1] .. ".jpg", data)
  i, frames = i + 1, 0
  cam = CAMS[i]
  goto_cam()
  if not cam then
    file.Write("penn_shots/fps.txt", table.concat(fpslog, "\n") .. "\n")
    file.Write("penn_shots/done.txt", "done")
    timer.Simple(1, function() RunConsoleCommand("quit") end)
  end
end)
timer.Simple(8, function()
  RunConsoleCommand("mat_autoexposure_max", "1.5")
  i = 1; cam = CAMS[1]; goto_cam()
end)
