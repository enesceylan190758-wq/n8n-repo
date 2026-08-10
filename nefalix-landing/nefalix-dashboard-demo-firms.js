/**
 * Sunum / satış örnek firmaları (slug: demo-*).
 * Yönetici panelinde klinik / otel / oto altında 10'ar kart;
 * net before→after sonuçları satış konuşmasında kullanılır.
 */

function uuid(sectorChar, n) {
  const seq = String(n).padStart(12, '0');
  return `${sectorChar}1000000-0000-4000-8000-${seq}`;
}

function result(months, before, after, ratingBefore, ratingAfter, note) {
  return {
    started_months_ago: months,
    reviews_before: before,
    reviews_after: after,
    rating_before: ratingBefore,
    rating_after: ratingAfter,
    headline: `${months} ayda ${before} → ${after} yorum`,
    detail: note || `Ortalama ★${ratingBefore} → ★${ratingAfter}`,
  };
}

function firm({ id, name, slug, sector, address, rating, count, maps, result: demoResult, website }) {
  const mapsUrl = maps || `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(name)}`;
  return {
    id,
    name,
    slug,
    sector,
    address,
    website_url: website || null,
    email: null,
    logo_url: null,
    booking_url: null,
    whatsapp_phone: null,
    google_maps_url: mapsUrl,
    google_review_url: mapsUrl,
    google_rating: rating,
    google_review_count: count,
    automation_enabled: false,
    integration_config: { demo_result: demoResult },
    created_at: new Date(Date.now() - demoResult.started_months_ago * 30 * 86400000).toISOString(),
  };
}

const CLINIC_DEMOS = [
  firm({
    id: uuid('c', 1),
    name: 'DentAcademia Nişantaşı',
    slug: 'demo-dentacademia-nisantasi',
    sector: 'clinic',
    address: 'Nişantaşı, İstanbul',
    rating: 4.8,
    count: 412,
    result: result(3, 168, 412, 4.2, 4.8, 'NPS sonrası Google daveti · kriz hastası içeri alındı'),
  }),
  firm({
    id: uuid('c', 2),
    name: 'SmileLab Kadıköy',
    slug: 'demo-smilelab-kadikoy',
    sector: 'clinic',
    address: 'Kadıköy, İstanbul',
    rating: 4.7,
    count: 356,
    result: result(4, 190, 356, 4.1, 4.7, 'Haftalık yorum +%47 · detractor alarmı aktif'),
  }),
  firm({
    id: uuid('c', 3),
    name: 'WhitePearl Diş Kliniği',
    slug: 'demo-whitepearl-dis',
    sector: 'clinic',
    address: 'Ataşehir, İstanbul',
    rating: 4.9,
    count: 528,
    result: result(5, 210, 528, 4.3, 4.9, '5★ oranı %61 → %78'),
  }),
  firm({
    id: uuid('c', 4),
    name: 'Ortodent Beşiktaş',
    slug: 'demo-ortodent-besiktas',
    sector: 'clinic',
    address: 'Beşiktaş, İstanbul',
    rating: 4.6,
    count: 289,
    result: result(2, 142, 289, 4.0, 4.6, 'İlk 60 günde yorum sayısı 2×'),
  }),
  firm({
    id: uuid('c', 5),
    name: 'ImplantPlus Bakırköy',
    slug: 'demo-implantplus-bakirkoy',
    sector: 'clinic',
    address: 'Bakırköy, İstanbul',
    rating: 4.8,
    count: 467,
    result: result(6, 220, 467, 4.2, 4.8, 'Şikayetvar krizleri 4 → 0 / ay'),
  }),
  firm({
    id: uuid('c', 6),
    name: 'KidsDent Çocuk Diş',
    slug: 'demo-kidsdent-cocuk',
    sector: 'clinic',
    address: 'Ümraniye, İstanbul',
    rating: 4.7,
    count: 318,
    result: result(3, 155, 318, 4.1, 4.7, 'Ebeveyn NPS 7.9 → 9.1'),
  }),
  firm({
    id: uuid('c', 7),
    name: 'EstetikDiş Şişli',
    slug: 'demo-estetikdis-sisli',
    sector: 'clinic',
    address: 'Şişli, İstanbul',
    rating: 4.8,
    count: 501,
    result: result(4, 198, 501, 4.0, 4.8, '3 ayda 200→500 bandı geçildi'),
  }),
  firm({
    id: uuid('c', 8),
    name: 'Ağız & Çene Cerrahisi Merkezi',
    slug: 'demo-agiz-cene-merkezi',
    sector: 'clinic',
    address: 'Mecidiyeköy, İstanbul',
    rating: 4.6,
    count: 274,
    result: result(3, 130, 274, 3.9, 4.6, 'Detractor → yönetici WA < 5 dk'),
  }),
  firm({
    id: uuid('c', 9),
    name: 'Periodontoloji Kliniği Kartal',
    slug: 'demo-perio-kartal',
    sector: 'clinic',
    address: 'Kartal, İstanbul',
    rating: 4.7,
    count: 341,
    result: result(5, 175, 341, 4.2, 4.7, 'Recall kampanyası ile tekrar ziyaret +%22'),
  }),
  firm({
    id: uuid('c', 10),
    name: 'Hollywood Smile Studio',
    slug: 'demo-hollywood-smile',
    sector: 'clinic',
    address: 'Levent, İstanbul',
    rating: 4.9,
    count: 612,
    result: result(6, 245, 612, 4.4, 4.9, 'Uluslararası hasta yorumları 2.5×'),
  }),
];

