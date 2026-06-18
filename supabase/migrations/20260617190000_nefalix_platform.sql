-- Nefalix Platform — merkezi veri modeli (PDF v4 modülleri)
-- Tüm n8n workflow'ları bu tablolara yazar/okur

-- Klinikler (çok lokasyon)
CREATE TABLE IF NOT EXISTS clinics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  google_review_url TEXT,
  complaint_form_url TEXT,
  booking_url TEXT,
  whatsapp_phone TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Hastalar
CREATE TABLE IF NOT EXISTS patients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id UUID REFERENCES clinics(id) ON DELETE CASCADE,
  full_name TEXT NOT NULL,
  phone TEXT NOT NULL,
  email TEXT,
  iys_consent BOOLEAN DEFAULT false,
  iys_consent_at TIMESTAMPTZ,
  language TEXT DEFAULT 'tr',
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (clinic_id, phone)
);

-- Randevular (HBYS sync)
CREATE TABLE IF NOT EXISTS appointments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id UUID REFERENCES clinics(id) ON DELETE CASCADE,
  patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
  external_id TEXT,
  doctor_name TEXT,
  treatment TEXT,
  status TEXT DEFAULT 'completed',
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id, completed_at DESC);

-- Modül 1: NPS yanıtları
CREATE TABLE IF NOT EXISTS nps_responses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id UUID REFERENCES clinics(id),
  patient_id UUID REFERENCES patients(id),
  appointment_id UUID REFERENCES appointments(id),
  score INT NOT NULL CHECK (score BETWEEN 1 AND 10),
  flow TEXT CHECK (flow IN ('promoter', 'detractor')),
  message_sent TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Modül 3: Google yorumları
CREATE TABLE IF NOT EXISTS google_reviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id UUID REFERENCES clinics(id),
  external_review_id TEXT,
  author_name TEXT,
  rating INT CHECK (rating BETWEEN 1 AND 5),
  review_text TEXT,
  sentiment TEXT,
  themes JSONB DEFAULT '[]',
  draft_reply TEXT,
  urgency TEXT,
  status TEXT DEFAULT 'pending_approval' CHECK (status IN ('pending_approval', 'approved', 'published', 'rejected')),
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Modül 2: Inbox mesajları
CREATE TABLE IF NOT EXISTS inbox_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id UUID REFERENCES clinics(id),
  patient_id UUID REFERENCES patients(id),
  channel TEXT NOT NULL CHECK (channel IN ('whatsapp', 'web_chat', 'sms', 'telegram')),
  direction TEXT NOT NULL CHECK (direction IN ('inbound', 'outbound')),
  body TEXT NOT NULL,
  ai_draft_reply TEXT,
  status TEXT DEFAULT 'open' CHECK (status IN ('open', 'draft_ready', 'replied', 'closed')),
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Modül 4: Çalışan eNPS
CREATE TABLE IF NOT EXISTS enps_responses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id UUID REFERENCES clinics(id),
  department TEXT,
  score INT NOT NULL CHECK (score BETWEEN 1 AND 10),
  feedback TEXT,
  flow TEXT CHECK (flow IN ('promoter', 'detractor')),
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Add-on Sentinel: mention / itibar
CREATE TABLE IF NOT EXISTS reputation_mentions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id UUID REFERENCES clinics(id),
  source TEXT NOT NULL,
  url TEXT,
  content TEXT NOT NULL,
  sentiment TEXT,
  risk_score INT,
  recommended_action TEXT,
  is_critical BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Add-on Recall: geri çağrı kampanyaları
CREATE TABLE IF NOT EXISTS recall_campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id UUID REFERENCES clinics(id),
  patient_id UUID REFERENCES patients(id),
  last_treatment TEXT,
  months_since_visit INT,
  message_sent TEXT,
  booking_url TEXT,
  status TEXT DEFAULT 'sent' CHECK (status IN ('queued', 'sent', 'booked', 'ignored')),
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Otomasyon olay logu (tüm workflow'lar)
CREATE TABLE IF NOT EXISTS automation_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id UUID REFERENCES clinics(id),
  workflow_name TEXT NOT NULL,
  event_type TEXT NOT NULL,
  payload JSONB DEFAULT '{}',
  status TEXT DEFAULT 'success',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_automation_events_clinic ON automation_events(clinic_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_nps_clinic ON nps_responses(clinic_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reviews_status ON google_reviews(clinic_id, status);

-- Pilot klinik seed (sabit UUID — n8n workflow'ları bu ID'yi kullanır)
INSERT INTO clinics (id, name, slug, google_review_url, complaint_form_url, booking_url, whatsapp_phone)
VALUES (
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
