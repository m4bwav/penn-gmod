"""Build src/gm_grand_central.vmf from the measured layout (1 ft = 12 u).

Blockout stage: Main Concourse only. Run: python tools/build_vmf.py
"""
import math
from pathlib import Path

FT = 12
OUT = Path(__file__).resolve().parent.parent / "src" / "gm_grand_central.vmf"

# Main Concourse: 275 x 120 ft floor, vault crown ~125 ft. Long axis = x (east +x).
HX, HY = 275 * FT // 2, 120 * FT // 2      # 1650, 720
CROWN = 125 * FT                            # 1500
VRISE = 40 * FT                             # vault rise: a flattened half-ellipse, half-width HY
SPRING = CROWN - VRISE                      # springline (cornice) height
BAYS = 5                                    # bays along each long wall, one lunette each
WALL = 64
BALC_Z = 26 * FT                            # balcony floor height
BALC_D = 22 * FT                            # balcony depth from the end wall
BAY_Z0 = 42 * FT                            # bottom of the long-wall bay windows (photo estimate)
ARCH_W, ARCH_TOP, ARCH_D = 18 * FT, 21 * FT, 16 * FT   # floor arcade under each balcony
BARCH_W, BARCH_H = 14 * FT, 14 * FT        # balcony-level arcade behind each balcony

# src/materials/gcs: stock HL2 textures tinted to colours sampled from refs/photos.
TEX_FLOOR = "gcs/floor"
TEX_WALL = "gcs/wall"
TEX_VAULT = "gcs/vault"
TEX_TRIM = "gcs/trim"
TEX_GLOW = "gcs/window_glow"
TEX_GOLD = "gcs/gold"
TEX_RAIL = "gcs/brass_rail"          # darker worn brass for stair and balcony handrails
TEX_STAIR = "gcs/stair"              # cream marble dimmed for the stair treads and balustrades
TEX_GRID = "gcs/mullion"
TEX_DIM = "gcs/window_dim"
TEX_GLASS = "gcs/window_glass"  # pale pane grid for the big windows
TEX_CREAM = "gcs/cream"
TEX_CLOCK = "gcs/clock"
TEX_BULB = "gcs/bulb"
TEX_COFFER = "gcs/coffer"
TEX_DOOR = "gcs/door_glow"
TEX_SHAFT = "gcs/shaft"        # additive sun beam, nonsolid
NODRAW = "tools/toolsnodraw"

_id = [0]


def nid():
    _id[0] += 1
    return _id[0]


def sub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def dot(a, b): return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]


# Texture scale per material (default 0.25); smaller floor tiles read closer to the photos.
SCALE = {TEX_FLOOR: 0.1875,   # 512 px texture = 2x2 slabs of 4 ft
         TEX_WALL: 0.5,        # 8 courses x 4 blocks over 21 ft: 2.7 x 5.3 ft blocks
         TEX_COFFER: 0.375,    # 2x2 coffers over 16 ft
         TEX_CLOCK: 30/256}    # one 256 px dial per 30 u clock side
USHIFT = {TEX_CLOCK: 128}      # centre the dial on faces spanning -15..15

# Departure board over the ticket windows (faces +y) and the flag hung from the crown
# (faces +-x); both map their texture once over the front faces, the rest gets black/gold.
BOARD = (-20*FT, 20*FT, 17*FT, 27*FT)         # x0, x1, z0, z1: 40 x 10 ft, inside the centre bay
FLAG = (-24*FT, 24*FT, HY - 8*FT, HY - 8*FT + 2, SPRING - 33*FT, SPRING - 8*FT)   # x0, x1, y0, y1 (thin), z0, z1: north centre bay; 48 ft long (Gothamist), 1.9:1


def _board_uv(n):
    x0, x1, z0, z1 = BOARD
    su, sv = (x1-x0)/1024, (z1-z0)/256
    if n[1] > 0.5:
        return "[-1 0 0 %g] %g" % (x1/su, su), "[0 0 -1 %g] %g" % (z1/sv, sv)


def _flag_uv(n):
    x0, x1, _, _, z0, z1 = FLAG
    su, sv = (x1-x0)/512, (z1-z0)/256
    if abs(n[1]) > 0.5:
        s = -1 if n[1] > 0 else 1
        return "[%d 0 0 %g] %g" % (s, -s*(x0 if s > 0 else x1)/su, su), "[0 0 -1 %g] %g" % (z1/sv, sv)


def _tickets_uv(n):
    # One 1024 px strip per 16 ft window pitch; plaque centre (window x + 3 ft) lands on texel 512.
    su, sv = 16*FT/1024, 1.5*FT/64
    if n[1] > 0.5:
        return "[-1 0 0 704] %g" % su, "[0 0 -1 %g] %g" % (13.25*FT/sv, sv)


def _mk_sign_uv(n):
    # GRAND CENTRAL MARKET band in the market door head, read from the passage (+y) and the market (-y).
    su, sv = (MK_D1 - MK_D0)/1024, 20/64
    v = "[0 0 -1 %g] %g" % (MK_DOOR_H/sv, sv)
    if n[1] > 0.5:
        return "[-1 0 0 %g] %g" % (MK_D1/su, su), v
    if n[1] < -0.5:
        return "[1 0 0 %g] %g" % (-MK_D0/su, su), v


def _oysterbar_uv(n):
    # OYSTER BAR band hung in the gallery's west arch, y -120..120, faces +x.
    su, sv = 240/1024, 20/64
    if n[0] > 0.5:
        return "[0 1 0 %g] %g" % (120/su, su), "[0 0 -1 %g] %g" % ((LOW_Z + 134)/sv, sv)


FACEUV = {"gcs/facade_win": lambda n: ("[1 0 0 0] 0.375", "[0 0 -1 0] 0.5625"), "gcs/inscription": lambda n: _ext_uv(n, "ins"), "gcs/clock_out": lambda n: _ext_uv(n, "clock"),
          "gcs/pershing": lambda n: _ext_uv(n, "pershing"),
          "gcs/oysterbar": _oysterbar_uv, "gcs/mk_sign": _mk_sign_uv, "gcs/board": _board_uv, "gcs/flag": _flag_uv, "gcs/tickets": _tickets_uv}


def axes_for(n, s=0.25):
    ax = max(range(3), key=lambda i: abs(n[i]))
    if ax == 2:
        return "[1 0 0 0] %g" % s, "[0 -1 0 0] %g" % s
    if ax == 0:
        return "[0 1 0 0] %g" % s, "[0 0 -1 0] %g" % s
    return "[1 0 0 0] %g" % s, "[0 0 -1 0] %g" % s


def side(pts, n, tex, uv=None):
    p1, p2, p3 = pts[0], pts[1], pts[2]
    # Source plane winding: outward normal = (p3-p1) x (p2-p1)
    if dot(cross(sub(p3, p1), sub(p2, p1)), n) < 0:
        p2, p3 = p3, p2
    f = lambda p: "(%g %g %g)" % p
    uv = uv or (FACEUV[tex](n) if tex in FACEUV else None)
    u, v = uv or axes_for(n, SCALE.get(tex, 0.25))
    if not uv and tex == TEX_CLOCK and abs(n[2]) < 0.5 and n[0] - n[1] < 0:
        u = u.replace("[0 1 0", "[0 -1 0").replace("[1 0 0", "[-1 0 0")   # unmirror -x and +y dials
    if not uv and tex in USHIFT:
        u = u.replace(" 0] ", " %g] " % USHIFT[tex])
    return ('\tside\n\t{\n\t\t"id" "%d"\n\t\t"plane" "%s %s %s"\n\t\t"material" "%s"\n'
            '\t\t"uaxis" "%s"\n\t\t"vaxis" "%s"\n\t\t"rotation" "0"\n\t\t"lightmapscale" "16"\n'
            '\t\t"smoothing_groups" "0"\n\t}\n') % (nid(), f(p1), f(p2), f(p3), tex, u, v)


def prism(poly, z0, z1, tex, caps=None):
    """Convex polygon in xy (counter-clockwise), extruded z0..z1."""
    caps = caps or tex
    s = side([(x, y, z1) for x, y in poly], (0, 0, 1), caps)
    s += side([(x, y, z0) for x, y in poly], (0, 0, -1), caps)
    for i in range(len(poly)):
        a, b = poly[i], poly[(i+1) % len(poly)]
        n = (b[1]-a[1], -(b[0]-a[0]), 0)
        s += side([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1)], n, tex)
    return "solid\n{\n\t\"id\" \"%d\"\n%s}\n" % (nid(), s)


def xprism(poly, x0, x1, tex, uvs=None):
    """Convex polygon in yz (counter-clockwise seen from +x), extruded x0..x1.
    uvs: optional {edge index: (uaxis, vaxis)} for the face on that edge."""
    s = side([(x1, y, z) for y, z in poly], (1, 0, 0), tex)
    s += side([(x0, y, z) for y, z in poly], (-1, 0, 0), tex)
    for i in range(len(poly)):
        a, b = poly[i], poly[(i+1) % len(poly)]
        n = (0, b[1]-a[1], -(b[0]-a[0]))
        s += side([(x0, a[0], a[1]), (x0, b[0], b[1]), (x1, b[0], b[1])], n, tex, (uvs or {}).get(i))
    return "solid\n{\n\t\"id\" \"%d\"\n%s}\n" % (nid(), s)


def yprism(poly, y0, y1, tex, uv=None, ends=None):
    """Convex polygon in xz (counter-clockwise seen from -y), extruded y0..y1.
    uv: one (u, v) for every face; ends: material for the two y faces (default tex)."""
    s = side([(x, y0, z) for x, z in poly], (0, -1, 0), ends or tex, uv)
    s += side([(x, y1, z) for x, z in poly], (0, 1, 0), ends or tex, uv)
    for i in range(len(poly)):
        a, b = poly[i], poly[(i+1) % len(poly)]
        n = (b[1]-a[1], 0, -(b[0]-a[0]))
        s += side([(a[0], y0, a[1]), (b[0], y0, b[1]), (b[0], y1, b[1])], n, tex, uv)
    return "solid\n{\n\t\"id\" \"%d\"\n%s}\n" % (nid(), s)


def halfdisc(cx, z0, r, n=10):
    return [(round(cx + r*math.cos(math.pi*i/n)), round(z0 + r*math.sin(math.pi*i/n))) for i in range(n+1)]


def ccw(poly):
    a = sum(poly[i][0]*poly[(i+1) % len(poly)][1] - poly[(i+1) % len(poly)][0]*poly[i][1] for i in range(len(poly)))
    return poly if a > 0 else poly[::-1]


