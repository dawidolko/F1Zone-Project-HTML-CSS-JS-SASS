"""F1Zone hero car: an invented open-wheel race car. All geometry is generated here."""
import sys
import time
import numpy as np
from scipy.interpolate import PchipInterpolator
from skimage.measure import marching_cubes
from mesh import *

H = float(sys.argv[1]) if len(sys.argv) > 1 else 0.012
OUT = sys.argv[2] if len(sys.argv) > 2 else "car"


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b + (a - b) * h - k * h * (1 - h)


def smax(a, b, k):
    return -smin(-a, -b, k)


class Loft:
    """Superellipse sections along z. Columns: z, top, bottom, half width, n, taper, centre x."""

    def __init__(self, rows, mirror=False):
        t = np.array(sorted(rows, key=lambda r: r[0]), "f8")
        self.z0, self.z1 = t[0, 0], t[-1, 0]
        self.lut_z = np.linspace(self.z0, self.z1, 3000)
        self.lut = [PchipInterpolator(t[:, 0], t[:, i])(self.lut_z) for i in range(1, t.shape[1])]
        self.mirror = mirror

    def __call__(self, x, y, z):
        zc = np.clip(z, self.z0, self.z1)
        f = (zc - self.z0) / (self.z1 - self.z0) * (len(self.lut_z) - 1)
        i = np.clip(f.astype("i4"), 0, len(self.lut_z) - 2)
        w = f - i
        v = [l[i] * (1 - w) + l[i + 1] * w for l in self.lut]
        top, bot, a, n, tap, cx = v
        mid, hh = (top + bot) / 2, (top - bot) / 2
        vy = (y - mid) / hh
        ax = a * (1 - tap * np.clip(vy, -1, 1) * 0.5)
        xx = np.abs(np.abs(x) - cx) if self.mirror else np.abs(x)
        vx = xx / ax
        s = (np.abs(vx) ** n + np.abs(vy) ** n) ** (1 / n)
        d = (s - 1) * np.minimum(ax, hh)
        return smax(d, np.maximum(z - self.z1, self.z0 - z), 0.02)


fuselage = Loft(
    [
        (2.76, 0.165, 0.095, 0.045, 2.4, 0.0, 0),
        (2.56, 0.235, 0.100, 0.092, 2.5, 0.0, 0),
        (2.30, 0.305, 0.125, 0.118, 2.6, 0.05, 0),
        (1.95, 0.375, 0.170, 0.128, 2.7, 0.10, 0),
        (1.60, 0.480, 0.190, 0.150, 2.8, 0.15, 0),
        (1.30, 0.610, 0.130, 0.212, 3.0, 0.20, 0),
        (0.95, 0.700, 0.065, 0.275, 3.2, 0.22, 0),
        (0.50, 0.690, 0.060, 0.305, 3.2, 0.20, 0),
        (0.10, 0.730, 0.060, 0.330, 3.2, 0.18, 0),
        (-0.30, 0.760, 0.070, 0.320, 3.0, 0.20, 0),
        (-0.80, 0.690, 0.090, 0.255, 3.0, 0.20, 0),
        (-1.30, 0.580, 0.120, 0.170, 3.0, 0.20, 0),
        (-1.80, 0.470, 0.160, 0.110, 3.0, 0.15, 0),
        (-2.20, 0.410, 0.210, 0.078, 3.0, 0.1, 0),
        (-2.46, 0.370, 0.260, 0.050, 3.0, 0.0, 0),
    ]
)

spine = Loft(
    [
        (0.04, 0.800, 0.560, 0.090, 2.2, 0.35, 0),
        (-0.10, 0.985, 0.600, 0.128, 2.3, 0.35, 0),
        (-0.45, 0.995, 0.600, 0.132, 2.4, 0.40, 0),
        (-0.90, 0.905, 0.520, 0.105, 2.4, 0.45, 0),
        (-1.40, 0.760, 0.420, 0.062, 2.4, 0.45, 0),
        (-1.95, 0.600, 0.360, 0.032, 2.4, 0.3, 0),
        (-2.22, 0.530, 0.360, 0.020, 2.4, 0.2, 0),
    ]
)

