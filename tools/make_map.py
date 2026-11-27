"""Rough top-down plan of the level from the VMF: every brush that stands at chest
height (4 ft) is drawn by its footprint, brushes at 30 ft faint, plus spawns and labels.
Penn's VMF has +x north and +y east, so the plan draws x up and y to the right.

python tools/make_map.py [out.png]
"""
import re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

VMF = Path(__file__).resolve().parent.parent / "src" / "gm_penn_station.vmf"
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "docs/level-map.png")
FT = 12
LAND = 16 * FT   # arcade and street level
PLAT = -240      # track platform level
txt = VMF.read_text()
solids = []
for blk in re.split(r"(?m)^\s*solid$", txt)[1:]:
    blk = re.split(r"(?m)^\s*(?:entity|editor)$", blk)[0]
    pts = [tuple(map(float, p)) for p in re.findall(r"\(([-\d.]+) ([-\d.]+) ([-\d.]+)\)", blk)]
    tex = re.findall(r'"material" "([^"]+)"', blk)
    skip = ("nodraw", "skybox", "shaft", "flag")
    if pts and not all(any(k in t.lower() for k in skip) for t in tex) and not any(k in t.lower() for t in tex for k in ("shaft", "flag")):
        solids.append((pts, tex))
spawn = [(float(x), float(y)) for x, y in re.findall(r'info_player_start"[^}]*?"origin" "([-\d.]+) ([-\d.]+)', txt, re.S)]

def hull(p):
    p = sorted(set(p))
    if len(p) < 3: return p
    def half(q):
        h = []
        for x in q:
            while len(h) > 1 and (h[-1][0]-h[-2][0])*(x[1]-h[-2][1]) - (h[-1][1]-h[-2][1])*(x[0]-h[-2][0]) <= 0: h.pop()
            h.append(x)
        return h
    return half(p)[:-1] + half(p[::-1])[:-1]

floor, faint = [], []
for pts, tex in solids:
    if all(t.lower() == 'penn/floor_travertine' for t in tex): continue   # floor slabs
    zs = [p[2] for p in pts]; lo, hi = min(zs), max(zs)
    xy = hull([(p[0], p[1]) for p in pts])
    if hi - lo > 2000 or len(xy) < 3: continue
    # two walking levels: the waiting room floor (z 0) and the arcade/street landing (z 16 ft)
    if any(lo <= z + 4*FT <= hi for z in (0, LAND, PLAT)): floor.append(xy)
    elif any(lo <= z + 30*FT <= hi for z in (0, LAND, PLAT)): faint.append(xy)
allx = [x for h in floor for x, _ in h]; ally = [y for h in floor for _, y in h]
x0, x1, y0, y1 = min(allx), max(allx), min(ally), max(ally)
W = 1600; s = (W - 120) / (y1 - y0)
H = int((x1 - x0) * s) + 260
img = Image.new("RGB", (W, H), (246, 240, 226)); d = ImageDraw.Draw(img)
try: f, fb = ImageFont.truetype("arial.ttf", 22), ImageFont.truetype("arialbd.ttf", 34)
except OSError: f = fb = ImageFont.load_default()
P = lambda x, y: (60 + (y - y0) * s, 170 + (x1 - x) * s)   # north (+x) up, east (+y) right
for g in range(0, int((y1-y0)/FT)+1, 50):
    X = P(0, y0 + g*FT)[0]; d.line((X, 160, X, H - 70), fill=(214, 204, 186))
for h in faint: d.polygon([P(*q) for q in h], fill=(222, 210, 186))
for h in floor: d.polygon([P(*q) for q in h], fill=(120, 96, 64))
for x, y in spawn:
    cx, cy = P(x, y); d.ellipse((cx-10, cy-10, cx+10, cy+10), fill=(200, 40, 40)); d.text((cx+14, cy-12), "spawn", fill=(200, 40, 40), font=f)
for lbl, x, y in (("Waiting room", 1300, 0), ("Stair", 0, 1000), ("Arcade", 0, 2800),
                  ("Train concourse", 0, -2068), ("Track platforms (below)", 0, -5200), ("Colonnade, Seventh Ave", -900, 4700),
                  ("33rd Street", 5300, -2068), ("31st Street", -5300, -2068)):
    cx, cy = P(x, y); w = d.textlength(lbl, font=f); d.rectangle((cx-w/2-6, cy-16, cx+w/2+6, cy+14), fill=(255, 255, 255)); d.text((cx-w/2, cy-13), lbl, fill=(30, 30, 30), font=f)
d.text((60, 30), "gm_penn_station: rough plan", fill=(40, 30, 20), font=fb)
d.text((60, 78), f"dark = walls and columns at chest height, light = at 30 ft, all three levels   |   grid 50 ft   |   {round((y1-y0)/FT)} x {round((x1-x0)/FT)} ft   |   N up", fill=(80, 70, 60), font=f)
d.text((60, H-45), "Generated from src/gm_penn_station.vmf by tools/make_map.py", fill=(120, 110, 100), font=f)
OUT.parent.mkdir(parents=True, exist_ok=True); img.save(OUT); print("wrote", OUT, len(floor), "brushes")
