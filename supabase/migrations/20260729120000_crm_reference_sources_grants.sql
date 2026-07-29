-- crm_reference_sources was created after initial GRANT ALL ON ALL TABLES;
-- service_role could not SELECT → clinic-bootstrap failed → UI temsilci names empty.

GRANT SELECT, INSERT, UPDATE, DELETE ON public.crm_reference_sources TO service_role;
