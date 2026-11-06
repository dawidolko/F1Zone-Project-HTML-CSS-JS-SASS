"""Mesh helpers: sweeps, lathes, extrusions, ear clipping, and binary export."""
import json
import numpy as np


def normalize(v):
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    n[n == 0] = 1
    return v / n


class Part:
    def __init__(self, pos, nor, idx, mat):
        self.pos, self.nor, self.idx, self.mat = pos.astype("f4"), nor.astype("f4"), idx.astype("u4"), mat


def grid_faces(n, m, wrap_m=False):
    i, j = np.meshgrid(np.arange(n - 1), np.arange(m if wrap_m else m - 1), indexing="ij")
    j2 = (j + 1) % m
    a = i * m + j
    b = (i + 1) * m + j
    c = (i + 1) * m + j2
    d = i * m + j2
    return np.stack([np.stack([a, b, c], -1), np.stack([a, c, d], -1)], 2).reshape(-1, 3)


def grid_part(P, mat, wrap_m=False, flip=False):
    """P is an n by m by 3 grid of points. Normals come from grid tangents."""
    n, m, _ = P.shape
    du = np.gradient(P, axis=0)
    if wrap_m:
        dv = np.roll(P, -1, 1) - np.roll(P, 1, 1)
    else:
        dv = np.gradient(P, axis=1)
    N = normalize(np.cross(dv, du))
    idx = grid_faces(n, m, wrap_m)
    if flip:
        N = -N
        idx = idx[:, ::-1]
    return Part(P.reshape(-1, 3), N.reshape(-1, 3), idx, mat)


def merge(parts, mat=None):
    pos, nor, idx, off = [], [], [], 0
    groups = []
    start = 0
    for p in parts:
        pos.append(p.pos)
        nor.append(p.nor)
        idx.append(p.idx + off)
        off += len(p.pos)
        for s, c, m in getattr(p, "groups", None) or [(0, len(p.idx), p.mat)]:
            groups.append((start + s, c, m))
        start += len(p.idx)
    out = Part(np.concatenate(pos), np.concatenate(nor), np.concatenate(idx), mat or parts[0].mat)
    out.groups = groups
    return out


def mirror_x(p):
    pos = p.pos * np.array([-1, 1, 1], "f4")
    nor = p.nor * np.array([-1, 1, 1], "f4")
    out = Part(pos, nor, p.idx[:, ::-1], p.mat)
    out.groups = getattr(p, "groups", None)
    return out


def both(p):
    return merge([p, mirror_x(p)])


def frames(path, up=(0, 1, 0)):
    t = normalize(np.gradient(path, axis=0))
    up = np.array(up, "f8")
    s = normalize(np.cross(t, up))
    u = normalize(np.cross(s, t))
    return t, s, u


def sweep(path, outline, mat, scale=None, up=(0, 1, 0), caps=True):
    """Sweep a closed 2D outline along path. scale may be a per-station factor."""
    path = np.asarray(path, "f8")
    t, s, u = frames(path, up)
    outline = np.asarray(outline, "f8")
    k = np.ones(len(path)) if scale is None else np.asarray(scale, "f8")
    P = path[:, None, :] + (outline[None, :, 0, None] * k[:, None, None]) * s[:, None, :] + (
        outline[None, :, 1, None] * k[:, None, None]
    ) * u[:, None, :]
    part = grid_part(P, mat, wrap_m=True, flip=False)
    c = part.pos.reshape(P.shape).mean(1)
    side = (part.nor.reshape(P.shape) * (P - c[:, None, :])).sum(-1).mean()
    if side < 0:
        part = Part(part.pos, -part.nor, part.idx[:, ::-1], mat)
    if not caps:
        return part
    parts = [part]
    for i, sign in ((0, -1), (len(path) - 1, 1)):
        ring = P[i]
        cen = ring.mean(0)
        pos = np.vstack([ring, cen[None]])
        nor = np.tile(t[i] * sign, (len(pos), 1))
        m = len(ring)
        idx = np.stack([np.full(m, m), np.arange(m), (np.arange(m) + 1) % m], 1)
        tri = pos[idx]
        if (np.cross(tri[0, 1] - tri[0, 0], tri[0, 2] - tri[0, 0]) * nor[0]).sum() < 0:
            idx = idx[:, ::-1]
        parts.append(Part(pos, nor, idx, mat))
    return merge(parts)


def ellipse(a, b, n=48):
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.stack([a * np.cos(th), b * np.sin(th)], 1)


def strut(p0, p1, a=0.024, b=0.008, mat="carbon", n=2, up=(0, 1, 0)):
    p0, p1 = np.array(p0, "f8"), np.array(p1, "f8")
    path = np.linspace(p0, p1, max(n, 2))
    return sweep(path, ellipse(a, b, 24), mat, up=up)