const HOTEL_DEMOS = [
  firm({
    id: 'a1b2c3d4-e5f6-7890-abcd-ef1111111111',
    name: 'Byotell İstanbul',
    slug: 'demo-byotell-istanbul',
    sector: 'hotel',
    address: 'Kozyatağı, İstanbul',
    rating: 4.6,
    count: 312,
    website: 'https://www.byotell.com',
    maps: 'https://www.google.com/maps/search/?api=1&query=Byotell+Istanbul',
    result: result(3, 148, 312, 4.1, 4.6, 'OTA puanı yükseldi · doğrudan rezervasyon +%18'),
  }),
  firm({
    id: 'a1b2c3d4-e5f6-7890-abcd-ef2222222222',
    name: 'Antwell Hotels',
    slug: 'demo-antwell-hotels',
    sector: 'hotel',
    address: 'Taksim, İstanbul',
    rating: 4.8,
    count: 528,
    website: 'https://www.antwellhotels.com',
    maps: 'https://www.google.com/maps/search/?api=1&query=Antwell+Hotels+Istanbul',
    result: result(4, 265, 528, 4.3, 4.8, 'Google yorum 2× · şikayet yanıt süresi −60%'),
  }),
  firm({
    id: 'a1b2c3d4-e5f6-7890-abcd-ef3333333333',
    name: 'Hilton İstanbul Bomonti',
    slug: 'demo-hilton-bomonti',
    sector: 'hotel',
    address: 'Bomonti, Şişli / İstanbul',
    rating: 4.7,
    count: 1840,
    website: 'https://www.hilton.com',
    maps: 'https://www.google.com/maps/search/?api=1&query=Hilton+Istanbul+Bomonti',
    result: result(6, 1210, 1840, 4.4, 4.7, 'Büyük ölçek: +630 yorum · ★+0.3'),
  }),
  firm({
    id: uuid('h', 4),
    name: 'The Grand Pera',
    slug: 'demo-grand-pera',
    sector: 'hotel',
    address: 'Beyoğlu, İstanbul',
    rating: 4.7,
    count: 445,
    result: result(3, 210, 445, 4.2, 4.7, 'Checkout sonrası NPS → Google'),
  }),
  firm({
    id: uuid('h', 5),
    name: 'Marina Bay Suites',
    slug: 'demo-marina-bay-suites',
    sector: 'hotel',
    address: 'Ataşehir, İstanbul',
    rating: 4.8,
    count: 389,
    result: result(4, 175, 389, 4.0, 4.8, 'Booking puanı 8.2 → 8.9'),
  }),
  firm({
    id: uuid('h', 6),
    name: 'Bosphorus View Hotel',
    slug: 'demo-bosphorus-view',
    sector: 'hotel',
    address: 'Üsküdar, İstanbul',
    rating: 4.6,
    count: 298,
    result: result(2, 160, 298, 4.1, 4.6, 'İlk 8 haftada yorum +%86'),
  }),
  firm({
    id: uuid('h', 7),
    name: 'CityNest Business Hotel',
    slug: 'demo-citynest-business',
    sector: 'hotel',
    address: 'Maslak, İstanbul',
    rating: 4.5,
    count: 267,
    result: result(3, 132, 267, 3.9, 4.5, 'Kurumsal konuk NPS 7.4 → 8.8'),
  }),
  firm({
    id: uuid('h', 8),
    name: 'Olive Garden Residence',
    slug: 'demo-olive-garden-res',
    sector: 'hotel',
    address: 'Bebek, İstanbul',
    rating: 4.9,
    count: 512,
    result: result(5, 248, 512, 4.3, 4.9, '5★ oranı %55 → %81'),
  }),
  firm({
    id: uuid('h', 9),
    name: 'Airport Comfort Inn',
    slug: 'demo-airport-comfort',
    sector: 'hotel',
    address: 'Yenibosna, İstanbul',
    rating: 4.4,
    count: 334,
    result: result(3, 188, 334, 3.8, 4.4, 'Gece check-in şikayetleri −70%'),
  }),
  firm({
    id: uuid('h', 10),
    name: 'Sultanahmet Heritage Hotel',
    slug: 'demo-sultanahmet-heritage',
    sector: 'hotel',
    address: 'Fatih, İstanbul',
    rating: 4.7,
    count: 476,
    result: result(4, 220, 476, 4.2, 4.7, 'Turist yorumları İngilizce/TR 2 dil yanıt'),
  }),
];

