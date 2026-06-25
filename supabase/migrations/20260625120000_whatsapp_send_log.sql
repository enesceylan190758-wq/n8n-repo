-- Global WhatsApp gönderim logu (Evolution rate limit / ban önleme)
CREATE TABLE IF NOT EXISTS whatsapp_send_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id UUID REFERENCES clinics(id),
  phone TEXT NOT NULL,
  message_preview TEXT,
  source_workflow TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'sent' CHECK (status IN ('sent', 'blocked', 'failed', 'skipped')),
  block_reason TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_whatsapp_send_log_created ON whatsapp_send_log (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_whatsapp_send_log_phone ON whatsapp_send_log (phone, created_at DESC);

ALTER TABLE whatsapp_send_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_whatsapp_log" ON whatsapp_send_log
  FOR ALL TO service_role USING (true) WITH CHECK (true);

GRANT ALL ON whatsapp_send_log TO service_role;
