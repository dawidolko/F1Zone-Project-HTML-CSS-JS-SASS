const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const repo = require('path').resolve(__dirname, '../..');
const uri = (f, m) => `data:${m};base64,${fs.readFileSync(f).toString('base64')}`;
const oswald = uri(repo + '/fonts/oswald-300-700-normal-latin.woff2', 'font/woff2');
const roboto = uri(repo + '/fonts/roboto-300-700-normal-latin.woff2', 'font/woff2');
const wm = fs.readFileSync(repo + '/img/brand/wordmark.svg', 'utf8');
const items = [
  ['harbour-circuit', 'Harbour', 'An invented street circuit'],
  ['airfield-circuit', 'Airfield', 'An invented circuit on an old runway'],
  ['forest-circuit', 'Forest', 'An invented circuit through the trees'],
  ['ivory-livery', 'Ivory Works', 'An invented livery in ivory and vermilion'],
  ['graphite-livery', 'Graphite Works', 'An invented livery in graphite and red'],
  ['ultramarine-livery', 'Ultramarine Works', 'An invented livery in ultramarine and white'],
  ['evergreen-livery', 'Evergreen Works', 'An invented livery in green and brass'],
  ['sand-livery', 'Sand Works', 'An invented livery in sand and black'],
  ['violet-livery', 'Violet Works', 'An invented livery in violet and silver'],
  ['chevron-helmet', 'Chevron', 'An invented helmet in bone and red'],
  ['split-helmet', 'Split', 'An invented helmet in black and amber'],
  ['checker-helmet', 'Checker', 'An invented helmet with a chequered crown'],
  ['comet-helmet', 'Comet', 'An invented helmet in blue and sky'],
  ['halftone-helmet', 'Halftone', 'An invented helmet in rose and black'],
  ['ring-helmet', 'Ring', 'An invented helmet in teal and bone'],
  ['bolt-helmet', 'Bolt', 'An invented helmet in violet and amber'],
  ['apex-helmet', 'Apex', 'An invented helmet in green and bone'],
];
(async () => {
  const dir = process.argv[2];
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1000, height: 1500 } });
  for (const [id, title, sub] of items) {
    const img = `${dir}/art_g/${id}.png`;
    if (!fs.existsSync(img)) continue;
    const size = title.length > 12 ? 118 : 158;
    await p.setContent(`<!doctype html><style>
@font-face{font-family:O;src:url(${oswald});font-weight:300 700}@font-face{font-family:R;src:url(${roboto});font-weight:300 700}
*{margin:0;box-sizing:border-box}body{width:1000px;height:1500px;position:relative;overflow:hidden;background:#000;color:#fff}
img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.g{position:absolute;inset:auto 0 0 0;height:560px;background:linear-gradient(180deg,#0000,#000000d9 72%)}
.t{position:absolute;left:64px;right:64px;bottom:64px}
h1{font:600 ${size}px/1 O;}p{font:400 30px/1.3 R;margin-top:18px;color:#ffffffd9}
.w{position:absolute;right:64px;top:60px;width:150px}.w svg{display:block;width:100%}
</style><img src="${uri(img, 'image/png')}"><div class="g"></div><div class="w">${wm}</div><div class="t"><h1>${title}</h1><p>${sub}</p></div>`);
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(120);
    await p.screenshot({ path: `${dir}/posters/${id}.png` });
  }
  await b.close();
})();
