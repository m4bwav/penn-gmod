"""Procedural marble floor for the concourse: 2x2 pale rose-grey slabs with soft
veining and thin joints, colour sampled from refs/photos/GCT_east_windows.jpg
(floor crop, lifted for the lightmap). Writes src/materials/gcs/floor_marble.vtf
and a preview PNG in shots/tex/. Needs pip srctools pillow numpy."""
import numpy as np
from PIL import Image
from srctools import vtf

N, SLABS, SEED = 512, 2, 7
BASE = np.array([138, 124, 116], float)      # photo floor (135,114,108); session 52 (was 160 138 128, 196 178 168)
rng = np.random.default_rng(SEED)


def fbm(n, octaves=6):
    out = np.zeros((n, n))
    for o in range(octaves):
        k = 4 * 2**o
        g = rng.random((k, k))
        img = Image.fromarray((g * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC)
        out += (np.asarray(img, float) / 255 - .5) / 2**o
    return out


y, x = np.mgrid[0:N, 0:N] / N
img = np.zeros((N, N, 3))
s = N // SLABS
for i in range(SLABS):
    for j in range(SLABS):
        sl = (slice(i*s, (i+1)*s), slice(j*s, (j+1)*s))
        a = rng.random() * np.pi
        t = (np.cos(a)*x[sl] + np.sin(a)*y[sl]) * 9 + fbm(s, 5) * 6
        vein = np.abs(np.sin(t)) ** 0.15                 # dark thin veins near zero
        cloud = fbm(s, 6) * 0.10 + rng.uniform(-.04, .04)
        img[sl] = BASE * (1 + cloud)[..., None] * (0.82 + 0.18*vein)[..., None]
joint = np.zeros((N, N), bool)
for k in range(SLABS):
    joint[k*s:k*s+2, :] = joint[:, k*s:k*s+2] = True
img[joint] = BASE * 0.7
rgb = np.clip(img, 0, 255).astype(np.uint8)
Image.fromarray(rgb).save("shots/tex/floor_marble.png")

tex = vtf.VTF(N, N, fmt=vtf.ImageFormats.RGB888)
rgba = np.dstack([rgb, np.full((N, N), 255, np.uint8)])
tex.get().copy_from(rgba.tobytes(), vtf.ImageFormats.RGBA8888)
tex.compute_mipmaps()
with open("src/materials/gcs/floor_marble.vtf", "wb") as f:
    tex.save(f)
print("wrote src/materials/gcs/floor_marble.vtf")
