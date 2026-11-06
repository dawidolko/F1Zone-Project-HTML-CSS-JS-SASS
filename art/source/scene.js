import * as THREE from 'three';
import { WebGLPathTracer } from 'three-gpu-pathtracer';
import { makeEnv } from './env.js';
import { liveries } from './livery.js';

const rgb = (h) => new THREE.Color(h);
function makeMaterials(L) {
  const P = (o) => new THREE.MeshPhysicalMaterial(o);
  return {
    paint: P({ color: 0xffffff, roughness: L.paintRough ?? 0.22, metalness: L.paintMetal ?? 0.0 }),
    wing: P({ color: rgb(L.wing), roughness: 0.34, metalness: 0.0 }),
    fin: P({ color: rgb(L.fin ?? L.wing), roughness: 0.34, metalness: 0.0 }),
    floor: P({ color: 0x08080a, roughness: 0.4 }),
    halo: P({ color: rgb(L.halo ?? L.wing), roughness: 0.3 }),
    carbon: P({ color: 0x0b0b0d, roughness: 0.36 }),
    tyre: P({ color: 0x0c0c0d, roughness: 0.62, specularIntensity: 0.6 }),
    rim: P({ color: rgb(L.rim ?? 0xb4b6ba), roughness: 0.26, metalness: 1 }),
    spoke: P({ color: rgb(L.spoke ?? 0x1a1b1e), roughness: 0.32, metalness: 0.6 }),
    matte: P({ color: 0x050506, roughness: 0.7 }),
    accent: P({ color: rgb(L.accent), roughness: 0.3 }),
    helmet: P({ color: rgb(L.helmet ?? 0xe9e6df), roughness: 0.2 }),
    visor: P({ color: rgb(L.visor ?? 0x34363c), roughness: 0.06, metalness: 1 }),
    line: P({ color: 0xf2efe8, roughness: 0.3 }),
    light: new THREE.MeshStandardMaterial({ color: 0x220000, emissive: 0xff1208, emissiveIntensity: L.lamp ?? 14 }),
  };
}

function paintTexture(L) {
  const W = 4096, H = 1024;
  const d = new Uint8Array(W * H * 4);
  for (let j = 0; j < H; j++) {
    const y = ((j + 0.5) / H) * 1.5;
    for (let i = 0; i < W; i++) {
      const z = ((i + 0.5) / W) * 6 - 3;
      const c = L.sphere ? L.paint(((i + 0.5) / W) * 2 * Math.PI - Math.PI, (j + 0.5) / H * 0.4 - 0.2) : L.paint(0, y, z);
      const k = (j * W + i) * 4;
      d[k] = (c >> 16) & 255; d[k + 1] = (c >> 8) & 255; d[k + 2] = c & 255; d[k + 3] = 255;
    }
  }
  const t = new THREE.DataTexture(d, W, H, THREE.RGBAFormat);
  t.colorSpace = THREE.SRGBColorSpace;
  t.magFilter = THREE.LinearFilter;
  t.minFilter = THREE.LinearFilter;
  t.needsUpdate = true;
  return t;
}

async function load(base) {
  const meta = await (await fetch(base + '.json')).json();
  const buf = await (await fetch(base + '.bin')).arrayBuffer();
  return meta.map((m) => {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(buf, m.pos, m.verts * 3), 3));
    g.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(buf, m.nor, m.verts * 3), 3));
    g.setIndex(new THREE.BufferAttribute(new Uint32Array(buf, m.idx, m.tris * 3), 1));
    if (m.zone !== undefined) g.userData.zone = new Float32Array(buf, m.zone, m.verts);
    return { meta: m, g };
  });
}

