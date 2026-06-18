-- Inbox: gönderici bilgisi (dashboard'dan manuel yanıt için)
ALTER TABLE inbox_messages
  ADD COLUMN IF NOT EXISTS sender_phone TEXT,
  ADD COLUMN IF NOT EXISTS sender_name TEXT;
