-- Dashboard Recall / eNPS pilot demo verisi (Medident — sabit clinic_id)
-- Sayfa yenileme ve farklı oturumlarda tablolar dolu kalsın.

ALTER TABLE enps_responses ADD COLUMN IF NOT EXISTS employee_name TEXT;
ALTER TABLE recall_campaigns ADD COLUMN IF NOT EXISTS patient_name TEXT;
ALTER TABLE recall_campaigns ADD COLUMN IF NOT EXISTS result TEXT;

ALTER TABLE recall_campaigns DROP CONSTRAINT IF EXISTS recall_campaigns_status_check;
ALTER TABLE recall_campaigns
  ADD CONSTRAINT recall_campaigns_status_check
  CHECK (status IN (
    'queued', 'sent', 'booked', 'ignored',
    'takipte', 'ulaşıldı', 'geri çağrıldı', 'randevu planlandı'
  ));

INSERT INTO enps_responses (id, clinic_id, department, employee_name, score, feedback, flow, created_at)
VALUES
  ('a1000001-0000-4000-8000-000000000001', '51738ea8-c12e-40ce-a0e2-42869496d76b', 'Doktor', 'Dr. Selin Aksoy', 9, 'Ekip iletişimi ve iş akışı güçlü.', 'promoter', now() - interval '2 days'),
  ('a1000001-0000-4000-8000-000000000002', '51738ea8-c12e-40ce-a0e2-42869496d76b', 'Doktor', 'Dr. Murat Ergin', 8, 'Ekip iletişimi ve iş akışı güçlü.', 'promoter', now() - interval '3 days'),
  ('a1000001-0000-4000-8000-000000000003', '51738ea8-c12e-40ce-a0e2-42869496d76b', 'Doktor', 'Dr. Derya Koç', 9, 'Ekip iletişimi ve iş akışı güçlü.', 'promoter', now() - interval '4 days'),
  ('a1000001-0000-4000-8000-000000000004', '51738ea8-c12e-40ce-a0e2-42869496d76b', 'Asistan', 'Elif Yıldız', 8, 'Ekip iletişimi ve iş akışı güçlü.', 'promoter', now() - interval '5 days'),
  ('a1000001-0000-4000-8000-000000000005', '51738ea8-c12e-40ce-a0e2-42869496d76b', 'Asistan', 'Buse Acar', 7, 'Yoğun saatlerde destek ve görev paylaşımı iyileştirilmeli.', 'detractor', now() - interval '6 days'),
  ('a1000001-0000-4000-8000-000000000006', '51738ea8-c12e-40ce-a0e2-42869496d76b', 'Asistan', 'Merve Şahin', 9, 'Ekip iletişimi ve iş akışı güçlü.', 'promoter', now() - interval '7 days'),
  ('a1000001-0000-4000-8000-000000000007', '51738ea8-c12e-40ce-a0e2-42869496d76b', 'Asistan', 'Seda Kılıç', 8, 'Ekip iletişimi ve iş akışı güçlü.', 'promoter', now() - interval '8 days'),
  ('a1000001-0000-4000-8000-000000000008', '51738ea8-c12e-40ce-a0e2-42869496d76b', 'Asistan', 'Nisa Polat', 8, 'Ekip iletişimi ve iş akışı güçlü.', 'promoter', now() - interval '9 days'),
  ('a1000001-0000-4000-8000-000000000009', '51738ea8-c12e-40ce-a0e2-42869496d76b', 'Asistan', 'İrem Öz', 6, 'Yoğun saatlerde destek ve görev paylaşımı iyileştirilmeli.', 'detractor', now() - interval '10 days'),
  ('a1000001-0000-4000-8000-00000000000a', '51738ea8-c12e-40ce-a0e2-42869496d76b', 'Resepsiyon', 'Gizem Yalçın', 9, 'Ekip iletişimi ve iş akışı güçlü.', 'promoter', now() - interval '11 days'),
  ('a1000001-0000-4000-8000-00000000000b', '51738ea8-c12e-40ce-a0e2-42869496d76b', 'Resepsiyon', 'Ece Taş', 8, 'Ekip iletişimi ve iş akışı güçlü.', 'promoter', now() - interval '12 days'),
  ('a1000001-0000-4000-8000-00000000000c', '51738ea8-c12e-40ce-a0e2-42869496d76b', 'Hasta ilişkileri', 'Burak Can', 8, 'Ekip iletişimi ve iş akışı güçlü.', 'promoter', now() - interval '13 days'),
  ('a1000001-0000-4000-8000-00000000000d', '51738ea8-c12e-40ce-a0e2-42869496d76b', 'Sterilizasyon', 'Fatma Çetin', 9, 'Ekip iletişimi ve iş akışı güçlü.', 'promoter', now() - interval '14 days'),
  ('a1000001-0000-4000-8000-00000000000e', '51738ea8-c12e-40ce-a0e2-42869496d76b', 'Laboratuvar', 'Kerem Uslu', 7, 'Yoğun saatlerde destek ve görev paylaşımı iyileştirilmeli.', 'detractor', now() - interval '15 days'),
  ('a1000001-0000-4000-8000-00000000000f', '51738ea8-c12e-40ce-a0e2-42869496d76b', 'Klinik müdürü', 'Klinik Müdürü', 9, 'Ekip iletişimi ve iş akışı güçlü.', 'promoter', now() - interval '16 days')
ON CONFLICT (id) DO UPDATE SET
  clinic_id = EXCLUDED.clinic_id,
  department = EXCLUDED.department,
  employee_name = EXCLUDED.employee_name,
  score = EXCLUDED.score,
  feedback = EXCLUDED.feedback,
  flow = EXCLUDED.flow,
  created_at = EXCLUDED.created_at;

INSERT INTO recall_campaigns (id, clinic_id, patient_name, last_treatment, months_since_visit, status, result, created_at)
VALUES
  ('b2000001-0000-4000-8000-000000000001', '51738ea8-c12e-40ce-a0e2-42869496d76b', 'Ayşe Yılmaz', 'Zirkonyum kaplama kontrolü', 6, 'geri çağrıldı', 'Randevu alındı', now() - interval '3 days'),
  ('b2000001-0000-4000-8000-000000000002', '51738ea8-c12e-40ce-a0e2-42869496d76b', 'Mehmet Kaya', 'İmplant kontrolü', 3, 'ulaşıldı', 'Kontrol hatırlatıldı', now() - interval '8 days'),
  ('b2000001-0000-4000-8000-000000000003', '51738ea8-c12e-40ce-a0e2-42869496d76b', 'Zeynep Demir', 'Diş taşı temizliği', 12, 'takipte', 'WhatsApp bilgilendirme gönderildi', now() - interval '14 days'),
  ('b2000001-0000-4000-8000-000000000004', '51738ea8-c12e-40ce-a0e2-42869496d76b', 'Can Arslan', 'Ortodonti kontrolü', 2, 'randevu planlandı', 'Asistan geri aradı', now() - interval '21 days')
ON CONFLICT (id) DO UPDATE SET
  clinic_id = EXCLUDED.clinic_id,
  patient_name = EXCLUDED.patient_name,
  last_treatment = EXCLUDED.last_treatment,
  months_since_visit = EXCLUDED.months_since_visit,
  status = EXCLUDED.status,
  result = EXCLUDED.result,
  created_at = EXCLUDED.created_at;
