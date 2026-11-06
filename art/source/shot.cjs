const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const cfgs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const b = await chromium.launch({ headless: true, args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 800, height: 600 } });
  p.on('console', (m) => { const t = m.text(); if (!/GPU stall|GL Driver/.test(t)) console.log('[page]', t.slice(0, 300)); });
  p.on('pageerror', (e) => console.log('[err]', e.message.slice(0, 500)));
  await p.goto('http://127.0.0.1:8123/render.html');
  await p.waitForFunction('window.ready===true', null, { timeout: 60000 });
  for (const c of cfgs) {
    const r = await p.evaluate((c) => window.renderShot(c), c);
    fs.writeFileSync(c.out, Buffer.from(r.data.split(',')[1], 'base64'));
    console.log(c.out, Math.round(r.ms / 1000) + 's', r.samples, r.gpu);
  }
  await b.close();
})();
