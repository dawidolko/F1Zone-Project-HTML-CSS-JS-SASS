"""A generic closed-face race helmet, meshed from a signed distance field."""
import numpy as np
from skimage.measure import marching_cubes
from mesh import *


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b + (a - b) * h - k * h * (1 - h)


def smax(a, b, k):
    return -smin(-a, -b, k)


def ell(x, y, z, c, r):
    q = np.sqrt(((x - c[0]) / r[0]) ** 2 + ((y - c[1]) / r[1]) ** 2 + ((z - c[2]) / r[2]) ** 2)
    return (q - 1) * min(r)


def outer(x, y, z):
    skull = ell(x, y, z, (0, 0.028, -0.008), (0.116, 0.118, 0.142))
    back = ell(x, y, z, (0, -0.045, -0.052), (0.104, 0.094, 0.096))
    chin = ell(x, y, z, (0, -0.094, 0.082), (0.074, 0.040, 0.092))
    cheek = ell(x, y, z, (0, -0.062, 0.018), (0.103, 0.070, 0.120))
    d = smin(smin(smin(skull, back, 0.035), cheek, 0.03), chin, 0.03)
    return smax(d, -0.142 - y + 0.14 * np.maximum(-z, 0), 0.01)


def window(x, y, z, grow=0.0):
    a = np.arctan2(np.abs(x), z)
    top = 0.052 + grow - 0.026 * (a / 1.15) ** 2
    bot = -0.016 - grow + 0.022 * (a / 1.15) ** 2
    d1 = np.maximum(y - top, bot - y)
    return smax(d1, (a - (1.16 + grow * 6)) * 0.1, 0.01)


def vents(x, y, z):
    d = np.full_like(x, 1.0)
    for i in range(2):
        yc = -0.084 - i * 0.017
        s = np.maximum(np.abs(y - yc) - 0.0032, np.abs(x) - (0.030 - i * 0.008))
        d = np.minimum(d, np.maximum(s, 0.12 - z))
    return d


def shell(x, y, z):
    d = smax(outer(x, y, z), -window(x, y, z), 0.004)
    d = smax(d, -vents(x, y, z), 0.002)
    return smax(d, -(outer(x, y, z) + 0.006), 0.002)


def visor(x, y, z):
    o = np.abs(outer(x, y, z) - 0.0015) - 0.0022
    return smax(o, window(x, y, z, 0.007) * 1.0, 0.002)


def inner(x, y, z):
    return ell(x, y, z, (0, -0.005, -0.01), (0.104, 0.118, 0.128))


def sdf_mesh(fn, h, mat):
    xs = np.arange(-0.16, 0.16, h)
    ys = np.arange(-0.19, 0.17, h)
    zs = np.arange(-0.17, 0.19, h)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    vol = fn(X, Y, Z).astype("f4")
    v, f, _, _ = marching_cubes(vol, 0.0, spacing=(h, h, h))
    v = v.astype("f8") + np.array([xs[0], ys[0], zs[0]])
    e = h * 0.35
    for _ in range(3):
        d = fn(v[:, 0], v[:, 1], v[:, 2])
        g = np.stack(
            [
                fn(v[:, 0] + e, v[:, 1], v[:, 2]) - fn(v[:, 0] - e, v[:, 1], v[:, 2]),
                fn(v[:, 0], v[:, 1] + e, v[:, 2]) - fn(v[:, 0], v[:, 1] - e, v[:, 2]),
                fn(v[:, 0], v[:, 1], v[:, 2] + e) - fn(v[:, 0], v[:, 1], v[:, 2] - e),
            ],
            1,
        ) / (2 * e)
        v -= (d / np.maximum((g * g).sum(1), 1e-6))[:, None] * g * 0.7
    return Part(v, normalize(g), f.astype("i8"), mat)


if __name__ == "__main__":
    parts = {
        "body": sdf_mesh(shell, 0.0016, "paint"),
        "visor": sdf_mesh(visor, 0.0013, "visor"),
        "inner": sdf_mesh(inner, 0.003, "matte"),
    }
    zone = np.zeros(len(parts["body"].pos), "f4")
    p = parts["body"].pos
    zone = (outer(p[:, 0], p[:, 1], p[:, 2]) < -0.0015).astype("f4")
    export(parts, "helmet", {"body": zone})
    print({k: len(v.idx) for k, v in parts.items()})