sidepod = Loft(
    [
        (0.86, 0.552, 0.355, 0.180, 3.6, 0.05, 0.62),
        (0.72, 0.566, 0.300, 0.230, 3.6, 0.06, 0.62),
        (0.45, 0.578, 0.230, 0.285, 3.6, 0.08, 0.60),
        (0.05, 0.566, 0.160, 0.300, 3.4, 0.10, 0.55),
        (-0.45, 0.505, 0.105, 0.270, 3.2, 0.12, 0.46),
        (-0.95, 0.435, 0.090, 0.205, 2.8, 0.14, 0.35),
        (-1.35, 0.370, 0.100, 0.125, 2.6, 0.14, 0.25),
        (-1.70, 0.280, 0.125, 0.060, 2.4, 0.1, 0.16),
    ],
    mirror=True,
)


def cut_cockpit(x, y, z):
    q = ((np.abs(x) / 0.225) ** 2.6 + (np.abs(z - 0.40) / 0.50) ** 2.6) ** (1 / 2.6)
    return np.maximum((q - 1) * 0.225, 0.47 - y)


def cut_airbox(x, y, z):
    q = ((np.abs(x) / 0.082) ** 2.2 + (np.abs(y - 0.885) / 0.072) ** 2.2) ** (1 / 2.2)
    return np.maximum((q - 1) * 0.07, np.abs(z + 0.02) - 0.26)


def cut_inlet(x, y, z):
    xx = np.abs(np.abs(x) - 0.635)
    q = ((xx / 0.145) ** 3.5 + (np.abs(y - 0.445) / 0.078) ** 3.5) ** (1 / 3.5)
    return np.maximum((q - 1) * 0.082, 0.56 - z)


def cut_louvres(x, y, z):
    """Cooling slots along the top of each sidepod, angled with the airflow."""
    ax = np.abs(x)
    d = np.full_like(x, 1.0, dtype="f4")
    for i in range(7):
        zc = -0.02 - i * 0.092
        hw = 0.14 - i * 0.008
        xc = 0.54 - i * 0.022
        s = np.maximum(np.abs(z - zc + (ax - xc) * 0.25) - 0.016, np.abs(ax - xc) - hw)
        s = np.maximum(s, 0.50 - i * 0.012 - y)
        d = np.minimum(d, s)
    return d


def body_parts(x, y, z):
    main = smin(fuselage(x, y, z), spine(x, y, z), 0.09)
    main = smin(main, sidepod(x, y, z), 0.11)
    cuts = np.minimum(np.minimum(cut_cockpit(x, y, z), cut_airbox(x, y, z)), cut_inlet(x, y, z))
    cuts = np.minimum(cuts, cut_louvres(x, y, z))
    return main, cuts


def body(x, y, z):
    main, cuts = body_parts(x, y, z)
    return smax(main, -cuts, 0.012)


