"""Denoises the graded hero renders, then writes AVIF and WebP at each size."""
import subprocess
import sys
import cv2
import numpy as np

repo = "../../img/hero/"
quick = len(sys.argv) > 1
jobs = [("shots/hero_d_g.png", "hero", (1280, 1920, 2400), 9 / 16), ("shots/hero_p_g.png", "hero-phone", (780, 1170), 1800 / 1170)]
for src, name, widths, ratio in jobs:
    im = cv2.imread(src)
    if not quick:
        im = cv2.fastNlMeansDenoisingColored(im, None, 2.2, 3.0, 5, 15)
        noise = np.random.default_rng(3).normal(0, 0.9, im.shape[:2] + (1,))
        im = np.clip(im.astype("f4") + noise, 0, 255).astype("u1")
    for w in widths:
        h = round(w * ratio)
        r = cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA)
        tmp = f"shots/_t{w}.png"
        cv2.imwrite(tmp, r)
        q = 68
        subprocess.run(["avifenc", "-q", str(q), "--speed", "8" if quick else "4", "--yuv", "444", "-j", "6", tmp, f"{repo}{name}-{w}.avif"], check=True, capture_output=True)
        subprocess.run(["cwebp", "-quiet", "-q", "80", "-m", "6", tmp, "-o", f"{repo}{name}-{w}.webp"], check=True)
