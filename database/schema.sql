create extension if not exists pgcrypto;

create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  telegram_user_id bigint unique not null,
  username text,
  first_name text,
  last_name text,
  language_code text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists tournaments (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  title text not null,
  status text not null default 'draft',
  starts_at timestamptz,
  lock_at timestamptz,
  ends_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists teams (
  id uuid primary key default gen_random_uuid(),
  tournament_id uuid not null references tournaments(id) on delete cascade,
  group_code text,
  name text not null,
  created_at timestamptz not null default now()
);

create table if not exists matches (
  id uuid primary key default gen_random_uuid(),
  tournament_id uuid not null references tournaments(id) on delete cascade,
  match_number integer not null,
  stage text not null,
  group_code text,
  home_team text not null,
  away_team text not null,
  kickoff_at timestamptz,
  is_locked boolean not null default false,
  home_score integer,
  away_score integer,
  winner_team text,
  created_at timestamptz not null default now(),
  unique (tournament_id, match_number)
);

create table if not exists tournament_submissions (
  id uuid primary key default gen_random_uuid(),
  tournament_id uuid not null references tournaments(id) on delete cascade,
  user_id uuid not null references users(id) on delete cascade,
  bracket_payload jsonb not null,
  submitted_at timestamptz not null default now(),
  unique (tournament_id, user_id)
);

create table if not exists community_snapshots (
  id uuid primary key default gen_random_uuid(),
  tournament_id uuid not null references tournaments(id) on delete cascade,
  snapshot_type text not null,
  payload jsonb not null,
  created_at timestamptz not null default now()
);