def mesh_body(h):
    t0 = time.time()
    x0, x1 = -1.12, 1.12
    y0, y1 = 0.0, 1.08
    z0, z1 = -2.56, 2.86
    c = 0.03
    xs = np.arange(x0, x1, c)
    ys = np.arange(y0, y1, c)
    zs = np.arange(z0, z1, c)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    coarse = body(X.astype("f8"), Y.astype("f8"), Z.astype("f8"))
    near = (np.abs(coarse) < 0.09).astype("f4")
    fx = np.arange(x0, x1 - c, h)
    fy = np.arange(y0, y1 - c, h)
    fz = np.arange(z0, z1 - c, h)
    vol = np.zeros((len(fx), len(fy), len(fz)), "f4")
    ix = np.clip(((fx - x0) / c).astype("i4"), 0, len(xs) - 1)
    iy = np.clip(((fy - y0) / c).astype("i4"), 0, len(ys) - 1)
    iz = np.clip(((fz - z0) / c).astype("i4"), 0, len(zs) - 1)
    for k in range(len(fz)):
        m = near[np.ix_(ix, iy, [iz[k]])][:, :, 0] > 0
        s = coarse[np.ix_(ix, iy, [iz[k]])][:, :, 0]
        slc = np.where(s > 0, 0.05, -0.05).astype("f4")
        if m.any():
            a, b = np.nonzero(m)
            slc[a, b] = body(fx[a], fy[b], np.full(len(a), fz[k]))
        vol[:, :, k] = slc
    print("volume", vol.shape, round(time.time() - t0, 1), "s", flush=True)
    v, f, _, _ = marching_cubes(vol, 0.0, spacing=(h, h, h))
    v = v.astype("f8") + np.array([x0, y0, z0])
    print("verts", len(v), "tris", len(f), round(time.time() - t0, 1), "s", flush=True)
    e = 0.0018
    for _ in range(3):
        d = body(v[:, 0], v[:, 1], v[:, 2])
        g = np.stack(
            [
                body(v[:, 0] + e, v[:, 1], v[:, 2]) - body(v[:, 0] - e, v[:, 1], v[:, 2]),
                body(v[:, 0], v[:, 1] + e, v[:, 2]) - body(v[:, 0], v[:, 1] - e, v[:, 2]),
                body(v[:, 0], v[:, 1], v[:, 2] + e) - body(v[:, 0], v[:, 1], v[:, 2] - e),
            ],
            1,
        ) / (2 * e)
        v -= (d / np.maximum((g * g).sum(1), 1e-6))[:, None] * g * 0.8
    n = normalize(g)
    main, cuts = body_parts(v[:, 0], v[:, 1], v[:, 2])
    zone = (cuts < 0.016).astype("f4")
    a, b, c3 = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    fn = np.cross(b - a, c3 - a)
    if (fn * n[f[:, 0]]).sum() < 0:
        f = f[:, ::-1]
    return Part(v, n, f.astype("i8"), "paint"), zone


def tyre(center, width, radius, sign):
    hw = width / 2
    s = 0.055
    th = np.linspace(0, np.pi / 2, 14)
    prof = [(0.228, -hw * 0.86), (0.245, -hw * 0.93), (0.27, -hw * 0.99)]
    prof += [(radius - s + s * np.sin(t), -hw + s * (1 - np.cos(t))) for t in th]
    prof += [(radius + 0.002, x) for x in np.linspace(-hw + s + 0.01, hw - s - 0.01, 8)]
    prof += [(radius - s + s * np.sin(t), hw - s * (1 - np.cos(t))) for t in th[::-1]]
    prof += [(0.27, hw * 0.99), (0.245, hw * 0.93), (0.228, hw * 0.86)]
    return lathe_x(prof, "tyre", center, 420, sign)


def wheel(center, width, sign):
    hw = width / 2
    face = hw * 0.9
    parts = []
    rim = [(0.240, face + 0.000), (0.238, face + 0.012), (0.230, face + 0.015), (0.224, face + 0.006), (0.220, face - 0.03)]
    parts.append(lathe_x(rim, "rim", center, 300, sign))
    dish = [(0.220, face - 0.03), (0.21, face - 0.055), (0.11, face - 0.07), (0.0, face - 0.07)]
    parts.append(lathe_x(dish, "matte", center, 200, sign))
    spokes = []
    n = 9
    for i in range(n):
        a = i * 2 * np.pi / n + 0.2
        twist = 0.16
        rr = np.linspace(0.075, 0.222, 18)
        ang = a + twist * (rr - 0.075) / 0.147
        path = np.stack(
            [
                center[0] + sign * (face - 0.052 + 0.03 * (rr - 0.075) / 0.147),
                center[1] + np.cos(ang) * rr,
                center[2] + np.sin(ang) * rr,
            ],
            1,
        )
        scale = np.linspace(1.15, 0.8, 18)
        spokes.append(sweep(path, ellipse(0.030, 0.009, 18), "spoke", scale=scale, up=(sign, 0, 0)))
    parts.append(merge(spokes))
    hub = [(0.098, face - 0.062), (0.094, face - 0.032), (0.05, face - 0.024), (0.046, face - 0.012), (0.03, face - 0.008), (0.0, face - 0.008)]
    parts.append(lathe_x(hub, "rim", center, 120, sign))
    band = [(0.296, hw * 0.999), (0.297, hw * 1.004), (0.303, hw * 1.004), (0.304, hw * 0.999)]
    parts.append(lathe_x(band, "accent", center, 300, sign))
    return merge(parts, "rim")