let cached = {};
window.renderShot = async function (cfg) {
  const { w, h, samples = 200, model = 'car_lo', livery = 'noir', cam, env = 'studio', floor = {}, tiles = 1, bounces = 6, exposure = 1, backdrop } = cfg;
  const canvas = document.querySelector('canvas') || document.body.appendChild(document.createElement('canvas'));
  canvas.style.width = '640px';
  const renderer = window.__r || (window.__r = new THREE.WebGLRenderer({ canvas, antialias: false, preserveDrawingBuffer: true, powerPreference: 'high-performance' }));
  renderer.setPixelRatio(1);
  renderer.setSize(w, h, false);
  renderer.toneMapping = { aces: THREE.ACESFilmicToneMapping, agx: THREE.AgXToneMapping, neutral: THREE.NeutralToneMapping }[cfg.tone ?? 'neutral'];
  renderer.toneMappingExposure = exposure;

  const L = { ...liveries[livery], ...(cfg.colors || {}) };
  const mats = makeMaterials(L);
  const scene = new THREE.Scene();
  const parts = cached[model] || (cached[model] = await load(model));
  for (const { meta, g } of parts) {
    if (meta.name === 'body') {
      if (!g.userData.split) {
        const pos = g.attributes.position.array, zone = g.userData.zone, idx = g.index.array;
        const uv = new Float32Array(meta.verts * 2);
        for (let i = 0; i < meta.verts; i++) {
          if (L.sphere) {
            uv[i * 2] = Math.atan2(pos[i * 3], pos[i * 3 + 2]) / (Math.PI * 2) + 0.5;
            uv[i * 2 + 1] = (pos[i * 3 + 1] + 0.2) / 0.4;
          } else {
            uv[i * 2] = (pos[i * 3 + 2] + 3) / 6;
            uv[i * 2 + 1] = pos[i * 3 + 1] / 1.5;
          }
        }
        g.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
        const a = [], b = [];
        for (let i = 0; i < idx.length; i += 3) {
          const z = zone[idx[i]] + zone[idx[i + 1]] + zone[idx[i + 2]];
          (z > 1.5 ? b : a).push(idx[i], idx[i + 1], idx[i + 2]);
        }
        const mk = (list) => {
          const n = new THREE.BufferGeometry();
          n.setAttribute('position', g.attributes.position);
          n.setAttribute('normal', g.attributes.normal);
          n.setAttribute('uv', g.attributes.uv);
          n.setIndex(new THREE.BufferAttribute(new Uint32Array(list), 1));
          return n;
        };
        g.userData.split = [mk(a), mk(b)];
      }
      const tex = paintTexture(L);
      mats.paint.map = tex;
      const clay = new THREE.MeshStandardMaterial({ color: 0xbbbbbb, roughness: 0.5 });
      scene.add(new THREE.Mesh(g.userData.split[0], cfg.clay ? clay : mats.paint));
      scene.add(new THREE.Mesh(g.userData.split[1], cfg.clay ? clay : mats.matte));
      continue;
    }
    const mesh = new THREE.Mesh(g, cfg.clay ? new THREE.MeshStandardMaterial({ color: 0xbbbbbb, roughness: 0.5 }) : (mats[meta.mat] || mats.carbon));
    scene.add(mesh);
  }
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), new THREE.MeshPhysicalMaterial({ color: rgb(floor.color ?? 0x0a0a0c), roughness: floor.rough ?? 0.3, specularIntensity: floor.spec ?? 1 }));
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = cfg.floorY ?? 0;
  scene.add(ground);
  if (backdrop) {
    const prof = [];
    const R = backdrop.r ?? 2.5;
    for (let i = 0; i <= 24; i++) {
      const a = (i / 24) * Math.PI / 2;
      prof.push([R * Math.sin(a), R - R * Math.cos(a)]);
    }
    prof.push([R, 40]);
    const pos = [], idx = [], nor = [];
    const halfW = 70;
    prof.forEach(([s, y], i) => {
      const p0 = prof[Math.max(0, i - 1)], p1 = prof[Math.min(prof.length - 1, i + 1)];
      let tx = p1[0] - p0[0], ty = p1[1] - p0[1];
      const l = Math.hypot(tx, ty);
      tx /= l; ty /= l;
      pos.push(-halfW, y, -s, halfW, y, -s);
      nor.push(0, tx, ty, 0, tx, ty);
    });
    for (let i = 0; i < prof.length - 1; i++) {
      const a = i * 2;
      idx.push(a, a + 1, a + 3, a, a + 3, a + 2);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
    g.setIndex(idx);
    const wall = new THREE.Mesh(g, new THREE.MeshPhysicalMaterial({ color: rgb(backdrop.color ?? 0x101012), roughness: backdrop.rough ?? 0.55, specularIntensity: 0.4, side: THREE.DoubleSide }));
    const d = backdrop.dist ?? 9;
    wall.position.set(-cam.pos[0] / Math.hypot(cam.pos[0], cam.pos[2]) * d, (cfg.floorY ?? 0) + 0.002, -cam.pos[2] / Math.hypot(cam.pos[0], cam.pos[2]) * d);
    wall.rotation.y = Math.atan2(cam.pos[0], cam.pos[2]);
    scene.add(wall);
  }
  scene.environment = makeEnv(env, cfg.envOpts || {});
  scene.environmentIntensity = 1;
  for (const l of cfg.lights || []) {
    const a = new THREE.RectAreaLight(rgb(l.color ?? 0xffffff), l.power, l.w, l.h);
    a.position.set(...l.pos);
    a.lookAt(...(l.at ?? [0, 0.4, 0]));
    a.updateMatrixWorld();
    scene.add(a);
  }
  scene.background = null;
  scene.backgroundIntensity = 0;

  const camera = new THREE.PerspectiveCamera(cam.fov, w / h, 0.1, 500);
  camera.position.set(...cam.pos);
  camera.lookAt(...cam.look);
  if (cam.shift) camera.setViewOffset(w, h, cam.shift[0] * w, cam.shift[1] * h, w, h);
  camera.updateMatrixWorld();
  camera.updateProjectionMatrix();

  const pt = window.__pt || (window.__pt = new WebGLPathTracer(renderer));
  pt.tiles.set(tiles, tiles);
  pt.bounces = bounces;
  pt.filterGlossyFactor = 0.25;
  pt.renderDelay = 0;
  pt.fadeDuration = 0;
  pt.minSamples = 1;
  pt.multipleImportanceSampling = true;
  pt.setScene(scene, camera);
  const t0 = performance.now();
  const done = () => pt.samples >= samples;
  await new Promise((res) => {
    const step = () => {
      pt.renderSample();
      const gl = renderer.getContext();
      gl.bindFramebuffer(gl.FRAMEBUFFER, null);
      gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array(4));
      if (done()) res();
      else setTimeout(step, 0);
    };
    step();
  });
  const ms = performance.now() - t0;
  const gl = renderer.getContext();
  return { ms, samples: pt.samples, gpu: gl.getParameter(gl.getExtension('WEBGL_debug_renderer_info')?.UNMASKED_RENDERER_WEBGL ?? gl.RENDERER), data: canvas.toDataURL('image/png') };
};
window.ready = true;
