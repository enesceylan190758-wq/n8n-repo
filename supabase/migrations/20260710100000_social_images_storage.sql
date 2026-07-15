-- Sosyal medya görselleri — Instagram/LinkedIn API için public URL
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'social-images',
  'social-images',
  true,
  5242880,
  ARRAY['image/png', 'image/jpeg', 'image/webp']
)
ON CONFLICT (id) DO UPDATE SET
  public = EXCLUDED.public,
  file_size_limit = EXCLUDED.file_size_limit,
  allowed_mime_types = EXCLUDED.allowed_mime_types;

DROP POLICY IF EXISTS "Public read social images" ON storage.objects;
CREATE POLICY "Public read social images"
  ON storage.objects FOR SELECT
  TO public
  USING (bucket_id = 'social-images');

DROP POLICY IF EXISTS "Service role manage social images" ON storage.objects;
CREATE POLICY "Service role manage social images"
  ON storage.objects FOR ALL
  TO service_role
  USING (bucket_id = 'social-images')
  WITH CHECK (bucket_id = 'social-images');
