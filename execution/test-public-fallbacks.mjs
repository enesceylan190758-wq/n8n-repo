#!/usr/bin/env node
import {
  STATIC_GEO_PILLARS,
  staticGeoPacks,
  geoSitemapXml,
  degradedIndexNote,
} from '../nefalix-landing/api/_lib/public-fallbacks.js';

let failed = 0;
function ok(cond, msg) {
  if (cond) console.log(`OK   ${msg}`);
  else {
    console.error(`FAIL ${msg}`);
    failed += 1;
  }
}

ok(STATIC_GEO_PILLARS.length === 6, '6 static GEO pillars');
const packs = staticGeoPacks();
ok(packs.every((p) => p.path.startsWith('/geo/')), 'pack paths are /geo/slug');
ok(packs[0].url.includes('nefalix.com/geo/'), 'pack urls are public');

const xml = geoSitemapXml({
  packs: [{ run_date: '2026-07-20' }, { run_date: 'klinik-itibar-yonetimi-yazilimi' }],
  lastmod: '2026-09-28',
});
ok(xml.includes('<urlset'), 'sitemap has urlset');
ok(xml.includes('https://nefalix.com/geo</loc>'), 'sitemap includes /geo index');
ok(xml.includes('/geo/klinik-itibar-yonetimi-yazilimi'), 'sitemap includes pillar');
ok(xml.includes('/geo/2026-07-20'), 'sitemap includes dated pack');
ok(!xml.includes('/geo/klinik-itibar-yonetimi-yazilimi</loc>\n    <lastmod>klinik'), 'non-date packs skipped');
ok(degradedIndexNote('geo').includes('data-degraded="1"'), 'degraded note marker');

if (failed) process.exit(1);
console.log('all public-fallback tests passed');
