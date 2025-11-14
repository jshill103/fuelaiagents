create extension if not exists pgcrypto;
create extension if not exists vector;

-- brands
create table if not exists brands (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  voice_traits jsonb default '{}',
  banned_topics text[] default '{}',
  visual_guidelines jsonb default '{}',
  account_handles jsonb default '{}',
  created_at timestamptz default now()
);

-- sources (inspiration accounts)
create table if not exists sources (
  id uuid primary key default gen_random_uuid(),
  platform text not null,
  handle text not null,
  is_competitor boolean default true,
  fetch_schedule text default 'daily',
  last_crawl_at timestamptz
);

-- raw posts from sources
create table if not exists posts_raw (
  id uuid primary key default gen_random_uuid(),
  source_id uuid references sources(id) on delete cascade,
  platform text not null,
  post_id text,
  caption text,
  hashtags text[],
  media_urls text[],
  posted_at timestamptz,
  engagement jsonb,
  created_at timestamptz default now()
);

-- embeddings over posts_raw
create table if not exists embeddings (
  id uuid primary key default gen_random_uuid(),
  post_raw_id uuid references posts_raw(id) on delete cascade,
  labels text[],
  style_tags text[],
  topic_tags text[],
  metrics jsonb,
  vector vector(1536)
);

-- ideation
create table if not exists content_ideas (
  id uuid primary key default gen_random_uuid(),
  brand_id uuid references brands(id) on delete cascade,
  topic text,
  angle text,
  priority int default 0,
  status text default 'new',
  inspiration_refs text[]
);

-- drafts to be approved or auto-posted
create table if not exists drafts (
  id uuid primary key default gen_random_uuid(),
  brand_id uuid references brands(id) on delete cascade,
  platform text,
  type text,
  caption text,
  hashtags text[],
  asset_refs text[],
  status text default 'draft',
  review_notes text,
  scheduled_at timestamptz
);

-- published posts
create table if not exists published (
  id uuid primary key default gen_random_uuid(),
  draft_id uuid references drafts(id) on delete set null,
  platform text,
  platform_post_id text,
  permalink text,
  media_refs text[],
  published_at timestamptz default now()
);

-- metrics snapshots
create table if not exists metrics (
  id uuid primary key default gen_random_uuid(),
  published_id uuid references published(id) on delete cascade,
  snapshot_at timestamptz default now(),
  impressions bigint,
  reach bigint,
  views bigint,
  likes bigint,
  comments bigint,
  saves bigint,
  shares bigint,
  ctr numeric,
  watch_time numeric
);