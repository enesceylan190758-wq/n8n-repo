#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const files = [
  'index.html',
  'anasayfa-detayi.html',
  'urunler.html',
  'sektorler.html',
  'platformlar.html',
  'kaynaklar.html',
  'blog.html',
  'hakkimizda.html',
  'fiyatlar.html',
  'ai-ajaniniz.html',
  'kullanici-sozlesmesi.html',
  'gizlilik-politikasi.html',
  'kvkk.html',
  'veri-guvenligi.html',
  'iys-izin.html',
  'hbys-entegrasyon.html',
  'guvenlik-standartlari.html',
];

const navPartial = fs.readFileSync(path.join(root, 'partials/site-nav.html'), 'utf8').trim();
const navInline = `<nav class="site-nav-mount" aria-label="Ana menü">\n${navPartial}\n</nav>`;

for (const file of files) {
  const fp = path.join(root, file);
  if (!fs.existsSync(fp)) {
    console.warn('skip missing', file);
    continue;
  }
  let html = fs.readFileSync(fp, 'utf8');
  html = html.replace(/<nav class="site-nav-mount"[^>]*>[\s\S]*?<\/nav>/, navInline);
  html = html.replace(/href="index\.html#cta"/g, 'href="/#cta"');
  html = html.replace(/class="btn-login"[^>]*href="#"/g, 'class="btn-login" href="/dashboard/login"');
  if (!html.includes('site-subpage') && !html.includes('home-refresh-body')) {
    html = html.replace(/<body([^>]*)>/, '<body$1 class="site-subpage">'.replace('class=""', ''));
    if (!html.includes('site-subpage')) {
      html = html.replace(/<body>/, '<body class="site-subpage">');
    }
  }
  fs.writeFileSync(fp, html);
  console.log('synced', file);
}
