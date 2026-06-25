-- Demo otel & oto servis kartları (sunum / satış paneli)
-- slug 'demo-*' → panelde "Örnek" rozeti

INSERT INTO clinics (
  id, name, slug, sector, logo_url, website_url, email, address,
  booking_url, google_maps_url, google_review_url,
  google_rating, google_review_count, whatsapp_phone
) VALUES
(
  'a1b2c3d4-e5f6-7890-abcd-ef1111111111',
  'Byotell İstanbul',
  'demo-byotell-istanbul',
  'hotel',
  '/logos/demo/byotell.svg',
  'https://www.byotell.com',
  'info@byotell.com',
  'Kozyatağı, İstanbul',
  'https://www.byotell.com/rezervasyon',
  'https://www.google.com/maps/search/?api=1&query=Byotell+Istanbul',
  'https://www.google.com/maps/search/?api=1&query=Byotell+Istanbul',
  4.6, 312, '+902165550001'
),
(
  'a1b2c3d4-e5f6-7890-abcd-ef2222222222',
  'Antwell Hotels',
  'demo-antwell-hotels',
  'hotel',
  '/logos/demo/antwell.svg',
  'https://www.antwellhotels.com',
  'rezervasyon@antwellhotels.com',
  'Taksim, İstanbul',
  'https://www.antwellhotels.com/book',
  'https://www.google.com/maps/search/?api=1&query=Antwell+Hotels+Istanbul',
  'https://www.google.com/maps/search/?api=1&query=Antwell+Hotels+Istanbul',
  4.8, 528, '+902124440022'
),
(
  'a1b2c3d4-e5f6-7890-abcd-ef3333333333',
  'Hilton İstanbul Bomonti',
  'demo-hilton-bomonti',
  'hotel',
  '/logos/demo/hilton.svg',
  'https://www.hilton.com',
  'bomonti@hilton.com',
  'Bomonti, Şişli / İstanbul',
  'https://www.hilton.com/en/book/reservation/',
  'https://www.google.com/maps/search/?api=1&query=Hilton+Istanbul+Bomonti',
  'https://www.google.com/maps/search/?api=1&query=Hilton+Istanbul+Bomonti',
  4.7, 1840, '+902123750000'
),
(
  'b1b2c3d4-e5f6-7890-abcd-ef1111111111',
  'Bosch Car Service — Kadıköy',
  'demo-bosch-car-kadikoy',
  'auto',
  '/logos/demo/bosch.svg',
  'https://www.boschcarservice.com',
  'kadikoy@boschcarservice.com.tr',
  'Kadıköy, İstanbul',
  'https://www.boschcarservice.com/tr/tr/booking/',
  'https://www.google.com/maps/search/?api=1&query=Bosch+Car+Service+Kadikoy',
  'https://www.google.com/maps/search/?api=1&query=Bosch+Car+Service+Kadikoy',
  4.5, 186, '+902165550101'
),
(
  'b1b2c3d4-e5f6-7890-abcd-ef2222222222',
  'King Auto Service',
  'demo-king-auto',
  'auto',
  '/logos/demo/king-auto.png',
  'https://kingautoservice.com',
  'info@kingautoservice.com',
  'Ümraniye, İstanbul',
  'https://kingautoservice.com/randevu',
  'https://www.google.com/maps/search/?api=1&query=King+Auto+Service+Istanbul',
  'https://www.google.com/maps/search/?api=1&query=King+Auto+Service+Istanbul',
  4.7, 243, '+902165550202'
),
(
  'b1b2c3d4-e5f6-7890-abcd-ef3333333333',
  'Yamanlar Expertiz',
  'demo-yamanlar-expertiz',
  'auto',
  '/logos/demo/yamanlar.png',
  'https://www.yamanlarexpertiz.com',
  'info@yamanlarexpertiz.com',
  'Kağıthane, İstanbul',
  'https://www.yamanlarexpertiz.com/randevu',
  'https://www.google.com/maps/search/?api=1&query=Yamanlar+Expertiz',
  'https://www.google.com/maps/search/?api=1&query=Yamanlar+Expertiz',
  4.9, 412, '+902125550303'
)
ON CONFLICT (id) DO UPDATE SET
  name = EXCLUDED.name,
  slug = EXCLUDED.slug,
  sector = EXCLUDED.sector,
  logo_url = EXCLUDED.logo_url,
  website_url = EXCLUDED.website_url,
  email = EXCLUDED.email,
  address = EXCLUDED.address,
  booking_url = EXCLUDED.booking_url,
  google_maps_url = EXCLUDED.google_maps_url,
  google_review_url = EXCLUDED.google_review_url,
  google_rating = EXCLUDED.google_rating,
  google_review_count = EXCLUDED.google_review_count,
  whatsapp_phone = EXCLUDED.whatsapp_phone;

INSERT INTO reputation_mentions (clinic_id, source, url, content, sentiment, risk_score, is_critical)
SELECT * FROM (VALUES
  ('a1b2c3d4-e5f6-7890-abcd-ef1111111111'::uuid, 'google', 'https://maps.google.com', 'Kahvaltı çeşitliliği harika, personel ilgili.', 'positive', 2, false),
  ('b1b2c3d4-e5f6-7890-abcd-ef2222222222'::uuid, 'google', 'https://maps.google.com', 'Hızlı servis, fiyat şeffaf anlatıldı.', 'positive', 2, false),
  ('b1b2c3d4-e5f6-7890-abcd-ef3333333333'::uuid, 'google', 'https://maps.google.com', 'Ekspertiz raporu detaylı, güven verdi.', 'positive', 3, false)
) AS v(clinic_id, source, url, content, sentiment, risk_score, is_critical)
WHERE NOT EXISTS (
  SELECT 1 FROM reputation_mentions m WHERE m.clinic_id = v.clinic_id AND m.content = v.content
);
