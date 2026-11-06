"""Three invented circuits, drawn as raised ribbons. None follows a real venue."""
import numpy as np
from scipy.interpolate import splev, splprep
from mesh import *

LAYOUTS = {
    "harbour": [
        (-0.82, -0.62), (-0.2, -0.78), (0.34, -0.74), (0.62, -0.52), (0.42, -0.30), (0.74, -0.08), (0.84, 0.30),
        (0.56, 0.42), (0.40, 0.20), (0.16, 0.26), (0.20, 0.60), (-0.08, 0.76), (-0.30, 0.48), (-0.22, 0.14),
        (-0.52, 0.06), (-0.60, 0.40), (-0.86, 0.34), (-0.80, -0.10), (-0.60, -0.28), (-0.86, -0.42),
    ],
    "forest": [
        (-0.70, -0.72), (-0.10, -0.60), (0.40, -0.76), (0.76, -0.52), (0.60, -0.16), (0.22, -0.20), (0.06, 0.02),
        (0.40, 0.14), (0.78, 0.22), (0.72, 0.62), (0.26, 0.74), (-0.08, 0.50), (-0.34, 0.74), (-0.72, 0.60),
        (-0.60, 0.26), (-0.28, 0.20), (-0.34, -0.10), (-0.76, -0.16), (-0.86, -0.46),
    ],
    "airfield": [
        (-0.84, -0.50), (-0.30, -0.70), (0.30, -0.70), (0.80, -0.56), (0.86, -0.18), (0.50, -0.14), (0.36, 0.10),
        (0.70, 0.30), (0.82, 0.62), (0.40, 0.72), (0.06, 0.50), (-0.20, 0.72), (-0.70, 0.72), (-0.84, 0.40),
        (-0.46, 0.22), (-0.14, 0.26), (-0.10, -0.04), (-0.50, -0.14), (-0.84, -0.12),
    ],
}


def path(name, n=1400):
    c = np.array(LAYOUTS[name] + [LAYOUTS[name][0]], "f8")
    tck, _ = splprep([c[:, 0], c[:, 1]], s=0.0015, per=True)
    u = np.linspace(0, 1, n)
    x, z = splev(u, tck)
    y = 0.045 + 0.02 * np.sin(u * 2 * np.pi * 2 + 0.6)
    if name == "forest":
        y = 0.05 + 0.05 * (0.5 + 0.5 * np.sin(u * 2 * np.pi + 0.4)) + 0.012 * np.sin(u * 2 * np.pi * 5)
    return np.stack([np.array(x), y, np.array(z)], 1)


def ribbon(p, w, h):
    o = np.array([(-w, 0.0), (w, 0.0), (w, 1.0), (-w, 1.0)], "f8")
    t = np.linspace(0, 1, 6, endpoint=False)
    out = []
    for i in range(4):
        a, b = o[i], o[(i + 1) % 4]
        for s in t:
            out.append(a * (1 - s) + b * s)
    out = np.array(out)
    N = len(p)
    tv, sv, uv = frames(p)
    P = np.zeros((N, len(out), 3))
    for j, (a, b) in enumerate(out):
        P[:, j, 0] = p[:, 0] + sv[:, 0] * a
        P[:, j, 1] = p[:, 1] * b
        P[:, j, 2] = p[:, 2] + sv[:, 2] * a
    return grid_part(P, "accent", wrap_m=True)


for name in LAYOUTS:
    p = path(name)
    road = ribbon(p, 0.021, 1.0)
    i = 40
    line = ribbon(p[i:i + 18], 0.026, 1.06)
    line = Part(line.pos, line.nor, line.idx, "line")
    export({"track": road, "start": line}, "track_" + name)
    print(name, len(road.idx))
