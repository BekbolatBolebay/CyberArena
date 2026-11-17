-- CyberArena Supabase Schema (Optional Cloud Leaderboard & Auth)
-- Flag hashes are stored in a locked table unreadable by clients;
-- verification happens strictly via the `submit_flag` RPC.

create extension if not exists pgcrypto;

create table if not exists public.operators (
  id uuid primary key references auth.users(id) on delete cascade,
  handle text not null unique check (handle ~ '^[a-zA-Z0-9_.-]{3,24}$'),
  created_at timestamptz not null default now()
);

create table if not exists public.mission_secrets (
  mission_id text primary key,
  points int not null check (points > 0),
  flag_sha256 text not null
);

create table if not exists public.mission_solves (
  user_id uuid not null references public.operators(id) on delete cascade,
  mission_id text not null references public.mission_secrets(mission_id) on delete cascade,
  points int not null,
  solved_at timestamptz not null default now(),
  primary key (user_id, mission_id)
);

alter table public.operators enable row level security;
alter table public.mission_secrets enable row level security;
alter table public.mission_solves enable row level security;

revoke all on public.mission_secrets from anon, authenticated;

create policy operators_read_public on public.operators
  for select to anon, authenticated using (true);

create policy operators_insert_own on public.operators
  for insert to authenticated with check (id = auth.uid());

create policy solves_read_own on public.mission_solves
  for select to authenticated using (user_id = auth.uid());

create or replace function public.submit_flag(p_mission_id text, p_flag text)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_uid uuid := auth.uid();
  v_points int;
  v_expected text;
  v_actual text;
begin
  if v_uid is null then
    raise exception 'Authentication required';
  end if;

  select points, flag_sha256 into v_points, v_expected
  from public.mission_secrets
  where mission_id = p_mission_id;

  if not found then
    return jsonb_build_object('ok', false, 'error', 'Mission not found');
  end if;

  v_actual := encode(extensions.digest(trim(p_flag), 'sha256'), 'hex');
  if v_actual <> v_expected then
    return jsonb_build_object('ok', false, 'error', 'Invalid flag');
  end if;

  insert into public.mission_solves(user_id, mission_id, points)
  values (v_uid, p_mission_id, v_points)
  on conflict (user_id, mission_id) do nothing;

  return jsonb_build_object('ok', true, 'points', v_points);
end;
$$;

revoke all on function public.submit_flag(text, text) from public;
grant execute on function public.submit_flag(text, text) to authenticated;

create or replace view public.leaderboard as
select
  o.handle,
  coalesce(sum(s.points), 0)::int as score,
  count(s.mission_id)::int as solved_count
from public.operators o
left join public.mission_solves s on s.user_id = o.id
group by o.id, o.handle
order by score desc, solved_count desc;

grant select on public.leaderboard to anon, authenticated;
