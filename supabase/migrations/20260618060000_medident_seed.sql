-- MediDent pilot verisi (clinic id sabit)
INSERT INTO clinics (
  id, name, slug, google_review_url, complaint_form_url, booking_url, whatsapp_phone
) VALUES (
  '51738ea8-c12e-40ce-a0e2-42869496d76b',
  'MediDent İstanbul Kartal',
  'medident-kartal',
  'https://g.page/r/medident-kartal/review',
  'https://nefalixai.com/sikayet',
  'https://cal.com/medident-kartal',
  '+902165551234'
) ON CONFLICT (slug) DO UPDATE SET
  google_review_url = EXCLUDED.google_review_url,
  complaint_form_url = EXCLUDED.complaint_form_url,
  booking_url = EXCLUDED.booking_url,
  whatsapp_phone = EXCLUDED.whatsapp_phone;

INSERT INTO patients (clinic_id, full_name, phone, email, iys_consent, iys_consent_at, language)
SELECT c.id, 'Ayşe Yılmaz', '+905551234567', 'ayse@example.com', true, now(), 'tr'
FROM clinics c WHERE c.slug = 'medident-kartal'
ON CONFLICT (clinic_id, phone) DO UPDATE SET
  full_name = EXCLUDED.full_name,
  iys_consent = EXCLUDED.iys_consent;

INSERT INTO patients (clinic_id, full_name, phone, iys_consent, language)
SELECT c.id, 'John Smith', '+905559876543', true, 'en'
FROM clinics c WHERE c.slug = 'medident-kartal'
ON CONFLICT (clinic_id, phone) DO NOTHING;
