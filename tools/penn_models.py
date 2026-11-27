"""Penn Station props as MDL, built with make_models.Mesh and Garry's Mod's studiomdl.

    python tools/penn_models.py      # writes src/modelsrc/, compiles into src/models/penn/

Models do not count against vbsp's 65,536 unique-vertex cap, so the waiting room's giant
fluted Corinthian columns live here. Origin of each column is the top of its pedestal.
"""
import math
import os
import shutil
import subprocess
from pathlib import Path

from make_models import Mesh

ROOT = Path(__file__).resolve().parent.parent
G = Path(os.environ.get("GMOD", "D:/SteamLibrary/steamapps/common/GarrysMod"))
SRC = ROOT / "src" / "modelsrc"
MAT = ROOT / "src" / "materials" / "models" / "penn"
FT = 12
COL_H = 60 * FT          # base to abacus top, matches build_vmf.py COL_TOP - PED
COL_R = 42               # shaft radius at the base (7 ft diameter)

VMTS = {
    "travertine": '"VertexLitGeneric"\n{\n\t"$basetexture" "penn/travertine"\n\t"$surfaceprop" "stone"\n}\n',
    "bronze": '"VertexLitGeneric"\n{\n\t"$basetexture" "models/debug/debugwhite"\n\t"$color2" "[0.32 0.22 0.11]"\n'
              '\t"$phong" "1"\n\t"$phongboost" "2"\n\t"$phongexponent" "20"\n\t"$phongfresnelranges" "[0.4 0.8 1]"\n\t"$surfaceprop" "metal"\n}\n',
    "steel": '"VertexLitGeneric"\n{\n\t"$basetexture" "models/debug/debugwhite"\n\t"$color2" "[0.13 0.14 0.15]"\n'
             '\t"$surfaceprop" "metal"\n}\n',
    "clockface": '"UnlitGeneric"\n{\n\t"$basetexture" "models/debug/debugwhite"\n\t"$color2" "[0.92 0.88 0.76]"\n\t"$surfaceprop" "glass"\n}\n',
    "globe": '"UnlitGeneric"\n{\n\t"$basetexture" "models/debug/debugwhite"\n\t"$color2" "[1 0.9 0.72]"\n\t"$surfaceprop" "glass"\n}\n',
}


def fluted(m, mat, r0, r1, z0, z1, flutes=24, depth=4, rings=6):
    """Tapered shaft with concave flutes: each flute is 4 facets dipping to `depth`."""
    n = flutes * 4
    dip = [0, depth * 0.7, depth, depth * 0.7]
    for k in range(rings):
        za, zb = z0 + (z1 - z0) * k / rings, z0 + (z1 - z0) * (k + 1) / rings
        ra, rb = r0 + (r1 - r0) * k / rings, r0 + (r1 - r0) * (k + 1) / rings
        for j in range(n):
            t0, t1 = 2 * math.pi * j / n, 2 * math.pi * (j + 1) / n
            d0, d1 = dip[j % 4], dip[(j + 1) % 4]
            def v(r, d, z, t, u):
                return ((math.cos(t) * (r - d), math.sin(t) * (r - d), z),
                        (math.cos(t), math.sin(t), 0), (u, z / 128.0))
            m.quad(mat, v(ra, d0, za, t0, j / n * 4), v(ra, d1, za, t1, (j + 1) / n * 4),
                   v(rb, d1, zb, t1, (j + 1) / n * 4), v(rb, d0, zb, t0, j / n * 4))


