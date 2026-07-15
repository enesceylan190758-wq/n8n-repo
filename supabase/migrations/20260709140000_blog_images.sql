-- Blog görselleri (kapak + alt banner)
ALTER TABLE blog_posts
  ADD COLUMN IF NOT EXISTS cover_image_url TEXT,
  ADD COLUMN IF NOT EXISTS footer_image_url TEXT;