def corner(cx, cz, width, r=0.36):
    c = (cx, r, cz)
    return tyre(c, width, r, 1), wheel(c, width, 1)


def front_wing():
    parts = []
    span = 0.975
    xs = np.linspace(-span, span, 161)
    u = np.abs(xs) / span
    sweepback = 0.30 * u**2.0
    els = [
        (0.0, 0.066, 0.270, 3.0, 0.00),
        (-0.225, 0.100, 0.150, 15.0, 0.02),
        (-0.335, 0.142, 0.122, 28.0, 0.05),
        (-0.425, 0.195, 0.105, 42.0, 0.09),
    ]
    for dz, y, c, ang, ramp in els:
        tip = np.clip((u - 0.55) / 0.45, 0, 1)
        centre = np.clip(1 - u / 0.2, 0, 1)
        yy = y + 0.014 * centre**2 + (0.012 + ramp) * tip**2 - (ramp * 0.9) * centre
        zz = 2.90 + dz - sweepback
        aa = ang + 4 * tip
        parts.append(wing(np.stack([xs, yy, zz, c * np.ones_like(xs), aa], 1), "wing", 0.085, -0.07))
    return merge(parts)


def endplate_front():
    o = spline2([(2.68, 0.052), (2.42, 0.046), (2.18, 0.050), (2.135, 0.085), (2.13, 0.205), (2.135, 0.305), (2.18, 0.338), (2.30, 0.335), (2.46, 0.262), (2.62, 0.170), (2.69, 0.095)], 96)
    return plate(o, (0, 0, 1), (0, 1, 0), (0.985, 0, 0), 0.008, "wing", 0.002)


def rear_wing():
    parts = []
    span = 0.50
    xs = np.linspace(-span, span, 81)
    u = np.abs(xs) / span
    dip = 0.055 * (1 - u**2.4)
    main = np.stack([xs, 0.905 - dip, -2.215 - 0.05 * u**2, 0.335 * np.ones_like(xs), 8 + 3 * (1 - u)], 1)
    flap = np.stack([xs, 0.962 - dip * 0.8, -2.525 - 0.05 * u**2, 0.185 * np.ones_like(xs), 34 + 8 * (1 - u)], 1)
    parts.append(wing(main, "wing", 0.11, -0.08))
    parts.append(wing(flap, "wing", 0.10, -0.07))
    bx = np.linspace(-0.44, 0.44, 41)
    beam = np.stack([bx, 0.485 + 0.02 * (bx / 0.44) ** 2, -2.27 * np.ones_like(bx), 0.22 * np.ones_like(bx), 14 * np.ones_like(bx)], 1)
    parts.append(wing(beam, "wing", 0.11, -0.06))
    o = spline2([(-2.13, 0.62), (-2.12, 0.98), (-2.20, 1.06), (-2.46, 1.075), (-2.68, 1.07), (-2.73, 1.00), (-2.71, 0.68), (-2.56, 0.50), (-2.26, 0.49)], 110)
    ep = plate(o, (0, 0, 1), (0, 1, 0), (0.505, 0, 0), 0.008, "wing", 0.002)
    parts.append(both(ep))
    n = spline2([(-2.26, 0.34), (-2.16, 0.46), (-2.26, 0.74), (-2.36, 0.90), (-2.45, 0.90), (-2.46, 0.72), (-2.46, 0.36)], 80)
    pyl = plate(n, (0, 0, 1), (0, 1, 0), (0.02, 0, 0), 0.007, "wing", 0.002)
    parts.append(both(pyl))
    return merge(parts)