def corinthian():
    m = Mesh()
    rt = COL_R * 0.86                       # entasis: shaft narrows to the top
    cap_h = 8 * FT
    shaft_top = COL_H - cap_h
    # Attic base: plinth ring, lower torus, scotia, upper torus, fillet.
    m.lathe("travertine", [(0, 0), (COL_R + 14, 0), (COL_R + 14, 10), (COL_R + 12, 12), (COL_R + 14, 18),
                           (COL_R + 10, 24), (COL_R + 4, 26), (COL_R + 4, 30), (COL_R + 9, 33),
                           (COL_R + 6, 38), (COL_R, 40)], 0, 0, 0, 32)
    fluted(m, "travertine", COL_R, rt, 40, shaft_top - 6)
    m.lathe("travertine", [(rt, shaft_top - 6), (rt + 4, shaft_top - 4), (rt + 4, shaft_top), (rt, shaft_top)], 0, 0, 0, 32)
    # Capital: bell flaring to the abacus, two rows of acanthus leaves, corner volutes.
    bell = [(rt, shaft_top), (rt + 2, shaft_top + cap_h * 0.5), (rt + 14, shaft_top + cap_h * 0.85),
            (rt + 20, shaft_top + cap_h * 0.85), (0, shaft_top + cap_h * 0.85)]
    m.lathe("travertine", bell, 0, 0, 0, 32)
    for row, (h, n, r, off) in enumerate(((cap_h * 0.22, 8, rt + 6, 0.0), (cap_h * 0.45, 8, rt + 9, 0.5))):
        for k in range(n):
            t = 2 * math.pi * (k + off) / n
            c = (r * math.cos(t), r * math.sin(t), shaft_top + h)
            m.blob("travertine", c, 9 + 3 * abs(math.cos(t)), 9 + 3 * abs(math.sin(t)), cap_h * 0.2, 6)
    for k in range(4):
        t = math.pi / 4 + k * math.pi / 2
        rv = rt + 20
        m.blob("travertine", (rv * math.cos(t), rv * math.sin(t), shaft_top + cap_h * 0.72), 10, 10, 10, 6)
    # Abacus: square slab with concave-cut sides approximated by a flat square.
    a, z0, z1 = rt + 28, shaft_top + cap_h * 0.85, COL_H
    up, dn = (0, 0, 1), (0, 0, -1)
    uv = lambda x, y: (x / 128.0, y / 128.0)
    c = [(-a, -a), (a, -a), (a, a), (-a, a)]
    m.quad("travertine", *[((x, y, z1), up, uv(x, y)) for x, y in c])
    m.quad("travertine", *[((x, y, z0), dn, uv(x, y)) for x, y in reversed(c)])
    for i in range(4):
        (x0, y0), (x1, y1) = c[i], c[(i + 1) % 4]
        nn = ((y1 - y0) / (2 * a), (x0 - x1) / (2 * a), 0)
        m.quad("travertine", ((x0, y0, z0), nn, (0, 0)), ((x1, y1, z0), nn, (1, 0)),
               ((x1, y1, z1), nn, (1, 0.3)), ((x0, y0, z1), nn, (0, 0.3)))
    return m


LAMP_GLOBE_Z = 15 * FT    # globe centres above the floor; build_vmf.py puts a light there


def lamp():
    """Arcade lamp standard (session 13, after Pennell's etching): a bronze candelabrum, stepped
    base, fluted post, four arms and a top finial, each ending in a frosted globe. Origin on the floor."""
    m = Mesh()
    m.lathe("bronze", [(0, 0), (20, 0), (20, 4), (16, 6), (16, 12), (12, 14), (9, 18), (6, 24), (0, 24)], 0, 0, 0, 16)
    fluted(m, "bronze", 5, 4, 24, 13 * FT, flutes=8, depth=1.2, rings=2)
    top = 13 * FT
    m.lathe("bronze", [(0, top), (8, top), (8, top + 3), (5, top + 6), (5, top + 12), (0, top + 12)], 0, 0, 0, 16)
    g = LAMP_GLOBE_Z
    for k in range(4):
        t = math.pi / 4 + k * math.pi / 2
        ex, ey = 30 * math.cos(t), 30 * math.sin(t)
        m.tube("bronze", (0, 0, top + 6), (ex, ey, g - 10), 2, 1.5, 6)
        m.lathe("bronze", [(0, g - 13), (4, g - 13), (5, g - 8), (0, g - 8)], ex, ey, 0, 10)
        m.sphere("globe", ex, ey, g, 8, 8)
    m.sphere("globe", 0, 0, top + 22, 9, 8)
    return m


