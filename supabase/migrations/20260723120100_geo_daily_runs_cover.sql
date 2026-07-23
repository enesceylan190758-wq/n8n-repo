-- Cover image for daily GEO packs (list + social).
alter table public.geo_daily_runs
  add column if not exists cover_image_url text;

comment on column public.geo_daily_runs.cover_image_url is
  'Optional hero/cover URL for /geo list and share cards.';
