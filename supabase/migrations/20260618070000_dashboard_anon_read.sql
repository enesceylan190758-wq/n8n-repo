-- Pilot dashboard: anon read-only (local / MVP)
CREATE POLICY "anon_read_clinics" ON clinics FOR SELECT TO anon USING (true);
CREATE POLICY "anon_read_nps" ON nps_responses FOR SELECT TO anon USING (true);
CREATE POLICY "anon_read_reviews" ON google_reviews FOR SELECT TO anon USING (true);
CREATE POLICY "anon_read_inbox" ON inbox_messages FOR SELECT TO anon USING (true);
CREATE POLICY "anon_read_enps" ON enps_responses FOR SELECT TO anon USING (true);
CREATE POLICY "anon_read_mentions" ON reputation_mentions FOR SELECT TO anon USING (true);
CREATE POLICY "anon_read_recall" ON recall_campaigns FOR SELECT TO anon USING (true);
CREATE POLICY "anon_read_events" ON automation_events FOR SELECT TO anon USING (true);
CREATE POLICY "anon_read_patients" ON patients FOR SELECT TO anon USING (true);

GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;
