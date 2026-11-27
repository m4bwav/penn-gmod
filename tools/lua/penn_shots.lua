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
  { "west_balcony", Vector(-1500, 0, 400), Angle(5, 0, 0) },
  { "floor_east",   Vector(-1200, -500, 72), Angle(-15, 20, 0) },
  { "chand",        Vector(-1100, -560, 330), Angle(-8, 40, 0) },
  { "booth",        Vector(-500, 300, 120), Angle(0, -30, 0) },
  { "clock",        Vector(-320, -60, 120), Angle(-8, 10, 0) },
  { "board",        Vector(150, 0, 150), Angle(-10, -95, 0) },
  { "flag",         Vector(0, -300, 72), Angle(-42, 90, 0) },
  { "vault_up",     Vector(-600, 0, 72), Angle(-70, 0, 0) },
  { "east_balcony", Vector(1500, 0, 400), Angle(5, 180, 0) },
  { "stairs_west",  Vector(-700, -300, 72), Angle(-5, 160, 0) },
  { "arcade_west",  Vector(-1480, 0, 80), Angle(-6, 180, 0) },
  { "balc_arcade",  Vector(-1450, 140, 380), Angle(-2, 180, 0) },
  { "ramp_head",    Vector(-950, 390, 90), Angle(12, 180, 0) },
  { "ramp_down",    Vector(-1900, 390, -40), Angle(8, 180, 0) },
  { "east_ramp",    Vector(950, -390, 90), Angle(12, 0, 0) },
  { "east_down",    Vector(1900, -390, -40), Angle(8, 0, 0) },
  { "east_land",    Vector(2750, 300, -200), Angle(5, -60, 0) },
  { "whisper",      Vector(-2720, -300, -200), Angle(-12, 155, 0) },
  { "oyster",       Vector(-3420, -380, -200), Angle(-4, 170, 0) },
  { "dining",       Vector(-960, -400, -200), Angle(-4, 20, 0) },
  { "ob_entry",     Vector(-2780, 0, -210), Angle(-6, 180, 0) },
  { "dining_clock", Vector(-220, -160, -190), Angle(4, 35, 0) },
  { "vh_door",      Vector(-1302, -400, 90), Angle(0, -90, 0) },
  { "vanderbilt",   Vector(-1500, -1456, 90), Angle(-12, 0, 0) },
  { "vh_chand",     Vector(-1000, -1660, 220), Angle(-14, 149, 0) },
  { "vh_east",      Vector(700, -1450, 90), Angle(-8, 180, 0) },
  { "vh_42nd",      Vector(-360, -1150, 90), Angle(-2, -90, 0) },
  { "ob_counter",   Vector(-3600, 300, -200), Angle(-6, 200, 0) },
  { "gate",         Vector(0, 200, 72), Angle(-6, 90, 0) },
  { "plat_head",    Vector(-40, 960, 64), Angle(0, 100, 0) },
  { "plat_long",    Vector(-700, 1200, 64), Angle(0, 90, 0) },
  { "car_door",     Vector(90, 1250, 64), Angle(0, 140, 0) },
  { "car_in",       Vector(-186, 1200, 60), Angle(0, 90, 0) },
  { "low_gate",     Vector(-480, 200, -200), Angle(-6, 90, 0) },
  { "low_ramp",     Vector(-480, 700, -210), Angle(8, 90, 0) },
  { "low_head",     Vector(-60, 1240, -248), Angle(0, 100, 0) },
  { "lex_door",     Vector(1350, 0, 64), Angle(0, 0, 0) },
  { "lex_in",       Vector(2000, -60, 64), Angle(0, 5, 0) },
  { "lex_sign",     Vector(1790, 0, 64), Angle(-14, 0, 0) },
  { "lex_end",      Vector(4200, 60, 64), Angle(0, 182, 0) },
  { "gb_in",        Vector(3106, 100, 64), Angle(-8, 90, 0) },
  { "gb_up",        Vector(3106, 900, 64), Angle(-22, 90, 0) },
  { "mk_door",      Vector(2912, -40, 64), Angle(0, -90, 0) },
  { "mk_window",    Vector(3330, 60, 80), Angle(8, -125, 0) },
  { "mk_sign",      Vector(2832, 60, 64), Angle(-25, -90, 0) },
  { "mk_front",     Vector(3100, 140, 72), Angle(5, -110, 0) },
  { "mk_in",        Vector(2850, -388, 64), Angle(-4, 0, 0) },
  { "mk_dome",      Vector(3800, -388, 64), Angle(-20, 0, 0) },
  { "cb_door",      Vector(-1500, -372, 376), Angle(0, 180, 0) },
  { "cb_room",      Vector(-2000, -300, 376), Angle(-6, 195, 0) },
  { "cb_bar",       Vector(-2550, -250, 376), Angle(-4, -30, 0) },
  { "tm_door",      Vector(600, -1456, 64), Angle(0, 0, 0) },
  { "tm_in",        Vector(940, -1456, 120), Angle(18, 0, 0) },
  { "tm_car",       Vector(1200, -1400, 64), Angle(0, -10, 0) },
  { "vl_link",      Vector(-1950, 0, 64), Angle(-6, 180, 0) },
  { "vl_esc",       Vector(-2380, 40, 64), Angle(-18, 180, 0) },
  { "vl_lobby",     Vector(-2960, 160, 304), Angle(-4, 195, 0) },
  { "md_gate",      Vector(-480, -300, -200), Angle(0, -90, 0) },
  { "md_esc",       Vector(-440, -900, -200), Angle(24, -90, 0) },
  { "md_conc",      Vector(-480, -3700, -1616), Angle(4, -90, 0) },
  { "md_plat",      Vector(-900, -4100, -1616), Angle(2, -20, 0) },
  { "md_screens",   Vector(-480, -4280, -1616), Angle(2, 90, 0) },
  { "t61_fence",    Vector(660, 4200, -244), Angle(0, 90, 0) },
  { "t61_in",       Vector(600, 4700, -244), Angle(-2, 80, 0) },
  { "hy_door",      Vector(3772, -100, 64), Angle(-6, 90, 0) },
  { "hy_atrium",    Vector(3600, 470, 180), Angle(-8, 60, 0) },
  { "low_long",     Vector(0, 1500, -244), Angle(0, 90, 0) },
  { "vest_out",     Vector(-360, -1972, 64), Angle(-3, -90, 0) },
  { "ext_door",     Vector(-360, -2616, 64), Angle(-8, 90, 0) },
  { "ext_street",   Vector(-360, -3516, 72), Angle(-28, 90, 0) },
  { "ext_clock",    Vector(-2076, -3100, 352), Angle(-37, 25, 0) },
  { "statue",       Vector(-360, -3200, 1900), Angle(-4, 90, 0) },
  { "ext_viaduct",  Vector(-2076, -3400, 352), Angle(-5, 90, 0) },
  { "ext_west",     Vector(2200, -2900, 72), Angle(-10, 180, 0) },
  { "ext_terrace",  Vector(1300, -2316, 352), Angle(0, 180, 0) },
  { "eagle",        Vector(1100, -3300, 600), Angle(-44, 69, 0) },
  { "taxis",        Vector(-1200, -2700, 140), Angle(-10, -40, 0) },
  { "pershing",     Vector(-2076, -3100, 352), Angle(-4, -90, 0) },
  { "pershing_ramp", Vector(-2076, -3700, 330), Angle(0, -90, 0) },
  { "bilt_door",    Vector(-1320, 600, 72), Angle(-2, 90, 0) },
  { "biltmore",     Vector(-1560, 940, 90), Angle(-10, 70, 0) },
  { "bilt_board",   Vector(-1360, 1200, 100), Angle(-4, 90, 0) },
  { "pershing_in",  Vector(-2076, -3900, 64), Angle(-2, -90, 0) },
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
