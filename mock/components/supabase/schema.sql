-- Run this whole file in Supabase -> SQL Editor

create table if not exists profiles (
  id uuid primary key references auth.users on delete cascade,
  full_name text,
  created_at timestamptz default now()
);

create table if not exists resumes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users on delete cascade,
  file_path text,
  parsed_profile jsonb,            -- Member 3's skill profile JSON
  created_at timestamptz default now()
);

create table if not exists saved_jobs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users on delete cascade,
  job_external_id text not null,
  title text, company text, location text, description text, url text,
  match_score int default 0,
  created_at timestamptz default now(),
  unique (user_id, job_external_id)
);

create table if not exists skill_gaps (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users on delete cascade,
  job_id uuid not null references saved_jobs on delete cascade,
  gap jsonb,                       -- Member 4's gap output
  created_at timestamptz default now(),
  unique (user_id, job_id)
);

create table if not exists roadmaps (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users on delete cascade,
  job_id uuid not null references saved_jobs on delete cascade,
  plan jsonb,                      -- Member 4's roadmap output
  progress jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  unique (user_id, job_id)
);

-- Row level security: users only touch their own rows
alter table profiles enable row level security;
alter table resumes enable row level security;
alter table saved_jobs enable row level security;
alter table skill_gaps enable row level security;
alter table roadmaps enable row level security;

create policy "own profile" on profiles for all using (auth.uid() = id) with check (auth.uid() = id);
create policy "own rows" on resumes for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own rows" on saved_jobs for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own rows" on skill_gaps for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own rows" on roadmaps for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- Auto-create a profile row on signup
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = ''
as $$
begin
  insert into public.profiles (id, full_name)
  values (new.id, new.raw_user_meta_data->>'full_name')
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

-- Private storage bucket for resumes (files stored under <user_id>/<filename>)
insert into storage.buckets (id, name, public) values ('resumes', 'resumes', false) on conflict do nothing;
create policy "own resume files" on storage.objects for all
  using (bucket_id = 'resumes' and (storage.foldername(name))[1] = auth.uid()::text)
  with check (bucket_id = 'resumes' and (storage.foldername(name))[1] = auth.uid()::text);
