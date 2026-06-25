-- Inbox: Estesoft NPS taslakları vs gelen WhatsApp mesajları
ALTER TABLE inbox_messages
  ADD COLUMN IF NOT EXISTS message_kind TEXT NOT NULL DEFAULT 'inbound',
  ADD COLUMN IF NOT EXISTS metadata JSONB NOT NULL DEFAULT '{}'::jsonb;

ALTER TABLE inbox_messages DROP CONSTRAINT IF EXISTS inbox_messages_message_kind_check;
ALTER TABLE inbox_messages
  ADD CONSTRAINT inbox_messages_message_kind_check
  CHECK (message_kind IN ('inbound', 'estesoft_nps'));

CREATE INDEX IF NOT EXISTS idx_inbox_messages_kind_clinic
  ON inbox_messages (clinic_id, message_kind, created_at DESC);
