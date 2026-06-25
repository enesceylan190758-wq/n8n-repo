-- Panel NPS alarm kayıtları (düşük puan — yönetici geri arama)
ALTER TABLE inbox_messages DROP CONSTRAINT IF EXISTS inbox_messages_message_kind_check;
ALTER TABLE inbox_messages
  ADD CONSTRAINT inbox_messages_message_kind_check
  CHECK (message_kind IN ('inbound', 'estesoft_nps', 'nps_alert'));
