-- Nefalix Saha CRM — ekip ortak durum (tek satır JSON blob)
create table if not exists public.nefalix_state (
  id int primary key,
  data jsonb not null default '{}'::jsonb,
  rev int not null default 0,
  updated_at timestamptz not null default now()
);

insert into public.nefalix_state (id, data, rev)
values (1, '{}'::jsonb, 0)
on conflict (id) do nothing;

create or replace function public.nefalix_state_touch()
returns trigger
language plpgsql
as $$
begin
  new.updated_at := now();
  return new;
end;
$$;

drop trigger if exists trg_nefalix_state_touch on public.nefalix_state;
create trigger trg_nefalix_state_touch
before update on public.nefalix_state
for each row execute function public.nefalix_state_touch();

revoke all on table public.nefalix_state from anon, authenticated;
grant select, insert, update on table public.nefalix_state to service_role;
