-- AI Ops Platform - Row Level Security Policies
-- Run this after 001_initial_schema.sql

-- ============================================
-- Enable RLS on all tables
-- ============================================
alter table public.profiles enable row level security;
alter table public.recommendations enable row level security;
alter table public.actions enable row level security;
alter table public.performance_snapshots enable row level security;
alter table public.content enable row level security;
alter table public.job_runs enable row level security;
alter table public.settings enable row level security;

-- ============================================
-- Helper function to get user role
-- ============================================
create or replace function public.get_user_role()
returns text as $$
    select role from public.profiles where id = auth.uid();
$$ language sql security definer;

-- ============================================
-- PROFILES policies
-- ============================================
-- Users can read their own profile
create policy "Users can read own profile"
    on public.profiles for select
    using (id = auth.uid());

-- Users can update their own profile
create policy "Users can update own profile"
    on public.profiles for update
    using (id = auth.uid());

-- Consultants can read all profiles
create policy "Consultants can read all profiles"
    on public.profiles for select
    using (public.get_user_role() = 'consultant');

-- ============================================
-- RECOMMENDATIONS policies
-- ============================================
-- Consultants have full access to recommendations
create policy "Consultants full access to recommendations"
    on public.recommendations for all
    using (public.get_user_role() = 'consultant');

-- Clients can only view executed recommendations
create policy "Clients can view executed recommendations"
    on public.recommendations for select
    using (
        public.get_user_role() = 'client'
        and status = 'executed'
    );

-- ============================================
-- ACTIONS policies
-- ============================================
-- Consultants have full access
create policy "Consultants full access to actions"
    on public.actions for all
    using (public.get_user_role() = 'consultant');

-- Clients can read all actions (transparency)
create policy "Clients can read actions"
    on public.actions for select
    using (public.get_user_role() = 'client');

-- ============================================
-- PERFORMANCE SNAPSHOTS policies
-- ============================================
-- Consultants have full access
create policy "Consultants full access to performance"
    on public.performance_snapshots for all
    using (public.get_user_role() = 'consultant');

-- Clients can read performance data
create policy "Clients can read performance"
    on public.performance_snapshots for select
    using (public.get_user_role() = 'client');

-- ============================================
-- CONTENT policies
-- ============================================
-- Consultants have full access
create policy "Consultants full access to content"
    on public.content for all
    using (public.get_user_role() = 'consultant');

-- Clients can read sent/published content
create policy "Clients can read sent content"
    on public.content for select
    using (
        public.get_user_role() = 'client'
        and status in ('sent', 'published')
    );

-- ============================================
-- JOB RUNS policies
-- ============================================
-- Consultants only
create policy "Consultants full access to job runs"
    on public.job_runs for all
    using (public.get_user_role() = 'consultant');

-- ============================================
-- SETTINGS policies
-- ============================================
-- Consultants only
create policy "Consultants full access to settings"
    on public.settings for all
    using (public.get_user_role() = 'consultant');

-- ============================================
-- Service role bypass (for Python backend)
-- ============================================
-- The Python backend uses the service_role key which bypasses RLS
-- This is intentional for automated operations