const AUTO_DEMOS = [
  firm({
    id: 'b1b2c3d4-e5f6-7890-abcd-ef1111111111',
    name: 'Bosch Car Service — Kadıköy',
    slug: 'demo-bosch-car-kadikoy',
    sector: 'auto',
    address: 'Kadıköy, İstanbul',
    rating: 4.5,
    count: 186,
    website: 'https://www.boschcarservice.com',
    maps: 'https://www.google.com/maps/search/?api=1&query=Bosch+Car+Service+Kadikoy',
    result: result(3, 92, 186, 4.0, 4.5, 'Servis çıkışı NPS · yorum +%102'),
  }),
  firm({
    id: 'b1b2c3d4-e5f6-7890-abcd-ef2222222222',
    name: 'King Auto Service',
    slug: 'demo-king-auto',
    sector: 'auto',
    address: 'Ümraniye, İstanbul',
    rating: 4.7,
    count: 243,
    website: 'https://kingautoservice.com',
    maps: 'https://www.google.com/maps/search/?api=1&query=King+Auto+Service+Istanbul',
    result: result(4, 118, 243, 4.1, 4.7, 'Fiyat şeffaflığı + hızlı onay yanıtı'),
  }),
  firm({
    id: 'b1b2c3d4-e5f6-7890-abcd-ef3333333333',
    name: 'Yamanlar Expertiz',
    slug: 'demo-yamanlar-expertiz',
    sector: 'auto',
    address: 'Kağıthane, İstanbul',
    rating: 4.9,
    count: 412,
    website: 'https://www.yamanlarexpertiz.com',
    maps: 'https://www.google.com/maps/search/?api=1&query=Yamanlar+Expertiz',
    result: result(5, 195, 412, 4.4, 4.9, 'Expertiz güven skoru · 5★ %72'),
  }),
  firm({
    id: uuid('a', 4),
    name: 'OtoTech Servis Merkezi',
    slug: 'demo-ototech-servis',
    sector: 'auto',
    address: 'Kartal, İstanbul',
    rating: 4.6,
    count: 278,
    result: result(3, 140, 278, 4.0, 4.6, 'Teslim SMS sonrası Google daveti'),
  }),
  firm({
    id: uuid('a', 5),
    name: 'Premium Detailing Studio',
    slug: 'demo-premium-detailing',
    sector: 'auto',
    address: 'Ataşehir, İstanbul',
    rating: 4.8,
    count: 356,
    result: result(4, 165, 356, 4.2, 4.8, 'Paket satış + yorum teşviki'),
  }),
  firm({
    id: uuid('a', 6),
    name: 'HızlıLastik 7/24',
    slug: 'demo-hizlilastik',
    sector: 'auto',
    address: 'Üsküdar, İstanbul',
    rating: 4.5,
    count: 221,
    result: result(2, 110, 221, 3.9, 4.5, '2 ayda yorum 2×'),
  }),
  firm({
    id: uuid('a', 7),
    name: 'EuroGarage Authorized',
    slug: 'demo-eurogarage',
    sector: 'auto',
    address: 'Beylikdüzü, İstanbul',
    rating: 4.7,
    count: 309,
    result: result(5, 152, 309, 4.1, 4.7, 'Yetkili servis NPS 8.1 → 9.0'),
  }),
  firm({
    id: uuid('a', 8),
    name: 'MotorCare Hybrid',
    slug: 'demo-motorcare-hybrid',
    sector: 'auto',
    address: 'Şişli, İstanbul',
    rating: 4.6,
    count: 264,
    result: result(3, 128, 264, 4.0, 4.6, 'Hibrit/elektrikli araç yorumları öne çıktı'),
  }),
  firm({
    id: uuid('a', 9),
    name: 'CityWash & Care',
    slug: 'demo-citywash-care',
    sector: 'auto',
    address: 'Beşiktaş, İstanbul',
    rating: 4.4,
    count: 198,
    result: result(3, 95, 198, 3.8, 4.4, 'Negatif yorum yanıt süresi −80%'),
  }),
  firm({
    id: uuid('a', 10),
    name: 'Anadolu Oto Ekspertiz',
    slug: 'demo-anadolu-ekspertiz',
    sector: 'auto',
    address: 'Maltepe, İstanbul',
    rating: 4.8,
    count: 387,
    result: result(4, 180, 387, 4.3, 4.8, 'Rapor güveni · Google ★+0.5'),
  }),
];

