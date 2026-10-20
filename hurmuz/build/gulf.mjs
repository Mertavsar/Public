// Basra Körfezi / Hürmüz haritası: 1080x1920 tuvalde görsel bölgeye (y 500–1160) oturur.
import fs from 'fs';
import * as topo from 'topojson-client';
import { geoMercator, geoPath, geoBounds } from 'd3-geo';
const w = JSON.parse(fs.readFileSync('node_modules/world-atlas/countries-10m.json'));
const all = topo.feature(w, w.objects.countries).features;
const box = [[33, 9], [66, 38]];
const feats = all.filter(f => { const [[a, b], [c, d]] = geoBounds(f); return c > box[0][0] && a < box[1][0] && d > box[0][1] && b < box[1][1] && c - a < 180; });
const frame = { type: 'Feature', geometry: { type: 'MultiPoint', coordinates: [[box[0][0], box[0][1]], [box[1][0], box[1][1]], [box[0][0], box[1][1]], [box[1][0], box[0][1]]] } };
const proj = geoMercator().fitExtent([[-20, 480], [1100, 1180]], frame);
proj.clipExtent([[-200, 300], [1280, 1400]]);
const path = geoPath(proj).digits(1);
const P = ll => proj(ll).map(v => Math.round(v * 10) / 10);
const land = path({ type: 'FeatureCollection', features: feats });
const borders = path(topo.mesh(w, w.objects.countries, (a, b) => a !== b));
const out = {
  land, borders,
  hormuz: P([56.45, 26.55]),
  narrow: [P([56.30, 26.36]), P([56.42, 26.80])],
  lane: [[50.6, 26.9], [52.6, 26.4], [54.6, 26.2], [55.8, 26.45], [56.45, 26.55], [56.9, 26.15], [57.4, 25.5], [58.4, 24.8], [60.2, 24.1], [62.5, 23.2]].map(P),
  pipeSA: [[49.7, 25.9], [46.7, 25.2], [43.0, 24.6], [40.0, 24.2], [38.1, 24.1]].map(P),
  pipeUAE: [[54.0, 23.6], [55.2, 24.2], [56.35, 25.12]].map(P),
  labels: {
    'İRAN': P([54.5, 31.0]), 'SUUDİ ARABİSTAN': P([45.0, 22.8]), 'IRAK': P([43.8, 32.6]), 'BAE': P([54.3, 23.3]),
    'UMMAN': P([57.2, 21.2]), 'KATAR': P([51.2, 25.1]), 'KUVEYT': P([47.6, 29.6]),
  },
  seaLabels: { 'Basra Körfezi': P([51.0, 27.6]), 'Umman Körfezi': P([59.8, 24.9]) },
  ports: { 'Yanbu': P([38.1, 24.1]), 'Fujairah': P([56.35, 25.12]) },
};
fs.writeFileSync(process.argv[2], 'window.GULF = ' + JSON.stringify(out) + ';\n');
console.log('land', land.length, 'borders', borders.length, 'hormuz', out.hormuz, 'narrow', out.narrow);
