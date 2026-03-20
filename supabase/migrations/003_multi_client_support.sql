-- Multi-Client Support Migration
-- Allows managing multiple businesses with separate Google Ads accounts

-- ============================================
-- CLIENTS TABLE (the businesses you manage)
-- ============================================
create table public.clients (
    id uuid primary key default uuid_generate_v4(),
    name text not null,
    slug text unique not null, -- URL-friendly identifier
    website_url text,

    -- Google Ads credentials (encrypted at rest by Supabase)
    google_ads_customer_id text, -- Without dashes, e.g., "1234567890"
    google_ads_login_customer_id text, -- MCC account ID if using manager account
    google_ads_refresh_token text, -- OAuth refresh token

    -- Google Search Console
    gsc_property_url text, -- e.g., "sc-domain:example.com"

    -- Contact info
    contact_email text,
    contact_name text,

    -- Agent settings per client (overrides global settings)
    settings jsonb default '{}',
    -- Example: {"google_ads": {"lookback_days": 7}, "seo_content": {"languages": ["en", "fr"]}}

    -- Status
    active boolean default true,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

create index idx_clients_active on public.clients(active);
create index idx_clients_slug on public.clients(slug);

-- ============================================
-- ADD client_id TO EXISTING TABLES
-- ============================================

-- Recommendations
alter table public.recommendations
    add column client_id uuid references public.clients(id) on delete cascade;
create index idx_recommendations_client_id on public.recommendations(client_id);

-- Actions
alter table public.actions
    add column client_id uuid references public.clients(id) on delete cascade;
create index idx_actions_client_id on public.actions(client_id);

-- Performance Snapshots
alter table public.performance_snapshots
    add column client_id uuid references public.clients(id) on delete cascade;
-- Update unique constraint to include client_id
alter table public.performance_snapshots drop constraint if exists performance_snapshots_date_source_key;
alter table public.performance_snapshots add constraint performance_snapshots_date_source_client_key unique(date, source, client_id);

-- Content
alter table public.content
    add column client_id uuid references public.clients(id) on delete cascade;
create index idx_content_client_id on public.content(client_id);

-- Job Runs
alter table public.job_runs
    add column client_id uuid references public.clients(id) on delete cascade;
create index idx_job_runs_client_id on public.job_runs(client_id);

-- ============================================
-- CONSULTANT-CLIENT RELATIONSHIP
-- ============================================
-- Links consultants to the clients they manage
create table public.consultant_clients (
    id uuid primary key default uuid_generate_v4(),
    consultant_id uuid not null references public.profiles(id) on delete cascade,
    client_id uuid not null references public.clients(id) on delete cascade,
    role text default 'manager' check (role in ('owner', 'manager', 'viewer')),
    created_at timestamptz default now(),
    unique(consultant_id, client_id)
);

create index idx_consultant_clients_consultant on public.consultant_clients(consultant_id);
create index idx_consultant_clients_client on public.consultant_clients(client_id);

-- ============================================
-- CLIENT USERS (for client portal access)
-- ============================================
-- Links client portal users to their business
alter table public.profiles
    add column client_id uuid references public.clients(id) on delete set null;

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Get clients for current user (consultant sees their managed clients, client sees their own)
create or replace function public.get_user_clients()
returns setof public.clients as $$
declare
    user_role text;
    user_client_id uuid;
begin
    -- Get current user's role and client_id
    select role, client_id into user_role, user_client_id
    from public.profiles
    where id = auth.uid();

    if user_role = 'consultant' then
        -- Consultants see clients they manage
        return query
        select c.*
        from public.clients c
        inner join public.consultant_clients cc on c.id = cc.client_id
        where cc.consultant_id = auth.uid()
        and c.active = true
        order by c.name;
    else
        -- Clients see only their own business
        return query
        select * from public.clients
        where id = user_client_id
        and active = true;
    end if;
end;
$$ language plpgsql security definer;

-- ============================================
-- ROW LEVEL SECURITY FOR CLIENTS
-- ============================================
alter table public.clients enable row level security;
alter table public.consultant_clients enable row level security;

-- Consultants can view clients they manage
create policy "Consultants can view their clients"
    on public.clients for select
    using (
        id in (
            select client_id from public.consultant_clients
            where consultant_id = auth.uid()
        )
        or
        id = (select client_id from public.profiles where id = auth.uid())
    );

-- Consultants can update clients they manage
create policy "Consultants can update their clients"
    on public.clients for update
    using (
        id in (
            select client_id from public.consultant_clients
            where consultant_id = auth.uid()
            and role in ('owner', 'manager')
        )
    );

-- Consultants can insert new clients
create policy "Consultants can create clients"
    on public.clients for insert
    with check (
        exists (
            select 1 from public.profiles
            where id = auth.uid()
            and role = 'consultant'
        )
    );

-- Consultant-client relationship policies
create policy "Users can view their consultant_clients"
    on public.consultant_clients for select
    using (consultant_id = auth.uid());

create policy "Consultants can manage consultant_clients"
    on public.consultant_clients for all
    using (
        consultant_id = auth.uid()
        or
        client_id in (
            select client_id from public.consultant_clients
            where consultant_id = auth.uid()
            and role = 'owner'
        )
    );

-- ============================================
-- UPDATE EXISTING RLS POLICIES TO INCLUDE client_id
-- ============================================

-- Drop existing policies that need updating (if they exist)
drop policy if exists "Consultants can view all recommendations" on public.recommendations;
drop policy if exists "Clients can view their recommendations" on public.recommendations;

-- Recommendations: scope by client
create policy "Users can view recommendations for their clients"
    on public.recommendations for select
    using (
        client_id in (select id from public.get_user_clients())
        or client_id is null -- Legacy data without client_id
    );

-- Actions: scope by client
drop policy if exists "Consultants can view all actions" on public.actions;
drop policy if exists "Clients can view their actions" on public.actions;

create policy "Users can view actions for their clients"
    on public.actions for select
    using (
        client_id in (select id from public.get_user_clients())
        or client_id is null
    );

-- Content: scope by client
drop policy if exists "Anyone can view published content" on public.content;

create policy "Users can view content for their clients"
    on public.content for select
    using (
        client_id in (select id from public.get_user_clients())
        or client_id is null
        or status = 'published'
    );

-- Performance snapshots: scope by client
create policy "Users can view snapshots for their clients"
    on public.performance_snapshots for select
    using (
        client_id in (select id from public.get_user_clients())
        or client_id is null
    );

-- Job runs: consultants only, scoped by client
create policy "Consultants can view job runs for their clients"
    on public.job_runs for select
    using (
        exists (select 1 from public.profiles where id = auth.uid() and role = 'consultant')
        and (
            client_id in (select id from public.get_user_clients())
            or client_id is null
        )
    );