def cassatt():
    """Weinman's bronze of Alexander Cassatt (session 14), simplified to a standing figure about
    9 ft tall in a long frock coat: plinth, coat as a lathe, arms as tubes, head. Origin on the floor
    of its niche pedestal top."""
    m = Mesh()
    m.lathe("bronze", [(0, 0), (16, 0), (16, 4), (0, 4)], 0, 0, 0, 12)
    # Coat hem flaring out at the knees, waist, chest, shoulders, collar.
    m.lathe("bronze", [(0, 4), (11, 4), (12, 40), (10, 60), (9, 72), (11, 88), (12, 94), (7, 99), (4, 102), (0, 102)], 0, 0, 0, 14)
    m.sphere("bronze", 0, 0, 108, 6, 10)
    m.tube("bronze", (0, -11, 92), (2, -13, 58), 3, 2.5, 8)       # right arm hanging
    m.tube("bronze", (0, 11, 92), (5, 9, 66), 3, 2.5, 8)          # left arm bent forward
    m.tube("bronze", (5, 9, 66), (10, 4, 62), 2.5, 2, 8)
    return m


DORIC_H = 35 * FT        # Seventh Avenue colonnade: 35 ft x 4 ft 6 in (dimensions note)


def doric():
    """Roman Doric column of the Seventh Avenue colonnade (session 15): no base, 20 shallow
    flutes with entasis, necking ring, echinus and a square abacus. Origin on the stylobate."""
    m = Mesh()
    r0, rt, cap = 27, 23, 3 * FT
    top = DORIC_H - cap
    fluted(m, "travertine", r0, rt, 0, top - 8, flutes=20, depth=3, rings=5)
    m.lathe("travertine", [(rt, top - 8), (rt + 2, top - 6), (rt + 2, top - 2), (rt, top), (0, top)], 0, 0, 0, 24)
    m.lathe("travertine", [(rt, top), (rt, top + 8), (rt + 3, top + 10), (rt + 9, top + 18), (rt + 10, top + 22),
                           (0, top + 22)], 0, 0, 0, 24)
    a, z0, z1 = rt + 12, top + 22, DORIC_H
    up, dn = (0, 0, 1), (0, 0, -1)
    c = [(-a, -a), (a, -a), (a, a), (-a, a)]
    m.quad("travertine", *[((x, y, z1), up, (x / 128.0, y / 128.0)) for x, y in c])
    m.quad("travertine", *[((x, y, z0), dn, (x / 128.0, y / 128.0)) for x, y in reversed(c)])
    for i in range(4):
        (x0, y0), (x1, y1) = c[i], c[(i + 1) % 4]
        nn = ((y1 - y0) / (2 * a), (x0 - x1) / (2 * a), 0)
        m.quad("travertine", ((x0, y0, z0), nn, (0, 0)), ((x1, y1, z0), nn, (1, 0)),
               ((x1, y1, z1), nn, (1, 0.1)), ((x0, y0, z1), nn, (0, 0.1)))
    return m


LAT_H = 45 * FT          # concourse lattice column: floor to the vault springing (build_vmf.py C_SPRING)


