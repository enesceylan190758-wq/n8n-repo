-- Medident İstanbul pilot verisi (clinic id sabit — medidentistanbul.com)
INSERT INTO clinics (
  id, name, slug, google_review_url, complaint_form_url, booking_url, whatsapp_phone
) VALUES (
  '51738ea8-c12e-40ce-a0e2-42869496d76b',
  'Medident İstanbul',
  'medident-istanbul',
  'https://www.google.com/maps/search/?api=1&query=Medident+%C4%B0stanbul+Ac%C4%B1badem+Cd+195F+%C3%9Csk%C3%BCdar',
  'https://www.sikayetvar.com/ozel-medident-agiz-ve-dis-sagligi-poliklinigi',
  'https://medidentistanbul.com/iletisim/',
  '+905491190819'
) ON CONFLICT (id) DO UPDATE SET
  name = EXCLUDED.name,
  slug = EXCLUDED.slug,
  google_review_url = EXCLUDED.google_review_url,
  complaint_form_url = EXCLUDED.complaint_form_url,
  booking_url = EXCLUDED.booking_url,
  whatsapp_phone = EXCLUDED.whatsapp_phone;

INSERT INTO patients (clinic_id, full_name, phone, email, iys_consent, iys_consent_at, language)
SELECT c.id, 'Ayşe Yılmaz', '+905551234567', 'ayse@example.com', true, now(), 'tr'
FROM clinics c WHERE c.slug = 'medident-istanbul'
ON CONFLICT (clinic_id, phone) DO UPDATE SET
  full_name = EXCLUDED.full_name,
  iys_consent = EXCLUDED.iys_consent;

INSERT INTO patients (clinic_id, full_name, phone, iys_consent, language)
SELECT c.id, 'John Smith', '+905559876543', true, 'en'
FROM clinics c WHERE c.slug = 'medident-istanbul'
ON CONFLICT (clinic_id, phone) DO NOTHING;
