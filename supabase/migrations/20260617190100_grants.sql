-- RLS + grants for n8n service_role
ALTER TABLE clinics ENABLE ROW LEVEL SECURITY;
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE nps_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE google_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE inbox_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE enps_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE reputation_mentions ENABLE ROW LEVEL SECURITY;
ALTER TABLE recall_campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE automation_events ENABLE ROW LEVEL SECURITY;

-- Service role bypasses RLS by default in Supabase, but needs table grants
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT USAGE ON SCHEMA public TO service_role;

-- MVP: service_role full access policies (local dev)
CREATE POLICY "service_role_all_clinics" ON clinics FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_patients" ON patients FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_appointments" ON appointments FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_nps" ON nps_responses FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_reviews" ON google_reviews FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_inbox" ON inbox_messages FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_enps" ON enps_responses FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_mentions" ON reputation_mentions FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_recall" ON recall_campaigns FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_events" ON automation_events FOR ALL TO service_role USING (true) WITH CHECK (true);
