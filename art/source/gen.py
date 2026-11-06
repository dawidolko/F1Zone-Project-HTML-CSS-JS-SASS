import json, sys
spp = int(sys.argv[1]) if len(sys.argv) > 1 else 90
scale = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
only = sys.argv[3].split(",") if len(sys.argv) > 3 else None
W, H = 1000, 1500


def car_lights(hue, key=1.0):
    return [
        {"pos": [0, 3.3, 0.001], "w": 2.6, "h": 8.5, "power": 12 * key, "at": [0, 0, 0]},
        {"pos": [7.5, 2.6, 0.6], "w": 11, "h": 1.1, "power": 26 * key, "at": [0, 0.5, 0.4]},
        {"pos": [-7.5, 2.6, 0.6], "w": 11, "h": 1.1, "power": 22 * key, "at": [0, 0.5, 0.4]},
        {"pos": [-3, 8, -3.5], "w": 16, "h": 2, "power": 26, "color": hue, "at": [-6, 1.5, -8]},
        {"pos": [3, 8, 3.5], "w": 16, "h": 2, "power": 26, "color": hue, "at": [6, 1.5, 8]},
    ]


def car(name, livery, hue, cam, wall="#1b1b1e", key=1.0, floor=None, backdrop=True, w=W, h=H):
    c = {
        "id": name, "out": f"../shots/art/{name}.png", "w": int(w * scale), "h": int(h * scale), "samples": spp, "model": "car", "livery": livery,
        "cam": cam, "floor": floor or {"color": "#050506", "rough": 0.17, "spec": 1},
        "lights": car_lights(hue, key),
    }
    if backdrop:
        c["backdrop"] = {"dist": 9, "r": 3, "color": wall, "rough": 0.6}
    return c


def helmet(name, design, hue, angle=0.62, wall="#1d1d20", w=W, h=H):
    import math
    r = 1.42
    pos = [math.sin(angle) * r, 0.03, math.cos(angle) * r]
    return {
        "id": name, "out": f"../shots/art/{name}.png", "w": int(w * scale), "h": int(h * scale), "samples": spp, "model": "helmet", "livery": design,
        "cam": {"fov": 21, "pos": pos, "look": [0, -0.02, 0], "shift": [0, 0.085]}, "floorY": -0.147,
        "floor": {"color": "#050506", "rough": 0.17, "spec": 1},
        "backdrop": {"dist": 1.5, "r": 0.5, "color": wall, "rough": 0.6},
        "lights": [
            {"pos": [0, 1.05, 0.25], "w": 0.9, "h": 0.5, "power": 7, "at": [0, 0, 0]},
            {"pos": [1.1, 0.25, 0.7], "w": 0.18, "h": 1.5, "power": 26, "at": [0, 0, 0]},
            {"pos": [0.5, 0.75, 1.6], "w": 1.8, "h": 0.5, "power": 5, "at": [0, 0, 0]},
            {"pos": [-1.1, 0.25, 0.25], "w": 0.3, "h": 1.5, "power": 10, "at": [0, 0, 0]},
            {"pos": [-0.8, 2.2, -0.8], "w": 4, "h": 0.6, "power": 26, "color": hue, "at": [-1.2, 0.35, -1.6]},
            {"pos": [0.8, 2.2, -0.8], "w": 4, "h": 0.6, "power": 26, "color": hue, "at": [1.2, 0.35, -1.6]},
        ],
    }


def track(name, layout, colour, hue, w=W, h=H, cam=None):
    return {
        "id": name, "out": f"../shots/art/{name}.png", "w": int(w * scale), "h": int(h * scale), "samples": spp, "model": "track_" + layout, "livery": "track",
        "colors": {"accent": colour},
        "cam": cam or {"fov": 30, "pos": [0, 5.1, 2.4], "look": [0, 0, 0.12], "shift": [0, 0.085]},
        "floor": {"color": "#08080a", "rough": 0.3, "spec": 1},
        "lights": [
            {"pos": [0, 2.8, -0.2], "w": 3.0, "h": 1.2, "power": 5, "at": [0, 0, 0]},
            {"pos": [3.0, 0.9, -2], "w": 3, "h": 0.5, "power": 34, "color": hue, "at": [0, 0, 0]},
            {"pos": [-3.0, 0.9, -2], "w": 3, "h": 0.5, "power": 34, "color": hue, "at": [0, 0, 0]},
        ],
    }


F34 = {"fov": 29, "pos": [3.3, 0.36, 10.6], "look": [-0.25, 1.05, 0.3], "shift": [0, 0.1]}
items = [
    track("harbour-circuit", "harbour", "#e10600", "#ff2a14"),
    track("airfield-circuit", "airfield", "#f2a10c", "#ffb020"),
    track("forest-circuit", "forest", "#129a5f", "#30d080"),
    car("ivory-livery", "ivory", "#ff1a0a", {"fov": 20, "pos": [4.4, 0.42, 12.2], "look": [-0.1, 0.74, 1.0], "shift": [0, 0.09]}),
    car("graphite-livery", "graphite", "#ff7a0a", {"fov": 20, "pos": [-4.4, 0.5, 12.2], "look": [0.1, 0.74, 1.0], "shift": [0, 0.09]}),
    car("ultramarine-livery", "ultramarine", "#1a7cff", {"fov": 20, "pos": [-4.2, 0.8, -12.0], "look": [0.15, 0.82, -1.0], "shift": [0, 0.09]}, key=1.5),
    car("evergreen-livery", "evergreen", "#ffb020", {"fov": 17, "pos": [0.5, 0.4, 14.0], "look": [0, 0.78, 1.0], "shift": [0, 0.09]}, key=1.4),
    car("sand-livery", "sand", "#10a7a0", {"fov": 28, "pos": [8.8, 2.2, -5.4], "look": [-0.1, 1.0, -0.2], "shift": [0, 0.1]}),
    car("violet-livery", "violet", "#ff2aa0", {"fov": 19, "pos": [6.2, 0.5, 10.4], "look": [-0.2, 0.72, 0.9], "shift": [0, 0.09]}, key=1.4),
    helmet("chevron-helmet", "chevron", "#ff1a0a"),
    helmet("split-helmet", "split", "#ffb020", 0.2),
    helmet("checker-helmet", "checker", "#d8d8e0", 0.9),
    helmet("comet-helmet", "comet", "#2a8cff", 0.8),
    helmet("halftone-helmet", "halftone", "#ff2a70"),
    helmet("ring-helmet", "ring", "#10b7a0", 0.5),
    helmet("bolt-helmet", "bolt", "#8a2aff", 0.7),
    helmet("apex-helmet", "apex", "#30c070", 0.6),
    track("tile-tracks", "harbour", "#e10600", "#ff2a14", 900, 900, {"fov": 24, "pos": [0.3, 2.6, 2.2], "look": [0.05, 0, 0.1]}),
    car("tile-liveries", "ivory", "#ff1a0a", {"fov": 16, "pos": [6.2, 0.55, 6.2], "look": [0.75, 0.42, 1.45]}, w=900, h=900),
    helmet("tile-helmets", "chevron", "#ff1a0a", 0.62, w=900, h=900),
    car("tile-offer", "graphite", "#ff1a0a", {"fov": 24, "pos": [-5.8, 0.7, -8.2], "look": [0.1, 0.62, -0.3]}, w=900, h=900),
]
if only:
    items = [i for i in items if i["id"] in only]
for i in items:
    i.pop("id")
json.dump(items, open("art.json", "w"))
print(len(items))
