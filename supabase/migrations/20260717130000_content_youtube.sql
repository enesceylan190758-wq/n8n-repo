-- Blog + GEO içeriklerine ilgili YouTube video eşlemesi
ALTER TABLE blog_posts
  ADD COLUMN IF NOT EXISTS youtube_video_id TEXT,
  ADD COLUMN IF NOT EXISTS youtube_title TEXT,
  ADD COLUMN IF NOT EXISTS cover_image_url TEXT,
  ADD COLUMN IF NOT EXISTS footer_image_url TEXT;

ALTER TABLE geo_daily_runs
  ADD COLUMN IF NOT EXISTS youtube_video_id TEXT,
  ADD COLUMN IF NOT EXISTS youtube_title TEXT;
