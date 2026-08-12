create table if not exists public.coach_messages (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null check (role in ('user', 'assistant')),
  content text not null,
  created_at timestamptz not null default now()
);

create index if not exists coach_messages_user_created_at_idx
  on public.coach_messages (user_id, created_at desc);

create table if not exists public.coach_memories (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  category text not null,
  content text not null,
  updated_at timestamptz not null default now(),
  unique (user_id, category, content)
);

create index if not exists coach_memories_user_updated_at_idx
  on public.coach_memories (user_id, updated_at desc);

alter table public.coach_messages enable row level security;
alter table public.coach_memories enable row level security;

create policy "Users can manage their own coach messages" on public.coach_messages
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "Users can manage their own coach memories" on public.coach_memories
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
