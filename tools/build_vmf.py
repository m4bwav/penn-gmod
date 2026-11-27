"""Build src/gm_penn_station.vmf: the 1910 Pennsylvania Station at 1 ft = 12 u.

Blockout stage: main waiting room. Run: python tools/build_vmf.py
Dimensions: ai-docs/notes/2026-11-26-dimensions.md.
"""
from pathlib import Path

import vmf_lib
from vmf_lib import axes_for as _ax, box, prism, xprism, yprism, halfdisc, ngon, ent, groin, nid, _id

FT = 12
OUT = Path(__file__).resolve().parent.parent / "src" / "gm_penn_station.vmf"

# Main waiting room: 314 ft 4 in x 108 ft 8 in, 150 ft to the crown. Long axis = x
# runs north-south in the station (+x toward 33rd St); +y is east, toward the arcade and Seventh Avenue;
# -y is west, toward the concourse.
HX, HY = 3772 // 2, 1304 // 2            # 1886, 652
CROWN = 150 * FT                          # 1800
RISE = HY                                 # groin barrels rise half the room width
SPRING = CROWN - RISE - 16                # 1132: groin() adds 16 u above the crown
BAYS = (-HX, -HX // 3, HX // 3, HX)       # three groin bays
T = 8 * FT                                # wall thickness
LUNETTE = 460                             # thermal window radius, 38 ft 4 in
PED = 14 * FT                             # column pedestal (session 5: taller, per the photos)
COL_TOP = PED + 60 * FT                   # capital top, 60 ft above the pedestal
ENT_Z0, ENT_Z1 = COL_TOP, COL_TOP + 14 * FT   # entablature over the columns
ARC_W, ARC_H, LAND = 40 * FT, 30 * FT, 16 * FT  # stair opening to the arcade, landing rise
ARCH_W, ARCH_SPRING = 30 * FT, 45 * FT    # round-headed arches in each long-wall bay, crown 60 ft
FACE = 4 * FT                             # arcade face layer standing proud of the long walls
NICHE, NICHE_H = 4 * FT, ARCH_SPRING + ARCH_W // 2   # recess behind the side arches, up to the crown
# Arcade (area 2): 45 ft x 225 ft at street level, east of the stair hall, five 45 ft groin bays
# lined with shops, Seventh Avenue at its east end.
AHX, AL, ABAY = 45 * FT // 2, 225 * FT, 45 * FT       # 270, 2700, 540
A_SPRING = LAND + 32 * FT                              # 576: vaults spring 32 ft above the arcade floor
YA = HY + T + 60 * FT                                  # 1468: west end of the arcade, top of the stair hall
YB = YA + AL                                           # 4168: Seventh Avenue end
VEST = 40 * FT                                         # entrance vestibule east of the arcade
# Train concourse (area 3): about 314 x 200 ft west of the waiting room, at the same floor level,
# under three glass groin vaults on steel lattice columns (HABS photos, refs/SOURCES.md).
CY1 = -HY - T - 10 * FT                                # -868: east edge, end of the west passages
CY0 = CY1 - 200 * FT                                   # -3268: west edge
C_SPRING, C_RISE = 45 * FT, 55 * FT                    # glass vaults spring at 45 ft, crown about 100 ft
TEX_STEEL = "metal/metalwall001a"
TEX_CGLASS = "penn/conc_glass"                         # session 19: gridded roof glass, 32 ft per tile

TEX_FLOOR = "penn/floor_travertine"
TEX_WALL = "penn/travertine_ashlar"
TEX_VAULT = "penn/vault_coffer"
TEX_TRIM = "penn/travertine"
TEX_COL = "penn/travertine"
# Texture scale: 512 px tiles. Ashlar 16 ft (4 ft courses), coffers 12 ft 10 in, floor slabs 10 ft 8 in.
vmf_lib.SCALE.update({TEX_WALL: 0.375, TEX_TRIM: 0.375, TEX_VAULT: 0.6, TEX_FLOOR: 0.5, "penn/conc_glass": 0.75})
TEX_GLASS = "penn/window_glass"
TEX_DOOR = "penn/window_glow"
NODRAW = "tools/toolsnodraw"
TEX_SHOP = "penn/shopfront"
# One shopfront tile per 45 ft bay along y (aligned to YA), 18 ft tall from the arcade floor.
_su, _sv = ABAY / 512, 18 * FT / 512
vmf_lib.FACEUV[TEX_SHOP] = lambda n: (("[0 1 0 %g] %g" % (-(YA / _su) % 512, _su), "[0 0 -1 %g] %g" % (((LAND + 18 * FT) / _sv) % 512, _sv))
                                      if abs(n[0]) > 0.5 else _ax(n))


def arcade(W, det, ents):
    """Area 2 blockout: the shopping arcade from the stair hall (y = YA) to Seventh Avenue (y = YB),
    floor at LAND, five groin bays, a shopfront in each bay on both sides, a vestibule at the east end."""
    z0, ztop = LAND, A_SPRING + AHX + 16 + 64
    W(box(-AHX - T, YA, z0 - 64, AHX + T, YB, z0, TEX_FLOOR))
    # West end wall over and beside the 40 ft stair hall opening (hall walls stop at YA).
    a, b = -ARC_W // 2, ARC_W // 2
    W(box(-AHX - T, YA - 32, ARC_H + LAND, AHX + T, YA, ztop, TEX_WALL))
    for x0, x1 in ((-AHX - T, a - 32), (b + 32, AHX + T)):
        W(box(x0, YA - 32, z0 - 64, x1, YA, ARC_H + LAND, TEX_WALL))
    # Side walls: per bay a shopfront 30 ft wide, 18 ft high, recessed the wall depth to a lit window.
    SW, SH = 30 * FT, 18 * FT
    for s in (-1, 1):
        x0, x1 = sorted((s * AHX, s * (AHX + T)))
        edges = [YA]
        for i in range(5):
            c = YA + i * ABAY + ABAY // 2
            edges += [c - SW // 2, c + SW // 2]
            W(box(x0, c - SW // 2, z0 + SH, x1, c + SW // 2, ztop, TEX_WALL))
            g0, g1 = sorted((s * (AHX + T), s * (AHX + T + 16)))
            W(box(g0, c - SW // 2, z0 - 64, g1, c + SW // 2, z0 + SH, TEX_SHOP))
            W(box(x0, c - SW // 2, z0 + SH - 16, x1, c + SW // 2, z0 + SH, TEX_TRIM))
        edges.append(YB)
        for i in range(0, len(edges), 2):
            W(box(x0, edges[i], z0 - 64, x1, edges[i + 1], ztop, TEX_WALL))
    # Session 10 detail (Pennell's etching, refs/photos/The_arcade_...): a 3 ft pilaster at each
    # bay line rising to a 2 ft impost cornice that runs the length of both walls at the springing.
    PW, PD, CH, CD = 3 * FT, FT, 2 * FT, FT + 6
    for s in (-1, 1):
        f0, f1 = sorted((s * AHX, s * (AHX - PD)))
        c0, c1 = sorted((s * AHX, s * (AHX - CD)))
        sol = [box(f0, YA + i * ABAY - PW // 2 if i else YA, z0, f1, YA + i * ABAY + PW // 2 if i < 5 else YB, A_SPRING - CH, TEX_TRIM)
               for i in range(6)]
        sol.append(box(c0, YA, A_SPRING - CH, c1, YB, A_SPRING, TEX_TRIM))
        det("".join(sol))
    # Session 11 (Pennell's etching): the stair-hall end. An architrave band frames the 40 ft
    # opening with a keystone at the head; above it the west lunette is a mullioned glass window.
    hz = ARC_H + LAND
    BW, KW = 2 * FT, 4 * FT
    sol = [box(a - BW, YA, z0, a, YA + 8, hz + BW, TEX_TRIM), box(b, YA, z0, b + BW, YA + 8, hz + BW, TEX_TRIM),
           box(a, YA, hz, b, YA + 8, hz + BW, TEX_TRIM),
           box(-KW // 2, YA, hz - FT, KW // 2, YA + 16, hz + BW + 3 * FT, TEX_TRIM)]
    det("".join(sol))
    LR = AHX - 2 * FT
    det(yprism(halfdisc(0, A_SPRING, LR, 12), YA, YA + 4, TEX_GLASS))
    bars = [(d - 8, A_SPRING, d + 8, A_SPRING + int(LR * 0.94)) for d in (-LR // 3, LR // 3)]
    bars.append((-LR + 30, A_SPRING + 100, LR - 30, A_SPRING + 112))
    bars.append((-LR - 12, A_SPRING - 18, LR + 12, A_SPRING))
    det("".join(box(u0, YA + 4, zz0, u1, YA + 16, zz1, TEX_TRIM) for u0, zz0, u1, zz1 in bars))
    arc, band = halfdisc(0, A_SPRING, LR, 12), halfdisc(0, A_SPRING, LR + 14, 12)
    det("".join(yprism([arc[i + 1], arc[i], band[i], band[i + 1]], YA, YA + 10, TEX_TRIM) for i in range(12)))
    for i in range(5):
        # Session 12: plain travertine webs, coffers only in the crown strips.
        groin(W, -AHX, AHX, YA + i * ABAY, YA + (i + 1) * ABAY, A_SPRING, AHX, TEX_TRIM, crown=TEX_VAULT)
    # East end: a 40 ft x 30 ft opening into the entrance vestibule; the street doors glow for now.
    W(box(-AHX - T, YB, ARC_H + LAND, AHX + T, YB + T, ztop, TEX_WALL))
    for x0, x1 in ((-AHX - T, a), (b, AHX + T)):
        W(box(x0, YB, z0 - 64, x1, YB + T, ARC_H + LAND, TEX_WALL))
    v1 = YB + T + VEST
    W(box(a, YB, z0 - 64, b, v1, z0, TEX_FLOOR))
    W(box(a - 32, YB + T, z0 - 64, a, v1, ARC_H + LAND + 32, TEX_WALL))
    W(box(b, YB + T, z0 - 64, b + 32, v1, ARC_H + LAND + 32, TEX_WALL))
    W(box(a, YB + T, ARC_H + LAND, b, v1, ARC_H + LAND + 32, TEX_TRIM))
    colonnade(W, det, ents, v1)
    # Session 13 (Pennell's etching): bronze lamp standards in front of the pilasters at the four
    # inner bay lines, each with a small warm light at its globes (penn_models.LAMP_GLOBE_Z = 15 ft).
    for i in range(1, 5):
        for s in (-1, 1):
            p = (s * (AHX - 5 * FT), YA + i * ABAY)
            ents.append(ent("prop_static", (p[0], p[1], z0), model="models/penn/lamp.mdl", solid="6"))
            ents.append(ent("light", (p[0], p[1], z0 + 15 * FT + 24), _light="255 214 160 8"))
    for i in range(5):
        ents.append(ent("light", (0, YA + i * ABAY + ABAY // 2, A_SPRING), _light="250 225 190 40"))
    ents.append(ent("light", (0, YB + T + VEST // 2, LAND + 20 * FT), _light="250 225 190 35"))
    ents.append(ent("env_cubemap", (0, (YA + YB) // 2, LAND + 200)))


def concourse(W, det, ents, top):
    """Area 3 blockout: floor, outer walls, three glass groin bays along x, lattice columns."""
    ctop = C_SPRING + C_RISE + 16 + 64
    # Session 23: six stairs down to the tracks in the west half of the floor (HABS CONCOURSE_FROM_SOUTH),
    # 10 ft wide, 30 steps of 8 x 16 in descending westward to a landing 20 ft down, a glowing door at
    # the foot until area 4 adds the platforms. Steel railings on three sides, open at the top step.
    sy0, sy1, sz, sw = CY0 + 48, CY0 + 600, -240, 60
    wells = [c + d for c in ((BAYS[i] + BAYS[i + 1]) // 2 for i in range(3)) for d in (-300, 300)]
    W(box(-HX - T, CY0 - T, -64, HX + T, sy0, 0, TEX_FLOOR))
    W(box(-HX - T, sy1, -64, HX + T, CY1, 0, TEX_FLOOR))
    xs = [-HX - T] + [v for c in wells for v in (c - sw, c + sw)] + [HX + T]
    for k in range(0, len(xs), 2):
        W(box(xs[k], sy0, -64, xs[k + 1], sy1, 0, TEX_FLOOR))
    for c in wells:
        x0, x1 = c - sw, c + sw
        for a, b in ((x0 - 32, x0), (x1, x1 + 32)):
            W(box(a, sy0 - 32, sz, b, sy1 + 32, -64, TEX_WALL))
        W(box(x0, sy1, sz, x1, sy1 + 32, -64, TEX_WALL))
        for k in range(30):
            det(box(x0, sy0 + 72 + 16 * k, sz, x1, sy1, sz + 8 * (k + 1), TEX_FLOOR))
        for ly, lz in ((sy0 + 40, sz + 96), (sy0 + 300, sz + 200)):
            ents.append(ent("light", (c, ly, lz), _light="255 220 170 160"))
        rz = 42
        for a in (x0 - 3, x1 + 1):                                         # side rails along y
            det(box(a, sy0 - 3, rz - 3, a + 2, sy1, rz, TEX_STEEL))
            for y in range(sy0, sy1 + 1, 46):
                det(box(a, y - 1, 0, a + 2, y + 1, rz - 3, TEX_STEEL))
        det(box(x0 - 3, sy0 - 3, rz - 3, x1 + 3, sy0 - 1, rz, TEX_STEEL))  # end rail
        for x in range(x0 + 24, x1 - 23, 24):
            det(box(x - 1, sy0 - 3, 0, x + 1, sy0 - 1, rz - 3, TEX_STEEL))
    W(box(-HX - T, CY0 - T, 0, HX + T, CY0, ctop, TEX_WALL))                 # west wall
    for s in (-1, 1):                                                      # 31st / 33rd St ends
        x0, x1 = (HX, HX + T) if s > 0 else (-HX - T, -HX)
        W(box(x0, CY0, 0, x1, CY1, ctop, TEX_WALL))
    # East wall: solid between the three 20 ft west passages of the waiting room, and above them.
    ops = [((BAYS[i] + BAYS[i + 1]) // 2 - 152, (BAYS[i] + BAYS[i + 1]) // 2 + 152) for i in range(3)]
    edges = [-HX - T] + [v for o in ops for v in o] + [HX + T]
    for i in range(0, len(edges), 2):
        W(box(edges[i], CY1, 0, edges[i + 1], -HY - T, top, TEX_WALL))
    for a, b in ops:
        W(box(a, CY1, ARC_H + 32, b, -HY - T, top, TEX_WALL))
    # Session 22: travertine arcade on the concourse face of the east wall (HABS photos): three
    # round-headed arches per bay, 25 ft 4 in wide, springing at the passage head; the middle one is
    # the passage, the side ones blind. A 2 ft face layer with a cornice band at 50 ft.
    d0, d1, atop = CY1 - 2 * FT, CY1, 50 * FT
    r = 152
    for i in range(3):
        cx = (BAYS[i] + BAYS[i + 1]) // 2
        lo, hi = (BAYS[i] if i else -HX), (BAYS[i + 1] if i < 2 else HX)
        cxs = [cx - 420, cx, cx + 420]
        edges = [lo] + [v for c in cxs for v in (c - r, c + r)] + [hi]
        for k in range(0, len(edges), 2):
            det(box(edges[k], d0, 0, edges[k + 1], d1, atop, TEX_WALL))
        for c in cxs:
            arc, band = halfdisc(c, ARC_H, r, 10), halfdisc(c, ARC_H, r + 18, 10)
            for j in range(10):
                (xa, za), (xb, zb) = arc[j + 1], arc[j]
                det(yprism([(xa, za), (xb, zb), (xb, atop), (xa, atop)], d0, d1, TEX_WALL))
                det(yprism([arc[j + 1], arc[j], band[j], band[j + 1]], d0 - 6, d0, TEX_TRIM))
            for x in (c - r - 16, c + r - 2):
                det(box(x, d0 - 12, ARC_H - 24, x + 18, d1, ARC_H, TEX_TRIM))
    det(box(-HX, d0 - 18, atop, HX, d1, atop + 2 * FT, TEX_TRIM))
    # Session 24: clock (clock.mdl, 10 ft face) on the east wall above the middle passage and cornice.
    ents.append(ent("prop_static", (0, d0, atop + 8 * FT), model="models/penn/clock.mdl", solid="0", disableshadows="1"))
    # Glass groin vaults: one per waiting-room bay, spanning the full 200 ft depth.
    for i in range(3):
        groin(W, BAYS[i], BAYS[i + 1], CY0, CY1, C_SPRING, C_RISE, TEX_CGLASS)
    # Fill between the vault crowns and the waiting room's west wall top.
    W(box(-HX - T, CY0 - T, ctop, HX + T, -HY - T, ctop + 64, NODRAW))
    platforms(W, det, ents, wells, sw)
    # Steel lattice columns (lattice.mdl since session 19): at every bay line
    # on both long sides and two rows across the floor, each 3 ft square up to the springing.
    for x in BAYS:
        for y in (CY0 + 2 * FT, CY0 + 70 * FT, CY1 - 70 * FT, CY1 - 2 * FT):
            xx = max(-HX + 2 * FT, min(HX - 2 * FT, x))
            ents.append(ent("prop_static", (xx, y, 0), model="models/penn/lattice.mdl", solid="6", disableshadows="1"))
    # Session 20: steel truss ribs on each vault's groins and a transverse arch at the inner bay lines.
    # studiomdl turns SMD geometry 90 degrees about z, so both stand at yaw 90 (session 21: at yaw 0 the
    # arches ran along the hall and showed as a line down its centre).
    yc = (CY0 + CY1) // 2
    for i in range(3):
        ents.append(ent("prop_static", ((BAYS[i] + BAYS[i + 1]) // 2, yc, 0), angles="0 90 0", model="models/penn/conc_diag.mdl", solid="0", disableshadows="1"))
    for x in BAYS[1:3]:
        ents.append(ent("prop_static", (x, yc, 0), angles="0 90 0", model="models/penn/conc_arch.mdl", solid="0", disableshadows="1"))
    for i in range(3):
        cx = (BAYS[i] + BAYS[i + 1]) // 2
        ents.append(ent("light", (cx, (CY0 + CY1) // 2, C_SPRING), _light="215 225 240 40"))
        # Session 26: daylight fill under the glass. The roof texlight alone left the floor and the
        # lower walls grey; a 3 x 3 grid per bay at 28 ft lifts them with cool skylight.
        for dx in (-380, 0, 380):
            for fy in (0.2, 0.5, 0.8):
                ents.append(ent("light", (cx + dx, int(CY0 + fy * (CY1 - CY0)), 28 * FT), _light="225 230 240 22"))
        ents.append(ent("env_cubemap", (cx, (CY0 + CY1) // 2, 200)))


def colonnade(W, det, ents, f0):
    """Session 15: the Seventh Avenue entrance. The facade wall (y f0..f0+T) has the 40 ft
    arcade opening; in front stands a Doric colonnade (doric.mdl, 35 ft) carrying a portico roof,
    entablature and attic, then the sidewalk, the avenue and a stand-in block opposite, under sky."""
    a, b, z0 = -ARC_W // 2, ARC_W // 2, LAND
    f1 = f0 + T
    FX, SKYZ, FTOP = 120 * FT, LAND + 130 * FT, LAND + 75 * FT
    cy = f1 + 18 * FT                                   # column centre line
    pe = cy + 4 * FT                                    # portico edge
    sw1, st1, far = pe + 20 * FT, pe + 80 * FT, pe + 95 * FT
    W(box(-FX, f0, z0 - 64, a, f1, FTOP, TEX_WALL))
    W(box(b, f0, z0 - 64, FX, f1, FTOP, TEX_WALL))
    W(box(a, f0, ARC_H + LAND, b, f1, FTOP, TEX_WALL))
    # Ground: travertine portico, granite sidewalks, asphalt avenue a curb lower.
    W(box(-FX, f1, z0 - 64, FX, pe, z0, TEX_FLOOR))
    W(box(-FX, pe, z0 - 64, FX, sw1, z0 - 8, "penn/sidewalk"))
    W(box(-FX, sw1, z0 - 64, FX, st1, z0 - 16, "penn/asphalt"))
    W(box(-FX, st1, z0 - 64, FX, far, z0 - 8, "penn/sidewalk"))
    # Enclosure: block opposite, side walls, sky over everything and behind the facade top.
    W(box(-FX, far, z0 - 64, FX, far + 32, SKYZ, TEX_WALL))
    for x0, x1 in ((-FX - 32, -FX), (FX, FX + 32)):
        W(box(x0, f0 - 32, z0 - 64, x1, far + 32, SKYZ, TEX_WALL))
    W(box(-FX, f0 - 32, FTOP, FX, f0, SKYZ, "tools/toolsskybox"))
    W(box(-FX - 32, f0 - 32, SKYZ, FX + 32, far + 32, SKYZ + 32, "tools/toolsskybox"))
    # Portico: roof slab on the columns, projecting cornice, attic; a cornice band on the facade.
    cz = z0 + 35 * FT
    PX = 11 * 108 + 5 * FT
    sol = [box(-PX, f1, cz, PX, pe, cz + 7 * FT, TEX_TRIM),
           box(-PX - 16, pe, cz + 5 * FT, PX + 16, pe + 18, cz + 7 * FT, TEX_TRIM),
           box(-PX, f1, cz + 7 * FT, PX, pe - 6, cz + 14 * FT, TEX_WALL),
           box(-PX - 8, pe - 6, cz + 14 * FT, PX + 8, pe + 4, cz + 15 * FT, TEX_TRIM),
           box(-FX, f1, FTOP - 3 * FT, FX, f1 + 18, FTOP, TEX_TRIM)]
    det("".join(sol))
    for k in range(12):
        ents.append(ent("prop_static", ((2 * k - 11) * 108, cy, z0), model="models/penn/doric.mdl", solid="6"))
    # Session 16: Seventh Avenue faces east (+y), so the morning sun travels west (yaw 250) onto
    # the facade; warm bounce lights under the portico soffit and inside the colonnade.
    ents.append(ent("light_environment", (0, cy, cz - 64), pitch="-35", angles="0 250 0",
                    _light="255 236 205 320", _ambient="150 170 205 140"))
    for k in range(-2, 3):
        ents.append(ent("light", (k * 5 * 108, (f1 + cy) // 2, cz - 3 * FT), _light="250 228 195 40"))
        ents.append(ent("light", (k * 5 * 108, pe - FT, z0 + 6 * FT), _light="255 232 200 25"))
    ents.append(ent("env_cubemap", (0, sw1, z0 + 100)))


# Track level (area 4): session 28 blockout. One 30 ft island platform under each concourse stair,
# a single track between neighbours (Penn had 21 tracks on 11 platforms, one track per gap), 500 ft
# of the platforms from the waiting room's west wall to the tunnel portals. Platform top = stair
# landing (-240, 20 ft below the concourse), rail top 4 ft lower, ceiling = underside of the
# concourse floor (-64). Rails are brush strips for now; the train comes in a later session.
PY0 = CY0 - 300 * FT                                   # -6868: west wall with the tunnel portals
P_TOP, P_RAIL, P_BED = -240, -288, -300
P_W = 30 * FT


def platforms(W, det, ents, wells, sw):
    W(box(-HX - T, PY0 - T, P_BED - 32, HX + T, CY1 + T, P_BED, TEX_FLOOR))     # track bed
    W(box(-HX - T, PY0 - T, -64, HX + T, CY0 - T, 0, TEX_FLOOR))                 # ceiling west of the concourse
    for x0, x1 in ((-HX - T, -HX), (HX, HX + T)):                                # 31st / 33rd St walls
        W(box(x0, PY0, P_BED, x1, CY1, -64, TEX_WALL))
    W(box(-HX - T, CY1, P_BED, HX + T, CY1 + T, -64, TEX_WALL))                  # east end
    # West wall: a 16 ft dark portal over every track, a black tunnel 40 ft deep behind it.
    tracks = [(-HX + wells[0] - P_W // 2) // 2]
    tracks += [(wells[i] + wells[i + 1]) // 2 for i in range(len(wells) - 1)]
    tracks += [(HX + wells[-1] + P_W // 2) // 2]
    # The outer tracks run 12 ft from the side walls: clamp their portals to the room, or the wall
    # pieces between come out inside-out and the world bounds go infinite (session 28).
    ops = [(max(-HX, t - 84), min(HX, t + 84)) for t in tracks]
    edges = [-HX] + [v for o in ops for v in o] + [HX]
    for i in range(0, len(edges), 2):
        if edges[i + 1] > edges[i]:
            W(box(edges[i], PY0 - T, P_BED, edges[i + 1], PY0, -64, TEX_WALL))
    for a, b in ops:
        W(box(a, PY0 - T, P_BED + 16 * FT + 12, b, PY0, -64, TEX_WALL))
        W(box(a - 16, PY0 - T - 40 * FT, P_BED, a, PY0 - T, P_BED + 16 * FT + 12, "tools/toolsblack"))
        W(box(b, PY0 - T - 40 * FT, P_BED, b + 16, PY0 - T, P_BED + 16 * FT + 12, "tools/toolsblack"))
        W(box(a, PY0 - T - 40 * FT, P_BED + 16 * FT + 12, b, PY0 - T, -64, "tools/toolsblack"))
        W(box(a, PY0 - T - 40 * FT - 16, P_BED, b, PY0 - T - 40 * FT, -64, "tools/toolsblack"))
    for t in tracks:                                                             # rails, standard gauge
        for g in (-28, 28):
            det(box(t + g - 2, PY0 - T - 40 * FT, P_BED, t + g + 2, CY1, P_RAIL, TEX_STEEL))
    # Session 29: a train (three coaches and a DD1 electric) on the middle track, engine west.
    ents.append(ent("prop_static", (tracks[3], CY1 - 20 * FT, P_RAIL), angles="0 180 0",
                    model="models/penn/train.mdl", solid="6", disableshadows="1"))
    for c in wells:
        W(box(c - P_W // 2, PY0, P_BED, c + P_W // 2, CY1, P_TOP, TEX_FLOOR))
        # Steel columns on the platform centre line every 40 ft, clear of the stair enclosure.
        for y in range(PY0 + 30 * FT, CY1 - 10 * FT, 40 * FT):
            if CY0 - 2 * FT < y < CY0 + 640:
                continue
            det(box(c - 9, y - 9, P_TOP, c + 9, y + 9, -64, TEX_STEEL))
        for y in range(PY0 + 50 * FT, CY1, 60 * FT):
            ents.append(ent("light", (c, y, -96), _light="255 214 160 90"))
    ents.append(ent("env_cubemap", (wells[2], CY0 - 100 * FT, P_TOP + 72)))


def build():
    world, ents = [], []
    W = world.append
    det = lambda s: ents.append(ent("func_detail", solids=s))

    top = SPRING + RISE + 16 + 64
    # Sealed nodraw hull around everything.
    X0, X1 = -HX - T - 256, HX + T + 256
    # Session 15: the hull now reaches past the Seventh Avenue block opposite (colonnade()).
    Y0, Y1 = PY0 - T - 40 * FT - 16 - 256, YB + T + VEST + T + 117 * FT + 32 + 256
    Z0, Z1 = -384, top + 128                 # session 23: below the track stairs (landing at -240)
    for b in ((X0, Y0, Z0 - 64, X1, Y1, Z0), (X0, Y0, Z1, X1, Y1, Z1 + 64),
              (X0 - 64, Y0, Z0, X0, Y1, Z1), (X1, Y0, Z0, X1 + 64, Y1, Z1),
              (X0, Y0 - 64, Z0, X1, Y0, Z1), (X0, Y1, Z0, X1, Y1 + 64, Z1)):
        W(box(*b, NODRAW))

    # Floor and end walls (x = +-HX, the 31st and 33rd St ends).
    W(box(-HX - T, -HY - T, -64, HX + T, HY + T, 0, TEX_FLOOR))
    for s in (-1, 1):
        x0, x1 = (HX, HX + T) if s > 0 else (-HX - T, -HX)
        W(box(x0, -HY - T, 0, x1, HY + T, top, TEX_WALL))

    def long_wall(y0, y1, ops, h):
        """Wall along x between y0 and y1 with openings [(x0, x1)] of height h."""
        edges = [-HX] + [v for o in ops for v in o] + [HX]
        for i in range(0, len(edges), 2):
            W(box(edges[i], y0, 0, edges[i + 1], y1, top, TEX_WALL))
        for a, b in ops:
            W(box(a, y0, h, b, y1, top, TEX_WALL))

    # Niches (session 8): behind each side arch the wall steps back 4 ft (NICHE) up to the arch
    # crown, so the arches read as openings into the side passages. The wall proper sits NICHE
    # back from the room face; filler brushes bring the face forward everywhere else.
    def niche_fill(s, gaps):
        """Face brushes between y = s*HY and s*(HY + NICHE), open over gaps [(x0, x1, z_top)]."""
        y0, y1 = sorted((s * HY, s * (HY + NICHE)))
        edges = [-HX] + [v for g in gaps for v in g[:2]] + [HX]
        for i in range(0, len(edges), 2):
            W(box(edges[i], y0, 0, edges[i + 1], y1, top, TEX_WALL))
        for x0, x1, zt in gaps:
            W(box(x0, y0, zt, x1, y1, top, TEX_WALL))
    side = lambda i: ((BAYS[i] + BAYS[i + 1]) // 2 - ARCH_W // 2, (BAYS[i] + BAYS[i + 1]) // 2 + ARCH_W // 2, NICHE_H)

    # West wall (y = -HY): one 20 ft opening per bay into the concourse (session 18).
    ops = [((BAYS[i] + BAYS[i + 1]) // 2 - 120, (BAYS[i] + BAYS[i + 1]) // 2 + 120) for i in range(3)]
    long_wall(-HY - T, -HY - NICHE, ops, ARC_H)
    niche_fill(-1, [side(i) for i in range(3)])
    py = -HY - T - 10 * FT
    for a, b in ops:
        W(box(a - 32, py, 0, a, -HY - T, ARC_H, TEX_WALL))
        W(box(b, py, 0, b + 32, -HY - T, ARC_H, TEX_WALL))
        W(box(a, py, ARC_H, b, -HY - T, ARC_H + 32, TEX_WALL))
        W(box(a, py, -64, b, -HY - T, 0, TEX_FLOOR))
    concourse(W, det, ents, top)

    # East wall (y = +HY): the 40 ft stair opening up to the arcade from Seventh Avenue.
    a, b = -ARC_W // 2, ARC_W // 2
    long_wall(HY + NICHE, HY + T, [(a, b)], ARC_H + LAND)
    niche_fill(1, [side(0), (a, b, ARC_H + LAND), side(2)])
    # Stair hall east of the opening: 16 steps up to a landing, sealed door at the arcade end.
    sy0, run, steps = HY, 32 * FT, 16
    sy1 = sy0 + T + 60 * FT
    W(box(a - 32, sy0 + T, -64, a, sy1, ARC_H + LAND + 32, TEX_WALL))
    # Session 14: the Cassatt niche in the north wall (+x) at the landing, a 10 ft round-headed
    # recess through the 32 u wall with Weinman's bronze of Alexander Cassatt on a pedestal, facing south.
    ny0, ny1, nz0, nr = 1240, 1360, LAND, 60
    nzs = nz0 + 18 * FT                       # springing of the niche head
    zt = ARC_H + LAND + 32
    W(box(b, sy0 + T, -64, b + 32, ny0, zt, TEX_WALL))
    W(box(b, ny1, -64, b + 32, sy1, zt, TEX_WALL))
    W(box(b, ny0, -64, b + 32, ny1, nz0, TEX_WALL))
    W(box(b, ny0, nzs + nr + 16, b + 32, ny1, zt, TEX_WALL))
    arc = halfdisc((ny0 + ny1) // 2, nzs, nr, 8)
    for i in range(8):
        (ya, za), (yb, zb) = arc[i + 1], arc[i]
        W(xprism([(ya, za), (yb, zb), (yb, nzs + nr + 16), (ya, nzs + nr + 16)], b, b + 32, TEX_WALL))
    W(box(b + 32, ny0 - 32, -64, b + 64, ny1 + 32, zt, TEX_WALL))          # back of the recess
    det(box(b - 30, ny0 + 12, nz0, b + 32, ny1 - 12, nz0 + 3 * FT, TEX_TRIM))     # pedestal
    det(box(b - 8, ny0 - 18, nzs - 16, b, ny0, nzs, TEX_TRIM))                    # imposts
    det(box(b - 8, ny1, nzs - 16, b, ny1 + 18, nzs, TEX_TRIM))
    ents.append(ent("prop_static", (b, (ny0 + ny1) // 2, nz0 + 3 * FT), angles="0 180 0",
                    model="models/penn/cassatt.mdl", solid="6"))
    ents.append(ent("light", (b - 6 * FT, (ny0 + ny1) // 2, nz0 + 14 * FT), _light="250 225 190 12"))
    W(box(a, sy0 + T, ARC_H + LAND, b, sy1, ARC_H + LAND + 32, TEX_TRIM))
    W(box(a, sy0, -64, b, sy0 + T, 0, TEX_FLOOR))
    for i in range(steps):
        y = sy0 + T + i * run // steps
        W(box(a, y, -64, b, y + run // steps, (i + 1) * LAND // steps, TEX_FLOOR))
    W(box(a, sy0 + T + run, -64, b, sy1, LAND, TEX_FLOOR))
    arcade(W, det, ents)

    # Groin vaults over the three bays.
    for i in range(3):
        groin(W, BAYS[i], BAYS[i + 1], -HY, HY, SPRING, RISE, TEX_VAULT)

    # Thermal windows in every lunette: long walls (per bay) and both ends.
    for i in range(3):
        cx = (BAYS[i] + BAYS[i + 1]) // 2
        for s in (-1, 1):
            y = s * HY
            det(yprism(halfdisc(cx, SPRING + 48, LUNETTE, 12), min(y, y - 8 * s), max(y, y - 8 * s), TEX_GLASS))
    for s in (-1, 1):
        x = s * HX
        det(xprism(halfdisc(0, SPRING + 48, LUNETTE, 12), min(x, x - 8 * s), max(x, x - 8 * s), TEX_GLASS))

    # Diocletian mullions: two stone piers split each lunette into three lights, a transom across.
    z0, mw, hz = SPRING + 48, 12, int(LUNETTE * 0.94)
    def mullions(c, wall, s, along_x):
        bars = [(c + d - mw, z0, c + d + mw, z0 + hz) for d in (-LUNETTE // 3, LUNETTE // 3)]
        bars.append((c - LUNETTE + 40, z0 + 168, c + LUNETTE - 40, z0 + 168 + 16))
        bars.append((c - LUNETTE, z0 - 24, c + LUNETTE, z0))
        d0, d1 = sorted((wall - 8 * s, wall - 24 * s))
        for u0, zz0, u1, zz1 in bars:
            det(box(u0, d0, zz0, u1, d1, zz1, TEX_TRIM) if along_x else box(d0, u0, zz0, d1, u1, zz1, TEX_TRIM))
    for i in range(3):
        for s in (-1, 1):
            mullions((BAYS[i] + BAYS[i + 1]) // 2, s * HY, s, True)
    for s in (-1, 1):
        mullions(0, s * HX, s, False)

    # Round-headed arches: one per bay in each long wall, a 4 ft face layer with the arch cut out;
    # the recess shows the wall behind. The east middle bay is the stair opening, so its arch is
    # 40 ft wide and springs at the opening head, with a glass tympanum.
    def arch_face(cx, s, w, zs):
        wy = s * HY
        d0, d1 = sorted((wy, wy - FACE * s))
        r = w // 2
        lo, hi = (BAYS[0], BAYS[1]) if cx < BAYS[1] else ((BAYS[1], BAYS[2]) if cx < BAYS[2] else (BAYS[2], BAYS[3]))
        det(box(lo, d0, 0, cx - r, d1, ENT_Z0, TEX_WALL))
        det(box(cx + r, d0, 0, hi, d1, ENT_Z0, TEX_WALL))
        arc = halfdisc(cx, zs, r, 10)
        for i in range(10):
            (xa, za), (xb, zb) = arc[i + 1], arc[i]          # left to right
            poly = [(xa, za), (xb, zb), (xb, ENT_Z0), (xa, ENT_Z0)]
            det(yprism(poly, d0, d1, TEX_WALL))
        # Archivolt: a plain travertine band round the arch, 6 u proud of the face.
        f0, f1 = (d0 - 6, d0) if s > 0 else (d1, d1 + 6)
        band = halfdisc(cx, zs, r + 18, 10)
        for i in range(10):
            det(yprism([arc[i + 1], arc[i], band[i], band[i + 1]], f0, f1, TEX_TRIM))
        # Impost blocks at the springing.
        for x in (cx - r - 16, cx + r - 2):
            det(box(x, min(d0, d1) - (12 if s > 0 else 0), zs - 24, x + 18, max(d0, d1) + (12 if s < 0 else 0), zs, TEX_TRIM))
    for i in range(3):
        cx = (BAYS[i] + BAYS[i + 1]) // 2
        arch_face(cx, -1, ARCH_W, ARCH_SPRING)
        if i == 1:
            arch_face(cx, 1, ARC_W, ARC_H + LAND)
            det(yprism(halfdisc(cx, ARC_H + LAND, ARC_W // 2, 10), HY - 4, HY, TEX_GLASS))
        else:
            arch_face(cx, 1, ARCH_W, ARCH_SPRING)

    # Entablature band round the room over the column tops.
    for s in (-1, 1):
        y0, y1 = (HY - 4 * FT, HY) if s > 0 else (-HY, -HY + 4 * FT)
        det(box(-HX, y0, ENT_Z0, HX, y1, ENT_Z1, TEX_TRIM))
        x0, x1 = (HX - 4 * FT, HX) if s > 0 else (-HX, -HX + 4 * FT)
        det(box(x0, -HY + 4 * FT, ENT_Z0, x1, HY - 4 * FT, ENT_Z1, TEX_TRIM))

    # Giant Corinthian columns (blockout: pedestal, 12-sided shaft, capital block) at the
    # bay piers and the room corners. The detail pass replaces them with MDL models.
    cols = [(x, s * (HY - 13 * FT)) for x in (BAYS[1], BAYS[2]) for s in (-1, 1)]
    cols += [(sx * (HX - 6 * FT), sy * (HY - 13 * FT)) for sx in (-1, 1) for sy in (-1, 1)]
    for cx, cy in cols:
        det(box(cx - 66, cy - 66, 0, cx + 66, cy + 66, PED, TEX_TRIM))
        ents.append(ent("prop_static", (cx, cy, PED), model="models/penn/corinthian.mdl", solid="6"))
        # The entablature breaks forward over every column.
        wy = HY if cy > 0 else -HY
        det(box(cx - 7 * FT, min(wy, cy - 6 * FT * (1 if cy < 0 else -1)), ENT_Z0,
                cx + 7 * FT, max(wy, cy - 6 * FT * (1 if cy < 0 else -1)), ENT_Z1, TEX_TRIM))
        # Pier behind the column: a pilaster strip of the wall up to the entablature.
        wy = HY if cy > 0 else -HY
        if abs(cx) < HX - 8 * FT:
            det(box(cx - 8 * FT, min(wy, wy - 7 * FT * (1 if cy > 0 else -1)), 0,
                    cx + 8 * FT, max(wy, wy - 7 * FT * (1 if cy > 0 else -1)), ENT_Z0, TEX_WALL))

    # Lights (session 6). Daylight comes in through the thermal windows: the glass panes are texture
    # lights (src/lights.rad), morning sun from the east lunettes falls as light_spot shafts on the
    # floor of the west half, and a dim warm fill keeps the column shadows readable.
    for i in range(3):
        cx = (BAYS[i] + BAYS[i + 1]) // 2
        ents.append(ent("light", (cx, 0, SPRING), _light="235 220 195 35"))
        ents.append(ent("light", (cx, 0, 30 * FT), _light="250 220 180 18"))
        # Sun shaft: from just inside the east lunette, aimed down and west (pitch -50, yaw 270).
        ents.append(ent("light_spot", (cx, HY - 120, SPRING + 160), angles="-50 270 0", pitch="-50",
                        _light="255 236 200 260", _inner_cone="14", _cone="22", _exponent="1",
                        _constant_attn="1", _linear_attn="0", _quadratic_attn="0"))
        ents.append(ent("light", (cx, -(HY - 200), SPRING + 200), _light="195 210 235 25"))
    for s in (-1, 1):
        ents.append(ent("light", (s * (HX - 200), 0, SPRING + 200), _light="195 210 235 25"))
    ents.append(ent("light", (0, HY + T + 40 * FT, LAND + 20 * FT), _light="250 225 190 20"))

    NL = "\n"
    ents.append(ent("env_tonemap_controller", (0, 0, 64), targetname="tonemap"))
    conn = ['"OnMapSpawn" "tonemap,SetAutoExposureMin,0.6,0,-1"',
            '"OnMapSpawn" "tonemap,SetAutoExposureMax,1.6,0,-1"',
            '"OnMapSpawn" "tonemap,SetBloomScale,0.25,0,-1"']
    block = "\tconnections" + NL + "\t{" + NL + "".join("\t\t" + c + NL for c in conn) + "\t}" + NL + "}" + NL
    ents.append(ent("logic_auto", (0, 0, 96), spawnflags="1")[:-2] + block)
    ents.append(ent("info_player_start", (0, YB - 10 * FT, LAND + 8), angles="0 270 0"))
    ents.append(ent("info_player_start", (0, -300, 8), angles="0 0 0"))
    for x in (0, BAYS[1] - 600, BAYS[2] + 600):
        ents.append(ent("env_cubemap", (x, 0, 200)))

    world_s = ('world' + NL + '{' + NL + '\t"id" "%d"' + NL + '\t"mapversion" "1"' + NL + '\t"classname" "worldspawn"' + NL
               + '\t"skyname" "sky_day01_01"' + NL + '%s}' + NL) % (nid(), "".join(world))
    head = ('versioninfo' + NL + '{' + NL + '\t"editorversion" "400"' + NL + '\t"editorbuild" "8000"' + NL + '\t"mapversion" "1"' + NL
            + '\t"formatversion" "100"' + NL + '\t"prefab" "0"' + NL + '}' + NL)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(head + world_s + "".join(ents), encoding="ascii", newline=NL)
    print("wrote", OUT, _id[0], "ids")


if __name__ == "__main__":
    build()
