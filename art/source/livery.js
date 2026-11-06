const mix = (a, b, t) => a.map((v, i) => v * (1 - t) + b[i] * t);
const sm = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const hex = (h) => [(h >> 16) & 255, (h >> 8) & 255, h & 255].map((v) => v / 255);
const toHex = (c) => (Math.round(c[0] * 255) << 16) | (Math.round(c[1] * 255) << 8) | Math.round(c[2] * 255);

/* Two lines rake back across the flank and meet the engine cover. */
function slash(base, stripe, x, y, z, width, offset = 0) {
  const u = z + 1.25 * (y - 0.4) + offset;
  const e = 0.006;
  return mix(base, stripe, sm(-e, e, u) * (1 - sm(width - e, width + e, u)));
}

function scheme(baseHex, stripeHex, lineHex, opts = {}) {
  const base = hex(baseHex), stripe = hex(stripeHex), line = hex(lineHex);
  return {
    wing: opts.wing ?? 0x121315, accent: stripeHex, helmet: opts.helmet ?? stripeHex, fin: opts.fin ?? 0x121315, halo: opts.halo ?? 0x17181b,
    paintMetal: opts.metal ?? 0, paintRough: opts.rough ?? 0.13,
    paint(x, y, z) {
      let c = base;
      c = slash(c, stripe, x, y, z, 0.42, 0.72);
      c = slash(c, line, x, y, z, 0.035, 0.235);
      return toHex(c);
    },
  };
}

const deg = Math.PI / 180;
function lid(fn, opts = {}) {
  return { sphere: true, wing: 0x121315, accent: 0xe10600, paintRough: opts.rough ?? 0.14, paintMetal: opts.metal ?? 0, paint: (a, y) => toHex(fn(Math.abs(a), y, a)) };
}
const C = { ink: hex(0x0e0f12), bone: hex(0xece8df), red: hex(0xe10600), blue: hex(0x1740c4), teal: hex(0x08857f), amber: hex(0xf2a10c), violet: hex(0x5b2bb5), green: hex(0x0f5c3a), sky: hex(0x9fd3ec), rose: hex(0xd93a6e) };

export const helmets = {
  chevron: lid((a, y) => {
    const u = y - 0.10 + a * 0.13;
    const band = Math.abs(((u * 13) % 2 + 2) % 2 - 1);
    return mix(C.bone, C.red, sm(0.46, 0.5, band));
  }),
  split: lid((a, y, s) => {
    const m = sm(-0.012, 0.012, s + 0.05 * Math.sin(y * 22));
    let c = mix(C.ink, C.amber, m);
    return mix(c, C.bone, 1 - sm(0.02, 0.03, Math.abs(s + 0.05 * Math.sin(y * 22))));
  }),
  checker: lid((a, y, s) => {
    const q = Math.floor((a * 0.145) / 0.022) + Math.floor((y + 0.2) / 0.022);
    const inBand = sm(0.01, 0.014, y - 0.015) * (1 - sm(0.092, 0.096, y));
    return mix(C.bone, q % 2 ? C.ink : C.bone, inBand);
  }),
  comet: lid((a, y) => {
    const c0 = y - 0.06 - 0.05 * Math.sin(a * 1.4);
    const w = 0.015 + 0.075 * (a / Math.PI);
    return mix(C.blue, C.sky, 1 - sm(w - 0.004, w + 0.004, Math.abs(c0)));
  }),
  halftone: lid((a, y) => {
    const u = a * 0.145, gx = 0.0125, gy = 0.0125;
    const cy = Math.round(y / gy), ox = cy % 2 ? gx / 2 : 0;
    const cx = Math.round((u - ox) / gx);
    const d = Math.hypot(u - (cx * gx + ox), y - cy * gy);
    const r = 0.0085 * Math.min(1, Math.max(0, (0.12 - y) / 0.26));
    return mix(C.rose, C.ink, 1 - sm(r - 0.0008, r + 0.0008, d));
  }),
  ring: lid((a, y) => {
    const h = 0.15 - y;
    const b = Math.abs(((h * 26) % 2 + 2) % 2 - 1);
    return mix(C.teal, C.bone, sm(0.62, 0.66, b));
  }),
  bolt: lid((a, y) => {
    const z = y - 0.045 + 0.05 * Math.abs(((a * 3.2) % 2) - 1);
    return mix(C.violet, C.amber, 1 - sm(0.02, 0.024, Math.abs(z)));
  }),
  apex: lid((a, y) => {
    const e = y + 0.03 - 0.14 * Math.pow(Math.max(0, 1 - a / 2.4), 2);
    let c = mix(C.green, C.bone, sm(-0.002, 0.002, e));
    return mix(c, C.red, 1 - sm(0.009, 0.012, Math.abs(e)));
  }),
};

export const liveries = {
  ...helmets,
  track: { sphere: false, wing: 0x121315, accent: 0xe10600, paint: () => 0xffffff },
  ivory: scheme(0xd8d5cd, 0xd80500, 0x101012),
  scarlet: scheme(0xc20802, 0x101012, 0xe9e6df),
  graphite: scheme(0x2b2d33, 0xe10600, 0xe9e6df),
  ultramarine: scheme(0x12308f, 0xece8df, 0xf2a10c),
  evergreen: scheme(0x0f4a32, 0xc9a24a, 0xece8df),
  sand: scheme(0xc8b28a, 0x101012, 0xd80500),
  violet: scheme(0x4a1f99, 0xc8cbd1, 0x101012),
  noir: {
    wing: 0x141517, accent: 0xe10600, fin: 0x141517, halo: 0x1d1f22, paintMetal: 0.9, paintRough: 0.16,
    paint(x, y, z) {
      const base = hex(0x3b3e45), red = hex(0xe10600), white = hex(0xe9e6df);
      let c = base;
      c = slash(c, red, x, y, z, 0.42, 0.72);
      c = slash(c, white, x, y, z, 0.035, 0.235);
      c = mix(c, red, sm(2.3, 2.312, z - 0.25 * (y - 0.2)));
      return toHex(c);
    },
  },
};