def lathe_x(profile, mat, center, seg=360, sign=1):
    """Revolve (r, x) profile round the x axis. Normals follow the profile tangent."""
    prof = np.asarray(profile, "f8")
    th = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    r, x = prof[:, 0], prof[:, 1] * sign
    P = np.zeros((len(prof), seg, 3))
    P[..., 0] = center[0] + x[:, None]
    P[..., 1] = center[1] + r[:, None] * np.cos(th)
    P[..., 2] = center[2] + r[:, None] * np.sin(th)
    part = grid_part(P, mat, wrap_m=True)
    c = np.array(center, "f8")
    radial = part.pos - np.stack([part.pos[:, 0], np.full(len(part.pos), c[1]), np.full(len(part.pos), c[2])], 1)
    outward = (part.nor * radial).sum(1)
    if outward.sum() < 0:
        part = Part(part.pos, -part.nor, part.idx[:, ::-1], mat)
    return part


def ellipsoid(c, r, mat, n=48, m=32):
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ph = np.linspace(1e-3, np.pi - 1e-3, m)
    P = np.zeros((m, n, 3))
    P[..., 0] = c[0] + r[0] * np.sin(ph)[:, None] * np.cos(th)
    P[..., 1] = c[1] + r[1] * np.cos(ph)[:, None] * np.ones(n)
    P[..., 2] = c[2] + r[2] * np.sin(ph)[:, None] * np.sin(th)
    nor = normalize((P - np.array(c)) / np.array(r) ** 2)
    idx = grid_faces(m, n, True)
    tri = P.reshape(-1, 3)[idx[0]]
    if (np.cross(tri[1] - tri[0], tri[2] - tri[0]) * nor.reshape(-1, 3)[idx[0, 0]]).sum() < 0:
        idx = idx[:, ::-1]
    return Part(P.reshape(-1, 3), nor.reshape(-1, 3), idx, mat)


def earclip(poly):
    pts = [tuple(p) for p in poly]
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    ids = list(range(len(pts)))
    if area < 0:
        ids.reverse()
    tris = []

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    guard = 0
    while len(ids) > 3 and guard < 200000:
        guard += 1
        clipped = False
        for k in range(len(ids)):
            i0, i1, i2 = ids[k - 1], ids[k], ids[(k + 1) % len(ids)]
            a, b, c = pts[i0], pts[i1], pts[i2]
            if cross(a, b, c) <= 1e-12:
                continue
            inside = False
            for j in ids:
                if j in (i0, i1, i2):
                    continue
                p = pts[j]
                if cross(a, b, p) >= 0 and cross(b, c, p) >= 0 and cross(c, a, p) >= 0:
                    inside = True
                    break
            if inside:
                continue
            tris.append((i0, i1, i2))
            ids.pop(k)
            clipped = True
            break
        if not clipped:
            break
    if len(ids) == 3:
        tris.append(tuple(ids))
    return np.array(tris)


def plate(outline, axis_u, axis_v, origin, half_t, mat, bevel=0.0):
    """Extrude a closed 2D outline by half_t on both sides, with flat faces and a rim."""
    out = np.asarray(outline, "f8")
    u, v = np.array(axis_u, "f8"), np.array(axis_v, "f8")
    w = normalize(np.cross(u, v))
    o = np.array(origin, "f8")
    world = o + out[:, 0, None] * u + out[:, 1, None] * v
    tris = earclip(out)
    parts = []
    for s in (1, -1):
        pos = world + w * half_t * s
        idx = tris if s > 0 else tris[:, ::-1]
        parts.append(Part(pos, np.tile(w * s, (len(pos), 1)), idx, mat))
    edge = np.roll(world, -1, 0) - np.roll(world, 1, 0)
    n = normalize(np.cross(edge, w))
    if (n * (world - world.mean(0))).sum() < 0:
        n = -n
    P = np.stack([world + w * half_t, world + n * bevel + w * half_t * 0.3, world + n * bevel - w * half_t * 0.3, world - w * half_t], 0)
    N = np.stack([normalize(n + w * 0.7), n, n, normalize(n - w * 0.7)], 0)
    idx = grid_faces(4, len(world), True)
    rim = Part(P.reshape(-1, 3), N.reshape(-1, 3), idx, mat)
    tri = rim.pos[idx[0]]
    if (np.cross(tri[1] - tri[0], tri[2] - tri[0]) * rim.nor[idx[0, 0]]).sum() < 0:
        rim = Part(rim.pos, rim.nor, idx[:, ::-1], mat)
    parts.append(rim)
    return merge(parts)


