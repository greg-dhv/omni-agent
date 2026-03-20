-- AI Ops Platform - Initial Schema
-- Run this in your Supabase SQL Editor

-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- ============================================
-- PROFILES (extends Supabase auth.users)
-- ============================================
create table public.profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    email text,
    full_name text,
    role text not null default 'client' check (role in ('consultant', 'client')),
    company_name text,
    avatar_url text,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- Auto-create profile on signup
create or replace function public.handle_new_user()
returns trigger as $$
begin
    insert into public.profiles (id, email, full_name, role)
    values (
        new.id,
        new.email,
        coalesce(new.raw_user_meta_data->>'full_name', split_part(new.email, '@', 1)),
        coalesce(new.raw_user_meta_data->>'role', 'client')
    );
    return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
    after insert on auth.users
    for each row execute procedure public.handle_new_user();

-- ============================================
-- RECOMMENDATIONS
-- ============================================
create table public.recommendations (
    id uuid primary key default uuid_generate_v4(),
    agent text not null check (agent in ('google_ads', 'seo_content', 'competitor')),
    type text not null,
    status text default 'pending' check (status in ('pending', 'approved', 'skipped', 'executed', 'failed')),
    priority text default 'medium' check (priority in ('high', 'medium', 'low')),
    title text not null,
    summary text,
    details jsonb default '{}',
    created_at timestamptz default now(),
    reviewed_at timestamptz,
    reviewed_by uuid references public.profiles(id),
    executed_at timestamptz
);

create index idx_recommendations_status on public.recommendations(status);
create index idx_recommendations_agent on public.recommendations(agent);
create index idx_recommendations_created_at on public.recommendations(created_at desc);

-- ============================================
-- ACTIONS (execution log)
-- ============================================
create table public.actions (
    id uuid primary key default uuid_generate_v4(),
    recommendation_id uuid references public.recommendations(id) on delete set null,
    agent text not null,
    action_type text not null,
    title text,
    description text,
    impact text,
    result text check (result in ('success', 'failed', 'partial')),
    error_message text,
    metadata jsonb default '{}',
    executed_at timestamptz default now()
);

create index idx_actions_agent on public.actions(agent);
create index idx_actions_executed_at on public.actions(executed_at desc);

-- ============================================
-- PERFORMANCE SNAPSHOTS (for reporting)
-- ============================================
create table public.performance_snapshots (
    id uuid primary key default uuid_generate_v4(),
    date date not null,
    source text not null check (source in ('google_ads', 'organic', 'meta_ads')),
    metrics jsonb not null default '{}',
    -- Expected metrics: cost, clicks, impressions, conversions, ctr, cpc, cost_per_conversion
    created_at timestamptz default now(),
    unique(date, source)
);

create index idx_performance_date on public.performance_snapshots(date desc);
create index idx_performance_source on public.performance_snapshots(source);

-- ============================================
-- CONTENT (blog articles)
-- ============================================
create table public.content (
    id uuid primary key default uuid_generate_v4(),
    recommendation_id uuid references public.recommendations(id) on delete set null,
    keyword text,
    slug text,
    -- Multilingual content
    title_en text,
    title_fr text,
    title_nl text,
    content_en text,
    content_fr text,
    content_nl text,
    meta_description_en text,
    meta_description_fr text,
    meta_description_nl text,
    -- Status tracking
    status text default 'draft' check (status in ('draft', 'approved', 'sent', 'published')),
    sent_to text, -- email address
    sent_at timestamptz,
    published_url text,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

create index idx_content_status on public.content(status);
create index idx_content_created_at on public.content(created_at desc);

-- ============================================
-- JOB RUNS (agent execution history)
-- ============================================
create table public.job_runs (
    id uuid primary key default uuid_generate_v4(),
    agent text not null,
    status text default 'running' check (status in ('running', 'completed', 'failed')),
    started_at timestamptz default now(),
    completed_at timestamptz,
    summary jsonb default '{}',
    error_message text
);

create index idx_job_runs_agent on public.job_runs(agent);
create index idx_job_runs_started_at on public.job_runs(started_at desc);

-- ============================================
-- SETTINGS (app configuration)
-- ============================================
create table public.settings (
    key text primary key,
    value jsonb not null,
    updated_at timestamptz default now()
);

-- Insert default settings
insert into public.settings (key, value) values
    ('google_ads_schedule', '{"enabled": true, "cron": "0 8 * * *", "timezone": "Europe/Brussels"}'),
    ('seo_content_schedule', '{"enabled": true, "cron": "0 9 * * 1", "timezone": "Europe/Brussels"}'),
    ('email_settings', '{"from_name": "AI Ops", "from_email": "noreply@example.com"}'),
    ('client_email', '{"email": "client@example.com", "name": "Client Name"}');
