-- Klinik profil alanları (logo, web, Google, Trustpilot vb.)
ALTER TABLE clinics ADD COLUMN IF NOT EXISTS logo_url TEXT;
ALTER TABLE clinics ADD COLUMN IF NOT EXISTS website_url TEXT;
ALTER TABLE clinics ADD COLUMN IF NOT EXISTS email TEXT;
ALTER TABLE clinics ADD COLUMN IF NOT EXISTS address TEXT;
ALTER TABLE clinics ADD COLUMN IF NOT EXISTS google_maps_url TEXT;
ALTER TABLE clinics ADD COLUMN IF NOT EXISTS trustpilot_url TEXT;
ALTER TABLE clinics ADD COLUMN IF NOT EXISTS sikayetvar_url TEXT;
ALTER TABLE clinics ADD COLUMN IF NOT EXISTS website_reviews_url TEXT;
ALTER TABLE clinics ADD COLUMN IF NOT EXISTS google_rating NUMERIC(2,1);
ALTER TABLE clinics ADD COLUMN IF NOT EXISTS google_review_count INT;

-- Pilot: Medident İstanbul (medidentistanbul.com — Abdulkadir Yaşar)
UPDATE clinics SET
  name = 'Medident İstanbul',
  slug = 'medident-istanbul',
  logo_url = 'https://medidentistanbul.com/wp-content/uploads/2021/07/cropped-MediDent_pdf.png',
  website_url = 'https://medidentistanbul.com',
  email = 'info@medidentistanbul.com',
  address = 'Acıbadem, Acıbadem Cd. 195F, 34718 Üsküdar/İstanbul',
  whatsapp_phone = '+905491190819',
  booking_url = 'https://medidentistanbul.com/iletisim/',
  google_maps_url = 'https://www.google.com/maps/search/?api=1&query=Medident+%C4%B0stanbul+Ac%C4%B1badem+Cd+195F+%C3%9Csk%C3%BCdar',
  google_review_url = 'https://www.google.com/maps/search/?api=1&query=Medident+%C4%B0stanbul+Ac%C4%B1badem+Cd+195F+%C3%9Csk%C3%BCdar',
  trustpilot_url = NULL,
  sikayetvar_url = 'https://www.sikayetvar.com/ozel-medident-agiz-ve-dis-sagligi-poliklinigi',
  website_reviews_url = 'https://medidentistanbul.com/musteri-yorumlari/',
  complaint_form_url = 'https://www.sikayetvar.com/ozel-medident-agiz-ve-dis-sagligi-poliklinigi'
WHERE id = '51738ea8-c12e-40ce-a0e2-42869496d76b';

-- Web sitesinden çekilen müşteri yorumları (Trustpilot profili yok)
INSERT INTO reputation_mentions (clinic_id, source, url, content, sentiment, risk_score, is_critical)
SELECT
  '51738ea8-c12e-40ce-a0e2-42869496d76b',
  'website',
  'https://medidentistanbul.com/musteri-yorumlari/',
  v.content,
  'positive',
  5,
  false
FROM (VALUES
  ('Tek kelimeyle mükemmel bir yer, klinik içi olsun personelleri olsun hepsi güler yüzlü kaliteli insanlar özellikle levent hocamın eli çok temiz diş taşı temizliği yaptırdım hiç acı hissetmedim.'),
  ('Tavsiye üzerine gittim. Profesyonel bir sağlık hizmeti sunuyorlar. Tüm süreçlerden memnun kaldım. Özellikle Enes ve Abdülkadir Bey''e ilgisi için çok teşekkür ederim.')
) AS v(content)
WHERE NOT EXISTS (
  SELECT 1 FROM reputation_mentions m
  WHERE m.clinic_id = '51738ea8-c12e-40ce-a0e2-42869496d76b'
    AND m.source = 'website'
    AND m.content = v.content
);
