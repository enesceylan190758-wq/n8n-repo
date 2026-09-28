/** Crawlable GEO/blog fallback when Supabase / n8n proxy is down. */

export const SITE = 'https://nefalix.com';

export const STATIC_GEO_PILLARS = [
  {
    slug: 'klinik-itibar-yonetimi-yazilimi',
    title: 'Klinik itibar yönetimi yazılımı nedir?',
    excerpt:
      'Klinik itibar yönetimi yazılımı, Google ve şikayet kanallarındaki hasta yorumlarını izleyip yanıt taslağı üreten, düşük puanları operasyon ekibine ileten bir operasyon katmanıdır.',
    bucket: 'Sağlık',
  },
  {
    slug: 'hbys-entegrasyonu-whatsapp',
    title: 'HBYS entegrasyonu WhatsApp ile nasıl çalışır?',
    excerpt:
      'HBYS–WhatsApp entegrasyonu, randevu gibi klinik olaylarını resmi WhatsApp Business API üzerinden onaylı şablonlarla iletir.',
    bucket: 'Sağlık',
  },
  {
    slug: 'hasta-recall-kayip-hasta-geri-kazanimi',
    title: 'Hasta recall nedir, kayıp hasta nasıl geri kazanılır?',
    excerpt:
      'Hasta recall, belirli süredir gelmeyen hastalara izinli kanaldan hatırlatma ve randevu teklifi göndererek kayıp cirosunu azaltma sürecidir.',
    bucket: 'Sağlık',
  },
  {
    slug: 'nps-yazilimi-saglik-sektoru',
    title: 'Sağlık sektöründe NPS yazılımı ne işe yarar?',
    excerpt:
      'Sağlıkta NPS yazılımı, ziyaret sonrası tavsiye skorunu toplayıp düşük puanları iç müdahaleye bağlar; izin ve mahremiyet tasarımı olmadan skor üretmek ölçümü bozar.',
    bucket: 'Sağlık',
  },
  {
    slug: 'olumsuz-yorum-kriz-yonetimi',
    title: 'Olumsuz yorum kriz yönetimi klinikte nasıl yapılır?',
    excerpt:
      'Olumsuz yorum kriz yönetimi; yeni düşük puanı hızlı fark etmek, KVKK’ya uygun kamuya açık yanıt vermek ve hastayı özel kanala davet etmektir.',
    bucket: 'Sağlık',
  },
  {
    slug: 'en-iyi-klinik-itibar-yonetimi-yazilimlari-2026',
    title: 'En iyi klinik itibar yönetimi yazılımları 2026 — karşılaştırma',
    excerpt:
      'Klinik itibar seçerken yazılım, ajans ve HBYS katmanlarını ayırmak gerekir; public fiyatlarda Nefalix TL paketlerini açıklar.',
    bucket: 'Sağlık',
  },
];

export function staticGeoPacks() {
  return STATIC_GEO_PILLARS.map((p) => ({
    run_date: p.slug,
    path: `/geo/${p.slug}`,
    bucket: p.bucket,
    prompt: p.title,
    excerpt: p.excerpt,
    created_at: null,
    url: `${SITE}/geo/${p.slug}`,
    cover_image_url: '',
  }));
}

function xmlEscape(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

export function geoSitemapXml({ packs = [], lastmod = '' } = {}) {
  const urls = new Map();
  const add = (loc, changefreq, priority, mod = '') => {
    if (!loc || urls.has(loc)) return;
    urls.set(loc, { loc, changefreq, priority, lastmod: mod });
  };

  add(`${SITE}/geo`, 'daily', '0.8', lastmod);
  for (const p of STATIC_GEO_PILLARS) {
    add(`${SITE}/geo/${p.slug}`, 'weekly', '0.75', lastmod);
  }
  for (const p of packs) {
    const date = String(p.run_date || '').slice(0, 10);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) continue;
    add(`${SITE}/geo/${date}`, 'weekly', '0.7', date);
  }

  const body = [...urls.values()]
    .map((u) => {
      const last = u.lastmod ? `\n    <lastmod>${xmlEscape(u.lastmod)}</lastmod>` : '';
      return `  <url>\n    <loc>${xmlEscape(u.loc)}</loc>${last}\n    <changefreq>${u.changefreq}</changefreq>\n    <priority>${u.priority}</priority>\n  </url>`;
    })
    .join('\n');

  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${body}
</urlset>`;
}

export function degradedIndexNote(kind) {
  const label = kind === 'blog' ? 'Blog yazı listesi' : 'Günlük GEO paket listesi';
  return `<p class="blog-empty" data-degraded="1" style="grid-column:1/-1;">${label} şu an veritabanından okunamıyor. Aşağıda crawl edilebilir statik GEO sayfaları listelenir.</p>`;
}