def floor_part():
    pts = np.array(
        [
            (1.26, 0.20),
            (1.12, 0.40),
            (0.92, 0.56),
            (0.66, 0.80),
            (0.32, 0.875),
            (-0.60, 0.875),
            (-1.20, 0.81),
            (-1.52, 0.70),
            (-1.86, 0.56),
            (-2.14, 0.50),
        ]
    )
    zs = np.linspace(1.26, -2.14, 220)
    w = PchipInterpolator(pts[::-1, 0], pts[::-1, 1])(zs)
    ybase = 0.042 + 0.10 * np.clip((-zs - 1.45) / 0.69, 0, 1) ** 2
    u = np.linspace(-1, 1, 3)
    grid_top = np.zeros((len(zs), 3, 3))
    grid_bot = np.zeros((len(zs), 3, 3))
    th = 0.018
    for j, s in enumerate(u):
        grid_top[:, j, 0] = s * w
        grid_top[:, j, 1] = ybase + th
        grid_top[:, j, 2] = zs
        grid_bot[:, j, 0] = s * w
        grid_bot[:, j, 1] = ybase - th * 0.3
        grid_bot[:, j, 2] = zs
    top = grid_part(grid_top, "floor")
    top = Part(top.pos, np.abs(top.nor) * np.array([0, 1, 0], "f4") + np.array([0, 1e-3, 0], "f4"), top.idx, "floor")
    if (np.cross(top.pos[top.idx[0, 1]] - top.pos[top.idx[0, 0]], top.pos[top.idx[0, 2]] - top.pos[top.idx[0, 0]])[1]) < 0:
        top = Part(top.pos, top.nor, top.idx[:, ::-1], "floor")
    edge = np.stack([grid_top[:, 2], grid_bot[:, 2]], 1)
    e = grid_part(edge, "floor")
    if e.nor[:, 0].mean() < 0:
        e = Part(e.pos, -e.nor, e.idx[:, ::-1], "floor")
    parts = [top, both(e)]
    for z0, z1, xx in ((1.02, 0.62, 0.36), (1.0, 0.60, 0.46), (0.96, 0.58, 0.56), (0.9, 0.56, 0.66)):
        o = [(z0, 0.05), (z1 - 0.06, 0.05), (z1 - 0.02, 0.125), (z0 - 0.10, 0.145), (z0, 0.10)]
        v = plate(spline2(o, 40), (0, 0, 1), (0, 1, 0), (xx, 0, 0), 0.005, "floor", 0.001)
        parts.append(both(v))
    return merge(parts)


def halo():
    ctrl = [(0, 0.70, 1.02), (0, 0.80, 0.97), (0, 0.885, 0.90)]
    leg = spline3([(0, 0.885, 0.90), (0.09, 0.925, 0.80), (0.19, 0.945, 0.60), (0.25, 0.94, 0.34), (0.265, 0.91, 0.14), (0.262, 0.84, 0.02), (0.255, 0.72, -0.05)], 100)
    a = sweep(leg, ellipse(0.036, 0.024, 40), "halo", scale=np.linspace(1.08, 0.9, len(leg)))
    pil = spline3(ctrl, 30)
    b = sweep(pil, ellipse(0.022, 0.030, 32), "halo")
    return merge([both(a), b])


def suspension():
    p = []
    fz = 1.75
    rz = -1.85
    lo = (0.74, 0.215, fz)
    up = (0.72, 0.505, fz - 0.02)
    p += [strut((0.15, 0.26, fz + 0.22), lo), strut((0.20, 0.26, 1.33), lo)]
    p += [strut((0.13, 0.50, fz + 0.12), up), strut((0.19, 0.55, 1.36), up)]
    p += [strut((0.71, 0.24, fz - 0.03), (0.14, 0.53, 1.62), a=0.018, b=0.012)]
    p += [strut((0.75, 0.36, fz + 0.10), (0.14, 0.36, fz + 0.09), a=0.018, b=0.007)]
    lo = (0.72, 0.215, rz)
    up = (0.70, 0.525, rz)
    p += [strut((0.09, 0.27, rz + 0.36), lo), strut((0.09, 0.27, rz - 0.22), lo)]
    p += [strut((0.09, 0.47, rz + 0.30), up), strut((0.09, 0.47, rz - 0.20), up)]
    p += [strut((0.70, 0.49, rz - 0.04), (0.09, 0.27, rz + 0.1), a=0.016, b=0.010)]
    p += [strut((0.72, 0.37, rz - 0.12), (0.10, 0.38, rz - 0.12), a=0.016, b=0.006)]
    return both(merge(p))


