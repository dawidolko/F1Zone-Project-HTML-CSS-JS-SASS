import * as THREE from 'three';

/* Procedural studio: soft rectangular lights painted into a float equirect map. */
function box(c, u, v, hu, hv, col, power, feather = 0.06) {
  const ul = Math.hypot(...u), vl = Math.hypot(...v);
  const U = u.map((a) => a / ul), V = v.map((a) => a / vl);
  const N = [U[1] * V[2] - U[2] * V[1], U[2] * V[0] - U[0] * V[2], U[0] * V[1] - U[1] * V[0]];
  return { c, U, V, N, hu, hv, col, power, feather };
}
const smooth = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };

const presets = { studio: () => [] };

export function makeEnv(name, opts) {
  const lights = presets[name](opts);
  const W = 2048, H = 1024;
  const data = new Float32Array(W * H * 4);
  const amb = opts.ambient ?? 0.012;
  for (let y = 0; y < H; y++) {
    const th = ((y + 0.5) / H) * Math.PI;
    const dy = Math.cos(th), s = Math.sin(th);
    for (let x = 0; x < W; x++) {
      const ph = ((x + 0.5) / W) * Math.PI * 2;
      const dx = s * Math.cos(ph), dz = s * Math.sin(ph);
      let r = amb, g = amb, b = amb * 1.05;
      for (const l of lights) {
        const denom = dx * l.N[0] + dy * l.N[1] + dz * l.N[2];
        const t = (l.c[0] * l.N[0] + l.c[1] * l.N[1] + l.c[2] * l.N[2]) / denom;
        if (!(t > 0)) continue;
        const px = dx * t - l.c[0], py = dy * t - l.c[1], pz = dz * t - l.c[2];
        const a = px * l.U[0] + py * l.U[1] + pz * l.U[2];
        const c = px * l.V[0] + py * l.V[1] + pz * l.V[2];
        const f = (1 - smooth(l.hu - l.feather * l.hu * 0 - l.feather, l.hu + l.feather, Math.abs(a))) * (1 - smooth(l.hv - l.feather, l.hv + l.feather, Math.abs(c)));
        r += l.col[0] * l.power * f;
        g += l.col[1] * l.power * f;
        b += l.col[2] * l.power * f;
      }
      const i = (y * W + x) * 4;
      data[i] = r; data[i + 1] = g; data[i + 2] = b; data[i + 3] = 1;
    }
  }
  const t = new THREE.DataTexture(data, W, H, THREE.RGBAFormat, THREE.FloatType);
  t.mapping = THREE.EquirectangularReflectionMapping;
  t.minFilter = t.magFilter = THREE.LinearFilter;
  t.wrapS = THREE.RepeatWrapping;
  t.flipY = true;
  t.needsUpdate = true;
  return t;
}