def _bar(m, mat, a, b, w):
    """Square-section steel bar from a to b, w across, as four long quads (ends hide in the joints)."""
    ax = [b[i] - a[i] for i in range(3)]
    ln = math.sqrt(sum(c * c for c in ax)) or 1
    wv = [c / ln for c in ax]
    up = (1, 0, 0) if abs(wv[0]) < 0.9 else (0, 1, 0)
    u = [wv[1] * up[2] - wv[2] * up[1], wv[2] * up[0] - wv[0] * up[2], wv[0] * up[1] - wv[1] * up[0]]
    lu = math.sqrt(sum(c * c for c in u))
    u = [c / lu for c in u]
    v = [wv[1] * u[2] - wv[2] * u[1], wv[2] * u[0] - wv[0] * u[2], wv[0] * u[1] - wv[1] * u[0]]
    h = w / 2
    cs = [(-h, -h), (h, -h), (h, h), (-h, h)]
    P = lambda base, p, q: tuple(base[k] + u[k] * p + v[k] * q for k in range(3))
    for i in range(4):
        (p0, q0), (p1, q1) = cs[i], cs[(i + 1) % 4]
        nx, ny = (p0 + p1) / w, (q0 + q1) / w
        n = tuple(u[k] * nx + v[k] * ny for k in range(3))
        m.quad(mat, (P(a, p0, q0), n, (0, 0)), (P(a, p1, q1), n, (1, 0)),
               (P(b, p1, q1), n, (1, ln / 64)), (P(b, p0, q0), n, (0, ln / 64)))


def lattice():
    """Concourse steel column (session 19, HABS photos): four angle posts on a 3 ft square tied by
    zigzag lacing on every face, a base shoe, and a cap from which four curved arch ribs flare out
    along +-x and +-y into the glass vaults. Origin on the floor."""
    m = Mesh()
    h, c = LAT_H, 16
    m.lathe("steel", [(0, 0), (30, 0), (30, 6), (24, 10), (22, 24), (0, 24)], 0, 0, 0, 4)
    corners = [(-c, -c), (c, -c), (c, c), (-c, c)]
    for x, y in corners:
        _bar(m, "steel", (x, y, 20), (x, y, h - 18), 5)
    step = 30
    for i in range(4):
        (x0, y0), (x1, y1) = corners[i], corners[(i + 1) % 4]
        z, k = 24, 0
        while z + step <= h - 24:
            a, b = ((x0, y0), (x1, y1)) if k % 2 == 0 else ((x1, y1), (x0, y0))
            _bar(m, "steel", (a[0], a[1], z), (b[0], b[1], z + step), 2.5)
            z += step
            k += 1
    m.lathe("steel", [(0, h - 24), (22, h - 24), (22, h - 12), (28, h - 8), (28, h), (0, h)], 0, 0, 0, 4)
    # Flared arch ribs: quarter curves from the cap rising 10 ft while reaching 16 ft out.
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        pts = []
        for j in range(7):
            t = j / 6 * math.pi / 2
            r, z = 16 * FT * (1 - math.cos(t)), h - 12 + 10 * FT * math.sin(t)
            pts.append((dx * (c + r), dy * (c + r), z))
        for p, q in zip(pts, pts[1:]):
            _bar(m, "steel", p, q, 8)
    return m


CONC_HX, CONC_HY = 3772 // 6, 100 * FT   # concourse bay half-width (build_vmf.py BAYS) and half-depth
CONC_SPRING, CONC_RISE = 45 * FT, 55 * FT  # build_vmf.py C_SPRING, C_RISE


def _truss(m, curve, depth=20, n=24):
    """Steel truss rib under a vault: an outer chord 4 u below the glass, an inner chord `depth`
    lower, zigzag lacing between them. curve(t, inset) -> point for t in 0..pi."""
    outer = [curve(math.pi * i / n, 4) for i in range(n + 1)]
    inner = [curve(math.pi * i / n, 4 + depth) for i in range(n + 1)]
    for ch in (outer, inner):
        for p, q in zip(ch, ch[1:]):
            _bar(m, "steel", p, q, 6)
    for i in range(n):
        a, b = (outer[i], inner[i + 1]) if i % 2 == 0 else (inner[i], outer[i + 1])
        _bar(m, "steel", a, b, 3)


def conc_arch():
    """Session 20: transverse arch across the concourse at an inner bay line, following the glass
    vaults' profile across y (spring 45 ft, rise 55 ft over the 200 ft depth). Origin: floor, mid-depth."""
    m = Mesh()
    hy, zs, rise = CONC_HY, CONC_SPRING, CONC_RISE
    _truss(m, lambda t, k: (0, (hy - k) * math.cos(t), zs + (rise - k) * math.sin(t)), depth=30)
    return m


