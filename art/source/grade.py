"""Fades the bottom of a render into the next section and adds a little dither."""
import sys
import numpy as np
from PIL import Image

src, dst, start, end = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
a = np.asarray(Image.open(src).convert("RGB")).astype("f4")
h, w, _ = a.shape
t = np.clip((np.arange(h) / h - start) / (end - start), 0, 1)
t = t * t * (3 - 2 * t)
target = np.array([26, 26, 26], "f4")
a = a * (1 - t)[:, None, None] + target * t[:, None, None]
rng = np.random.default_rng(7)
a += rng.normal(0, 1.1, (h, w, 1))
Image.fromarray(np.clip(a, 0, 255).astype("u1")).save(dst)
