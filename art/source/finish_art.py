"""Denoises and fades each render, ready for poster type and final encoding."""
import glob
import os
import subprocess
import cv2
import numpy as np

repo = "../../img/collections/"
os.makedirs(repo, exist_ok=True)
os.makedirs("shots/art_g", exist_ok=True)
for f in sorted(glob.glob("shots/art/*.png")):
    n = os.path.basename(f)[:-4]
    im = cv2.imread(f)
    im = cv2.fastNlMeansDenoisingColored(im, None, 3.0, 4.0, 5, 15)
    h, w = im.shape[:2]
    s, e = (0.72, 1.0) if n.startswith("tile") else (0.56, 0.86)
    t = np.clip((np.arange(h) / h - s) / (e - s), 0, 1)
    t = t * t * (3 - 2 * t)
    a = im.astype("f4") * (1 - t)[:, None, None]
    a += np.random.default_rng(5).normal(0, 0.9, (h, w, 1))
    a = np.clip(a, 0, 255).astype("u1")
    if n.startswith("tile"):
        tmp = "shots/_tile.png"
        cv2.imwrite(tmp, cv2.resize(a, (640, 640), interpolation=cv2.INTER_AREA))
        out = {"tile-tracks": "tracks", "tile-liveries": "liveries", "tile-helmets": "helmets", "tile-offer": "offer"}[n]
        subprocess.run(["cwebp", "-quiet", "-q", "76", "-m", "6", tmp, "-o", f"{repo}{out}.webp"], check=True)
    else:
        cv2.imwrite(f"shots/art_g/{n}.png", a)