def box(x0, y0, z0, x1, y1, z1, tex):
    return prism([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, tex)


def ngon(cx, cy, r, n, rot=0.0):
    return [(round(cx + r*math.cos(rot + 2*math.pi*i/n)), round(cy + r*math.sin(rot + 2*math.pi*i/n))) for i in range(n)]


def ent(cls, origin=None, solids="", **kv):
    kv = {"classname": cls, **kv}
    if origin:
        kv["origin"] = "%g %g %g" % origin
    body = "".join('\t"%s" "%s"\n' % (k, v) for k, v in kv.items())
    return "entity\n{\n\t\"id\" \"%d\"\n%s%s}\n" % (nid(), body, solids)



def arcade_bay(W, ents, sgn, xin, xout, c, z0, r, top, roof, ramp=False, open_=False):
    """One arched opening in an end wall (z0..top, half-width r) and its lit passage.
    ramp: the opening leads to a ramp down to the dining concourse (lower_level builds it)."""
    xa, xb = sorted((xin, xout))
    arc = halfdisc(c, top - r, r, 8)
    for i in range(8):
        corner = (c + r, top) if i < 4 else (c - r, top)
        ents.append(ent("func_detail", solids=xprism(ccw([corner, arc[i], arc[i+1]]), xa, xb, TEX_WALL)))
    # Cream archivolt proud of the wall, on cream jambs.
    fa, fb = sorted((xin, xin - sgn*8))
    outer, inner = halfdisc(c, top - r, r + 18), halfdisc(c, top - r, r)
    for i in range(len(outer)-1):
        ents.append(ent("func_detail", solids=xprism(ccw([outer[i], outer[i+1], inner[i+1], inner[i]]), fa, fb, TEX_CREAM)))
    for y0 in (c - r - 18, c + r):
        ents.append(ent("func_detail", solids=box(fa, y0, z0, fb, y0 + 18, top - r, TEX_CREAM)))
    if ramp:
        return
    # Passage behind, sealed: warm cream corridor ending in lit glass doors with brass frames.
    pa, pb = sorted((xout, xout + sgn*ARCH_D))
    W(box(pa, c - r - WALL, z0 - WALL, pb, c + r + WALL, z0, TEX_FLOOR))
    W(box(pa, c - r - WALL, top, pb, c + r + WALL, top + roof, TEX_CREAM))
    W(box(pa, c - r - WALL, z0, pb, c - r, top, TEX_CREAM))
    W(box(pa, c + r, z0, pb, c + r + WALL, top, TEX_CREAM))
    # Cream barrel vault over the passage, continuing the opening's arch.
    for i in range(8):
        corner = (c + r, top) if i < 4 else (c - r, top)
        ents.append(ent("func_detail", solids=xprism(ccw([corner, arc[i], arc[i+1]]), pa, pb, TEX_CREAM)))
    xback = xout + sgn*ARCH_D
    lx = sgn*(HX + WALL + ARCH_D//2)
    if open_:   # the back opens on a passage built elsewhere (lex_passage)
        ents.append(ent("func_detail", solids=box(lx - 1, c - 1, top - 30, lx + 1, c + 1, top, TEX_GOLD)))
        ents.append(ent("func_detail", solids=box(lx - 8, c - 8, top - 44, lx + 8, c + 8, top - 30, TEX_BULB)))
        ents.append(ent("light", (lx, c, top - 60), _light="255 205 140 40"))
        return
    ba, bb = sorted((xback, xback + sgn*WALL))
    W(box(ba, c - r - WALL, z0 - WALL, bb, c + r + WALL, top + WALL, TEX_DOOR))
    # Brass door frames: posts, transom bar and a header panel over the doors.
    fa2, fb2 = sorted((xback, xback - sgn*6))
    for yy in (c - r, c - 3*FT, c + 3*FT - 6, c + r - 6, c - 6, c):
        ents.append(ent("func_detail", solids=box(fa2, yy, z0, fb2, yy + 6, top, TEX_GRID)))
    ents.append(ent("func_detail", solids=box(fa2, c - r, z0 + 8*FT, fb2, c + r, z0 + 8*FT + 6, TEX_GRID)))
    ents.append(ent("func_detail", solids=box(fa2, c - r, z0 + 12*FT, fb2, c + r, top, TEX_CREAM)))
    # Pendant lamp.
    lx = sgn*(HX + WALL + ARCH_D//2)
    ents.append(ent("func_detail", solids=box(lx - 1, c - 1, top - 30, lx + 1, c + 1, top, TEX_GOLD)))
    ents.append(ent("func_detail", solids=box(lx - 8, c - 8, top - 44, lx + 8, c + 8, top - 30, TEX_BULB)))
    ents.append(ent("light", (lx, c, top - 60), _light="255 205 140 40"))
    ents.append(ent("light", (xback - sgn*24, c, z0 + 6*FT), _light="255 190 120 20"))


# Lower level (area 2). The Oyster Bar ramps flank the west staircase, run west under the
# balcony through the side arches and land at the Whispering Gallery; the Oyster Bar opens
# off its west side, and a corridor runs back east to the dining concourse under the floor.
LOW_Z = -22 * FT                    # dining level floor
RAMP_X0, RAMP_XF = -1100, -2684     # ramp head in the concourse floor, ramp foot (slope ~1:6)
RAMP_Y0, RAMP_Y1 = 300, 480         # ramp well, |y|; inside the side arches (264..480)
COR_Y = 168                         # half-width of the corridor between the ramps
GAL_X0 = RAMP_XF - 50 * FT          # Whispering Gallery, 50 ft square
OB_X1 = GAL_X0 - WALL
OB_X0 = OB_X1 - 4 * 288             # Oyster Bar, four 24 ft bays by four
DIN_X0, DIN_X1, DIN_Y = -1000, 1000, 600   # dining concourse under the main floor
EAST_D = 40 * FT                    # east ramp landing hall depth
TEX_TILE = "gcs/guastavino"
TEX_WOOD = "gcs/wood"
TEX_PALE = "gcs/guastavino_pale"   # Whispering Gallery glaze
TEX_LOWF = "gcs/floor_low"         # darker mauve-grey tile floor of the lower level
TEX_GALF = "gcs/floor_gal"         # Whispering Gallery floor, lighter and warmer (session 57, photo)


def groin(W, x0, x1, y0, y1, zs, rise, tex, n=8):
    """Groin vault over x0..x1, y0..y1 springing at zs: the solid is the intersection of two
    crossing barrels' solids, so the plan splits along the diagonals into four triangles and
    each triangle follows the barrel whose arch stands on its wall. n even. World brushes."""
    top = zs + rise + 16
    yc, hy, xc, hx = (y0+y1)/2, (y1-y0)/2, (x0+x1)/2, (x1-x0)/2
    a = [math.pi*i/n for i in range(n+1)]
    for axis in (0, 1):                      # 0: triangles on the x walls, profile across y
        c, h, oc, oh = (yc, hy, xc, hx) if axis == 0 else (xc, hx, yc, hy)
        prof = [(c + h*math.cos(t), zs + rise*math.sin(t)) for t in a]
        for sgn in (-1, 1):                  # wall at oc + sgn*oh
            for i in range(n):
                (u0, z0), (u1, z1) = prof[i], prof[i+1]
                # Diagonal: |v - oc|/oh = |u - c|/h; the strip runs from the wall to it.
                d0, d1 = oh*abs(u0 - c)/h, oh*abs(u1 - c)/h
                uv = [(u0, oc + sgn*oh), (u1, oc + sgn*oh), (u1, oc + sgn*d1), (u0, oc + sgn*d0)]
                if abs(d0 - oh) < 1e-6:
                    uv.pop(3)
                elif abs(d1 - oh) < 1e-6:
                    uv.pop(2)
                poly =ccw([(v, u) for u, v in uv]) if axis == 0 else ccw(list(uv))
                s = (z1 - z0) / (u1 - u0)
                zf = (lambda x, y, u0=u0, z0=z0, s=s: z0 + s*((y if axis == 0 else x) - u0))
                nb = (0, s, -1) if axis == 0 else (s, 0, -1)
                W(_slab(poly, zf, nb, top, tex))
    W(box(x0, y0, top, x1, y1, top + WALL, tex))


def _slab(poly, zf, nb, top, tex):
    """Convex xy polygon (ccw) from the plane z = zf(x, y) (outward normal nb) up to top."""
    r = lambda v: round(v, 2)
    s = side([(r(x), r(y), top) for x, y in poly], (0, 0, 1), tex)
    s += side([(r(x), r(y), r(zf(x, y))) for x, y in poly], nb, tex)
    for i in range(len(poly)):
        a, b = poly[i], poly[(i+1) % len(poly)]
        n = (b[1]-a[1], -(b[0]-a[0]), 0)
        s += side([(r(a[0]), r(a[1]), r(zf(*a))), (r(b[0]), r(b[1]), r(zf(*b))), (r(b[0]), r(b[1]), top)], n, tex)
    return "solid\n{\n\t\"id\" \"%d\"\n%s}\n" % (nid(), s)


def lower_level(W, ents):
    det = lambda s: ents.append(ent("func_detail", solids=s))
    Z, H = LOW_Z, 216
    # Ramps, one each side: a sloped floor slab, walls, rails round the well in the
    # concourse, and past the end wall a sloping Guastavino-tiled soffit.
    for e, s in ((e, s) for e in (1, -1) for s in (-1, 1)):   # e=-1 mirrors to the east end
        X = lambda x: e*x
        B = lambda x0, y0, z0, x1, y1, z1, t: box(min(X(x0), X(x1)), y0, z0, max(X(x0), X(x1)), y1, z1, t)
        P = lambda poly: ccw([(X(x), z) for x, z in poly])
        ya, yb = sorted((s*RAMP_Y0, s*RAMP_Y1))
        W(yprism(P([(RAMP_X0, 0), (RAMP_XF, Z), (RAMP_XF, Z - WALL), (RAMP_X0, -WALL)]), ya, yb, TEX_FLOOR))
        ia, ib = sorted((s*COR_Y, s*RAMP_Y0))
        oa, ob = sorted((s*RAMP_Y1, s*(RAMP_Y1 + WALL)))
        for wa, wb in ((ia, ib), (oa, ob)):
            W(B(-HX, wa, Z - WALL, RAMP_X0, wb, 0, TEX_CREAM))
            W(B(RAMP_XF, wa, Z - WALL, -HX, wb, ARCH_TOP, TEX_CREAM))
        x1 = -HX - WALL
        W(yprism(P([(x1, ARCH_TOP), (RAMP_XF, Z + H), (RAMP_XF, Z + H + WALL), (x1, ARCH_TOP + WALL)]), ya, yb, TEX_TILE))
        # Cream parapets with brass rails on the floor round the well.
        for ra, rb in (sorted((s*(RAMP_Y0 - 16), s*RAMP_Y0)), sorted((s*RAMP_Y1, s*(RAMP_Y1 + 16)))):
            det(B(-HX, ra, 0, RAMP_X0, rb, 42, TEX_CREAM))
            det(B(-HX, ra - 2, 42, RAMP_X0, rb + 2, 46, TEX_GOLD))
        det(B(RAMP_X0, ya, 0, RAMP_X0 + 16, yb, 42, TEX_CREAM))
        det(B(RAMP_X0 - 2, ya, 42, RAMP_X0 + 18, yb, 46, TEX_GOLD))
        for k in range(4):
            x = round(-HX - WALL - 100 - k*(-HX - WALL - 100 - RAMP_XF)/3.5)
            t = (x - RAMP_X0) / (RAMP_XF - RAMP_X0)
            ents.append(ent("light", (X(x), s*(RAMP_Y0+RAMP_Y1)//2, Z*t + 150), _light="255 205 150 30"))
    # East ramp foot: a cream landing hall (EAST_D deep) with a flat coffered ceiling; its
    # west side opens on a corridor back to the dining concourse, as the west ramps do.
    ex0, ex1, ey = -RAMP_XF, -RAMP_XF + EAST_D, RAMP_Y1
    W(box(ex0, -ey, Z - WALL, ex1, ey, Z, TEX_LOWF))
    W(box(ex0, -ey, Z + H, ex1, ey, 0, TEX_COFFER))     # tops at 0: Lexington Passage runs above
    W(box(ex1, -ey, Z - WALL, ex1 + WALL, ey, 0, TEX_CREAM))
    for s in (-1, 1):
        ya, yb = sorted((s*ey, s*(ey + WALL)))
        W(box(ex0, ya, Z - WALL, ex1 + WALL, yb, 0, TEX_CREAM))
        # Wall between ramp foot and corridor, up to the landing ceiling.
        wa, wb = sorted((s*COR_Y, s*RAMP_Y0))
        W(box(ex0 - WALL, wa, Z + H - 8, ex0, wb, 0, TEX_CREAM))
    W(box(ex0 - WALL, -COR_Y, Z + H - 8, ex0, COR_Y, 0, TEX_CREAM))
    # Brass-framed lit doors to the platforms (sealed until area 4) on the landing's east wall.
    for c in (-200, 0, 200):
        det(box(ex1 - 6, c - 60, Z, ex1, c + 60, Z + 132, TEX_GRID))
        det(box(ex1 - 8, c - 52, Z, ex1 - 6, c + 52, Z + 124, TEX_DOOR))
    for y in (-240, 0, 240):
        det(box(ex0 + EAST_D//2 - 8, y - 8, Z + H - 30, ex0 + EAST_D//2 + 8, y + 8, Z + H - 14, TEX_BULB))
        ents.append(ent("light", (ex0 + EAST_D//2, y, Z + H - 60), _light="255 210 160 40"))
    ents.append(ent("env_cubemap", (ex0 + EAST_D//2, 0, Z + 72)))
    W(box(DIN_X1 + WALL, -COR_Y, Z - WALL, ex0, COR_Y, Z, TEX_LOWF))
    W(box(DIN_X1 + WALL, -COR_Y, -WALL - 16, ex0 - WALL, COR_Y, 0, TEX_CREAM))
    for s in (-1, 1):
        wa, wb = sorted((s*COR_Y, s*RAMP_Y0))
        W(box(DIN_X1 + WALL, wa, Z - WALL, HX, wb, -WALL, TEX_CREAM))
    for x in range(DIN_X1 + 160, ex0, 320):
        ents.append(ent("light", (x, 0, -110), _light="255 210 160 25"))
    # Corridor between the ramps from the gallery east to the dining concourse.
    W(box(RAMP_XF, -COR_Y, Z - WALL, DIN_X0, COR_Y, Z, TEX_LOWF))
    W(box(RAMP_XF, -COR_Y, -WALL - 16, DIN_X0, COR_Y, 0, TEX_CREAM))
    for s in (-1, 1):
        wa, wb = sorted((s*COR_Y, s*RAMP_Y0))
        W(box(-HX, wa, Z - WALL, DIN_X0, wb, -WALL, TEX_CREAM))
    for x in range(RAMP_XF + 160, DIN_X0, 320):
        ents.append(ent("light", (x, 0, -110), _light="255 210 160 25"))

    # Whispering Gallery: a low groin vault of pale Guastavino tile where four arches meet,
    # each opening framed by a cream stone arch, brass handrails along the walls.
    gx0, gx1, gy = GAL_X0, RAMP_XF, RAMP_Y1
    W(box(gx0, -gy, Z - WALL, gx1, gy, Z, TEX_GALF))
    for s in (-1, 1):
        ya, yb = sorted((s*gy, s*(gy + WALL)))
        W(box(gx0 - WALL, ya, Z - WALL, gx1, yb, 64, TEX_PALE))
    # West side: a wide segmental stone arch into the Oyster Bar (session 58, photo), not a door.
    aw, asp, ar = 216, Z + 84, 96
    for y0, y1 in ((-gy, -aw), (aw, gy)):
        W(box(gx0 - WALL, y0, Z, gx0, y1, 64, TEX_PALE))
    for i in range(8):
        t0, t1 = math.pi*i/8, math.pi*(i+1)/8
        a = (round(aw*math.cos(t0)), round(asp + ar*math.sin(t0)))
        b = (round(aw*math.cos(t1)), round(asp + ar*math.sin(t1)))
        W(xprism(ccw([a, b, (b[0], 64), (a[0], 64)]), gx0 - WALL, gx0, TEX_PALE))
        a2 = (round((aw+24)*math.cos(t0)), round(asp + (ar+24)*math.sin(t0)))
        b2 = (round((aw+24)*math.cos(t1)), round(asp + (ar+24)*math.sin(t1)))
        det(xprism(ccw([a, b, b2, a2]), gx0, gx0 + 6, TEX_CREAM))
    for s in (-1, 1):
        ya, yb = sorted((s*aw, s*(aw + 24)))
        det(box(gx0, ya, Z, gx0 + 6, yb, asp, TEX_CREAM))
    zs, rise = Z + 10*FT, 9*FT
    groin(W, gx0, gx1, -gy, gy, zs, rise, TEX_PALE)
    # Cream stone ribs: a band of the arch profile 16 u deep along each wall face.
    gxc = (gx0 + gx1) / 2
    hx = (gx1 - gx0) / 2
    n = 8
    for x in (gx0 + 12, gx1 - 12):
        for i in range(n):
            t0, t1 = math.pi*i/n, math.pi*(i+1)/n
            a = (round(gy*math.cos(t0)), round(zs + rise*math.sin(t0)))
            b = (round(gy*math.cos(t1)), round(zs + rise*math.sin(t1)))
            a2 = (round((gy-30)*math.cos(t0)), round(zs + (rise-30)*math.sin(t0)))
            b2 = (round((gy-30)*math.cos(t1)), round(zs + (rise-30)*math.sin(t1)))
            det(xprism(ccw([a2, b2, b, a]), x - 12, x + 12, TEX_CREAM))
    for y in (-gy + 12, gy - 12):
        for i in range(n):
            t0, t1 = math.pi*i/n, math.pi*(i+1)/n
            a = (round(gxc + hx*math.cos(t0)), round(zs + rise*math.sin(t0)))
            b = (round(gxc + hx*math.cos(t1)), round(zs + rise*math.sin(t1)))
            a2 = (round(gxc + (hx-30)*math.cos(t0)), round(zs + (rise-30)*math.sin(t0)))
            b2 = (round(gxc + (hx-30)*math.cos(t1)), round(zs + (rise-30)*math.sin(t1)))
            det(yprism(ccw([a2, b2, b, a]), y - 12, y + 12, TEX_CREAM))
    # Cream piers in the four corners carry the ribs down to the floor.
    for x in (gx0, gx1 - 28):
        for y in (-gy, gy - 28):
            det(box(x, y, Z, x + 28, y + 28, zs, TEX_CREAM))
    # Brass handrail on short posts along the solid walls (y = +-gy) between the piers.
    for s in (-1, 1):
        y = s*(gy - 6)
        det(box(gx0 + 40, y - 2, Z + 34, gx1 - 40, y + 2, Z + 37, TEX_GOLD))
        for x in range(gx0 + 60, gx1 - 40, 96):
            det(box(x - 1, y - 1, Z + 4, x + 1, y + 1, Z + 34, TEX_GOLD))
    # One lamp at the crown and warm fill under each arch.
    det(box(gxc - 1, -1, zs + rise - 40, gxc + 1, 1, zs + rise + 2, TEX_GOLD))
    det(prism(ngon(gxc, 0, 10, 8, math.pi/8), zs + rise - 58, zs + rise - 40, TEX_BULB))
    ents.append(ent("light", (round(gxc), 0, zs + rise - 76), _light="250 230 205 120"))
    for x, y in ((gxc, gy - 120), (gxc, -gy + 120), (gx0 + 120, 0), (gx1 - 120, 0)):
        ents.append(ent("light", (round(x), y, Z + 90), _light="250 232 210 45"))
    ents.append(ent("env_cubemap", (round(gxc), 0, Z + 72)))
    # OYSTER BAR band hung in the arch on two brass rods.
    det(box(gx0 - 4, -120, asp + 30, gx0 + 4, 120, asp + 50, "gcs/oysterbar"))
    for y in (-100, 100):
        det(box(gx0 - 1, y - 1, asp + 50, gx0 + 1, y + 1, asp + ar - 4, TEX_GOLD))

    # Oyster Bar: 4 x 4 bays of shallow Guastavino groins on piers; a long oak counter.
    bx, by = 288, 240
    oy = 2*by
    W(box(OB_X0, -oy, Z - WALL, OB_X1, oy, Z, TEX_LOWF))
    for s in (-1, 1):
        ya, yb = sorted((s*oy, s*(oy + WALL)))
        W(box(OB_X0 - WALL, ya, Z - WALL, OB_X1, yb, 64, TEX_CREAM))
    W(box(OB_X0 - WALL, -oy, Z - WALL, OB_X0, oy, 64, TEX_CREAM))
    zs = Z + 11*FT
    for i in range(4):
        for j in range(4):
            x0, y0 = OB_X0 + i*bx, -oy + j*by
            groin(W, x0, x0 + bx, y0, y0 + by, zs, 6*FT, TEX_TILE)
            ents.append(ent("light", (x0 + bx//2, y0 + by//2, zs - 40), _light="255 195 130 45"))
            det(box(x0 + bx//2 - 1, y0 + by//2 - 1, zs - 10, x0 + bx//2 + 1, y0 + by//2 + 1, zs + 70, TEX_GOLD))
            det(prism(ngon(x0 + bx//2, y0 + by//2, 8, 8, math.pi/8), zs - 22, zs - 10, TEX_BULB))
    for i in range(1, 4):
        for j in range(1, 4):
            x, y = OB_X0 + i*bx, -oy + j*by
            det(box(x - 14, y - 14, Z, x + 14, y + 14, zs + 20, TEX_TILE))
    # Counter: oak top on a cream marble base, running down the middle with stools.
    cx0, cx1 = OB_X0 + 96, OB_X1 - 192
    det(box(cx0, -30, Z, cx1, 30, Z + 40, TEX_CREAM))
    det(box(cx0 - 6, -38, Z + 40, cx1 + 6, 38, Z + 43, TEX_WOOD))
    for x in range(cx0 + 24, cx1, 48):
        for y in (-56, 56):
            det(prism(ngon(x, y, 2, 6), Z, Z + 24, TEX_GOLD))
            det(prism(ngon(x, y, 8, 8, math.pi/8), Z + 24, Z + 28, TEX_WOOD))
    # Wall counters: oak-topped cream counters along both long walls, stools in front.
    for sg in (-1, 1):
        ya, yb = sorted((sg*oy, sg*(oy - 30)))
        det(box(OB_X0 + 48, ya, Z, OB_X1 - 96, yb, Z + 40, TEX_CREAM))
        ya, yb = sorted((sg*oy, sg*(oy - 38)))
        det(box(OB_X0 + 42, ya, Z + 40, OB_X1 - 90, yb, Z + 43, TEX_WOOD))
        for x in range(OB_X0 + 72, OB_X1 - 96, 48):
            y = sg*(oy - 58)
            det(prism(ngon(x, y, 2, 6), Z, Z + 24, TEX_GOLD))
            det(prism(ngon(x, y, 8, 8, math.pi/8), Z + 24, Z + 28, TEX_WOOD))
    ents.append(ent("env_cubemap", ((OB_X0+OB_X1)//2, -200, Z + 72)))

    # Dining concourse under the main floor: cream walls, pylons, lit shop fronts round
    # the edge and a small brass-topped lower information booth in the middle.
    W(box(DIN_X0, -DIN_Y, Z - WALL, DIN_X1, DIN_Y, Z, TEX_FLOOR))
    W(box(DIN_X0, -DIN_Y, -WALL - 16, DIN_X1, DIN_Y, -WALL, TEX_COFFER))
    W(box(DIN_X0 - WALL, -DIN_Y - WALL, Z - WALL, MD_X0 - WALL, -DIN_Y, 0, TEX_CREAM))   # south wall, cut by the
    W(box(MD_X1 + WALL, -DIN_Y - WALL, Z - WALL, DIN_X1 + WALL, -DIN_Y, 0, TEX_CREAM))   # Madison escalator gate
    W(box(MD_X0 - WALL, -DIN_Y - WALL, Z + 16 * FT, MD_X1 + WALL, -DIN_Y, 0, TEX_CREAM))
    W(box(MD_X0 - WALL, -DIN_Y - WALL, Z - WALL, MD_X1 + WALL, -DIN_Y, Z, TEX_LOWF))
    ned = [DIN_X0 - WALL] + [e for gx, _ in LGATES for e in (gx - GATE_W//2, gx + GATE_W//2)] + [DIN_X1 + WALL]
    for j in range(0, len(ned), 2):
        W(box(ned[j], DIN_Y, Z - WALL, ned[j + 1], DIN_Y + WALL, 0, TEX_CREAM))
    for gx, _ in LGATES:
        W(box(gx - GATE_W//2, DIN_Y, LC, gx + GATE_W//2, DIN_Y + WALL, 0, TEX_CREAM))
    for y0, y1 in ((-DIN_Y, -COR_Y), (COR_Y, DIN_Y)):
        W(box(DIN_X1, y0, Z - WALL, DIN_X1 + WALL, y1, 0, TEX_CREAM))
    for y0, y1 in ((-DIN_Y, -COR_Y), (COR_Y, DIN_Y)):
        W(box(DIN_X0 - WALL, y0, Z - WALL, DIN_X0, y1, 0, TEX_CREAM))
    # Shop glass (make_board.py din_shop): 1024 px per 240 u pitch, 180 u window at px 0..767,
    # glass z Z+12..Z+110 (north faces -y: +x right; south faces +y: -x right).
    xs, su, sv = DIN_X0 + 70, 240 / 1024, 98 / 512
    FACEUV["gcs/din_shop_n"] = lambda n: ("[1 0 0 %g] %g" % (-xs / su, su), "[0 0 -1 %g] %g" % ((Z + 110) / sv, sv))
    FACEUV["gcs/din_shop_s"] = lambda n: ("[-1 0 0 %g] %g" % ((xs + 180) / su, su), "[0 0 -1 %g] %g" % ((Z + 110) / sv, sv))
    # Pylon plinths and moulded capitals (gold band under a cream flare), in one func_brush.
    pyl = []
    for x in range(DIN_X0 + 160, DIN_X1 - 100, 240):
        for y in (-320, 320):
            pyl.append(box(x - 20, y - 20, Z, x + 20, y + 20, Z + 30, TEX_TRIM))
            pyl.append(box(x - 19, y - 19, -WALL - 64, x + 19, y + 19, -WALL - 58, TEX_GOLD))
            pyl.append(box(x - 22, y - 22, -WALL - 58, x + 22, y + 22, -WALL - 40, TEX_CREAM))
    # Lower information booth (like the real one): stone octagon with a marble counter,
    # a brass-framed glass ring with posts at the corners, gold cornice and a stone cap
    # under the brass clock column. In din_decor, so it costs no world vertices.
    oc = lambda r: ngon(0, 0, r, 8, math.pi/8)
    bp = lambda poly, z0, z1, tex: pyl.append(prism(poly, z0, z1, tex))
    bp(oc(7*FT + 3), Z, Z + 6, TEX_TRIM)
    bp(oc(7*FT), Z + 6, Z + 40, TEX_CREAM)
    bp(oc(7*FT + 5), Z + 40, Z + 44, TEX_CREAM)
    bp(oc(7*FT + 3), Z + 44, Z + 46, TEX_GOLD)
    go, gi = oc(6.8*FT), oc(6.7*FT)
    for i in range(8):
        a, b = go[i], go[(i+1) % 8]
        bp(ccw([a, b, gi[(i+1) % 8], gi[i]]), Z + 46, Z + 92, "gcs/booth_glass")
        bp(ngon(a[0], a[1], 4, 4, math.pi/4), Z + 46, Z + 92, TEX_GOLD)
        mx, my = (a[0] + b[0])/2, (a[1] + b[1])/2
        bp(ngon(mx, my, 2, 4, math.pi/4), Z + 46, Z + 92, TEX_GOLD)
    bp(oc(5*FT), Z + 46, Z + 92, TEX_CREAM)
    bp(oc(7*FT + 4), Z + 92, Z + 96, TEX_GOLD)
    bp(oc(7*FT + 1), Z + 96, Z + 104, TEX_CREAM)
    bp(oc(5*FT), Z + 104, Z + 110, TEX_CREAM)
    bp(oc(2*FT), Z + 110, Z + 113, TEX_GOLD)
    for s_ in (-1, 1):
        ents.append(ent("light", (0, s_*6*FT, Z + 80), _light="255 220 160 20"))
    ents.append(ent("func_brush", solids="".join(pyl), targetname="din_decor", Solidity="2",
                    disableshadows="1", vrad_brush_cast_shadows="1"))
    for x in range(DIN_X0 + 160, DIN_X1 - 100, 240):
        for s in (-1, 1):
            if s > 0 and any(abs(x - gx) < 90 + GATE_W//2 + 16 for gx, _ in LGATES):
                continue
            if s < 0 and MD_X0 - 110 < x < MD_X1 + 110:
                continue
            ya, yb = sorted((s*(DIN_Y - 4), s*DIN_Y))
            det(box(x - 90, ya, Z + 12, x + 90, yb, Z + 110, "gcs/din_shop_%s" % ("n" if s > 0 else "s")))
            det(box(x - 90, ya, Z + 120, x + 90, yb, Z + 140, TEX_GOLD))
        for y in (-320, 320):
            det(box(x - 16, y - 16, Z, x + 16, y + 16, -WALL - 16, TEX_CREAM))
        # Beams between the pylons; round brass lamps hung in the bays between them.
        det(box(x - 12, -DIN_Y, -WALL - 40, x + 12, DIN_Y, -WALL - 16, TEX_CREAM))
        for y in (-440, 0, 440):
            lx = x + 120
            if lx < DIN_X1 - 60:
                det(prism(ngon(lx, y, 18, 8, math.pi/8), -WALL - 30, -WALL - 16, TEX_GOLD))
                det(prism(ngon(lx, y, 14, 8, math.pi/8), -WALL - 38, -WALL - 30, TEX_BULB))
                ents.append(ent("light", (lx, y, -WALL - 60), _light="255 215 170 40"))
    for y in (-440, 0, 440):   # west end bay, so the first pylons are lit from both sides
        ents.append(ent("light", (DIN_X0 + 60, y, -WALL - 60), _light="255 215 170 30"))
    oct8 = lambda r: ngon(0, 0, r, 8, math.pi/8)
    # Brass column with a four-faced opal clock, like the one upstairs.
    det(prism(oct8(10), Z + 104, -150, TEX_GOLD))
    det(prism([(-15, -15), (15, -15), (15, 15), (-15, 15)], -150, -120, TEX_CLOCK, TEX_GOLD))
    det(prism(oct8(20), -120, -116, TEX_GOLD))
    det(prism(oct8(10), -116, -104, TEX_GOLD))
    ents.append(ent("env_cubemap", (0, -300, Z + 72)))


# Vanderbilt Hall (area 3): the old main waiting room south of the concourse, reached
# through a passage in the west bay of the south wall. Flat gilded-cornice ceiling, ashlar
# walls, tall grilled windows, five tiered chandeliers; the 42nd Street vestibule opens
# off its south wall and ends in lit doors (sealed until the exterior, area 5).
VH_PX0, VH_PX1 = -115 * FT, -102 * FT     # passage through the concourse south wall
VH_PH = 16 * FT                           # passage height
VH_Y1 = -HY - WALL - 24 * FT              # hall's inner north face
VH_Y0 = VH_Y1 - 64 * FT                   # hall 200 x 64 ft (estimate)
VH_X0, VH_X1 = -130 * FT, 70 * FT
VH_H = 56 * FT
VS_X0, VS_X1, VS_D = -40 * FT, -20 * FT, 24 * FT   # 42nd Street vestibule
# Transit Museum store (chamber 5): through Vanderbilt Hall's pedimented east door (stand-in for
# the real Shuttle Passage location; flagged). 40 x 30 ft, 14 ft: shelves, glass cases, a counter
# and the cab end of a vintage subway car on display.
TM_X0 = VH_X1 + WALL
TM_X1 = TM_X0 + 40 * FT
TM_H = 14 * FT


def vanderbilt(W, ents):
    # Decor goes into one func_brush: the world model is at vbsp's t-junction index cap (65536).
    decor = []
    det = decor.append
    # Hall shell.
    W(box(VH_X0, VH_Y0, -WALL, VH_X1, VH_Y1, 0, TEX_FLOOR))
    W(box(VH_X0, VH_Y0, VH_H, VH_X1, VH_Y1, VH_H + WALL, TEX_COFFER))
    W(box(VH_X0 - WALL, VH_Y0 - WALL, -WALL, VH_X0, VH_Y1 + WALL, VH_H + WALL, TEX_WALL))
    # East wall, cut by the doorway to the Transit Museum store (TM_*).
    _cy = (VH_Y0 + VH_Y1) // 2
    W(box(VH_X1, VH_Y0 - WALL, -WALL, VH_X1 + WALL, _cy - 6 * FT, VH_H + WALL, TEX_WALL))
    W(box(VH_X1, _cy + 6 * FT, -WALL, VH_X1 + WALL, VH_Y1 + WALL, VH_H + WALL, TEX_WALL))
    W(box(VH_X1, _cy - 6 * FT, 11 * FT, VH_X1 + WALL, _cy + 6 * FT, VH_H + WALL, TEX_WALL))
    W(box(VH_X1, _cy - 6 * FT, -WALL, VH_X1 + WALL, _cy + 6 * FT, 0, TEX_FLOOR))
    for (y0, y1), (g0, g1, gh) in (((VH_Y1, VH_Y1 + WALL), (VH_PX0, VH_PX1, VH_PH)),
                                   ((VH_Y0 - WALL, VH_Y0), (VS_X0, VS_X1, 20 * FT))):
        W(box(VH_X0, y0, -WALL, g0, y1, VH_H, TEX_WALL))
        W(box(g1, y0, -WALL, VH_X1, y1, VH_H, TEX_WALL))
        W(box(g0, y0, gh, g1, y1, VH_H, TEX_WALL))
        W(box(g0, y0, -WALL, g1, y1, 0, TEX_FLOOR))
    # Passage from the concourse: cream walls and ceiling, a lamp.
    py0, py1 = VH_Y1 + WALL, -HY - WALL
    W(box(VH_PX0, py0, -WALL, VH_PX1, py1, 0, TEX_FLOOR))
    W(box(VH_PX0 - WALL, py0, -WALL, VH_PX0, py1, VH_PH + WALL, TEX_CREAM))
    W(box(VH_PX1, py0, -WALL, VH_PX1 + WALL, py1, VH_PH + WALL, TEX_CREAM))
    W(box(VH_PX0, py0, VH_PH, VH_PX1, py1, VH_PH + WALL, TEX_CREAM))
    pc = (VH_PX0 + VH_PX1) // 2
    ents.append(ent("light", (pc, (py0 + py1) // 2, VH_PH - 40), _light="255 210 150 30"))
    # Cream jambs, lintel and gold edge framing both ends of the passage.
    for ya, yb in ((-HY, -HY + 12), (VH_Y1 - 12, VH_Y1)):
        for x0, x1 in ((VH_PX0 - 24, VH_PX0), (VH_PX1, VH_PX1 + 24)):
            det(box(x0, ya, 0, x1, yb, VH_PH, TEX_CREAM))
        det(box(VH_PX0 - 24, ya, VH_PH, VH_PX1 + 24, yb, VH_PH + 24, TEX_CREAM))
        det(box(VH_PX0 - 24, ya, VH_PH + 24, VH_PX1 + 24, yb, VH_PH + 30, TEX_GOLD))
    # Vestibule to 42nd Street with lit brass doors.
    vy1, vy0 = VH_Y0 - WALL, VH_Y0 - WALL - VS_D
    W(box(VS_X0, vy0, -WALL, VS_X1, vy1, 0, TEX_FLOOR))
    W(box(VS_X0 - WALL, vy0 - WALL, -WALL, VS_X0, vy1, 20 * FT + WALL, TEX_CREAM))
    W(box(VS_X1, vy0 - WALL, -WALL, VS_X1 + WALL, vy1, 20 * FT + WALL, TEX_CREAM))
    W(box(VS_X0, vy0, 20 * FT, VS_X1, vy1, 20 * FT + WALL, TEX_CREAM))
    # The vestibule's south wall is the 42nd Street facade (exterior()); its three doorways stand open.
    dw = (VS_X1 - VS_X0) // 3
    for k in range(3):
        x0 = VS_X0 + k * dw
        det(box(x0, vy0, 0, x0 + 12, vy0 + 8, 13 * FT, TEX_GOLD))
    det(box(VS_X1 - 12, vy0, 0, VS_X1, vy0 + 8, 13 * FT, TEX_GOLD))
    det(box(VS_X0, vy0, 12 * FT, VS_X1, vy0 + 8, 13 * FT, TEX_GOLD))
    det(box(VS_X0 + 12, vy0, 13 * FT, VS_X1 - 12, vy0 + 4, 19 * FT, TEX_DOOR))
    ents.append(ent("light", ((VS_X0 + VS_X1) // 2, vy0 + 120, 16 * FT), _light="255 215 160 40"))
    # Tall dark-green grilled windows on both long walls (dark glass behind a green iron grid), cream sills.
    for yw, s in ((VH_Y1, -1), (VH_Y0, 1)):
        for cx in range(VH_X0 + 30 * FT, VH_X1 - 20 * FT + 1, 40 * FT):
            if VH_PX0 - 10 * FT < cx < VH_PX1 + 10 * FT or VS_X0 - 10 * FT < cx < VS_X1 + 10 * FT:
                continue
            wz0, wz1, hw = 14 * FT, 50 * FT, 8 * FT
            ga, gb = sorted((yw, yw + s * 2))
            det(box(cx - hw, ga, wz0, cx + hw, gb, wz1, "gcs/vh_glass"))
            ma, mb = sorted((yw + s * 2, yw + s * 6))
            for j in range(-4, 5):
                det(box(cx + j * 24 - 2, ma, wz0, cx + j * 24 + 2, mb, wz1, "gcs/vh_grille"))
            for z in range(wz0, wz1 + 1, 36):
                det(box(cx - hw, ma, z - 2, cx + hw, mb, z + 2, "gcs/vh_grille"))
            fa, fb = sorted((yw, yw + s * 10))
            for x0, x1 in ((cx - hw - 8, cx - hw), (cx + hw, cx + hw + 8)):
                det(box(x0, fa, wz0, x1, fb, wz1 + 8, "gcs/vh_grille"))
            det(box(cx - hw - 8, fa, wz1, cx + hw + 8, fb, wz1 + 8, "gcs/vh_grille"))
            sa, sb = sorted((yw, yw + s * 18))
            det(box(cx - hw - 12, sa, wz0 - 12, cx + hw + 12, sb, wz0, TEX_CREAM))
    # Gilded cornice and cream frieze round the ceiling; marble dado at the foot of the walls.
    for d, z0, z1, tex in ((48, VH_H - 30, VH_H, TEX_GOLD), (24, VH_H - 72, VH_H - 30, TEX_CREAM)):
        det(box(VH_X0, VH_Y1 - d, z0, VH_X1, VH_Y1, z1, tex))
        det(box(VH_X0, VH_Y0, z0, VH_X1, VH_Y0 + d, z1, tex))
        det(box(VH_X0, VH_Y0 + d, z0, VH_X0 + d, VH_Y1 - d, z1, tex))
        det(box(VH_X1 - d, VH_Y0 + d, z0, VH_X1, VH_Y1 - d, z1, tex))
    for x0, y0, x1, y1 in ((VH_X0, VH_Y1 - 6, VH_PX0 - 24, VH_Y1), (VH_PX1 + 24, VH_Y1 - 6, VH_X1, VH_Y1),
                           (VH_X0, VH_Y0, VS_X0, VH_Y0 + 6), (VS_X1, VH_Y0, VH_X1, VH_Y0 + 6),
                           (VH_X0, VH_Y0 + 6, VH_X0 + 6, VH_Y1 - 6),
                           (VH_X1 - 6, VH_Y0 + 6, VH_X1, (VH_Y0 + VH_Y1) // 2 - 6 * FT),   # stops at the store door
                           (VH_X1 - 6, (VH_Y0 + VH_Y1) // 2 + 6 * FT, VH_X1, VH_Y1 - 6)):
        det(box(x0, y0, 0, x1, y1, 8 * FT, TEX_CREAM))
    # Each end wall carries a large moulded panel frame (cream, gold inner bead) above the door height.
    for xw, s in ((VH_X0, 1), (VH_X1, -1)):
        fa, fb = sorted((xw, xw + s * 6))
        ga, gb = sorted((xw, xw + s * 8))
        y0, y1, z0, z1 = VH_Y0 + 14 * FT, VH_Y1 - 14 * FT, 22 * FT, VH_H - 10 * FT
        for b in ((y0, z0, y0 + 10, z1), (y1 - 10, z0, y1, z1), (y0, z0, y1, z0 + 10), (y0, z1 - 10, y1, z1)):
            det(box(fa, b[0], b[1], fb, b[2], b[3], TEX_CREAM))
        for b in ((y0 + 10, z0 + 10, y0 + 12, z1 - 10), (y1 - 12, z0 + 10, y1 - 10, z1 - 10),
                  (y0 + 10, z0 + 10, y1 - 10, z0 + 12), (y0 + 10, z1 - 12, y1 - 10, z1 - 10)):
            det(box(ga, b[0], b[1], gb, b[2], b[3], TEX_GOLD))
    # East end: a doorway with a carved cream pediment, lit glass doors behind.
    ex, cy = VH_X1, (VH_Y0 + VH_Y1) // 2
    for y0, y1 in ((cy - 8 * FT, cy - 6 * FT), (cy + 6 * FT, cy + 8 * FT)):
        det(box(ex - 24, y0, 0, ex - 6, y1, 13 * FT, TEX_CREAM))
    det(box(ex - 30, cy - 9 * FT, 13 * FT, ex - 6, cy + 9 * FT, 15 * FT, TEX_CREAM))
    det(box(ex - 36, cy - 9 * FT, 15 * FT, ex - 6, cy + 9 * FT, 15 * FT + 4, TEX_GOLD))
    det(xprism(ccw([(cy - 4 * FT, 15 * FT + 4), (cy + 4 * FT, 15 * FT + 4), (cy, 20 * FT)]), ex - 26, ex - 6, TEX_CREAM))
    # Five chandeliers down the centre: models/gcs/vh_chandelier.mdl from tools/make_models.py.
    for k in range(5):
        x = VH_X0 + (2 * k + 1) * (VH_X1 - VH_X0) // 10
        zc = VH_H - 30 * FT
        ents.append(ent("prop_static", (x, cy, zc), model="models/gcs/vh_chandelier.mdl", angles="0 0 0", solid="0", disableshadows="1", disablevertexlighting="0"))
        ents.append(ent("light", (x, cy, zc - 90), _light="255 220 170 45"))
    ents.append(ent("light", ((VH_X0 + VH_X1) // 2, cy, VH_H - 60), _light="255 225 180 15"))
    ents.append(ent("env_cubemap", ((VH_X0 + VH_X1) // 2, cy, 160)))
    ents.append(ent("env_cubemap", (pc, (py0 + py1) // 2, 100)))
    ents.append(ent("func_brush", solids="".join(decor), targetname="vh_decor", Solidity="2",
                    disableshadows="1", vrad_brush_cast_shadows="1"))


# The exterior (area 5): the 42nd Street facade through the Vanderbilt vestibule doors
# (photo: 42nd_Street_Facade_Grand_Central_Terminal_October_2025). Three great arched windows
# between paired columns, oval windows over the narrow bays, entablature, attic with the
# GRAND CENTRAL TERMINAL inscription, the Tiffany clock under the Glory of Commerce group
# (Mercury, Hercules, Minerva) on top; a balustraded terrace with a stair at the east end;
# the Park Avenue Viaduct crossing 42nd Street at the west end; office towers round the
# street and the MetLife tower behind; sky above (toolsskybox, light_environment).
VEST_Y0 = VH_Y0 - WALL - VS_D               # vestibule inner south face
YF = VEST_Y0 - WALL                         # facade face (faces -y)
FCX = (VS_X0 + VS_X1) // 2                  # facade axis = vestibule axis = hall centre
FHW = 160 * FT                              # facade half-width (estimate)
FX0, FX1 = FCX - FHW, FCX + FHW
RZ = 134 * FT                               # attic top / roof
SKYZ = 320 * FT
SW = 30 * FT                                # sidewalk depth
YS = YF - 110 * FT                          # face of the towers across 42nd Street
EX0, EX1 = FCX - 230 * FT, FCX + 230 * FT   # street ends
RN = 120 * FT                               # roof behind the facade, north of YF
TER_Z, TER_D = 24 * FT, 10 * FT             # terrace top and depth
WIN = (-80 * FT, 0, 80 * FT)                # great windows (x offsets), 33 ft wide
WIN_HW, WIN_Z0 = 198, 28 * FT
WIN_SP = WIN_Z0 + 60 * FT - WIN_HW          # arch springline: windows 60 ft tall
PAIRS = (-116 * FT, -40 * FT, 40 * FT, 116 * FT)
VIA_X0, VIA_X1 = FX0, FX0 + 34 * FT         # Park Avenue Viaduct deck
CLK_R, CLK_Z = 78, RZ + 15 * FT             # 13 ft clock
PX0, PX1 = VIA_X0 - 6 * FT, VIA_X1 + 6 * FT  # Pershing Square portal under the tower across 42nd St
PZ = TER_Z + 20 * FT                        # portal head
PD = 90 * FT                                # depth of the pocket behind it
PY0 = YS - PD                               # pocket back wall face


def _ext_uv(n, which):
    if which == "pershing":
        su, sv = 40 * FT / 1024, 3 * FT / 64
        if n[1] > 0.5:
            return "[-1 0 0 %g] %g" % ((PX0 + PX1) / 2 / su + 512, su), "[0 0 -1 %g] %g" % ((PZ + 5 * FT) / sv, sv)
        return None
    if n[1] > -0.5:
        return None
    if which == "ins":
        x0, x1, z1, w, h = FCX - 40 * FT, FCX + 40 * FT, 120 * FT, 1024, 128
        su, sv = (x1 - x0) / w, 10 * FT / h
    else:
        x0, z1, su = FCX - CLK_R, CLK_Z + CLK_R, 2 * CLK_R / 512
        sv = su
    return "[1 0 0 %g] %g" % (-x0 / su, su), "[0 0 -1 %g] %g" % (z1 / sv, sv)


def _arch_ring(cx, zs, r0, r1, y0, y1, tex, n=12):
    out = []
    for i in range(n):
        a, b = math.pi * i / n, math.pi * (i + 1) / n
        q = [(cx + r1 * math.cos(a), zs + r1 * math.sin(a)), (cx + r1 * math.cos(b), zs + r1 * math.sin(b)),
             (cx + r0 * math.cos(b), zs + r0 * math.sin(b)), (cx + r0 * math.cos(a), zs + r0 * math.sin(a))]
        out.append(yprism(ccw([(round(x), round(z)) for x, z in q]), y0, y1, tex))
    return out


def exterior(W, ents):
    decor = []
    det = decor.append
    STONE, GRILLE, GLASS, WINTEX = "gcs/facade_stone", "gcs/vh_grille", "gcs/vh_glass", "gcs/facade_win"
    # Facade wall with the vestibule doorway; roof slab behind the attic.
    W(box(FX0, YF, -WALL, VS_X0, VEST_Y0, RZ - WALL, STONE))
    W(box(VS_X1, YF, -WALL, FX1, VEST_Y0, RZ - WALL, STONE))
    W(box(VS_X0, YF, 20 * FT, VS_X1, VEST_Y0, RZ - WALL, STONE))
    W(box(VS_X0, YF, -WALL, VS_X1, VEST_Y0, 0, TEX_FLOOR))
    W(box(FX0, YF, RZ - WALL, FX1, YF + RN, RZ, STONE))
    W(box(FX0, YF + RN, RZ - WALL, FX1, YF + RN + WALL, SKYZ, "tools/toolsskybox"))
    # Street: sidewalks either side of the roadway, a double yellow centre line.
    W(box(EX0, YF - SW, -WALL, EX1, YF, 0, "gcs/sidewalk"))
    W(box(EX0, YS, -WALL, EX1, YS + 20 * FT, 0, "gcs/sidewalk"))
    W(box(EX0, YS + 20 * FT, -WALL, EX1, YF - SW, -8, "gcs/asphalt"))
    ym = (YS + 20 * FT + YF - SW) // 2
    for y in (ym - 8, ym + 4):
        det(box(EX0, y, -8, EX1, y + 4, -7, "gcs/plat_edge"))
    # Towers: across the street (glass, pale precast, glass), at both street ends, beside the terminal.
    for x0, x1, tex in ((EX0, PX0, "gcs/office"), (PX1, FCX - 70 * FT, "gcs/office"),
                        (FCX - 70 * FT, FCX + 60 * FT, "gcs/metlife"), (FCX + 60 * FT, EX1, "gcs/office")):
        W(box(x0, YS - WALL, -WALL, x1, YS, SKYZ, tex))
    W(box(PX0, YS - WALL, PZ, PX1, YS, SKYZ, "gcs/office"))
    W(box(EX0 - WALL, YS - WALL, -WALL, EX0, YF + RN + WALL, SKYZ, "gcs/office"))
    W(box(EX1, YS - WALL, -WALL, EX1 + WALL, YF + RN + WALL, SKYZ, "gcs/office"))
    W(box(EX0, YF, -WALL, FX0, YF + RN + WALL, SKYZ, "gcs/office"))
    W(box(FX1, YF, -WALL, EX1, YF + RN + WALL, SKYZ, "gcs/metlife"))
    W(box(EX0 - WALL, YS - WALL, SKYZ, EX1 + WALL, YF + RN + WALL, SKYZ + WALL, "tools/toolsskybox"))
    W(box(FCX - 100 * FT, YF + 60 * FT, RZ, FCX + 100 * FT, YF + 110 * FT, SKYZ, "gcs/metlife"))   # MetLife
    # Terrace along the facade at the windows' foot, with a stair down to the sidewalk at the east end.
    W(box(FX0, YF - TER_D, TER_Z - 2 * FT, FX1, YF, TER_Z, STONE))
    W(box(FX0, YF - TER_D, 0, VS_X0, YF, TER_Z - 2 * FT, STONE))          # solid under the terrace, open at the door
    W(box(VS_X1, YF - TER_D, 0, FX1 - 32 * FT, YF, TER_Z - 2 * FT, STONE))
    sx = FX1 - 4
    for k in range(24):
        W(box(sx - (k + 1) * 14, YF - TER_D - 8 * FT, 0, sx - k * 14, YF - TER_D, (k + 1) * 12, STONE))
    W(box(sx - 24 * 14, YF - TER_D, 0, sx, YF, TER_Z - 2 * FT, STONE))
    by0, by1 = YF - TER_D, YF - TER_D + 8
    for x0, x1 in ((FX0, VIA_X0), (VIA_X1, sx - 24 * 14 - 8)):
        if x1 <= x0:
            continue
        det(box(x0, by0, TER_Z, x1, by1, TER_Z + 6, STONE))
        det(box(x0, by0 - 2, TER_Z + 36, x1, by1 + 2, TER_Z + 42, STONE))
        det(box(x0, by0 + 2, TER_Z + 6, x1, by1 - 2, TER_Z + 36, STONE))   # solid balustrade: the BSP is near its vertex cap
    det(box(FX0, YF - TER_D - 4, TER_Z - 2 * FT, FX1, YF - TER_D, TER_Z, STONE))   # terrace fascia
    det(box(FX0, YF - 12, 0, FX1, YF, 3 * FT, STONE))                              # plinth
    # Great arched windows: dark glass, green iron grid, stone archivolt, jambs and keystone.
    for dx in WIN:
        cx = FCX + dx
        hw, z0, zs = WIN_HW, WIN_Z0, WIN_SP
        det(yprism(ccw([(cx - hw, z0), (cx + hw, z0)] + halfdisc(cx, zs, hw, 8)[:-1] + [(cx - hw, zs)]), YF - 2, YF, WINTEX))
        for d in _arch_ring(cx, zs, hw, hw + 30, YF - 12, YF, STONE, 8):
            det(d)
        for x0, x1 in ((cx - hw - 30, cx - hw), (cx + hw, cx + hw + 30)):
            det(box(x0, YF - 12, z0, x1, YF, zs, STONE))
        det(box(cx - hw - 36, YF - 16, z0 - 18, cx + hw + 36, YF, z0, STONE))         # sill
        det(box(cx - 20, YF - 18, zs + hw - 6, cx + 20, YF, zs + hw + 40, STONE))      # keystone
    # Paired fluted columns (12-sided) on bases, capitals under the entablature; oval and
    # tall windows between the inner pairs.
    for px in PAIRS:
        for dx in (-6 * FT, 6 * FT):
            x, y = FCX + px + dx, YF - 30
            det(box(x - 38, y - 38, TER_Z, x + 38, YF, TER_Z + 18, STONE))
            det(prism(ngon(x, y, 30, 8, math.pi / 8), TER_Z + 18, 86 * FT, STONE))
            det(box(x - 40, y - 40, 86 * FT, x + 40, YF, 90 * FT, STONE))
        if abs(px) < 60 * FT:
            cx = FCX + px
            ell = [(round(cx + 48 * math.cos(2 * math.pi * i / 10)), round(70 * FT + 66 * math.sin(2 * math.pi * i / 10))) for i in range(10)]
            rim = [(round(cx + 62 * math.cos(2 * math.pi * i / 10)), round(70 * FT + 80 * math.sin(2 * math.pi * i / 10))) for i in range(10)]
            det(yprism(ccw(rim), YF - 6, YF, STONE))
            det(yprism(ccw(ell), YF - 8, YF - 6, GLASS))
            det(box(cx - 48, YF - 2, 32 * FT, cx + 48, YF, 58 * FT, WINTEX))
            det(box(cx - 60, YF - 10, 58 * FT, cx + 60, YF, 59 * FT, STONE))
    # Entablature, cornice, attic band, inscription panel, top cornice.
    det(box(FX0, YF - 4 * FT, 90 * FT, FX1, YF, 100 * FT, STONE))
    det(box(FX0, YF - 7 * FT, 100 * FT, FX1, YF, 104 * FT, STONE))
    det(box(FX0, YF - 2 * FT, 104 * FT, FX1, YF, 126 * FT, STONE))
    det(box(FCX - 40 * FT, YF - 2 * FT - 4, 110 * FT, FCX + 40 * FT, YF - 2 * FT, 120 * FT, "gcs/inscription"))
    det(box(FX0, YF - 4 * FT, 126 * FT, FX1, YF, RZ, STONE))
    # Glory of Commerce: pedestal and the clock in a stone surround; the figures are a model.
    det(box(FCX - 34 * FT, YF - 4 * FT, RZ, FCX + 34 * FT, YF + 24 * FT, RZ + 8 * FT, STONE))
    det(yprism(ccw([(FCX - 11 * FT, RZ + 8 * FT), (FCX + 11 * FT, RZ + 8 * FT)] + halfdisc(FCX, RZ + 16 * FT, 11 * FT, 10)[:-1]
                   + [(FCX - 11 * FT, RZ + 16 * FT)]), YF - 3 * FT, YF + 10 * FT, STONE))
    det(yprism(ngon_xz(FCX, CLK_Z, CLK_R + 6, 20), YF - 3 * FT - 4, YF - 3 * FT, "gcs/gold"))
    det(yprism(ngon_xz(FCX, CLK_Z, CLK_R, 20), YF - 3 * FT - 8, YF - 3 * FT - 4, "gcs/clock_out"))
    # Figures as one model (make_models.py statue_group): brushes cost too many vertices.
    ents.append(ent("prop_static", (FCX, YF + 3 * FT, RZ + 8 * FT), model="models/gcs/statue_group.mdl",
                    angles="0 -90 0", solid="0", disableshadows="1"))   # studiomdl turns SMD +x to model +y
    # Bronze eagles on the facade's top corners (make_models.py eagle).
    for x in (FX0 + 6 * FT, FX1 - 6 * FT):
        ents.append(ent("prop_static", (x, YF - 2 * FT, RZ), model="models/gcs/eagle.mdl",
                        angles="0 -90 0", solid="0", disableshadows="1"))
    # Yellow cabs on 42nd Street (make_models.py taxi), both directions.
    for dx, y, yaw in ((-170, 62, 90), (-20, 62, 90), (150, 62, 90), (-90, 36, -90), (100, 36, -90)):
        ents.append(ent("prop_static", (FCX + dx * FT, YS + y * FT, -8), model="models/gcs/taxi.mdl",
                        angles="0 %d 0" % yaw, solid="6"))
    # Park Avenue Viaduct crossing 42nd Street: deck at terrace level, arched steel fascias,
    # bronze railings, a lit portal into the building across the street.
    W(box(VIA_X0, YS, TER_Z - 4 * FT, VIA_X1, YF - TER_D, TER_Z, "gcs/sidewalk"))
    n, ya, yb = 10, YS, YF - TER_D
    for x0, x1 in ((VIA_X0 - 10, VIA_X0), (VIA_X1, VIA_X1 + 10)):
        for i in range(n):
            y0, y1 = ya + (yb - ya) * i // n, ya + (yb - ya) * (i + 1) // n
            zb = lambda y: round(TER_Z - 4 * FT - 6 * FT * math.sin(math.pi * (y - ya) / (yb - ya)))
            det(xprism(ccw([(y0, zb(y0)), (y1, zb(y1)), (y1, TER_Z - 2 * FT), (y0, TER_Z - 2 * FT)]), x0, x1, "gcs/steel"))
        det(box(x0, ya, TER_Z - 2 * FT, x1, yb, TER_Z, "gcs/gold"))
    for x in (VIA_X0 + 4, VIA_X1 - 4):
        det(box(x - 3, ya, TER_Z + 38, x + 3, yb, TER_Z + 42, "gcs/bronze"))
        det(box(x - 1, ya, TER_Z, x + 1, yb, TER_Z + 38, "gcs/vh_grille"))
    ents.append(ent("light", ((VIA_X0 + VIA_X1) // 2, YS + 100, TER_Z + 8 * FT), _light="255 215 160 60"))
    pershing(W, ents, det)
    # Street lamps along the north kerb.
    for k in range(-3, 4):
        x, y = FCX + k * 60 * FT + 30 * FT, YF - SW + 24
        if not (FX0 - 10 * FT < x < EX1 - 10 * FT) or VIA_X0 - 4 * FT < x < VIA_X1 + 4 * FT:
            continue
        det(prism(ngon(x, y, 5, 8), 0, 20 * FT, GRILLE))
        det(prism(ngon(x, y, 12, 8), 20 * FT, 21 * FT, GRILLE))
        det(prism(ngon(x, y, 9, 8), 19 * FT - 10, 20 * FT, TEX_BULB))
        ents.append(ent("light", (x, y, 18 * FT), _light="255 235 200 40"))
    ents.append(ent("light_environment", (FCX, YS + 40 * FT, 60 * FT), angles="0 75 0", pitch="-42",
                    _light="255 248 236 420", _ambient="160 180 215 220"))
    ents.append(ent("env_cubemap", (FCX, YF - 50 * FT, 6 * FT)))
    ents.append(ent("env_cubemap", ((VIA_X0 + VIA_X1) // 2, YF - 50 * FT, TER_Z + 6 * FT)))
    ents.append(ent("func_brush", solids="".join(decor), targetname="ext_decor", Solidity="2",
                    disableshadows="1", vrad_brush_cast_shadows="1"))


# Pershing Square portal (2026-11-24): the viaduct runs on south through a stone-framed opening
# in the building across 42nd Street and ramps down toward Pershing Square; under the deck at
# street level the Pershing Square Cafe's lit storefront. A pocket 90 ft deep, sealed at the
# far end by a dark tunnel mouth (photo: Park_Avenue_Viaduct_Pershing_Square, estimates).
def pershing(W, ents, det):
    STONE, BRICK = "gcs/facade_stone", "gcs/wall"
    cx = (VIA_X0 + VIA_X1) // 2
    # Pocket shell: floor, side walls, ceiling, back wall.
    W(box(PX0, PY0, -WALL, PX1, YS, 0, "gcs/sidewalk"))
    W(box(PX0 - WALL, PY0 - WALL, -WALL, PX0, YS - WALL, PZ + WALL, BRICK))
    W(box(PX1, PY0 - WALL, -WALL, PX1 + WALL, YS - WALL, PZ + WALL, BRICK))
    W(box(PX0, PY0, PZ, PX1, YS - WALL, PZ + WALL, "gcs/coffer"))
    W(box(PX0, PY0 - WALL, -WALL, PX1, PY0, PZ, BRICK))
    # Deck ramps down 10 ft from the street bridge to the back wall (1:9).
    zt = lambda y: round(TER_Z - 10 * FT * (YS - y) / PD)
    W(xprism(ccw([(PY0, zt(PY0) - 4 * FT), (YS, TER_Z - 4 * FT), (YS, TER_Z), (PY0, zt(PY0))]), VIA_X0, VIA_X1, "gcs/sidewalk"))
    for x0, x1 in ((VIA_X0 - 10, VIA_X0), (VIA_X1, VIA_X1 + 10)):
        det(xprism(ccw([(PY0, zt(PY0) - 2 * FT), (YS, TER_Z - 2 * FT), (YS, TER_Z), (PY0, zt(PY0))]), x0, x1, "gcs/gold"))
        det(xprism(ccw([(PY0, zt(PY0) + 36), (YS, TER_Z + 36), (YS, TER_Z + 42), (PY0, zt(PY0) + 42)]), x0, x1, "gcs/bronze"))
    # Dark tunnel mouth over the deck end, lamps either side.
    det(box(VIA_X0 + 2 * FT, PY0, zt(PY0), VIA_X1 - 2 * FT, PY0 + 4, zt(PY0) + 14 * FT, "gcs/shed_dark"))
    for x in (VIA_X0 + FT, VIA_X1 - FT):
        det(prism(ngon(x, PY0 + 12, 8, 8), zt(PY0) + 15 * FT, zt(PY0) + 16 * FT, TEX_BULB))
    ents.append(ent("light", (cx, PY0 + 6 * FT, zt(PY0) + 12 * FT), _light="255 220 170 70"))
    # Wall lamps over the ramp: brass bracket globes on both side walls, a warm light each.
    for k in range(3):
        y = YS - (k + 1) * PD // 4
        for x, s in ((PX0, 1), (PX1, -1)):
            det(box(min(x, x + s * 16), y - 4, PZ - 8 * FT, max(x, x + s * 16), y + 4, PZ - 8 * FT + 6, "gcs/gold"))
            det(prism(ngon(x + s * 20, y, 7, 8), PZ - 8 * FT - 10, PZ - 8 * FT + 4, TEX_BULB))
            ents.append(ent("light", (x + s * 40, y, PZ - 9 * FT), _light="255 215 160 50"))
    # Pershing Square Cafe under the deck: lit glass storefront in brass frames, a bronze sign band.
    zf = zt(PY0) - 4 * FT - 16
    det(box(PX0 + 4 * FT, PY0, 0, PX1 - 4 * FT, PY0 + 2, zf - 3 * FT, TEX_DOOR))
    for k in range(7):
        x = PX0 + 4 * FT + (PX1 - PX0 - 8 * FT) * k // 6
        det(box(x - 4, PY0, 0, x + 4, PY0 + 6, zf - 3 * FT, "gcs/gold"))
    det(box(PX0 + 4 * FT, PY0, zf - 3 * FT, PX1 - 4 * FT, PY0 + 6, zf - 3 * FT + 10, "gcs/gold"))
    for k in range(3):
        ents.append(ent("light", (PX0 + (PX1 - PX0) * (k + 1) // 4, PY0 + 6 * FT, zf - 4 * FT), _light="255 200 140 45"))
    # Portal surround on the tower face: stone jambs, lintel with the bronze PERSHING SQUARE band, cornice.
    for x0, x1 in ((PX0 - 4 * FT, PX0), (PX1, PX1 + 4 * FT)):
        det(box(x0, YS, 0, x1, YS + 12, PZ, STONE))
    det(box(PX0 - 4 * FT, YS, PZ, PX1 + 4 * FT, YS + 12, PZ + 7 * FT, STONE))
    det(box(cx - 20 * FT, YS + 12, PZ + 2 * FT, cx + 20 * FT, YS + 14, PZ + 5 * FT, "gcs/pershing"))
    det(box(PX0 - 6 * FT, YS, PZ + 7 * FT, PX1 + 6 * FT, YS + 24, PZ + 8 * FT, STONE))
    ents.append(ent("env_cubemap", (cx, YS - PD // 2, TER_Z + 6 * FT)))


def ngon_xz(cx, cz, r, n):
    return ccw([(round(cx + r * math.cos(2 * math.pi * i / n)), round(cz + r * math.sin(2 * math.pi * i / n))) for i in range(n)])


# Upper-level track platforms (area 4). Three gates in the concourse north wall (bay centres)
# lead through short passages to a low dark train shed; tracks run north, three island
# platforms (rose tile, yellow edge), riveted steel columns, fluorescent strips; a Metro-North
# car stands open on the track west of the centre platform (photos: Grand_Central_Station_tracks,
# Metro_North_M7a_Rainbow_Heart_Sticker_Grand_Central).
GATES = ((-660, 29), (0, 30), (660, 31))   # gate x, track number on the sign
GATE_W, GATE_H = 12 * FT, 12 * FT
SH_Y0 = HY + WALL + 8 * FT                 # shed south face
SH_Y1 = SH_Y0 + 300 * FT                   # 300 ft of platform (real ones run ~800 ft)
SH_X = 85 * FT                             # shed half-width
SH_H = 18 * FT
PIT = 4 * FT                               # rail head below platform
HEAD = 20 * FT                             # cross-platform strip at the platform heads
PLATS = ((-780, -540), (-120, 120), (540, 780))
PITS = ((-SH_X, -780), (-540, -120), (120, 540), (780, SH_X))
TRACKS = (-900, -474, -186, 186, 474, 900)
CAR_X = (-246, -126)                       # walk-in car on track -186, 10 ft wide
CAR_Y0 = SH_Y0 + HEAD + 5 * FT
CAR_L = 85 * FT


def _sign_uv(gx, zt=180):
    def uv(n):
        su, sv = 96/512, 24/128
        if n[1] < -0.5:
            return "[1 0 0 %g] %g" % (-(gx - 48)/su, su), "[0 0 -1 %g] %g" % (zt/sv, sv)
    return uv


for _gx, _n in GATES:
    FACEUV["gcs/track%d" % _n] = _sign_uv(_gx)

# Lower-level track platforms (chamber 1 of the 60-session chain). Two gates in the dining
# concourse's north wall open on sloped passages down 44 u to a second shed under the
# upper one: same platform plan, lower and darker, ceiling just under the upper ballast pits.
LGATES = ((-480, 108), (480, 112))
LC = -PIT - WALL - 16                      # lower ceiling underside, -128 (under the upper pits)
LZ = LC - 15 * FT                          # lower platform top, -308: 15 ft clear (photos: 12-15 ft)
LSH_Y0 = DIN_Y + WALL + 40 * FT            # lower shed south face
for _gx, _n in LGATES:
    FACEUV["gcs/track%d" % _n] = _sign_uv(_gx, LC + 28)
# Track 61 (chamber 8): through the lower shed's north wall over the east platform and its two
# tracks, a dim fenced stretch running on to the freight elevator that took cars up to the hotel
# garage; an old steel car stands on Track 61 (refs: M42 photos only, no platform photo; layout is
# a flagged ruling: the real Track 61 lies in the Lex yard under the Waldorf, off the upper level).
T61_X0 = 300
T61_Y1 = SH_Y1 + WALL + 120 * FT


def pit_rail(W, ents, x0, x1, y, z):
    """Brass railing across a pit end as a model (no brush verts), with a player clip behind it."""
    ents.append(ent("prop_static", (x0, y, z), model="models/gcs/pit_rail_%d.mdl" % (x1 - x0),
                    angles="0 -90 0", solid="0", disableshadows="1"))
    W(box(x0, y - 2, z, x1, y + 2, z + 72, "tools/toolsplayerclip"))


def platforms(W, ents):
    # Decor goes into one func_brush (world model is at vbsp's t-junction cap).
    decor = []
    det = decor.append
    T_TILE, T_EDGE, T_DARK, T_STEEL = "gcs/plat_tile", "gcs/plat_edge", "gcs/shed_dark", "gcs/steel"
    # Shed shell: walls, dark ceiling, head strip, platforms, ballast pits.
    W(box(-SH_X, SH_Y0, SH_H, SH_X, SH_Y1, SH_H + WALL, T_DARK))
    W(box(-SH_X - WALL, SH_Y0, -PIT - WALL, -SH_X, SH_Y1, SH_H + WALL, T_DARK))
    W(box(SH_X, SH_Y0, -PIT - WALL, SH_X + WALL, SH_Y1, SH_H + WALL, T_DARK))
    W(box(-SH_X - WALL, SH_Y1, -PIT - WALL, SH_X + WALL, SH_Y1 + WALL, SH_H + WALL, T_DARK))
    W(box(-SH_X, SH_Y0, -PIT - WALL, SH_X, SH_Y0 + HEAD, 0, T_TILE))
    for x0, x1 in PLATS:
        W(box(x0, SH_Y0 + HEAD, -PIT - WALL, x1, SH_Y1, 0, T_TILE))
    for x0, x1 in PITS:
        W(box(x0, SH_Y0 + HEAD, -PIT - WALL, x1, SH_Y1, -PIT, "gcs/ballast"))
    # South wall of the shed and the gate passages through the concourse north wall.
    edges = [-SH_X - WALL] + [e for gx, _ in GATES for e in (gx - GATE_W//2, gx + GATE_W//2)] + [SH_X + WALL]
    for j in range(0, len(edges), 2):
        W(box(edges[j], HY + WALL, -WALL, edges[j + 1], SH_Y0, SH_H + WALL, TEX_CREAM))
    for gx, n in GATES:
        g0, g1 = gx - GATE_W//2, gx + GATE_W//2
        W(box(g0, HY + WALL, GATE_H, g1, SH_Y0, SH_H + WALL, TEX_CREAM))
        W(box(g0, HY, -WALL, g1, SH_Y0, 0, TEX_FLOOR))
        ents.append(ent("light", (gx, (HY + SH_Y0)//2, GATE_H - 30), _light="255 215 160 25"))
        # Brass gate frame and TRACK sign on the concourse face; the same sign hangs in the shed.
        det(box(g0 - 10, HY - 4, 0, g0, HY, GATE_H + 10, TEX_GOLD))
        det(box(g1, HY - 4, 0, g1 + 10, HY, GATE_H + 10, TEX_GOLD))
        det(box(g0, HY - 4, GATE_H, g1, HY, GATE_H + 10, TEX_GOLD))
        det(box(gx - 48, HY - 3, 156, gx + 48, HY, 180, "gcs/track%d" % n))
        sy = SH_Y0 + HEAD + 2 * FT
        det(box(gx - 48, sy, 156, gx + 48, sy + 3, 180, "gcs/track%d" % n))
        det(box(gx - 50, sy - 1, 180, gx + 50, sy + 4, 184, T_STEEL))
        det(box(gx - 2, sy, 184, gx + 2, sy + 3, SH_H, T_STEEL))
    # Brass railing round the pit ends, bumpers and rails.
    for x0, x1 in PITS:
        pit_rail(W, ents, x0, x1, SH_Y0 + HEAD, 0)
    for t in TRACKS:
        det(box(t - 40, SH_Y0 + HEAD, -PIT, t + 40, SH_Y0 + HEAD + 24, -12, T_STEEL))
        for r in (-30, 26):
            det(box(t + r, SH_Y0 + HEAD + 24, -PIT, t + r + 4, SH_Y1, -PIT + 6, T_STEEL))
    # Yellow edges, steel columns (platform centres and between paired tracks), cross beams,
    # fluorescent strips with cool lights.
    for x0, x1 in PLATS:
        det(box(x0, SH_Y0 + HEAD, 0, x0 + 24, SH_Y1, 1, T_EDGE))
        det(box(x1 - 24, SH_Y0 + HEAD, 0, x1, SH_Y1, 1, T_EDGE))
    beams = range(SH_Y0 + 30 * FT, SH_Y1, 30 * FT)
    for y in beams:
        det(box(-SH_X, y - 8, SH_H - 20, SH_X, y + 8, SH_H, T_STEEL))
        for cx, z0 in ((-660, 0), (0, 0), (660, 0), (-330, -PIT), (330, -PIT)):
            det(box(cx - 8, y - 8, z0, cx + 8, y + 8, SH_H - 20, T_STEEL))
    for x0, x1 in PLATS:
        cx = (x0 + x1) // 2
        for y in beams:
            for ox in (-60, 60):
                det(box(cx + ox - 4, y + 40, SH_H - 28, cx + ox + 4, y + 30 * FT - 40, SH_H - 22, "gcs/fluor"))
        for y in range(SH_Y0 + HEAD + 15 * FT, SH_Y1, 40 * FT):
            ents.append(ent("light", (cx, y, SH_H - 50), _light="235 240 255 45"))
        ents.append(ent("env_cubemap", (cx, SH_Y0 + 60 * FT, 64)))
    # Backlit ad boxes (make_board.py plat_ads, 72x144 u, tiling from world 0 so every box
    # starts on a multiple of 72): on both side walls between the beams, and one hanging over
    # each platform head facing the gates, as in Grand_Central_Station_tracks.jpg.
    ADS = ("gcs/ad_hudson", "gcs/ad_show", "gcs/ad_coffee", "gcs/ad_city")
    for a in ADS:
        FACEUV[a] = lambda n, s=72 / 256: (
            ("[0 %d 0 0] %g" % (1 if n[0] > 0 else -1, s), "[0 0 -1 %g] %g" % (192 / s, s))
            if abs(n[0]) > 0.5 else
            ("[%d 0 0 0] %g" % (-1 if n[1] > 0 else 1, s), "[0 0 -1 %g] %g" % (192 / s, s)))
    k = 0
    for y in beams:
        y0 = (y + 15 * FT - 36) // 72 * 72
        if y0 + 72 > SH_Y1 - 20:
            continue
        for sx in (-1, 1):
            xw = sx * SH_X
            det(box(min(xw, xw - sx * 6), y0 - 4, 44, max(xw, xw - sx * 6), y0 + 76, 196, T_STEEL))
            det(box(min(xw - sx * 6, xw - sx * 8), y0, 48, max(xw - sx * 6, xw - sx * 8), y0 + 72, 192,
                    ADS[k % 4]))
            k += 1
    for (x0, x1), a in zip(PLATS, ADS[1:]):
        bx = (x0 + 48) // 72 * 72 + 72                       # off-centre, clear of the sign
        hy = SH_Y0 + HEAD + 6 * FT
        det(box(bx - 4, hy - 1, 44, bx + 76, hy + 9, 196, T_STEEL))
        det(box(bx, hy - 3, 48, bx + 72, hy + 11, 192, a))
        for ox in (8, 64):
            det(box(bx + ox - 1, hy + 3, 196, bx + ox + 1, hy + 5, SH_H, T_STEEL))
    for y in range(SH_Y0 + 40 * FT, SH_Y1, 80 * FT):
        for x in (-330, 330, -900, 900):
            ents.append(ent("light", (x, y, SH_H - 60), _light="200 210 230 12"))
    # Metro-North cars: a walk-in car on track -186 with two open doors on the platform
    # side, benches and lights; a closed car coupled behind it and another on track 474.
    cx0, cx1 = CAR_X
    T_TR = "gcs/train"

    # Sides carry make_board.py train_side (windows, doors at L/4 and 3L/4, one car per
    # 1024 px); one material per car (train_a/b/c, same vtf) so each car's u starts at y0.
    def car(x0, x1, y0, y1, doors, side):
        FACEUV[side] = lambda n, su=CAR_L / 1024, sv=150 / 256: None if abs(n[0]) < 0.5 else (
            "[0 1 0 %g] %g" % (-y0 / su, su), "[0 0 -1 %g] %g" % (150 / sv, sv))
        det(box(x0, y0, -PIT + 8, x1, y1, 0, T_TR))                         # underframe
        det(box(x0 + 4, y0 + 4, 0, x1 - 4, y1 - 4, 1, "gcs/car_floor"))      # floor
        det(box(x0, y0, 150, x1, y1, 162, T_TR))                            # roof
        det(box(x0, y0, 0, x1, y0 + 4, 150, T_TR))                          # ends
        det(box(x0, y1 - 4, 0, x1, y1, 150, T_TR))
        for wx0, wx1, dd in ((x0, x0 + 4, ()), (x1 - 4, x1, doors)):
            cuts = [y0 + 4] + [e for d in dd for e in (d - 36, d + 36)] + [y1 - 4]
            for j in range(0, len(cuts), 2):
                det(box(wx0, cuts[j], 0, wx1, cuts[j + 1], 150, side))
            for d in dd:
                det(box(wx0, d - 36, 88, wx1, d + 36, 150, side))
    d1, d2 = CAR_Y0 + CAR_L // 4, CAR_Y0 + 3 * CAR_L // 4
    car(cx0, cx1, CAR_Y0, CAR_Y0 + CAR_L, (d1, d2), "gcs/train_a")
    car(cx0, cx1, CAR_Y0 + CAR_L + 24, CAR_Y0 + 2 * CAR_L + 24, (), "gcs/train_b")
    car(414, 534, CAR_Y0 + 10 * FT, CAR_Y0 + 10 * FT + CAR_L, (), "gcs/train_c")
    for y in range(CAR_Y0 + 60, CAR_Y0 + CAR_L - 40, 54):
        if any(abs(y - d) < 60 for d in (d1, d2)):
            continue
        for bx0, bx1 in ((cx0 + 4, cx0 + 44), (cx1 - 44, cx1 - 4)):
            det(box(bx0, y, 1, bx1, y + 20, 18, "gcs/vh_grille"))
            det(box(bx0, y + 20, 1, bx1, y + 26, 36, "gcs/vh_grille"))
    for y in (CAR_Y0 + 200, CAR_Y0 + CAR_L // 2, CAR_Y0 + CAR_L - 200):
        det(box(-190, y - 100, 146, -182, y + 100, 150, "gcs/fluor"))
        ents.append(ent("light", (-186, y, 120), _light="235 240 255 18"))
    ents.append(ent("func_brush", solids="".join(decor), targetname="plat_decor", Solidity="2",
                    disableshadows="1", vrad_brush_cast_shadows="1"))


def lower_tracks(W, ents):
    decor = []
    det = decor.append
    T_TILE, T_EDGE, T_DARK, T_STEEL = "gcs/plat_tile", "gcs/plat_edge", "gcs/shed_dark", "gcs/steel"
    Y0, Y1, Z0 = LSH_Y0, SH_Y1, LZ
    W(box(-SH_X - WALL, Y0 - WALL, LC, SH_X + WALL, Y1 + WALL, LC + 16, T_DARK))
    W(box(-SH_X - WALL, Y0, Z0 - PIT - WALL, -SH_X, Y1, LC, T_DARK))
    W(box(SH_X, Y0, Z0 - PIT - WALL, SH_X + WALL, Y1, LC, T_DARK))
    W(box(-SH_X - WALL, Y1, Z0 - PIT - WALL, T61_X0 - WALL, Y1 + WALL, LC, T_DARK))   # north wall, open
    W(box(T61_X0 - WALL, Y1, LC - 16, SH_X + WALL, Y1 + WALL, LC, T_DARK))            # on Track 61
    W(box(-SH_X, Y0, Z0 - PIT - WALL, SH_X, Y0 + HEAD, Z0, T_TILE))
    for x0, x1 in PLATS:
        W(box(x0, Y0 + HEAD, Z0 - PIT - WALL, x1, Y1, Z0, T_TILE))
    for x0, x1 in PITS:
        W(box(x0, Y0 + HEAD, Z0 - PIT - WALL, x1, Y1, Z0 - PIT, "gcs/ballast"))
    edges = [-SH_X - WALL] + [e for gx, _ in LGATES for e in (gx - GATE_W//2, gx + GATE_W//2)] + [SH_X + WALL]
    for j in range(0, len(edges), 2):
        W(box(edges[j], Y0 - WALL, Z0 - PIT - WALL, edges[j + 1], Y0, LC, T_DARK))
    # Sloped passages from the dining concourse, cream walls, flat ceiling.
    for gx, n in LGATES:
        g0, g1 = gx - GATE_W//2, gx + GATE_W//2
        W(xprism(ccw([(DIN_Y, LOW_Z), (Y0, Z0), (Y0, Z0 - WALL), (DIN_Y, LOW_Z - WALL)]), g0, g1, TEX_LOWF))
        W(box(g0, DIN_Y + WALL, LC, g1, Y0 - WALL, LC + 16, TEX_CREAM))
        for a, b in ((g0 - WALL, g0), (g1, g1 + WALL)):
            W(box(a, DIN_Y + WALL, Z0 - WALL, b, Y0 - WALL, LC + 16, TEX_CREAM))
        for k in (1, 3):
            ents.append(ent("light", (gx, DIN_Y + k*(Y0 - DIN_Y)//4, LC - 24), _light="255 215 160 20"))
        gy = DIN_Y + WALL + 48
        det(box(gx - 1, gy - 1, LC - 30, gx + 1, gy + 1, LC, TEX_GOLD))
        det(box(gx - 10, gy - 10, LC - 50, gx + 10, gy + 10, LC - 30, TEX_BULB))
        det(box(g0 - 10, DIN_Y - 4, LOW_Z, g0, DIN_Y, LC + 10, TEX_GOLD))
        det(box(g1, DIN_Y - 4, LOW_Z, g1 + 10, DIN_Y, LC + 10, TEX_GOLD))
        det(box(gx - 48, DIN_Y - 3, LC + 4, gx + 48, DIN_Y, LC + 28, "gcs/track%d" % n))
        sy = Y0 + HEAD + 2 * FT
        det(box(gx - 48, sy, LC - 44, gx + 48, sy + 3, LC - 20, "gcs/track%d" % n))
        det(box(gx - 2, sy, LC - 20, gx + 2, sy + 3, LC, T_STEEL))
    # Pit-end rails, bumpers, rails, yellow edges.
    for x0, x1 in PITS:
        pit_rail(W, ents, x0, x1, Y0 + HEAD, Z0)
    for t in TRACKS:
        det(box(t - 40, Y0 + HEAD, Z0 - PIT, t + 40, Y0 + HEAD + 24, Z0 - 12, T_STEEL))
        for r in (-30, 26):
            det(box(t + r, Y0 + HEAD + 24, Z0 - PIT, t + r + 4, Y1, Z0 - PIT + 6, T_STEEL))
    for x0, x1 in PLATS:
        det(box(x0, Y0 + HEAD, Z0, x0 + 24, Y1, Z0 + 1, T_EDGE))
        det(box(x1 - 24, Y0 + HEAD, Z0, x1, Y1, Z0 + 1, T_EDGE))
    # Riveted columns in rows along the platforms and between tracks, low beams, a single
    # fluorescent strip down each platform; dimmer and warmer than the upper shed.
    H = LC - Z0
    for y in range(Y0 + 30 * FT, Y1, 30 * FT):
        det(box(-SH_X, y - 8, LC - 20, SH_X, y + 8, LC, T_STEEL))
        for cx, z0 in ((-660, Z0), (0, Z0), (660, Z0), (-330, Z0 - PIT), (330, Z0 - PIT)):
            det(box(cx - 10, y - 10, z0, cx + 10, y + 10, LC - 20, T_STEEL))
    for x0, x1 in PLATS:
        cx = (x0 + x1) // 2
        det(box(cx - 4, Y0 + HEAD, LC - 28, cx + 4, Y1, LC - 22, "gcs/fluor"))
        for y in range(Y0 + HEAD + 15 * FT, Y1, 40 * FT):
            ents.append(ent("light", (cx, y, LC - 40), _light="230 235 250 35"))
        ents.append(ent("env_cubemap", (cx, Y0 + 60 * FT, Z0 + 64)))
    # A closed car standing on track 474.
    det(box(414, Y0 + HEAD + 10 * FT, Z0 - PIT + 8, 534, Y0 + HEAD + 10 * FT + CAR_L, Z0 + 150, "gcs/train"))
    ents.append(ent("func_brush", solids="".join(decor), targetname="low_decor", Solidity="2",
                    disableshadows="1", vrad_brush_cast_shadows="1"))


# Lexington Passage (chamber 2): the east floor arch's back opens on a shop-lined passage
# running east under the Graybar Building to lit Lexington Avenue doors. Width and height are
# estimates from photos (refs/SOURCES.md); shop fronts are lit glass under a dark sign band.
# Grand Central Madison (chamber 7): from a gate in the dining concourse's south wall, a 36 ft
# escalator bank drops 118 ft in two 30-degree runs with a mezzanine between (real banks run up
# to 180 ft and drop 90 ft each; Madison lies over 140 ft below Park Avenue: refs/concourse-
# dimensions.md) to a low modern concourse with an LIRR track edge. Runs south under Vanderbilt
# Hall and 42nd Street. Sizes besides the depth are estimates.
MD_X0, MD_X1 = -696, -264                  # shaft, 36 ft wide
MD_Y0 = -DIN_Y - WALL                      # gate, -664
MD_YA = MD_Y0 - 28 * FT                    # top of run 1
MD_DROP = 708                              # per run (59 ft)
MD_RUN = round(MD_DROP * 3 ** 0.5)         # 30 degrees
MD_YB = MD_YA - MD_RUN                     # foot of run 1 / mezzanine
MD_YC = MD_YB - 25 * FT                    # top of run 2
MD_YD = MD_YC - MD_RUN                     # foot of run 2, concourse north face
MD_Z = LOW_Z - 2 * MD_DROP                 # -1680: 140 ft below the main floor
MC_X0, MC_X1, MC_Y0 = -1080, 120, MD_YD - 67 * FT
MD_HEAD = 16 * FT
LEX_X0 = HX + WALL + ARCH_D                # 1906, back of the east centre arch
LEX_X1 = LEX_X0 + 200 * FT
LEX_Y = 13 * FT                            # half-width 156: clear of the east ramp walls (|y| 168)
LEX_H = 15 * FT                             # photos show 10-12 ft; 15 clears the 14 ft side doors
# Graybar Passage (chamber 2b): north off Lexington Passage, five groin-vaulted bays (photos:
# GCT_Graybar_Passage, Graybar_Passage_mural): cream vaults, buff walls, a brass chandelier per
# bay, glass kiosks down the middle, lit doors at the north end. 32 ft wide, crown 28 ft (estimates).
GB_X0, GB_X1 = LEX_X0 + 84 * FT, LEX_X0 + 116 * FT
GB_Y0 = LEX_Y + WALL
GB_BAY, GB_N = 32 * FT, 5
GB_Y1 = GB_Y0 + GB_N * GB_BAY
GB_ZS, GB_RISE = 16 * FT, 12 * FT
GB_TOP = GB_ZS + GB_RISE + 16
# The Campbell (chamber 4): John W. Campbell's office, now a bar, behind the west balcony's south
# arch (stand-in for the real stair up from the southwest corner; flagged). Photos: GCT_Campbell_1/3,
# Campbell_Apartment_nyc1. About 58 x 30 x 25 ft: dark beams painted ochre/red/green on gilt
# corbels, a big leaded window over the bar on the south wall, stone fireplace on the west wall.
CB_C = -31 * FT                            # the balcony arch's centre y
CB_X1 = -(HX + WALL + ARCH_D + WALL)       # room's inner east face, -1970
CB_X0 = CB_X1 - 690
CB_Y0, CB_Y1 = CB_C - 180, CB_C + 180
CB_Z, CB_H = BALC_Z, 25 * FT
# One Vanderbilt link (chamber 6): the west floor arch opens on a link west (|y| < LK_Y, clear of
# the ramp walls at |y| 168 and the Campbell's wall), an escalator run rising 20 ft over the
# Whispering Gallery, and a 30 ft lobby at its top with glass Vanderbilt Avenue doors (flagged
# ruling: the real link is a new hall reached from the concourse's west side; sizes estimated).
LK_X0 = -(HX + WALL + ARCH_D)              # -1906, back of the west centre arch
LK_E, LK_W = -2400, -2900                  # escalator foot and top
LK_Y, LK_ZT, LK_C = 120, 20 * FT, 35 * FT
LB_X0, LB_Y, LB_H = -3500, 300, 30 * FT
# Grand Central Market (chamber 3): a long hall south of Lexington Passage, entered by a door at
# its west end, Lexington Avenue doors at the east (photos: GCT_Market*, Grand_Central_Mart_Lex_Av).
# 240 x 28 ft, 15 ft flat ceiling rising to a shallow centre dome with a chandelier, open counters
# along both walls, drum pendants down the aisle (estimates). Starts east of the east ramp soffits.
# Grand Hyatt entrance (chamber 9): a door in Lexington Passage's north wall east of Graybar, a
# short stair up 6 ft, and a glass-roofed atrium lobby 60 x 60 x 40 ft (the Hyatt, once the
# Commodore, is joined to the terminal on the Lexington side; placement and sizes are a ruling).
HY_D0, HY_D1 = LEX_X0 + 150 * FT, LEX_X0 + 162 * FT
HY_Y0 = LEX_Y + WALL                       # 220
HY_Y1 = HY_Y0 + 18 * FT                    # stair passage end, atrium south face
HY_Z = 72
HA_X0, HA_X1 = (HY_D0 + HY_D1)//2 - 30 * FT, (HY_D0 + HY_D1)//2 + 30 * FT
HA_Y1, HA_H = HY_Y1 + 60 * FT, 40 * FT
MK_X0, MK_X1 = 2720, 2720 + 240 * FT
MK_Y1 = -LEX_Y - WALL                      # north face, Lexington Passage's south wall
MK_Y0 = MK_Y1 - 28 * FT
MK_H, MK_DH = 15 * FT, 21 * FT
MK_DX0, MK_DX1 = (MK_X0 + MK_X1)//2 - 14 * FT, (MK_X0 + MK_X1)//2 + 14 * FT
MK_D0, MK_D1, MK_DOOR_H = MK_X0 + 120, MK_X0 + 120 + 12 * FT, 14 * FT
MK_SL = 5 * FT                             # storefront side light width


def lex_passage(W, ents):
    decor = []
    det = decor.append
    x0, x1, y, h = LEX_X0, LEX_X1, LEX_Y, LEX_H
    r, top = ARCH_W // 2, ARCH_TOP
    W(box(x0, -y - WALL, -WALL, x1, y + WALL, 0, TEX_FLOOR))
    W(box(x0, -y - WALL, h, x1 + WALL, y + WALL, h + WALL, TEX_COFFER))
    W(box(x0, -y - WALL, 0, MK_D0, -y, h, TEX_CREAM))      # south wall, cut by the Market door
    W(box(MK_D1, -y - WALL, 0, x1, -y, h, TEX_CREAM))
    W(box(MK_D0, -y - WALL, MK_DOOR_H, MK_D1, -y, h, TEX_CREAM))
    W(box(x0, y, 0, GB_X0, y + WALL, h, TEX_CREAM))        # north wall, cut by Graybar Passage
    W(box(GB_X1, y, 0, HY_D0, y + WALL, h, TEX_CREAM))
    W(box(HY_D1, y, 0, x1, y + WALL, h, TEX_CREAM))
    W(box(HY_D0, y, 14 * FT, HY_D1, y + WALL, h, TEX_CREAM))
    W(box(HY_D0, y, -WALL, HY_D1, y + WALL, 0, TEX_FLOOR))
    W(box(GB_X0, y, h, GB_X1, y + WALL, GB_TOP + WALL, TEX_CREAM))
    # West wall round the arch opening, east wall with the Lexington doors.
    W(box(x0, -y, 0, x0 + WALL, -r, h, TEX_CREAM))
    W(box(x0, r, 0, x0 + WALL, y, h, TEX_CREAM))
    W(box(x0, -r, min(top, h), x0 + WALL, r, max(top, h) + WALL, TEX_CREAM))   # header: passage lower than the arch
    W(box(x1, -y - WALL, -WALL, x1 + WALL, y + WALL, h, TEX_CREAM))
    for c in (-84, 0, 84):
        det(box(x1 - 6, c - 36, 0, x1, c + 36, 120, TEX_GRID))
        det(box(x1 - 8, c - 30, 0, x1 - 6, c + 30, 114, TEX_DOOR))
    det(box(x1 - 6, -130, 132, x1, 130, 168, TEX_GOLD))
    # Dado, cornice, shop fronts (lit glass, brass frames, dark sign band) along both walls.
    for s in (-1, 1):
        ya, yb = sorted((s*(y - 4), s*y))
        gaps = ((GB_X0, GB_X1), (HY_D0, HY_D1)) if s > 0 else ((MK_D0 - 20 - MK_SL, MK_D1 + 20 + MK_SL),)
        xa = x0 + WALL
        for g0, g1 in gaps + ((x1, x1),):                  # dado stops at each door opening
            det(box(xa, ya, 0, g0, yb, 36, TEX_TRIM))
            xa = g1
        ca, cb = sorted((s*(y - 10), s*y))
        det(box(x0 + WALL, ca, h - 20, x1, cb, h - 8, TEX_GOLD))
        # Shop glass (make_board.py lex_shop): 1024 px per 380 u shop pitch, window at px 0..593,
        # read from the passage (north faces -y: +x right; south faces +y: -x right).
        xs, su, sv = x0 + WALL + 160, 380 / 1024, 108 / 512
        FACEUV["gcs/lex_shop_n"] = lambda n: ("[1 0 0 %g] %g" % (-xs / su, su), "[0 0 -1 %g] %g" % (120 / sv, sv))
        FACEUV["gcs/lex_shop_s"] = lambda n: ("[-1 0 0 %g] %g" % ((xs + 220) / su, su), "[0 0 -1 %g] %g" % (120 / sv, sv))
        for k in range(6):
            sx = x0 + WALL + 160 + k*380
            if s > 0 and sx < GB_X1 + 16 and sx + 228 > GB_X0 - 16:
                continue
            if s > 0 and sx < HY_D1 + 16 and sx + 228 > HY_D0 - 16:
                continue
            if s < 0 and sx < MK_D1 + 36 + MK_SL and sx + 228 > MK_D0 - 36 - MK_SL:
                continue
            ga, gb = sorted((s*(y - 6), s*(y - 4)))
            det(box(sx, ga, 12, sx + 220, gb, 120, "gcs/lex_shop_%s" % ("n" if s > 0 else "s")))
            fa, fb = sorted((s*(y - 8), s*(y - 4)))
            det(box(sx - 8, fa, 0, sx, fb, 150, TEX_GOLD))
            det(box(sx + 220, fa, 0, sx + 228, fb, 150, TEX_GOLD))
            det(box(sx - 8, fa, 120, sx + 228, fb, 150, "gcs/shed_dark"))
    # Cross beams every 20 ft (the coffer bands in the photos), a brass dome pendant between them.
    for x in range(x0 + 240, x1 - 60, 240):
        det(box(x - 8, -y, h - 14, x + 8, y, h, TEX_GOLD))
    for x in range(x0 + 360, x1 - 100, 480):
        ents.append(ent("prop_static", (x, 0, h), model="models/gcs/lex_pendant.mdl",
                        angles="0 0 0", solid="0", disableshadows="1"))
        ents.append(ent("light", (x, 0, h - 70), _light="255 210 160 45"))
    # Navy blade sign (make_board.py lex_sign) hung across the passage near the west end on two
    # brass rods; both faces read left to right.
    bx, bw, bz1 = x0 + 120, 60, h - 30
    bz0 = bz1 - 30
    FACEUV["gcs/lex_sign"] = lambda n, su=2 * bw / 1024, sv=30 / 256: (
        ("[0 %d 0 %g] %g" % (-1 if n[0] < 0 else 1, bw / su, su), "[0 0 -1 %g] %g" % (bz1 / sv, sv))
        if abs(n[0]) > 0.5 else None)
    det(box(bx - 2, -bw, bz0, bx + 2, bw, bz1, "gcs/lex_sign"))
    for yy in (-bw + 10, bw - 12):
        det(box(bx - 1, yy, bz1, bx + 1, yy + 2, h, TEX_GOLD))
    ents.append(ent("env_cubemap", ((x0 + x1)//2, 0, 72)))
    ents.append(ent("func_brush", solids="".join(decor), targetname="lex_decor", Solidity="2",
                    disableshadows="1", vrad_brush_cast_shadows="1"))


def graybar(W, ents):
    decor = []
    det = decor.append
    x0, x1, y0, y1 = GB_X0, GB_X1, GB_Y0, GB_Y1
    cx = (x0 + x1) // 2
    W(box(x0 - WALL, y0, -WALL, x1 + WALL, y1 + WALL, 0, TEX_FLOOR))
    for a, b in ((x0 - WALL, x0), (x1, x1 + WALL)):
        W(box(a, y0, 0, b, y1, GB_TOP + WALL, "gcs/gb_stone"))
    W(box(x0 - WALL, y1, 0, x1 + WALL, y1 + WALL, GB_TOP + WALL, "gcs/gb_stone"))
    # Painted vaults: gcs/gb_mural (tools/make_mural.py) is drawn in plan, one tile per bay,
    # so it maps top-down on every vault face with the tile's diagonals on the groins.
    sc = GB_BAY / 512
    FACEUV["gcs/gb_mural"] = lambda n: ("[1 0 0 %g] %g" % (-x0 / sc % 512, sc), "[0 -1 0 %g] %g" % (y0 / sc % 512, sc))
    for k in range(GB_N):
        groin(W, x0, x1, y0 + k*GB_BAY, y0 + (k + 1)*GB_BAY, GB_ZS, GB_RISE, "gcs/gb_mural", n=6)
    # Pilasters with gold capitals between bays, dado, lit doors north.
    for k in range(GB_N + 1):
        yk = y0 + k*GB_BAY
        for a, b in ((x0, x0 + 12), (x1 - 12, x1)):
            det(box(a, yk - 14, 0, b, yk + 14, GB_ZS - 16, TEX_CREAM))
            det(box(a, yk - 18, GB_ZS - 16, b, yk + 18, GB_ZS, TEX_GOLD))
    for a, b in ((x0, x0 + 4), (x1 - 4, x1)):
        det(box(a, y0, 0, b, y1, 36, TEX_TRIM))
    for c in (cx - 84, cx, cx + 84):
        det(box(c - 36, y1 - 6, 0, c + 36, y1, 120, TEX_GRID))
        det(box(c - 30, y1 - 8, 0, c + 30, y1 - 6, 114, TEX_DOOR))
    # Kiosk walls (make_board.py gb_kiosk): 512 px = 120 u across, 96 u high; tops keep the default.
    FACEUV["gcs/gb_kiosk"] = lambda n, s=120 / 512, sv=96 / 512: None if abs(n[2]) > 0.5 else (
        ("[0 1 0 0] %g" if abs(n[0]) > 0.5 else "[1 0 0 0] %g") % s, "[0 0 -1 512] %g" % sv)
    # Lit glass kiosks with bronze roofs in bays 2 and 4, a chandelier and a light per bay.
    for k in (1, 3):
        yc = y0 + k*GB_BAY + GB_BAY//2
        det(box(cx - 48, yc - 60, 0, cx + 48, yc + 60, 96, "gcs/gb_kiosk"))
        det(box(cx - 52, yc - 64, 96, cx + 52, yc + 64, 108, "gcs/bronze"))
        ents.append(ent("light", (cx, yc, 80), _light="255 220 170 30"))
    for k in range(GB_N):
        yc = y0 + k*GB_BAY + GB_BAY//2
        ents.append(ent("prop_static", (cx, yc, GB_ZS + GB_RISE - 110), model="models/gcs/vh_chandelier.mdl",
                        angles="0 0 0", solid="0", disableshadows="1"))
        ents.append(ent("light", (cx, yc, GB_ZS + 10), _light="255 210 160 55"))
    ents.append(ent("env_cubemap", (cx, (y0 + y1)//2, 72)))
    ents.append(ent("func_brush", solids="".join(decor), targetname="gb_decor", Solidity="2",
                    disableshadows="1", vrad_brush_cast_shadows="1"))


def market(W, ents):
    decor = []
    det = decor.append
    x0, x1, y0, y1, h, dh = MK_X0, MK_X1, MK_Y0, MK_Y1, MK_H, MK_DH
    W(box(x0 - WALL, y0 - WALL, -WALL, x1 + WALL, y1, 0, "gcs/floor_low"))
    W(box(x0 - WALL, y0 - WALL, 0, x1 + WALL, y0, dh + WALL, TEX_CREAM))
    W(box(x0 - WALL, y0, 0, x0, y1, dh + WALL, TEX_CREAM))
    W(box(LEX_X1 + WALL, y1, -WALL, x1 + WALL, y1 + WALL, dh + WALL, TEX_CREAM))
    W(box(x1, y0, 0, x1 + WALL, y1, dh + WALL, TEX_CREAM))
    # Flat ceiling either side of the dome bay, dome ceiling higher, step walls closing the gap.
    W(box(x0, y0, h, MK_DX0, y1, h + WALL, TEX_COFFER))
    W(box(MK_DX1, y0, h, x1, y1, h + WALL, TEX_COFFER))
    W(box(MK_DX0, y0, dh, MK_DX1, y1, dh + WALL, TEX_COFFER))
    W(box(MK_DX0 - WALL, y0, h + WALL, MK_DX0, y1, dh, TEX_CREAM))
    W(box(MK_DX1, y0, h + WALL, MK_DX1 + WALL, y1, dh, TEX_CREAM))
    W(box(x0, y1, h, x1, y1 + WALL, dh + WALL, TEX_CREAM))      # over the shared wall's top
    # Door from the passage: gold frame both faces; street doors east.
    for yy in (y1, -LEX_Y - 4):
        det(box(MK_D0 - 10, yy, 0, MK_D0, yy + 4, MK_DOOR_H + 10, TEX_GOLD))
        det(box(MK_D1, yy, 0, MK_D1 + 10, yy + 4, MK_DOOR_H + 10, TEX_GOLD))
        det(box(MK_D0, yy, MK_DOOR_H, MK_D1, yy + 4, MK_DOOR_H + 10, TEX_GOLD))
    wy, wx0, wx1 = -LEX_Y, MK_D1 + 24, MK_D1 + 340
    # Goods behind the glass (make_board.py mk_display): 1024 px over the run, read from the
    # passage (+y faces: -x to the right).
    FACEUV["gcs/mk_display"] = lambda n, su=(wx1 - wx0) / 1024, sv=108 / 512: (
        "[-1 0 0 %g] %g" % (wx1 / su, su), "[0 0 -1 %g] %g" % (132 / sv, sv))
    # Storefront: lit glass side lights in gold frames either side of the door, both faces
    # (the real entrance is a glazed shop front; the 15 ft ceilings leave no room for its arch).
    for ga, gb, fa, fb in ((-LEX_Y + 4, -LEX_Y + 6, -LEX_Y, -LEX_Y + 8), (y1 - 6, y1 - 4, y1 - 8, y1)):
        for sa, sb in ((MK_D0 - 10 - MK_SL, MK_D0 - 10), (MK_D1 + 10, MK_D1 + 10 + MK_SL)):
            det(box(sa, ga, 14, sb, gb, 144, "gcs/mk_display"))  # stalls behind the glass, as in GCT_Market.jpg
            det(box(sa, fa, 0, sb, fb, 14, TEX_GOLD))
            det(box(sa, fa, 144, sb, fb, 156, TEX_GOLD))
            det(box(sa + MK_SL//2 - 2, fa, 14, sa + MK_SL//2 + 2, fb, 144, TEX_GOLD))
            o = sa - 10 if sa < MK_D0 else sb
            det(box(o, fa, 0, o + 10, fb, 156, TEX_GOLD))
    # Lettering on 1 u skins only, so the band's underside stays plain gold.
    det(box(MK_D0, y1 + 1, MK_DOOR_H - 20, MK_D1, -LEX_Y - 1, MK_DOOR_H, TEX_GOLD))
    for a in (y1, -LEX_Y - 1):
        det(box(MK_D0, a, MK_DOOR_H - 20, MK_D1, a + 1, MK_DOOR_H, "gcs/mk_sign"))
    # Storefront east of the door on the passage face: lit display window, gold frame, two mullions
    # (the west side is taken by the next shop front).
    # The window bows out into the passage as a shallow curve of glass (8 flat panes),
    # sill and head following it; a brass guard rail on the floor in front.
    n, bow = 8, 16
    arc = [(wx0 + (wx1 - wx0) * i // n, wy + round(bow * math.sin(math.pi * i / n))) for i in range(n + 1)]
    for (ax, ay), (bx, by) in zip(arc, arc[1:]):
        det(prism(ccw([(ax, ay), (bx, by), (bx, by + 2), (ax, ay + 2)]), 24, 132, "gcs/mk_display"))
        det(prism(ccw([(ax, ay + 2), (bx, by + 2), (bx, by + 3), (ax, ay + 3)]), 24, 132, "gcs/booth_glass"))
        det(prism(ccw([(ax, wy), (bx, wy), (bx, by + 6), (ax, ay + 6)]), 0, 24, TEX_WOOD))
        det(prism(ccw([(ax, wy), (bx, wy), (bx, by + 6), (ax, ay + 6)]), 132, 140, TEX_GOLD))
    for i, (fx, fy) in enumerate(arc):
        if i % 2 == 0:
            det(box(fx - (4 if 0 < i < n else 0) - (8 if i == n else 0), fy, 24,
                    fx + (4 if 0 < i < n else 0) + (8 if i == 0 else 0), fy + 6, 132, TEX_GOLD))
    ents.append(ent("prop_static", (wx0 - 8, wy + bow + 30, 0), model="models/gcs/mk_rail.mdl",
                    angles="0 -90 0", solid="0", disableshadows="1"))
    # Name band above it at a whole sign width from the door band, so _mk_sign_uv tiles into place.
    det(box(MK_D0 + 288, wy, MK_DOOR_H - 20, MK_D0 + 432, wy + 4, MK_DOOR_H, TEX_GOLD))
    det(box(MK_D0 + 288, wy + 4, MK_DOOR_H - 20, MK_D0 + 432, wy + 5, MK_DOOR_H, "gcs/mk_sign"))
    yc = (y0 + y1)//2
    for c in (yc - 84, yc, yc + 84):
        det(box(x1 - 6, c - 36, 0, x1, c + 36, 120, TEX_GRID))
        det(box(x1 - 8, c - 30, 0, x1 - 6, c + 30, 114, TEX_DOOR))
    # Counters along both walls (oak front, cream top) in runs with gaps, lit glass cases on them.
    for a, b in ((y0, y0 + 40), (y1 - 40, y1)):
        for cx in range(x0 + 120, x1 - 200, 300):
            det(box(cx, a, 0, cx + 240, b, 40, TEX_WOOD))
            det(box(cx - 2, a - 2 if a == y0 else a - 2, 40, cx + 242, b, 44, TEX_CREAM))
            det(box(cx + 20, a + 8, 44, cx + 220, b - 8, 62, "gcs/booth_glass"))
    # Drum pendants down the aisle and lights; chandelier under the dome.
    for x in range(x0 + 150, x1 - 100, 240):
        if MK_DX0 - 60 < x < MK_DX1 + 60:
            continue
        det(box(x - 1, yc - 1, h - 24, x + 1, yc + 1, h, TEX_GOLD))
        det(box(x - 12, yc - 12, h - 40, x + 12, yc + 12, h - 24, TEX_BULB))
        ents.append(ent("light", (x, yc, h - 60), _light="255 200 140 35"))
    cxd = (MK_DX0 + MK_DX1)//2
    ents.append(ent("prop_static", (cxd, yc, dh), model="models/gcs/root_chandelier.mdl", angles="0 0 0", solid="0", disableshadows="1"))
    ents.append(ent("light", (cxd, yc, h - 20), _light="255 210 160 60"))
    ents.append(ent("env_cubemap", (cxd, yc, 72)))
    ents.append(ent("func_brush", solids="".join(decor), targetname="mk_decor", Solidity="2",
                    disableshadows="1", vrad_brush_cast_shadows="1"))


def campbell(W, ents):
    decor = []
    det = decor.append
    x0, x1, y0, y1, z, h = CB_X0, CB_X1, CB_Y0, CB_Y1, CB_Z, CB_H
    r, top = BARCH_W // 2, CB_Z + BARCH_H
    W(box(x0 - WALL, y0 - WALL, z - WALL, x1 + WALL, y1 + WALL, z, TEX_WOOD))
    W(box(x0 - WALL, y0 - WALL, z + h, x1 + WALL, y1 + WALL, z + h + WALL, "gcs/cb_ceil"))
    W(box(x0 - WALL, y0 - WALL, z, x1, y0, z + h, "gcs/cb_wall"))
    W(box(x0 - WALL, y1, z, x1, y1 + WALL, z + h, "gcs/cb_wall"))
    W(box(x0 - WALL, y0, z, x0, y1, z + h, "gcs/cb_wall"))
    # East wall from the balcony arch's back to the room, with the arch's opening through it.
    xe0, xe1 = x1, -(HX + WALL + ARCH_D)
    W(box(xe0, y0 - WALL, z, xe1, CB_C - r, z + h, "gcs/cb_wall"))
    W(box(xe0, CB_C + r, z, xe1, y1 + WALL, z + h, "gcs/cb_wall"))
    W(box(xe0, CB_C - r, top, xe1, CB_C + r, z + h, "gcs/cb_wall"))
    W(box(xe0, CB_C - r, z - WALL, xe1, CB_C + r, z, TEX_WOOD))
    # Dark oak wainscot, 4 ft, round the room; the east wall's run stops at the arch.
    for bx in ((x0, y0, x1, y0 + 4), (x0, y1 - 4, x1, y1), (x0, y0, x0 + 4, y1),
               (x1 - 4, y0, x1, CB_C - r), (x1 - 4, CB_C + r, x1, y1)):
        det(box(bx[0], bx[1], z, bx[2], bx[3], z + 48, "gcs/cb_wain"))
        det(box(bx[0], bx[1], z + 48, bx[2], bx[3], z + 52, TEX_GOLD))
    # Painted beams on gilt corbels across the room; ochre/red/green read from the coffer and trim.
    for x in range(x0 + 60, x1, 115):
        det(box(x - 10, y0, z + h - 30, x + 10, y1, z + h, TEX_WOOD))
        det(box(x - 12, y0, z + h - 34, x + 12, y1, z + h - 30, TEX_GOLD))
        for a, b in ((y0, y0 + 16), (y1 - 16, y1)):
            det(box(x - 12, a, z + h - 60, x + 12, b, z + h - 30, TEX_GOLD))
    # Leaded window on the south wall over the bar, glowing; bar counter under it.
    wx0, wx1 = x0 + 160, x0 + 160 + 240
    det(box(wx0, y0, z + 96, wx1, y0 + 4, z + 96 + 216, "gcs/cb_leaded"))
    det(box(wx0 - 8, y0, z + 88, wx1 + 8, y0 + 6, z + 96, TEX_GOLD))
    ents.append(ent("light", ((wx0 + wx1)//2, y0 + 60, z + 200), _light="255 220 170 60"))
    det(box(x0 + 120, y0 + 60, z, x0 + 560, y0 + 96, z + 42, TEX_WOOD))
    det(box(x0 + 116, y0 + 56, z + 42, x0 + 564, y0 + 100, z + 46, "gcs/plat_edge"))
    det(box(x0 + 120, y0, z, x0 + 560, y0 + 16, z + 84, TEX_WOOD))
    # Fireplace on the west wall: stone surround, dark opening, tall hood.
    fc = (y0 + y1)//2
    det(box(x0, fc - 70, z, x0 + 24, fc + 70, z + 80, "gcs/cb_wall"))
    det(box(x0, fc - 40, z, x0 + 26, fc + 40, z + 56, "gcs/shed_dark"))
    det(box(x0, fc - 76, z + 80, x0 + 30, fc + 76, z + 90, TEX_GOLD))
    det(box(x0, fc - 56, z + 90, x0 + 14, fc + 56, z + 220, "gcs/cb_wall"))
    # Green banquette along the north wall, small tables; sconces with warm lights.
    det(box(x0 + 120, y1 - 40, z, x1 - 120, y1, z + 18, "gcs/vh_grille"))
    det(box(x0 + 120, y1 - 12, z + 18, x1 - 120, y1, z + 44, "gcs/vh_grille"))
    for x in range(x0 + 180, x1 - 120, 140):
        det(box(x - 14, y1 - 90, z, x + 14, y1 - 62, z + 28, TEX_WOOD))
    for x in range(x0 + 120, x1 - 60, 170):
        for yy, d in ((y1, -1), (y0, 1)):
            a, b = sorted((yy, yy + d*10))
            det(box(x - 8, a, z + 110, x + 8, b, z + 128, TEX_BULB))
            ents.append(ent("light", (x, yy + d*40, z + 120), _light="255 190 130 18"))
    ents.append(ent("env_cubemap", ((x0 + x1)//2, fc, z + 64)))
    ents.append(ent("func_brush", solids="".join(decor), targetname="cb_decor", Solidity="2",
                    disableshadows="1", vrad_brush_cast_shadows="1"))


def transit_store(W, ents):
    decor = []
    det = decor.append
    cy = (VH_Y0 + VH_Y1) // 2
    x0, x1, y0, y1, h = TM_X0, TM_X1, cy - 15 * FT, cy + 15 * FT, TM_H
    W(box(x0, y0 - WALL, -WALL, x1 + WALL, y1 + WALL, 0, "gcs/floor_low"))
    W(box(x0, y0 - WALL, h, x1 + WALL, y1 + WALL, h + WALL, TEX_COFFER))
    W(box(x0, y0 - WALL, 0, x1 + WALL, y0, h, TEX_CREAM))
    W(box(x0, y1, 0, x1 + WALL, y1 + WALL, h, TEX_CREAM))
    W(box(x1, y0, 0, x1 + WALL, y1, h, TEX_CREAM))
    # Wall shelving (oak frame, lit backs), glass cases, the counter by the door.
    for a, b in ((y0, y0 + 24), (y1 - 24, y1)):
        for sx in range(x0 + 40, x1 - 60, 130):
            det(box(sx, a, 0, sx + 110, b, 96, TEX_WOOD))
            ga, gb = (b - 2, b) if a == y0 else (a, a + 2)
            det(box(sx + 6, ga, 10, sx + 104, gb, 90, TEX_DOOR))
    for k, yy in enumerate((cy - 90, cy + 90)):
        det(box(x0 + 140, yy - 30, 0, x0 + 260, yy + 30, 34, TEX_WOOD))
        det(box(x0 + 140, yy - 30, 34, x0 + 260, yy + 30, 52, "gcs/booth_glass"))
    det(box(x0 + 40, y1 - 140, 0, x0 + 64, y1 - 40, 42, TEX_WOOD))
    det(box(x0 + 36, y1 - 144, 42, x0 + 68, y1 - 36, 46, TEX_CREAM))
    # Vintage car cab end on the east wall: steel body, dark windows, a red route sign.
    det(box(x1 - 60, cy - 60, 0, x1, cy + 60, 150, "gcs/train"))
    det(box(x1 - 62, cy - 50, 70, x1 - 60, cy - 6, 110, "gcs/vh_glass"))
    det(box(x1 - 62, cy + 6, 70, x1 - 60, cy + 50, 110, "gcs/vh_glass"))
    det(box(x1 - 62, cy - 20, 120, x1 - 60, cy + 20, 140, TEX_DOOR))
    for x in range(x0 + 80, x1, 160):
        for yy in (cy - 90, cy + 90):
            det(box(x - 8, yy - 8, h - 14, x + 8, yy + 8, h, TEX_BULB))
            ents.append(ent("light", (x, yy, h - 40), _light="255 225 190 80"))
    ents.append(ent("env_cubemap", ((x0 + x1)//2, cy, 72)))
    ents.append(ent("func_brush", solids="".join(decor), targetname="tm_decor", Solidity="2",
                    disableshadows="1", vrad_brush_cast_shadows="1"))


def vanderbilt_link(W, ents):
    decor = []
    det = decor.append
    y, zt, c = LK_Y, LK_ZT, LK_C
    W(box(LK_E, -y - WALL, -WALL, LK_X0, y + WALL, 0, TEX_FLOOR))
    W(yprism(ccw([(LK_E, 0), (LK_W, zt), (LK_W, zt - WALL), (LK_E, -WALL)]), -y, y, "gcs/steel"))
    for a, b in ((-y - WALL, -y), (y, y + WALL)):
        W(box(LK_W, a, -WALL, LK_X0, b, c + WALL, TEX_CREAM))
    W(box(LK_W, -y - WALL, c, LK_X0, y + WALL, c + WALL, TEX_COFFER))
    # Lobby: stone floor at the escalator top, tall glass west wall over the street doors.
    x0, x1, ly, top = LB_X0, LK_W, LB_Y, zt + LB_H
    W(box(x0 - WALL, -ly - WALL, zt - WALL, x1, ly + WALL, zt, "gcs/floor_low"))
    W(box(x0 - WALL, -ly - WALL, top, x1 + WALL, ly + WALL, top + WALL, TEX_COFFER))
    for a, b in ((-ly - WALL, -ly), (ly, ly + WALL)):
        W(box(x0 - WALL, a, zt - WALL, x1 + WALL, b, top, TEX_CREAM))
    W(box(x0 - WALL, -ly, zt, x0, ly, top, TEX_CREAM))
    W(box(x1, -ly, zt - WALL, x1 + WALL, -y - WALL, top, TEX_CREAM))
    W(box(x1, y + WALL, zt - WALL, x1 + WALL, ly, top, TEX_CREAM))
    W(box(x1, -y - WALL, c, x1 + WALL, y + WALL, top, TEX_CREAM))
    # Escalator rails (sloped brass bars), a centre divider, steel skirts.
    def rail(yc, w, z0, z1, tex):
        det(yprism(ccw([(LK_E, z0), (LK_W, zt + z0), (LK_W, zt + z1), (LK_E, z1)]), yc - w, yc + w, tex))
    for yc in (-y + 8, 0, y - 8):
        rail(yc, 6, 0, 36, "gcs/steel")
        rail(yc, 4, 36, 42, TEX_GOLD)
    det(box(LK_E - 40, -y, 0, LK_E, y, 2, TEX_GOLD))
    det(box(LK_W, -y, zt, LK_W + 40, y, zt + 2, TEX_GOLD))
    # West glass wall: big glazed panel, lit doors below, a bronze band.
    det(box(x0, -ly + 40, zt + 150, x0 + 4, ly - 40, top - 40, "gcs/window_glass"))
    for cy in (-150, -50, 50, 150):
        det(box(x0, cy - 40, zt, x0 + 6, cy + 40, zt + 120, TEX_GRID))
        det(box(x0, cy - 34, zt, x0 + 8, cy + 34, zt + 114, TEX_DOOR))
    det(box(x0, -ly, zt + 128, x0 + 8, ly, zt + 140, TEX_GOLD))
    for x in (LK_X0 - 200, (LK_E + LK_W)//2, LK_W - 100, x0 + 150):
        ents.append(ent("light", (x, 0, (c if x > LK_W else top) - 60), _light="255 235 210 60"))
    for x in range(x0 + 120, x1, 200):
        for yy in (-180, 180):
            det(box(x - 10, yy - 10, top - 12, x + 10, yy + 10, top, TEX_BULB))
    ents.append(ent("env_cubemap", ((x0 + x1)//2, 0, zt + 72)))
    ents.append(ent("func_brush", solids="".join(decor), targetname="vl_decor", Solidity="2",
                    disableshadows="1", vrad_brush_cast_shadows="1"))


def madison(W, ents):
    decor = []
    det = decor.append
    x0, x1, hd = MD_X0, MD_X1, MD_HEAD
    zt, zm, zb = LOW_Z, LOW_Z - MD_DROP, MD_Z
    T = "gcs/md_floor"
    # White enamel panels and slatted light ceilings (tools/make_madison.py), like the real hall.
    # Flat landing, run 1, mezzanine, run 2: floor and parallel ceiling slabs (xprism over y,z).
    flats = ((MD_Y0, MD_YA, zt), (MD_YB, MD_YC, zm))
    runs = ((MD_YA, zt, MD_YB, zm), (MD_YC, zm, MD_YD, zb))
    for ya, yb, z in flats:
        W(box(x0, yb, z - WALL, x1, ya, z, T))
        W(box(x0, yb, z + hd, x1, ya, z + hd + WALL, "gcs/md_ceil"))
    for ya, za, yb, zb_ in runs:
        W(xprism(ccw([(ya, za), (yb, zb_), (yb, zb_ - WALL), (ya, za - WALL)]), x0, x1, "gcs/md_step"))
        W(xprism(ccw([(ya, za + hd), (yb, zb_ + hd), (yb, zb_ + hd + WALL), (ya, za + hd + WALL)]), x0, x1, "gcs/md_ceil"))
    for a, b in ((x0 - WALL, x0), (x1, x1 + WALL)):
        W(box(a, MD_YD, zb - WALL, b, MD_Y0, zt + hd + WALL, "gcs/md_panel"))
    # Concourse: low white hall, LIRR track pit along its south side.
    c0, c1, y0, y1, h = MC_X0, MC_X1, MC_Y0, MD_YD, 14 * FT
    py = y0 + 20 * FT
    W(box(c0 - WALL, py, zb - WALL, c1 + WALL, y1, zb, T))
    W(box(c0 - WALL, y0 - WALL, zb - PIT - WALL, c1 + WALL, py, zb - PIT, "gcs/ballast"))
    W(box(c0 - WALL, y0 - WALL, zb + h, c1 + WALL, y1 + WALL, zb + h + WALL, "gcs/md_ceil"))
    W(box(c0 - WALL, y0 - WALL, zb - PIT - WALL, c1 + WALL, y0, zb + h, "gcs/md_panel"))
    for a, b in ((c0 - WALL, c0), (c1, c1 + WALL)):
        W(box(a, y0, zb - PIT - WALL, b, y1, zb + h, "gcs/md_panel"))
    W(box(c0, y1, zb, x0 - WALL, y1 + WALL, zb + h, "gcs/md_panel"))
    W(box(x1 + WALL, y1, zb, c1, y1 + WALL, zb + h, "gcs/md_panel"))
    # Escalator lanes: dark cleated steps, four lanes split by stainless balustrades with black
    # handrails, and a wide lit band down each sloped ceiling, on both runs.
    for ya, za, yb, zb_ in runs:
        for xc in (x0 + 8, x0 + 112, x0 + 216, x0 + 320, x1 - 8):
            det(xprism(ccw([(ya, za), (yb, zb_), (yb, zb_ + 36), (ya, za + 36)]), xc - 6, xc + 6, "gcs/md_steel"))
            det(xprism(ccw([(ya, za + 36), (yb, zb_ + 36), (yb, zb_ + 42), (ya, za + 42)]), xc - 4, xc + 4, "gcs/md_rail"))
        mid = (x0 + x1) // 2
        det(xprism(ccw([(ya, za + hd - 8), (yb, zb_ + hd - 8), (yb, zb_ + hd), (ya, za + hd)]), mid - 40, mid + 40, "gcs/fluor"))
        for k in range(1, 5):
            t = k / 5
            ents.append(ent("light", ((x0 + x1)//2, round(ya + (yb - ya)*t), round(za + (zb_ - za)*t + hd - 40)),
                            _light="225 235 255 40"))
    # Gate frame in the dining wall, yellow platform edge, a waiting LIRR car, ceiling strips.
    for xx in (x0 - 10, x1):
        det(box(xx, -DIN_Y - 4, zt, xx + 10, -DIN_Y, zt + 16 * FT, TEX_GOLD))
    det(box(c0, py, zb, c1, py + 24, zb + 1, "gcs/plat_edge"))
    det(box(c0 + 100, y0 + 60, zb - PIT + 8, c1 - 100, y0 + 180, zb + 150, "gcs/train"))
    # Departure screens (make_board.py md_screen) on the north wall either side of the escalators;
    # 280 u wide, the west one 3 widths further west so one mapping serves both.
    sz0, sz1, sx = zb + 7 * FT, zb + 7 * FT + 70, -200
    FACEUV["gcs/md_screen"] = lambda n, su=280 / 1024, sv=70 / 256: (
        ("[1 0 0 %g] %g" % (-sx / su, su), "[0 0 -1 %g] %g" % (sz1 / sv, sv)) if n[1] < -0.5 else None)
    for a in (sx, sx - 840):
        det(prism([(a, y1 - 4), (a + 280, y1 - 4), (a + 280, y1), (a, y1)], sz0, sz1, "gcs/md_screen", "gcs/steel"))
        det(box(a - 6, y1 - 6, sz0 - 6, a + 286, y1, sz0, "gcs/steel"))
        det(box(a - 6, y1 - 6, sz1, a + 286, y1, sz1 + 6, "gcs/steel"))
    # Mosaic mural on the west wall, glazed shop band on the east wall (make_madison.py; ruling:
    # the real hall has them on its long walls, here the long walls hold the track and escalators),
    # charcoal terrazzo bands across the floor.
    mz0, mz1 = zb + 12, zb + h - 12
    su, sv = (y1 - py) / 1024, (mz1 - mz0) / 256
    FACEUV["gcs/md_mural"] = lambda n: (
        ("[0 1 0 %g] %g" % (-py / su, su), "[0 0 -1 %g] %g" % (mz1 / sv, sv)) if n[0] > 0.5 else None)
    FACEUV["gcs/md_shops"] = lambda n: (
        ("[0 -1 0 %g] %g" % (y1 / su, su), "[0 0 -1 %g] %g" % (mz1 / sv, sv)) if n[0] < -0.5 else None)
    det(box(c0, py, mz0, c0 + 2, y1, mz1, "gcs/md_mural"))
    det(box(c1 - 2, py, mz0, c1, y1, mz1, "gcs/md_shops"))
    for x in range(c0 + 150, c1 - 100, 300):
        det(box(x - 24, py + 24, zb, x + 24, y1, zb + 1, "gcs/md_band"))
    for x in range(c0 + 100, c1, 200):
        det(box(x - 4, py + 60, zb + h - 8, x + 4, y1 - 60, zb + h, "gcs/fluor"))
    for x in range(c0 + 200, c1, 400):
        for y in (py + 150, (py + y1)//2, y1 - 150):
            ents.append(ent("light", (x, y, zb + h - 40), _light="230 238 255 45"))
    for y, z in ((MD_Y0 - 150, zt), ((MD_YB + MD_YC)//2, zm)):
        ents.append(ent("light", ((x0 + x1)//2, y, z + hd - 40), _light="230 238 255 40"))
    ents.append(ent("env_cubemap", ((c0 + c1)//2, (py + y1)//2, zb + 64)))
    ents.append(ent("func_brush", solids="".join(decor), targetname="md_decor", Solidity="2",
                    disableshadows="1", vrad_brush_cast_shadows="1"))


def track61(W, ents):
    decor = []
    det = decor.append
    x0, x1, y0, y1, z = T61_X0, SH_X, SH_Y1 + WALL, T61_Y1, LZ
    W(box(x0, SH_Y1, z - PIT - WALL, 540, y1, z - PIT, "gcs/ballast"))
    W(box(540, SH_Y1, z - PIT - WALL, 780, y1, z, "gcs/plat_tile"))
    W(box(780, SH_Y1, z - PIT - WALL, x1, y1, z - PIT, "gcs/ballast"))
    W(box(x0 - WALL, SH_Y1, LC, x1 + WALL, y1 + WALL, LC + 16, "gcs/shed_dark"))
    W(box(x0 - WALL, y0, z - PIT - WALL, x0, y1, LC, "gcs/shed_dark"))
    W(box(x1, y0, z - PIT - WALL, x1 + WALL, y1, LC, "gcs/shed_dark"))
    W(box(x0 - WALL, y1, z - PIT - WALL, x1 + WALL, y1 + WALL, LC, "gcs/shed_dark"))
    # Rails carried on from the shed, bumpers at the north end; the freight elevator door.
    for t in (474, 900):
        for r in (-30, 26):
            det(box(t + r, y0, z - PIT, t + r + 4, y1 - 60, z - PIT + 6, "gcs/steel"))
        det(box(t - 40, y1 - 60, z - PIT, t + 40, y1 - 36, z - 12, "gcs/steel"))
    det(box(570, y1 - 24, z, 750, y1, z + 150, "gcs/steel"))
    det(box(580, y1 - 26, z, 740, y1 - 24, z + 140, "gcs/shed_dark"))
    det(box(560, y1 - 30, z + 150, 760, y1, z + 162, "gcs/plat_edge"))
    det(box(540, y0, z, 564, y1 - 30, z + 1, "gcs/plat_edge"))
    det(box(756, y0, z, 780, y1 - 30, z + 1, "gcs/plat_edge"))
    # The old steel car on Track 61.
    det(box(840, y0 + 200, z - PIT + 8, 960, y0 + 200 + 60 * FT, z + 150, "gcs/train"))
    # Cage lamps, dim.
    for y in range(y0 + 200, y1 - 100, 420):
        det(box(652, y - 8, LC - 20, 668, y + 8, LC, "gcs/bulb"))
        ents.append(ent("light", (660, y, LC - 40), _light="255 200 140 22"))
    ents.append(ent("env_cubemap", (660, (y0 + y1)//2, z + 64)))
    ents.append(ent("func_brush", solids="".join(decor), targetname="t61_decor", Solidity="2",
                    disableshadows="1", vrad_brush_cast_shadows="1"))
    # Chain-link fence across the opening, a gate gap on the platform.
    fence = (box(x0, y0 - 6, z - PIT, 620, y0 - 2, LC - 16, "metal/metalfence001a")
             + box(700, y0 - 6, z - PIT, x1, y0 - 2, LC - 16, "metal/metalfence001a"))
    ents.append(ent("func_brush", solids=fence, targetname="t61_fence", Solidity="2"))


def hyatt(W, ents):
    decor = []
    det = decor.append
    d0, d1, y0, y1, z = HY_D0, HY_D1, HY_Y0, HY_Y1, HY_Z
    # Stair passage: six 12 u risers over the first 9 ft, then a landing.
    for k in range(6):
        ya, yb = y0 + k * 18, y0 + (k + 1) * 18
        W(box(d0, ya, -WALL, d1, yb, (k + 1) * 12, TEX_CREAM))
    W(box(d0, y0 + 108, -WALL, d1, y1, z, TEX_FLOOR))
    W(box(d0 - WALL, y0, -WALL, d0, y1, z + 15 * FT, TEX_CREAM))
    W(box(d1, y0, -WALL, d1 + WALL, y1, z + 15 * FT, TEX_CREAM))
    W(box(d0, y0, 14 * FT, d1, y1, z + 15 * FT, TEX_CREAM))
    # Atrium.
    x0, x1, ya, yb, h = HA_X0, HA_X1, y1, HA_Y1, HA_H
    W(box(x0 - WALL, ya, z - WALL, x1 + WALL, yb + WALL, z, "gcs/floor_low"))
    W(box(x0 - WALL, ya - WALL, z + h, x1 + WALL, yb + WALL, z + h + WALL, "gcs/window_glass"))
    W(box(x0 - WALL, ya, z, x0, yb, z + h, TEX_CREAM))
    W(box(x1, ya, z, x1 + WALL, yb, z + h, TEX_CREAM))
    W(box(x0 - WALL, yb, z, x1 + WALL, yb + WALL, z + h, TEX_CREAM))
    W(box(x0 - WALL, ya - WALL, z, d0, ya, z + h, TEX_CREAM))
    W(box(d1, ya - WALL, z, x1 + WALL, ya, z + h, TEX_CREAM))
    W(box(d0, ya - WALL, z + 15 * FT, d1, ya, z + h, TEX_CREAM))
    cx, cy = (x0 + x1)//2, (ya + yb)//2
    # Fountain: cream octagonal basin with a dark pool and a brass jet; reception desk; planters.
    det(prism(ngon(cx, cy, 120, 8, math.pi/8), z, z + 30, TEX_CREAM))
    det(prism(ngon(cx, cy, 104, 8, math.pi/8), z + 30, z + 31, "gcs/vh_glass"))
    det(prism(ngon(cx, cy, 10, 8, math.pi/8), z + 31, z + 90, TEX_GOLD))
    det(box(x1 - 300, yb - 80, z, x1 - 60, yb - 40, z + 44, TEX_WOOD))
    det(box(x1 - 304, yb - 84, z + 44, x1 - 56, yb - 36, z + 48, TEX_CREAM))
    for px, py in ((x0 + 80, ya + 80), (x1 - 80, ya + 80), (x0 + 80, yb - 80)):
        det(box(px - 30, py - 30, z, px + 30, py + 30, z + 36, TEX_CREAM))
        det(box(px - 24, py - 24, z + 36, px + 24, py + 24, z + 90, "gcs/vh_grille"))
    det(box(x0, ya + 40, z + h - 200, x0 + 4, yb - 40, z + h - 40, "gcs/window_glass"))
    for lx in (x0 + 180, x1 - 180):
        for ly in (ya + 180, yb - 180):
            ents.append(ent("light", (lx, ly, z + h - 80), _light="255 240 220 90"))
    ents.append(ent("light", ((d0 + d1)//2, (y0 + y1)//2, z + 12 * FT), _light="255 220 170 35"))
    ents.append(ent("env_cubemap", (cx, cy, z + 72)))
    ents.append(ent("func_brush", solids="".join(decor), targetname="hy_decor", Solidity="2",
                    disableshadows="1", vrad_brush_cast_shadows="1"))


# The Biltmore Room (area 6 extra): the old arrival room off the concourse's northwest corner
# (photos: Biltmore_Room_at_Grand_Central_Terminal, MTA_Reopens_Biltmore_Room, the schedule board
# and clock). Cream marble walls and floor, a beamed and coffered ceiling, dentil cornice, the
# old arrivals board (dark glass in a brass frame) on the north wall, brass sconces, and a railed
# well where the escalators go down (sealed). Reached through a doorway in the concourse north wall.
BD0, BD1, BD_H = -1404, -1236, 16 * FT      # doorway through the concourse north wall (14 ft)
BX0, BX1 = -1600, -1120                     # room 40 x 80 ft (estimate), clear of the shed
BY0, BY1 = HY + WALL + 8 * FT, HY + WALL + 88 * FT
BH = 30 * FT


def biltmore(W, ents):
    decor = []
    det = decor.append
    T_DARK = "gcs/vh_glass"
    # Floor with a railed well (10 x 20 ft, 8 ft deep) for the escalators.
    wx0, wx1, wy0, wy1 = -1420, -1300, 1240, 1480
    for b in ((BX0, BY0, BX1, wy0), (BX0, wy1, BX1, BY1), (BX0, wy0, wx0, wy1), (wx1, wy0, BX1, wy1)):
        W(box(b[0], b[1], -WALL, b[2], b[3], 0, TEX_CREAM))
    W(box(wx0, wy0, -96 - WALL, wx1, wy1, -96, T_DARK))
    for b in ((wx0 - 16, wy0, wx0, wy1), (wx1, wy0, wx1 + 16, wy1)):
        W(box(b[0], b[1], -96 - WALL, b[2], b[3], 0, TEX_CREAM))
    for b in ((wx0 - 16, wy0 - 16, wx1 + 16, wy0), (wx0 - 16, wy1, wx1 + 16, wy1 + 16)):
        W(box(b[0], b[1], -96 - WALL, b[2], b[3], 0, TEX_CREAM))
    # Shell: cream marble walls and ceiling.
    W(box(BX0, BY0, BH, BX1, BY1, BH + WALL, TEX_CREAM))
    W(box(BX0 - WALL, BY0 - WALL, -WALL, BX0, BY1 + WALL, BH + WALL, TEX_CREAM))
    W(box(BX1, BY0 - WALL, -WALL, BX1 + WALL, BY1 + WALL, BH + WALL, TEX_CREAM))
    W(box(BX0, BY1, -WALL, BX1, BY1 + WALL, BH + WALL, TEX_CREAM))
    W(box(BX0, BY0 - WALL, -WALL, BD0, BY0, BH + WALL, TEX_CREAM))
    W(box(BD1, BY0 - WALL, -WALL, BX1, BY0, BH + WALL, TEX_CREAM))
    W(box(BD0, BY0 - WALL, BD_H, BD1, BY0, BH + WALL, TEX_CREAM))
    # Passage from the concourse.
    W(box(BD0, HY, -WALL, BD1, BY0, 0, TEX_FLOOR))
    W(box(BD0 - WALL, HY + WALL, -WALL, BD0, BY0 - WALL, BD_H + WALL, TEX_CREAM))
    W(box(BD1, HY + WALL, -WALL, BD1 + WALL, BY0 - WALL, BD_H + WALL, TEX_CREAM))
    W(box(BD0, HY + WALL, BD_H, BD1, BY0 - WALL, BD_H + WALL, TEX_CREAM))
    ents.append(ent("light", ((BD0 + BD1) // 2, (HY + BY0) // 2, BD_H - 30), _light="255 215 160 25"))
    # Square marble door frames with a gold edge on both faces.
    for ya, yb in ((HY - 12, HY), (BY0, BY0 + 12)):
        for x0, x1 in ((BD0 - 30, BD0), (BD1, BD1 + 30)):
            det(box(x0, ya, 0, x1, yb, BD_H, TEX_CREAM))
        det(box(BD0 - 30, ya, BD_H, BD1 + 30, yb, BD_H + 30, TEX_CREAM))
        det(box(BD0 - 30, ya, BD_H + 30, BD1 + 30, yb, BD_H + 34, TEX_GOLD))
    # Brass railing round the well.
    for b in ((wx0 - 16, wy0 - 16, wx1 + 16, wy0 - 12), (wx0 - 16, wy1 + 12, wx1 + 16, wy1 + 16),
              (wx0 - 16, wy0 - 12, wx0 - 12, wy1 + 12), (wx1 + 12, wy0 - 12, wx1 + 16, wy1 + 12)):
        det(box(b[0], b[1], 36, b[2], b[3], 40, TEX_GOLD))
    for x in range(wx0 - 16, wx1 + 17, 24):
        for y in (wy0 - 16, wy1 + 12):
            det(box(x, y, 0, x + 3, y + 4, 36, TEX_GOLD))
    for y in range(wy0, wy1 + 1, 24):
        for x in (wx0 - 16, wx1 + 12):
            det(box(x, y, 0, x + 4, y + 3, 36, TEX_GOLD))
    # Beamed ceiling: deep cross beams every 16 ft and a long beam each side, cream with a gold soffit line.
    for y in range(BY0 + 192, BY1 - 1, 192):
        det(box(BX0, y - 12, BH - 30, BX1, y + 12, BH, TEX_CREAM))
        det(box(BX0, y - 4, BH - 31, BX1, y + 4, BH - 30, TEX_GOLD))
    for x in (BX0 + 160, BX1 - 160):
        det(box(x - 10, BY0, BH - 20, x + 10, BY1, BH, TEX_CREAM))
    # Dentil cornice and a marble dado round the room.
    for d, z0, z1, tex in ((20, BH - 24, BH, TEX_CREAM), (14, BH - 30, BH - 24, TEX_GOLD)):
        det(box(BX0, BY0, z0, BX1, BY0 + d, z1, tex))
        det(box(BX0, BY1 - d, z0, BX1, BY1, z1, tex))
        det(box(BX0, BY0 + d, z0, BX0 + d, BY1 - d, z1, tex))
        det(box(BX1 - d, BY0 + d, z0, BX1, BY1 - d, z1, tex))
    for x in range(BX0 + 24, BX1 - 23, 12):
        for y0, y1 in ((BY0 + 14, BY0 + 18), (BY1 - 18, BY1 - 14)):
            det(box(x, y0, BH - 36, x + 6, y1, BH - 30, TEX_CREAM))
    # The arrivals board: split-flap lettering (make_board.py arrivals) in a brass frame with three brass mullions, north wall.
    cx, bw, z0, z1 = (BX0 + BX1) // 2, 15 * FT, 8 * FT, 17 * FT
    FACEUV["gcs/arrivals"] = lambda n, x0=cx - bw, su=2 * bw / 1024, sv=(z1 - z0) / 256: (
        ("[1 0 0 %g] %g" % (-x0 / su, su), "[0 0 -1 %g] %g" % (z1 / sv, sv)) if n[1] < -0.5 else None)
    det(prism([(cx - bw, BY1 - 4), (cx + bw, BY1 - 4), (cx + bw, BY1), (cx - bw, BY1)], z0, z1, "gcs/arrivals", T_DARK))
    for x in (cx - bw - 6, cx - bw // 2 - 2, cx - 2, cx + bw // 2 - 2, cx + bw):
        det(box(x, BY1 - 8, z0, x + (6 if abs(x - cx) > bw else 4), BY1 - 4, z1, TEX_GOLD))
    for z in (z0 - 6, z1):
        det(box(cx - bw - 6, BY1 - 8, z, cx + bw + 6, BY1 - 4, z + 6, TEX_GOLD))
    det(box(cx - bw - 12, BY1 - 14, z0 - 14, cx + bw + 12, BY1, z0 - 6, TEX_CREAM))
    # Wall clock above the board: the Tiffany dial (clock_out.vtf) in a gold ring.
    cz, cr = z1 + 6 * FT, 3 * FT
    FACEUV["gcs/bilt_clock"] = lambda n, x0=cx - cr, z=cz + cr, su=2 * cr / 512: (
        ("[1 0 0 %g] %g" % (-x0 / su, su), "[0 0 -1 %g] %g" % (z / su, su)) if n[1] < -0.5 else None)
    det(yprism(ngon_xz(cx, cz, cr + 6, 20), BY1 - 6, BY1, TEX_GOLD))
    det(yprism(ngon_xz(cx, cz, cr, 20), BY1 - 8, BY1 - 6, TEX_GOLD, ends="gcs/bilt_clock"))
    # Brass sconces with glowing globes on the long walls, a lamp each side of the board.
    sc = [(BX0, y, 1) for y in range(BY0 + 96, BY1 - 95, 192)] + [(BX1, y, -1) for y in range(BY0 + 96, BY1 - 95, 192)]
    for xw, y, s in sc:
        xa, xb = sorted((xw, xw + s * 14))
        det(box(xa, y - 3, 108, xb, y + 3, 150, TEX_GOLD))
        ga, gb = sorted((xw + s * 8, xw + s * 20))
        det(box(ga, y - 6, 150, gb, y + 6, 162, TEX_BULB))
        ents.append(ent("light", (xw + s * 40, y, 140), _light="255 215 165 22"))
    for x in (cx - bw - 30, cx + bw + 18):
        det(box(x, BY1 - 14, 150, x + 12, BY1, 162, TEX_BULB))
    # Ceiling lights between the beams.
    for y in range(BY0 + 96, BY1, 192):
        for x in (BX0 + 80, (BX0 + BX1) // 2, BX1 - 80):
            det(box(x - 12, y - 12, BH - 2, x + 12, y + 12, BH, TEX_BULB))
        ents.append(ent("light", ((BX0 + BX1) // 2, y, BH - 60), _light="255 228 190 30"))
    ents.append(ent("env_cubemap", ((BX0 + BX1) // 2, (BY0 + BY1) // 2, 120)))
    ents.append(ent("func_brush", solids="".join(decor), targetname="bilt_decor", Solidity="2",
                    disableshadows="1", vrad_brush_cast_shadows="1"))


def build():
    world, ents = [], []
    W = world.append

    # Sealed outer hull (nodraw) so the interior can't leak while geometry is rough.
    O = 256
    X0, X1, Y0, Y1, Z1 = OB_X0 - 128, -RAMP_XF + EAST_D + 2*WALL + 128, PY0 - 2*WALL - 128, T61_Y1+WALL+64, SKYZ+WALL+64
    X0, X1 = min(X0, EX0 - 2*WALL - 128), max(X1, EX1 + 2*WALL + 128, LEX_X1 + WALL + 128, MK_X1 + WALL + 128)
    ZB = MD_Z - PIT - 2*WALL - 64
    W(box(X0, Y0, ZB, X1, Y1, ZB+64, NODRAW))
    W(box(X0, Y0, Z1, X1, Y1, Z1+64, NODRAW))
    W(box(X0, Y0-64, ZB, X1, Y0, Z1+64, NODRAW))
    W(box(X0, Y1, ZB, X1, Y1+64, Z1+64, NODRAW))
    W(box(X0-64, Y0-64, ZB, X0, Y1+64, Z1+64, NODRAW))
    W(box(X1, Y0-64, ZB, X1+64, Y1+64, Z1+64, NODRAW))

    # Floor (cut by the two west ramp wells) and long walls.
    W(box(RAMP_X0, -HY, -WALL, -RAMP_X0, HY, 0, TEX_FLOOR))
    for y0, y1 in ((-HY, -RAMP_Y1), (-RAMP_Y0, RAMP_Y0), (RAMP_Y1, HY)):
        W(box(-HX, y0, -WALL, RAMP_X0, y1, 0, TEX_FLOOR))
        W(box(-RAMP_X0, y0, -WALL, HX, y1, 0, TEX_FLOOR))
    lower_level(W, ents)
    # South wall, cut by the passage to Vanderbilt Hall in its west bay.
    W(box(-HX, -HY-WALL, -WALL, VH_PX0, -HY, SPRING, TEX_WALL))
    W(box(VH_PX1, -HY-WALL, -WALL, HX, -HY, SPRING, TEX_WALL))
    W(box(VH_PX0, -HY-WALL, VH_PH, VH_PX1, -HY, SPRING, TEX_WALL))
    W(box(VH_PX0, -HY-WALL, -WALL, VH_PX1, -HY, 0, TEX_FLOOR))
    vanderbilt(W, ents)
    exterior(W, ents)
    # North wall, cut by the three track gates.
    gedges = [-HX, BD0, BD1] + [e for gx, _ in GATES for e in (gx - GATE_W//2, gx + GATE_W//2)] + [HX]
    for j in range(0, len(gedges), 2):
        W(box(gedges[j], HY, -WALL, gedges[j+1], HY+WALL, SPRING, TEX_WALL))
    for gx, _ in GATES:
        W(box(gx - GATE_W//2, HY, GATE_H, gx + GATE_W//2, HY+WALL, SPRING, TEX_WALL))
    W(box(BD0, HY, BD_H, BD1, HY+WALL, SPRING, TEX_WALL))
    platforms(W, ents)
    lower_tracks(W, ents)
    lex_passage(W, ents)
    graybar(W, ents)
    market(W, ents)
    campbell(W, ents)
    transit_store(W, ents)
    vanderbilt_link(W, ents)
    madison(W, ents)
    track61(W, ents)
    hyatt(W, ents)
    biltmore(W, ents)

    # Barrel vault, segmented flattened half-ellipse around the x axis.
    # The inner faces carry the zodiac mural (2048x1024) once: u along x, v along the arc.
    N = 20
    r0, r1 = 0, WALL
    p = lambda r, a: (round((HY+r)*math.cos(a)), round(SPRING + (VRISE+r)*math.sin(a)))
    arc = [p(r0, math.pi*i/N) for i in range(N+1)]
    seg = [math.dist(arc[i], arc[i+1]) for i in range(N)]
    su, sv = 2*HX/2048, sum(seg)/1024
    s0 = 0
    for i in range(N):
        a0, a1 = math.pi*i/N, math.pi*(i+1)/N
        poly = [p(r1, a0), p(r1, a1), p(r0, a1), p(r0, a0)]
        q0, q1 = arc[i], arc[i+1]
        ty, tz = (q1[0]-q0[0])/seg[i], (q1[1]-q0[1])/seg[i]
        uv = ("[1 0 0 %g] %g" % (HX/su, su),
              "[0 %g %g %g] %g" % (ty, tz, (s0 - (q0[0]*ty + q0[1]*tz))/sv, sv))
        W(xprism(poly, -HX, HX, TEX_VAULT, {2: uv}))
        s0 += seg[i]
    # Corners behind the vault so the wall tops are solid.
    W(box(-HX, -HY-WALL, SPRING, HX, -HY, SPRING+8, TEX_TRIM))
    W(box(-HX, HY, SPRING, HX, HY+WALL, SPRING+8, TEX_TRIM))

    # End walls with three tall arched windows (blockout: rectangular openings into glowing alcoves).
    win_w, win_z0, win_z1 = 26*FT, BALC_Z + 16*FT, SPRING + 22*FT
    win_zc = SPRING + 29*FT + 6                # the centre window rises higher, under the crown
    centres = [-31*FT, 0, 31*FT]            # close-set, as in the photos: narrow piers between
    for sgn in (-1, 1):
        xin, xout = sgn*HX, sgn*(HX+WALL)
        xa, xb = min(xin, xout), max(xin, xout)
        # Arcades: three arched openings under the balcony and three behind it, each into a
        # short sealed passage. Wall bands between them are solid.
        for y0, y1 in ((-HY, -RAMP_Y1), (-RAMP_Y0, RAMP_Y0), (RAMP_Y1, HY)):   # ramps pass under the side arches
            W(box(xa, y0, -WALL, xb, y1, 0, TEX_WALL))
        W(box(xa, -HY, ARCH_TOP, xb, HY, BALC_Z, TEX_WALL))
        W(box(xa, -HY, BALC_Z + BARCH_H, xb, HY, win_z0, TEX_WALL))
        for z0, aw, ah in ((0, ARCH_W, ARCH_TOP), (BALC_Z, BARCH_W, BARCH_H)):
            top = z0 + ah
            aedges = [-HY] + [e for c in centres for e in (c-aw//2, c+aw//2)] + [HY]
            for j in range(0, len(aedges), 2):
                W(box(xa, aedges[j], z0, xb, aedges[j+1], top, TEX_WALL))
            for c in centres:
                arcade_bay(W, ents, sgn, xin, xout, c, z0, aw//2, top, min(WALL, BALC_Z - ARCH_TOP) if z0 == 0 else WALL,
                           ramp=(z0 == 0 and c != 0),
                           open_=(z0 == 0 and c == 0) or (z0 == BALC_Z and c == CB_C and sgn < 0))
        W(box(xa, -HY, win_zc, xb, HY, CROWN+WALL, TEX_WALL))
        W(box(xa, -HY, win_z1, xb, -win_w//2, win_zc, TEX_WALL))
        W(box(xa, win_w//2, win_z1, xb, HY, win_zc, TEX_WALL))
        edges = [-HY] + [e for c in centres for e in (c-win_w//2, c+win_w//2)] + [HY]
        for j in range(0, len(edges), 2):
            W(box(xa, edges[j], win_z0, xb, edges[j+1], win_z1, TEX_WALL))
        # Alcove behind: glowing back panel.
        xg0, xg1 = sorted((sgn*(HX+WALL+192), sgn*(HX+WALL+224)))
        W(box(xg0, -HY, win_z0-32, xg1, HY, win_zc+32, TEX_GLASS))
        # Arched heads: fill the corners above each arch with triangle fans.
        for c in centres:
            r, zt = win_w//2, (win_zc if c == 0 else win_z1)
            arc = halfdisc(c, zt - r, r, 8)
            for i in range(8):
                corner = (c + r, zt) if i < 4 else (c - r, zt)
                ents.append(ent("func_detail", solids=xprism(ccw([corner, arc[i], arc[i+1]]), xa, xb, TEX_WALL)))
        for c in centres:
            ents.append(ent("light", (sgn*(HX+WALL+96), c, (win_z0+win_z1)/2),
                            _light="240 244 255 45", _quadratic_attn="0", _linear_attn="1", _fifty_percent_distance="900", _zero_percent_distance="2400"))
            ents.append(ent("light_spot", (sgn*(HX+WALL+150), c, win_z1-40),
                            angles="-38 %d 0" % (180 if sgn > 0 else 0), pitch="-38",
                            _light="235 240 255 65", _inner_cone="30", _cone="65", _exponent="1",
                            _distance="0", _fifty_percent_distance="2600", _zero_percent_distance="5200"))

        # Sun shafts: one additive beam per window, falling inward at the spotlight pitch.
        a = math.radians(38)
        dx, dz = -sgn*math.cos(a), -math.sin(a)
        x0 = sgn*HX
        for c in centres:
            zt = (win_zc if c == 0 else win_z1) - 6*FT
            zb = win_z0 + 2*FT
            L, lb = (zt - 8) / -dz, (zb - 8) / -dz   # slant lengths to the floor
            poly = ccw([(x0, zb), (x0, zt), (round(x0 + dx*L), 8), (round(x0 + dx*lb), 8)])
            w = round(win_w * 0.55)
            y0 = c - w//2
            su, sv = w/256, L/256
            uv = ("[0 1 0 %g] %g" % (-y0/su, su),
                  "[%g 0 %g %g] %g" % (dx, dz, -(dx*x0 + dz*zt)/sv, sv))
            ents.append(ent("func_illusionary", solids=yprism(poly, y0, y0 + w, TEX_SHAFT, uv, NODRAW), disableshadows="1"))

    # Mullion grid in the end windows, gilded band across each end at the springline.
    for sgn in (-1, 1):
        xm0, xm1 = sorted((sgn*(HX+WALL//2), sgn*(HX+WALL//2+4)))
        # One alpha-tested grid panel per window (gcs/endwin_a/b/c share endwin_grid.vtf: 8 columns
        # across the window, a bar every 96 u); was ~50 bar brushes per window (vertex budget).
        for c, m in zip(centres, ("a", "b", "c")):
            su, sv = win_w / 512, 1.5
            FACEUV["gcs/endwin_" + m] = (lambda n, c=c, su=su, sv=sv: ("[0 1 0 %g] %g" % (-(c - win_w/2)/su, su),
                                                                     "[0 0 -1 %g] %g" % ((win_z0 - 48)/sv, sv))
                                         if abs(n[0]) > 0.5 else None)
            ents.append(ent("func_detail", solids=box(xm0, c - win_w//2, win_z0, xm1, c + win_w//2,
                                                      win_zc if c == 0 else win_z1, "gcs/endwin_" + m)))
        xa, xb = sorted((sgn*HX, sgn*(HX-24)))
        for j in range(0, len(edges), 2):
            ents.append(ent("func_detail", solids=box(xa, edges[j], SPRING-40, xb, edges[j+1], SPRING, TEX_GOLD)))
        # Paired engaged columns on the piers between the windows, gilded capitals.
        xc0, xc1 = sorted((sgn*HX, sgn*(HX-3*FT)))
        for py in (-31*FT//2, 31*FT//2):
            for dy in (-2*FT, 2*FT):
                y = py + dy
                ents.append(ent("func_detail", solids=box(xc0, y-18, BALC_Z, xc1, y+18, SPRING-64, TEX_CREAM)))
                ents.append(ent("func_detail", solids=box(xc0, y-24, SPRING-64, xc1, y+24, SPRING-40, TEX_GOLD)))
                ents.append(ent("func_detail", solids=box(xc0, y-24, BALC_Z, xc1, y+24, BALC_Z+18, TEX_TRIM)))
        # The great end arch: a deep soffit following the vault, gilded on its inner edge.
        e = lambda dy, dz, a: (round((HY-dy)*math.cos(a)), round(SPRING + (VRISE-dz)*math.sin(a)))
        for i in range(N):
            a0, a1 = math.pi*i/N, math.pi*(i+1)/N
            xa, xb = sorted((sgn*HX, sgn*(HX-6*FT)))
            ents.append(ent("func_detail", solids=xprism(ccw([e(0, 0, a0), e(0, 0, a1), e(11*FT, 9*FT, a1), e(11*FT, 9*FT, a0)]), xa, xb, TEX_COFFER)))
            xa, xb = sorted((sgn*(HX-5*FT), sgn*(HX-6*FT-8)))
            ents.append(ent("func_detail", solids=xprism(ccw([e(11*FT, 9*FT, a0), e(11*FT, 9*FT, a1), e(12*FT, 10*FT, a1), e(12*FT, 10*FT, a0)]), xa, xb, TEX_GOLD)))

    # Long walls: pilasters between bays, a tall dark window grid in each bay, the
    # gilded cornice at the springline and a lunette window cut into the vault above.
    bay = 2*HX // BAYS
    for sgn in (-1, 1):
        yw = sgn*HY
        inset = lambda d0, d1: sorted((yw - sgn*d0, yw - sgn*d1))
        for k in range(BAYS + 1):
            x = -HX + k*bay
            ya, yb = inset(0, 60)
            ents.append(ent("func_detail", solids=box(max(x-7*FT, -HX), ya, 0, min(x+7*FT, HX), yb, SPRING-72, TEX_WALL)))
            ya, yb = inset(0, 72)
            ents.append(ent("func_detail", solids=box(max(x-8*FT, -HX), ya, 0, min(x+8*FT, HX), yb, 3*FT, TEX_CREAM)))
        for k in range(BAYS):
            cx = -HX + k*bay + bay//2
            w = bay//2 - 10*FT
            ga, gb = inset(0, 2)
            ents.append(ent("func_detail", solids=box(cx-w, ga, BAY_Z0, cx+w, gb, SPRING-8*FT, TEX_GLASS)))
            ma, mb = inset(2, 6)
            for j in range(-3, 4):
                ents.append(ent("func_detail", solids=box(cx + j*w//4 - 3, ma, BAY_Z0, cx + j*w//4 + 3, mb, SPRING-8*FT, TEX_GRID)))
            for z in range(BAY_Z0, SPRING-8*FT+1, 96):
                ents.append(ent("func_detail", solids=box(cx-w, ma, z-3, cx+w, mb, z+3, TEX_GRID)))
            # Lunette: half-disc glass standing on the cornice, poking through the vault.
            la, lb = inset(88, 92)
            # gcs/lunette (512x256): one texture spans the whole half-disc (384x192 u at 0.75): low glass arc,
            # carved cream tympanum above it (Flag_Ceiling photo; was 5 mullion brushes, then all glass).
            FACEUV["gcs/lunette"] = lambda n, s=0.75, ox=-(cx - 16*FT)/0.75, oy=(SPRING + 16*FT)/0.75: None if abs(n[1]) < 0.5 else (
                "[1 0 0 %g] %g" % (ox, s), "[0 0 -1 %g] %g" % (oy, s))
            ents.append(ent("func_detail", solids=yprism(halfdisc(cx, SPRING, 16*FT), la, lb, "gcs/lunette")))
            # Sculpted cream surround (Flag_Ceiling photo): a wide stepped hood, gold-edged.
            for r0, r1, d0, d1, tex in ((16, 19, 92, 112, TEX_CREAM), (19, 23, 92, 104, TEX_CREAM), (23, 24, 92, 100, TEX_GOLD)):
                fa, fb = inset(d0, d1)
                outer, inner = halfdisc(cx, SPRING, r1*FT), halfdisc(cx, SPRING, r0*FT)
                for i in range(len(outer)-1):
                    # Carved relief: alternate voussoirs of the middle ring stand 6 u proud.
                    a, b = inset(d0, d1 + 6) if r0 == 19 and i % 2 == 0 else (fa, fb)
                    ents.append(ent("func_detail", solids=yprism([outer[i], outer[i+1], inner[i+1], inner[i]], a, b, tex)))
            # Keystone at the crown of the hood.
            ka, kb = inset(92, 118)
            ents.append(ent("func_detail", solids=box(cx - 2*FT, ka, SPRING + 15*FT, cx + 2*FT, kb, SPRING + 25*FT, TEX_CREAM)))
            ents.append(ent("light", (cx, yw - sgn*200, SPRING + 80), _light="200 220 240 8"))
        ca, cb = inset(0, 88)
        # Front face carries the row of cornice bulbs (gcs/cornice_lit, a bulb every 24 u, shifted to
        # x = 6 mod 24 so they sit between the modillion brackets below).
        FACEUV["gcs/cornice_lit"] = lambda n, su=96/256, sv=40/64: None if abs(n[1]) < 0.5 else (
            "[%d 0 0 %d] %g" % ((1, 16, su) if n[1] < 0 else (-1, -16, su)), "[0 0 -1 %g] %g" % (SPRING / sv, sv))
        ents.append(ent("func_detail", solids=box(-HX, ca, SPRING-40, HX, cb, SPRING, "gcs/cornice_lit")))
        ca, cb = inset(0, 72)
        ents.append(ent("func_detail", solids=box(-HX, ca, SPRING-72, HX, cb, SPRING-40, TEX_TRIM)))
        # Modillion band (east_balcony photo): cream brackets every 2 ft under an overhanging crown.
        ca, cb = inset(88, 104)
        ents.append(ent("func_detail", solids=box(-HX, ca, SPRING-10, HX, cb, SPRING, TEX_GOLD)))
        # The brackets themselves are painted into gcs/cornice_lit between the bulbs (vertex budget).

    # Balconies at both ends with a parapet.
    for sgn in (-1, 1):
        xa, xb = sorted((sgn*HX, sgn*(HX-BALC_D)))
        ents.append(ent("func_detail", solids=box(xa, -HY, BALC_Z-24, xb, HY, BALC_Z, TEX_CREAM)))
        rx = sgn*(HX-BALC_D)
        ra, rb = sorted((rx, rx+sgn*-16))
        for y0, y1 in ((-HY, -24*FT), (24*FT, HY)):
            # Cream marble parapet with a brass handrail on top, like the stair balustrades.
            ents.append(ent("func_detail", solids=box(ra, y0, BALC_Z, rb, y1, BALC_Z+42, TEX_CREAM)))
            ents.append(ent("func_detail", solids=box(ra-2, y0, BALC_Z+42, rb+2, y1, BALC_Z+46, TEX_RAIL)))
        # Ceiling lamps under the balcony so the floor arcade and stair sides aren't black.
        lx = sgn*(HX - BALC_D//2)
        for ly in (-3*HY//4, -HY//4, HY//4, 3*HY//4):
            ents.append(ent("func_detail", solids=box(lx-10, ly-10, BALC_Z-32, lx+10, ly+10, BALC_Z-24, TEX_GOLD)))
            ents.append(ent("func_detail", solids=box(lx-7, ly-7, BALC_Z-40, lx+7, ly+7, BALC_Z-32, TEX_BULB)))
            ents.append(ent("light", (lx, ly, BALC_Z-64), _light="255 205 145 30"))

    # Double staircases: two flights per end, landing on the balcony.
    rise, run = 12, 18
    steps = BALC_Z // rise
    for sgn in (-1, 1):
        for yc in (-8*FT, 8*FT):
            y0, y1 = sorted((yc, yc + (1 if yc > 0 else -1)*14*FT))
            for k in range(steps):
                xs = sgn*(HX-BALC_D) - sgn*(steps-k)*run
                xa, xb = sorted((xs, xs+sgn*run))
                ents.append(ent("func_detail", solids=box(xa, y0, 0, xb, y1, (k+1)*rise, TEX_STAIR)))
            # Solid cream balustrades on both sides with a brass handrail, newel at the foot.
            xf, xt = sgn*(HX-BALC_D) - sgn*steps*run, sgn*(HX-BALC_D)
            for ya, yb in ((y0-18, y0), (y1, y1+18)):
                wall = [(xf, 0), (xt, 0), (xt, BALC_Z+42), (xf, 42)]
                rail = [(xf, 42), (xt, BALC_Z+42), (xt, BALC_Z+46), (xf, 46)]
                ents.append(ent("func_detail", solids=yprism(ccw(wall), ya, yb, TEX_STAIR)))
                ents.append(ent("func_detail", solids=yprism(ccw(rail), ya-2, yb+2, TEX_RAIL)))
                na, nb = sorted((xf, xf-sgn*24))
                ents.append(ent("func_detail", solids=box(na, ya-3, 0, nb, yb+3, 54, TEX_STAIR)))
                ents.append(ent("func_detail", solids=box(na+4, ya+1, 54, nb-4, yb-1, 66, TEX_RAIL)))

    # Information booth with the four-faced clock above it.
    # Booth: cream marble base, dark glass with brass posts, gold cornice; the clock sits
    # on a brass column: four opal dials (30 u = 2.5 ft) under a gold cap and acorn finial.
    for y in (-440, 0, 440):   # west end bay, so the first pylons are lit from both sides
        ents.append(ent("light", (DIN_X0 + 60, y, -WALL - 60), _light="255 215 170 30"))
    oct8 = lambda r: ngon(0, 0, r, 8, math.pi/8)
    det = lambda *a: ents.append(ent("func_detail", solids=prism(*a)))
    det(oct8(13*FT), 0, 3*FT, TEX_CREAM)
    # Glass is a thin translucent ring; inside, a cream counter runs round under the
    # glass and a cream cabinet core holds up the clock column, lit warm.
    ring = lambda ro, ri, z0, z1, tex: [det(ccw([ro[i], ro[(i+1) % 8], ri[(i+1) % 8], ri[i]]), z0, z1, tex)
                                        for i in range(8)]
    ring(oct8(12.5*FT), oct8(12.4*FT), 3*FT, 8*FT, "gcs/booth_glass")
    ring(oct8(12.4*FT), oct8(10.5*FT), 3*FT, 4*FT, TEX_CREAM)
    ring(oct8(12.4*FT), oct8(10.4*FT), 4*FT, 4*FT+2, TEX_GOLD)
    det(oct8(4*FT), 3*FT, 8*FT, TEX_CREAM)
    det(oct8(4.3*FT), 7*FT, 8*FT, TEX_GOLD)
    ents.append(ent("light", (0, 7*FT, 7*FT), _light="255 220 160 55"))
    ents.append(ent("light", (0, -7*FT, 7*FT), _light="255 220 160 55"))
    for x, y in oct8(13*FT):
        det(ngon(x, y, 6, 4, math.pi/4), 3*FT, 8*FT, TEX_GOLD)
    # Brass grille on the glass: two mullions per face, a counter ledge and a top rail.
    out, inn = oct8(12.75*FT), oct8(12.55*FT)
    for i in range(8):
        a, b, ai, bi = out[i], out[(i+1) % 8], inn[i], inn[(i+1) % 8]
        for t in (1/3, 2/3):
            px, py = a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t
            det(ngon(px, py, 3, 4, math.pi/4), 3*FT, 8*FT, TEX_GOLD)
        det(ccw([a, b, bi, ai]), 4*FT, 4*FT+3, TEX_GOLD)
        det(ccw([a, b, bi, ai]), 7*FT, 7*FT+2, TEX_GOLD)
    det(oct8(13.5*FT), 8*FT, 9*FT, TEX_GOLD)
    det(oct8(12*FT), 9*FT, 10*FT, TEX_CREAM)
    det(oct8(2.5*FT), 10*FT, 11*FT, TEX_GOLD)
    det(oct8(1*FT), 11*FT, 150, TEX_GOLD)
    det([(-15, -15), (15, -15), (15, 15), (-15, 15)], 150, 180, TEX_CLOCK, TEX_GOLD)
    det(oct8(20), 180, 184, TEX_GOLD)
    det(oct8(12), 184, 192, TEX_GOLD)
    det(oct8(6), 192, 200, TEX_GOLD)
    ents.append(ent("light", (0, 0, 20*FT), _light="255 225 170 25"))

    # Ticket windows along the south wall: a row of recess frames.
    for k in range(-6, 7):
        x = k*16*FT
        ents.append(ent("func_detail", solids=box(x-6*FT, -HY+0, 0, x-5*FT, -HY+3*FT, 14*FT, TEX_CREAM)))
        # Brass bracket lamp on each pier: wall plate, arm, cup and a glowing globe.
        lx, ly = x-5.5*FT, -HY+3*FT
        det(ngon(lx, ly+2, 4, 6), 10.5*FT, 12*FT, TEX_GOLD)
        ents.append(ent("func_detail", solids=box(lx-1, ly, 11*FT, lx+1, ly+16, 11*FT+2, TEX_GOLD)))
        det(ngon(lx, ly+18, 5, 8, math.pi/8), 11*FT-4, 11*FT, TEX_GOLD)
        det(ngon(lx, ly+18, 6, 8, math.pi/8), 11*FT, 11*FT+10, TEX_BULB)
        ents.append(ent("light", (lx, ly+30, 11*FT+4), _light="255 210 150 8"))
        if k < 6:
            # Each window: cream marble counter with a brass top, brass-grilled dim glass, cream lintel.
            w0, w1 = x-5*FT, x+11*FT
            ents.append(ent("func_detail", solids=box(w0, -HY, 0, w1, -HY+2*FT, 3.5*FT, TEX_CREAM)))
            ents.append(ent("func_detail", solids=box(w0, -HY, 3.5*FT, w1, -HY+2*FT+3, 3.5*FT+2, TEX_GOLD)))
            ents.append(ent("func_detail", solids=box(w0, -HY, 3.5*FT+2, w1, -HY+4, 10*FT, TEX_DIM)))
            for gx in range(int(w0)+12, int(w1)-11, 12):
                ents.append(ent("func_detail", solids=box(gx-1, -HY+4, 3.5*FT+2, gx+1, -HY+7, 10*FT, TEX_GOLD)))
            # Cream marble reveals frame the glass on both sides.
            for j0, j1 in ((w0, w0+10), (w1-10, w1)):
                ents.append(ent("func_detail", solids=box(j0, -HY, 3.5*FT+2, j1, -HY+2*FT, 10*FT, TEX_CREAM)))
            # Segmental arched head: cream spandrels between the reveals, 1.5 ft rise.
            xl, xr, zs, zt = w0+10, w1-10, 8.5*FT, 10*FT
            a, s = (xr - xl)/2, zt - zs
            R, xc = (a*a + s*s)/(2*s), (xl + xr)/2
            pts = [(round(xc + dx), round(zt - R + math.sqrt(R*R - dx*dx)))
                   for dx in (-a + 2*a*i/8 for i in range(9))]
            for i in range(8):
                corner = (xl, zt) if i < 4 else (xr, zt)
                ents.append(ent("func_detail", solids=yprism(ccw([corner, pts[i], pts[i+1]]), -HY, -HY+2*FT, TEX_CREAM)))
            ents.append(ent("func_detail", solids=box(w0, -HY, 10*FT, w1, -HY+2*FT, 11*FT, TEX_GOLD)))
            ents.append(ent("func_detail", solids=box(w0, -HY, 11*FT, w1, -HY+18, 14*FT, TEX_CREAM)))
            # Bronze TICKETS plaque centred on the lintel.
            det([(x, -HY+18), (x+6*FT, -HY+18), (x+6*FT, -HY+20), (x, -HY+20)],
                11.75*FT, 13.25*FT, "gcs/tickets", TEX_GOLD)
    # Cream marble cornice over the ticket windows with a thin gold lower edge.
    ents.append(ent("func_detail", solids=box(-100*FT, -HY, 14*FT, 100*FT, -HY+4*FT-2, 14*FT+2, TEX_GOLD)))
    ents.append(ent("func_detail", solids=box(-100*FT, -HY, 14*FT+2, 100*FT, -HY+4*FT, 16*FT, TEX_CREAM)))
    bx0, bx1, bz0, bz1 = BOARD
    det([(bx0, -HY), (bx1, -HY), (bx1, -HY+16), (bx0, -HY+16)], bz0, bz1, "gcs/board", TEX_GOLD)

    # The flag hangs in the north centre bay from a gold pole bracketed to the wall.
    fx0, fx1, fy0, fy1, fz0, fz1 = FLAG
    ents.append(ent("func_detail", solids=box(fx0, fy0, fz0, fx1, fy1, fz1, "gcs/flag")))
    ents.append(ent("func_detail", solids=box(fx0-6, fy0-3, fz1, fx1+6, fy1+3, fz1+6, TEX_GOLD)))
    for x in (fx0+12, fx1-12):
        ents.append(ent("func_detail", solids=box(x-2, fy0, fz1+2, x+2, HY, fz1+6, TEX_GOLD)))

    def globe(cx, cy, cz, r):
        # A glowing globe: three stacked octagonal slices approximating a sphere.
        for z0, z1, k in ((-1.0, -0.5, 0.75), (-0.5, 0.5, 1.0), (0.5, 1.0, 0.75)):
            det(ngon(cx, cy, max(2, round(r*k)), 8, math.pi/8), round(cz+z0*r), round(cz+z1*r), TEX_BULB)

    # Chandeliers down both long sides: a gold rod from the cornice, a gold drum with
    # two tiers of glowing bulbs, a finial below; a light at each body.
    for x in range(-HX+300, HX-299, 450):
        for y in (-HY+120, HY-120):
            zc = 32*FT
            # Model (tools/make_models.py): rod, drum, two tiers of globes, finial; no brush vertices.
            ents.append(ent("prop_static", (x, y, zc), model="models/gcs/chandelier.mdl", angles="0 0 0", solid="0"))
            ents.append(ent("light", (x, y, zc-64), _light="245 228 205 12"))
        ents.append(ent("light", (x, 0, SPRING+300), _light="160 200 210 10"))

    ents.append(ent("env_tonemap_controller", (0, 0, 64), targetname="tonemap"))
    # Clamp auto exposure and bloom so the pale stone doesn't blow out.
    ents.append(ent("logic_auto", (0, 0, 96), spawnflags="1").replace("}\n",
        '\tconnections\n\t{\n'
        '\t\t"OnMapSpawn" "tonemap,SetAutoExposureMin,0.5,0,-1"\n'
        '\t\t"OnMapSpawn" "tonemap,SetAutoExposureMax,1.2,0,-1"\n'
        '\t\t"OnMapSpawn" "tonemap,SetBloomScale,0.1,0,-1"\n\t}\n}\n'))
    ents.append(ent("info_player_start", (-HX+BALC_D//2, 0, BALC_Z+8), angles="0 0 0"))
    ents.append(ent("info_player_start", (0, -400, 8), angles="0 90 0"))
    ents.append(ent("env_cubemap", (0, 0, 200)))
    ents.append(ent("env_cubemap", (-HX+BALC_D//2, 0, BALC_Z+100)))

    world_s = 'world\n{\n\t"id" "%d"\n\t"mapversion" "1"\n\t"classname" "worldspawn"\n\t"skyname" "sky_day01_01"\n%s}\n' % (nid(), "".join(world))
    head = 'versioninfo\n{\n\t"editorversion" "400"\n\t"editorbuild" "8000"\n\t"mapversion" "1"\n\t"formatversion" "100"\n\t"prefab" "0"\n}\n'
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(head + world_s + "".join(ents), encoding="ascii", newline="\n")
    print("wrote", OUT, _id[0], "ids")


if __name__ == "__main__":
    build()