def conc_diag():
    """Session 20: the two diagonal ribs on one glass groin vault's groins (corner to corner over
    the crown). Origin: floor at the bay centre."""
    m = Mesh()
    hx, hy, zs, rise = CONC_HX, CONC_HY, CONC_SPRING, CONC_RISE
    for sx in (1, -1):
        _truss(m, lambda t, k, sx=sx: (sx * hx * math.cos(t), hy * math.cos(t), zs + rise * math.sin(t) - k))
    return m


CLOCK_R = 5 * FT


def clock():
    """Session 24: concourse clock, a round face 10 ft across in a moulded bronze rim, twelve bronze
    hour bars and hands at ten past ten. Built facing SMD +x, which studiomdl turns to world -y at
    yaw 0 (session 21), so it faces into the concourse from the east wall. Origin: back of the rim, centre."""
    m = Mesh()
    R = CLOCK_R
    o, u, v, w = (0, 0, 0), (0, 1, 0), (0, 0, 1), (1, 0, 0)
    m.frame("bronze", [(R - 6, 0), (R + 8, 0), (R + 10, 4), (R + 8, 10), (R + 3, 13), (R, 12), (R - 2, 8)], o, u, v, w, 32)
    m.frame("clockface", [(R - 2, 8), (0, 8)], o, u, v, w, 32)
    for k in range(12):
        t = 2 * math.pi * k / 12
        a, b = R - (16 if k % 3 == 0 else 10), R - 4
        _bar(m, "bronze", (9, a * math.sin(t), a * math.cos(t)), (9, b * math.sin(t), b * math.cos(t)), 4 if k % 3 == 0 else 3)
    for t, ln, wd in ((2 * math.pi * (10 + 1 / 6) / 12, R * 0.55, 4), (2 * math.pi * 2 / 12, R * 0.82, 3)):
        _bar(m, "bronze", (10, -6 * math.sin(t), -6 * math.cos(t)), (10, ln * math.sin(t), ln * math.cos(t)), wd)
    m.frame("bronze", [(0, 8), (4, 9), (3, 12), (0, 12)], o, u, v, w, 12)
    return m


MODELS = {"clock": clock, "conc_arch": conc_arch, "conc_diag": conc_diag, "lattice": lattice, "corinthian": corinthian, "lamp": lamp, "cassatt": cassatt, "doric": doric}


def build():
    SRC.mkdir(parents=True, exist_ok=True)
    MAT.mkdir(parents=True, exist_ok=True)
    gmat = G / "garrysmod" / "materials" / "models" / "penn"
    gmat.mkdir(parents=True, exist_ok=True)
    for name, text in VMTS.items():
        (MAT / f"{name}.vmt").write_text(text, encoding="ascii", newline="\n")
        shutil.copy(MAT / f"{name}.vmt", gmat)
    out = ROOT / "src" / "models" / "penn"
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in MODELS.items():
        (SRC / f"{name}.smd").write_text(fn().smd(), encoding="ascii", newline="\n")
        (SRC / f"{name}.qc").write_text(
            f'$modelname "penn/{name}.mdl"\n$body body "{name}.smd"\n$cdmaterials "models/penn/"\n'
            f'$staticprop\n$surfaceprop "stone"\n$sequence idle "{name}.smd"\n', encoding="ascii", newline="\n")
        r = subprocess.run([str(G / "bin" / "studiomdl.exe"), "-game", str(G / "garrysmod"), "-nop4",
                            str(SRC / f"{name}.qc")], capture_output=True, text=True)
        if r.returncode or "ERROR" in r.stdout:
            raise SystemExit(r.stdout[-2000:] + r.stderr[-1000:])
        for f in (G / "garrysmod" / "models" / "penn").glob(f"{name}.*"):
            shutil.copy(f, out)
        print("built", name, sorted(p.name for p in out.glob(f"{name}.*")))


if __name__ == "__main__":
    build()