def airfoil(thick=0.11, camber=0.05, n=40):
    t = (1 - np.cos(np.linspace(0, np.pi, n))) / 2
    yt = 5 * thick * (0.2969 * np.sqrt(t) - 0.126 * t - 0.3516 * t**2 + 0.2843 * t**3 - 0.1036 * t**4)
    yc = camber * 4 * t * (1 - t)
    up = np.stack([t, yc + yt], 1)
    lo = np.stack([t, yc - yt], 1)[::-1][1:-1]
    return np.vstack([up, lo])


def wing(stations, mat, thick=0.1, camber=-0.06):
    """Stations are rows of x, y (leading edge), z (leading edge), chord, angle in degrees.
    The trailing edge points rearward (minus z) and up for positive angles."""
    st = np.asarray(stations, "f8")
    af = airfoil(thick, camber)
    a = np.radians(st[:, 4])
    P = np.zeros((len(st), len(af), 3))
    for i in range(len(st)):
        c = st[i, 3]
        lz = -af[:, 0] * c
        ly = af[:, 1] * c
        P[i, :, 0] = st[i, 0]
        P[i, :, 1] = st[i, 1] + ly * np.cos(a[i]) - lz * np.sin(a[i])
        P[i, :, 2] = st[i, 2] + lz * np.cos(a[i]) + ly * np.sin(a[i])
    part = grid_part(P, mat, wrap_m=True)
    c = P.mean(1, keepdims=True)
    if (part.nor * (P - c).reshape(-1, 3)).sum() < 0:
        part = Part(part.pos, -part.nor, part.idx[:, ::-1], mat)
    parts = [part]
    for i, sign in ((0, -1), (len(st) - 1, 1)):
        ring = P[i]
        pos = ring
        nor = np.tile(np.array([sign, 0, 0], "f4"), (len(ring), 1))
        tris = earclip(np.stack([ring[:, 2], ring[:, 1]], 1))
        t = pos[tris[0]]
        if (np.cross(t[1] - t[0], t[2] - t[0]) * nor[0]).sum() < 0:
            tris = tris[:, ::-1]
        parts.append(Part(pos, nor, tris, mat))
    return merge(parts)


def spline2(ctrl, n=120):
    """Closed Catmull-Rom spline through 2D points."""
    c = np.asarray(ctrl, "f8")
    m = len(c)
    out = []
    per = max(2, n // m)
    for i in range(m):
        p0, p1, p2, p3 = c[(i - 1) % m], c[i], c[(i + 1) % m], c[(i + 2) % m]
        for t in np.linspace(0, 1, per, endpoint=False):
            out.append(
                0.5
                * (
                    2 * p1
                    + (p2 - p0) * t
                    + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t**2
                    + (3 * p1 - p0 - 3 * p2 + p3) * t**3
                )
            )
    return np.array(out)


def spline3(ctrl, n=80):
    c = np.asarray(ctrl, "f8")
    c = np.vstack([2 * c[0] - c[1], c, 2 * c[-1] - c[-2]])
    out = []
    segs = len(c) - 3
    per = max(2, n // segs)
    for i in range(segs):
        p0, p1, p2, p3 = c[i : i + 4]
        ts = np.linspace(0, 1, per, endpoint=(i == segs - 1))
        for t in ts:
            out.append(
                0.5
                * (
                    2 * p1
                    + (p2 - p0) * t
                    + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t**2
                    + (3 * p1 - p0 - 3 * p2 + p3) * t**3
                )
            )
    return np.array(out)


def export(parts, path_base, extra=None):
    meta = []
    with open(path_base + ".bin", "wb") as f:
        off = 0

        def put(arr):
            nonlocal off
            b = arr.tobytes()
            f.write(b)
            start = off
            off += len(b)
            return start

        for name, p in parts.items():
            by = {}
            for s, c, m in getattr(p, "groups", None) or [(0, len(p.idx), p.mat)]:
                by.setdefault(m, []).append(p.idx[s : s + c])
            for m, chunks in by.items():
                idx = np.concatenate(chunks)
                a, b, c = p.pos[idx[:, 0]], p.pos[idx[:, 1]], p.pos[idx[:, 2]]
                fn = np.cross(b - a, c - a)
                vn = p.nor[idx[:, 0]] + p.nor[idx[:, 1]] + p.nor[idx[:, 2]]
                bad = (fn * vn).sum(1) < 0
                idx = idx.copy()
                idx[bad] = idx[bad][:, ::-1]
                keep, inv = np.unique(idx, return_inverse=True)
                entry = {"name": name, "mat": m, "verts": len(keep), "tris": len(idx)}
                entry["pos"] = put(p.pos[keep])
                entry["nor"] = put(p.nor[keep])
                entry["idx"] = put(inv.reshape(-1, 3).astype("u4"))
                if extra and name in extra:
                    entry["zone"] = put(extra[name][keep].astype("f4"))
                meta.append(entry)
    json.dump(meta, open(path_base + ".json", "w"))
