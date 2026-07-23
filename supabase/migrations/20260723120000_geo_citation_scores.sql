-- GEO weekly citation scores (manual CLI/CSV; not auto-scraped).
create table if not exists public.geo_citation_scores (
  id uuid primary key default gen_random_uuid(),
  week date not null,
  prompt_id text not null,
  prompt text not null,
  engine text not null check (engine in ('chatgpt', 'perplexity', 'gemini')),
  mention boolean not null default false,
  citation_url text,
  competitor text,
  notes text,
  scored_at timestamptz not null default now(),
  unique (week, prompt_id, engine)
);

create index if not exists geo_citation_scores_week_idx
  on public.geo_citation_scores (week desc);

alter table public.geo_citation_scores enable row level security;

drop policy if exists "geo_citation_scores_public_read" on public.geo_citation_scores;
create policy "geo_citation_scores_public_read"
  on public.geo_citation_scores for select
  to anon, authenticated
  using (true);

comment on table public.geo_citation_scores is
  'Manual GEO citation checks per ISO week / prompt / engine. Source of truth; markdown baseline is template only.';