export const DEMO_PRESENTATION_FIRMS = [...CLINIC_DEMOS, ...HOTEL_DEMOS, ...AUTO_DEMOS];

export function demoResultOf(clinic) {
  return clinic?.integration_config?.demo_result || null;
}

/** DB listesine eksik demo kartları ekler; mevcut demo-* kayıtlarını satış sonucu ile zenginleştirir. */
export function mergePresentationDemoFirms(clinics) {
  const list = [...(clinics || [])];
  const bySlug = new Map(list.filter((c) => c?.slug).map((c) => [c.slug, c]));

  for (const demo of DEMO_PRESENTATION_FIRMS) {
    const existing = bySlug.get(demo.slug);
    if (existing) {
      const cfg = { ...(existing.integration_config || {}) };
      if (!cfg.demo_result && demo.integration_config?.demo_result) {
        cfg.demo_result = demo.integration_config.demo_result;
        existing.integration_config = cfg;
      }
      if (existing.google_review_count == null && demo.google_review_count != null) {
        existing.google_review_count = demo.google_review_count;
      }
      if (existing.google_rating == null && demo.google_rating != null) {
        existing.google_rating = demo.google_rating;
      }
      if (!existing.google_maps_url && demo.google_maps_url) {
        existing.google_maps_url = demo.google_maps_url;
        existing.google_review_url = demo.google_review_url || demo.google_maps_url;
      }
    } else {
      const row = { ...demo, integration_config: { ...demo.integration_config } };
      list.push(row);
      bySlug.set(demo.slug, row);
    }
  }
  return list;
}

export function demoResultHtml(clinic) {
  const r = demoResultOf(clinic);
  if (!r) return '';
  return `<div class="firm-result">
    <strong>${escapeAttr(r.headline)}</strong>
    <span>${escapeAttr(r.detail)}</span>
  </div>`;
}

function escapeAttr(s) {
  return String(s || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
