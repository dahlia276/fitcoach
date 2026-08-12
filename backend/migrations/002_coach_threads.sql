create table if not exists public.coach_threads (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists coach_threads_user_updated_at_idx
  on public.coach_threads (user_id, updated_at desc);

alter table if exists public.coach_messages
  add column if not exists thread_id uuid references public.coach_threads(id) on delete cascade;

create index if not exists coach_messages_thread_created_at_idx
  on public.coach_messages (thread_id, created_at asc);

alter table public.coach_threads enable row level security;

do $$
begin
  if not exists (
    select 1
    from pg_policies
    where schemaname = 'public'
      and tablename = 'coach_threads'
      and policyname = 'Users can manage their own coach threads'
  ) then
    create policy "Users can manage their own coach threads"
      on public.coach_threads
      for all
      using (auth.uid() = user_id)
      with check (auth.uid() = user_id);
  end if;
end
$$;