def helmet_shell(c, r=0.135):
    """Closed-face helmet facing plus z. The visor is a band of the same surface."""
    cx, cy, cz = c
    th = np.linspace(0, 2 * np.pi, 160, endpoint=False)
    ph = np.linspace(0.02, np.pi - 0.02, 110)
    P = np.zeros((len(ph), len(th), 3))
    for i, p in enumerate(ph):
        rr = np.sin(p)
        yy = np.cos(p)
        chin = np.clip(-yy, 0, 1)
        fwd = np.sin(th)
        P[i, :, 0] = cx + r * 0.94 * rr * np.cos(th)
        P[i, :, 1] = cy + r * (yy if yy > 0 else yy * 1.06)
        P[i, :, 2] = cz + r * rr * (fwd * (1.08 + 0.10 * chin * np.clip(fwd, 0, 1)) - 0.06)
    part = grid_part(P, "helmet", wrap_m=True)
    c0 = part.pos[part.idx].mean(1) - np.array(c, "f4")
    ang = np.degrees(np.arctan2(c0[:, 0], c0[:, 2]))
    edge = 66 - 10 * np.clip(np.abs(c0[:, 1] - r * 0.1) / (r * 0.3), 0, 1) ** 4
    mask = (np.abs(ang) < edge) & (c0[:, 1] > -r * 0.12) & (c0[:, 1] < r * 0.40)
    a = Part(part.pos, part.nor, part.idx[~mask], "helmet")
    b = Part(part.pos, part.nor, part.idx[mask], "visor")
    return merge([a, b])


def details():
    p = []
    p.append(helmet_shell((0, 0.745, 0.20)))
    p.append(ellipsoid((0, 0.62, 0.17), (0.10, 0.06, 0.10), "matte"))
    f = []
    f.append(ellipsoid((0.455, 0.735, 0.62), (0.072, 0.034, 0.055), "wing"))
    f.append(strut((0.34, 0.70, 0.60), (0.40, 0.73, 0.61), a=0.016, b=0.005))
    f.append(strut((0.05, 0.14, 2.55), (0.05, 0.19, 2.58), a=0.03, b=0.006, up=(0, 0, 1)))
    d = merge(f)
    p.append(both(d))
    p.append(ellipsoid((0, 1.0, -0.20), (0.05, 0.02, 0.09), "wing"))
    fin = spline2([(-0.62, 0.955), (-1.30, 0.885), (-2.10, 0.79), (-2.13, 0.60), (-1.6, 0.66), (-0.9, 0.85)], 80)
    p.append(plate(fin, (0, 0, 1), (0, 1, 0), (0, 0, 0), 0.0045, "fin", 0.001))
    wheelhub = [(0.0, -0.10), (0.15, -0.10), (0.165, -0.05), (0.17, 0.09), (0.0, 0.09)]
    for cx, cz in ((0.70, 1.75), (0.66, -1.85)):
        p.append(both(lathe_x(wheelhub, "wing", (cx, 0.36, cz), 96)))
    sw = spline2([(-0.10, -0.06), (0.10, -0.06), (0.12, 0.05), (0.05, 0.08), (-0.05, 0.08), (-0.12, 0.05)], 40)
    p.append(plate(sw, (1, 0, 0), (0, 1, 0), (0, 0.615, 0.70), 0.018, "matte", 0.002))
    p.append(ellipsoid((0, 0.54, 0.04), (0.17, 0.20, 0.09), "matte"))
    return merge(p), plate([(-0.045, 0.60), (0.045, 0.60), (0.045, 0.64), (-0.045, 0.64)], (1, 0, 0), (0, 1, 0), (0, 0, -2.505), 0.008, "light", 0.001)


if __name__ == "__main__":
    t0 = time.time()
    b, zone = mesh_body(H)
    parts = {"body": b}
    tf, wf = corner(0.875, 1.75, 0.305)
    tr, wr = corner(0.835, -1.85, 0.405)
    parts["tyres"] = merge([both(tf), both(tr)])
    parts["wheels"] = merge([both(wf), both(wr)])
    parts["front_wing"] = merge([front_wing(), both(endplate_front())])
    parts["rear_wing"] = rear_wing()
    parts["floor"] = floor_part()
    parts["halo"] = halo()
    parts["suspension"] = suspension()
    d, light = details()
    parts["details"] = d
    parts["light"] = light
    export(parts, OUT, {"body": zone})
    print({k: len(v.idx) for k, v in parts.items()}, round(time.time() - t0, 1), "s")
