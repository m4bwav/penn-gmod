"""Rough top-down plan of the level from the VMF: every brush that stands at chest
height (4 ft) is drawn by its footprint, balcony-level brushes faint, plus spawns and labels;
a second panel cuts the lower level (-22 ft floor) the same way.

python tools/make_map.py [out.png]
"""
import re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

VMF = Path(__file__).resolve().parent.parent / "src" / "gm_penn_station.vmf"
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "docs/level-map.png")
FT = 12
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

floor, balc, low = [], [], []
for pts, tex in solids:
    if all(t.lower() in ('gcs/floor', 'gcs/floor_low') for t in tex): continue   # floor slabs and ramps
    zs = [p[2] for p in pts]; lo, hi = min(zs), max(zs)
    xy = hull([(p[0], p[1]) for p in pts])
    if hi - lo > 2000 or len(xy) < 3: continue
    if lo <= 4*FT <= hi and (max(p[0] for p in pts) > -1714 or lo >= -2*FT): floor.append(xy)   # west of the concourse: only brushes standing on the main floor
    elif lo <= 30*FT <= hi: balc.append(xy)
    if lo <= -18*FT <= hi: low.append(xy)   # lower level (floor -22 ft), cut at chest height
allx = [x for h in floor + low for x, _ in h]; ally = [y for h in floor + low for _, y in h]
x0, x1, y0, y1 = min(allx), max(allx), min(ally), max(ally)
W = 1600; s = (W - 120) / (x1 - x0)
yr = lambda ps: (min(y for h in ps for _, y in h), max(y for h in ps for _, y in h))
(ya0, ya1), (yb0, yb1) = yr(floor), yr(low)   # each panel is as tall as its own level
PH1, PH2 = int((ya1 - ya0) * s) + 90, int((yb1 - yb0) * s) + 90; H = PH1 + PH2 + 220
img = Image.new("RGB", (W, H), (246, 240, 226)); d = ImageDraw.Draw(img)
try: f, fb = ImageFont.truetype("arial.ttf", 22), ImageFont.truetype("arialbd.ttf", 34)
except OSError: f = fb = ImageFont.load_default()

def panel(top, ytop, PH, polys, faint, title, labels, spawns=()):
    P = lambda x, y: (60 + (x - x0) * s, top + 40 + (ytop - y) * s)   # north (+y) up
    d.text((60, top), title, fill=(60, 45, 30), font=f)
    for gx in range(0, int((x1-x0)/FT)+1, 50):
        X = P(x0 + gx*FT, 0)[0]; d.line((X, top + 36, X, top + PH - 10), fill=(214, 204, 186))
    for h in faint: d.polygon([P(*q) for q in h], fill=(222, 210, 186))
    for h in polys: d.polygon([P(*q) for q in h], fill=(120, 96, 64))
    for x, y in spawns:
        cx, cy = P(x, y); d.ellipse((cx-10, cy-10, cx+10, cy+10), fill=(200, 40, 40)); d.text((cx+14, cy-12), "spawn", fill=(200, 40, 40), font=f)
    for lbl, x, y in labels:
        cx, cy = P(x, y); w = d.textlength(lbl, font=f); d.rectangle((cx-w/2-6, cy-16, cx+w/2+6, cy+14), fill=(255, 255, 255)); d.text((cx-w/2, cy-13), lbl, fill=(30, 30, 30), font=f)

d.text((60, 30), "gm_penn_station: rough plan of both levels", fill=(40, 30, 20), font=fb)
d.text((60, 78), f"dark = walls and fixtures at chest height, light = balcony level   |   grid 50 ft   |   {round((x1-x0)/FT)} x {round((y1-y0)/FT)} ft   |   N up", fill=(80, 70, 60), font=f)
cx0 = -1650  # concourse west wall
panel(130, ya1, PH1, floor, balc, "Main Concourse level (0 ft)",
      (("Information booth", 0, 0), ("Ticket windows (south)", 0, -600), ("Flag (north centre bay)", 0, 600),
       ("West balcony + stairs", cx0 + 360, 0), ("East balcony + stairs", -cx0 - 360, 0), ("Ramp wells", -1300, 390), ("Ramp wells", 1300, 390),
       ("Vanderbilt Hall", -360, -1456), ("Passage", -1302, -930), ("42nd St doors", -360, -2050),
       ("Track gates", 0, 830), ("Track platforms (shed)", 0, 2600), ("Metro-North cars", -186, 1900),
       ("42nd Street facade", -360, -2400), ("42nd Street", 600, -2900), ("Park Ave Viaduct", -2076, -3000), ("Terrace stair", 1300, -2500), ("Biltmore Room", -1360, 1500),
       ("Lexington Passage", 3106, 156), ("Graybar Passage", 3106, 1500), ("Grand Central Market", 4160, -388),
       ("Grand Hyatt atrium", 3778, 800), ("Transit Museum store", 1144, -1456), ("One Vanderbilt link", -2650, 120),
       ("One Vanderbilt lobby", -3200, 450), ("The Campbell (balcony level)", -2315, -700)), spawn)
panel(130 + PH1, yb1, PH2, low, (), "Lower level (-22 ft): ramps, Whispering Gallery, Oyster Bar, dining concourse, east landing hall, lower tracks",
      (("Dining concourse", 0, 0), ("Ramps", -2000, 390), ("Ramps", -2000, -390), ("Corridor", -1700, 0),
       ("Ramps", 2000, 390), ("Ramps", 2000, -390), ("Corridor", 1850, 0), ("East landing hall", 2924, 0),
       ("Whispering Gallery", -2984, 0), ("Oyster Bar", -3950, 0),
       ("Lower track platforms", 0, 2800), ("Track 61 (fenced)", 660, 5300), ("To Grand Central Madison (escalators, -140 ft)", -480, -2300)))
d.text((60, H-45), "Generated from src/gm_penn_station.vmf by tools/make_map.py", fill=(120, 110, 100), font=f)
OUT.parent.mkdir(parents=True, exist_ok=True); img.save(OUT); print("wrote", OUT, len(floor), "+", len(low), "brushes")
