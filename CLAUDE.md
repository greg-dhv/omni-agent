# Omni Agent Platform

## Overview

Omni is an AI-powered marketing operations platform that automates repetitive marketing tasks through specialized agents. Each agent focuses on a specific marketing domain (Google Ads, SEO, competitor analysis, etc.) and generates recommendations that require human approval before execution.

**Core Principle:** All agent recommendations require consultant approval before execution. No automatic changes without human oversight.

## Vision

Build a suite of marketing agents that handle the grunt work of digital marketing while keeping humans in control of strategic decisions. Consultants approve recommendations, clients see results through a dedicated portal.

## Architecture

```
omniagent/
├── frontend/          # Next.js 16 + React 19 + TypeScript + Tailwind CSS 4
├── backend/           # Python + Claude AI agents
├── supabase/          # Database migrations and RLS policies
└── CLAUDE.md          # This file
```

## Agents

### Current Agents

| Agent | Status | Description |
|-------|--------|-------------|
| **Google Ads Agent** | Active | Analyzes campaign performance, identifies optimization opportunities (pause keywords, add negatives, adjust bids) |
| **SEO Content Agent** | Active | Identifies keyword opportunities, generates multilingual blog content (EN, FR, NL) |

### Planned Agents

| Agent | Priority | Description |
|-------|----------|-------------|
| **Competitor Analysis Agent** | High | Monitor competitor ads, keywords, and content strategies |
| **Meta Ads Agent** | Medium | Facebook/Instagram ad optimization |
| **LinkedIn Ads Agent** | Medium | B2B ad campaign optimization |
| **Email Marketing Agent** | Low | Campaign analysis and subject line optimization |
| **Landing Page Agent** | Low | Conversion rate optimization suggestions |

## User Roles

### Consultant (Marketing Agency)
- Reviews and approves/rejects agent recommendations
- Configures agent schedules and thresholds
- Manages client accounts
- Full access to all data and settings

### Client (Brand/Business)
- Views performance reports and trends
- Accesses content library (approved blog posts)
- Reviews action history (what was optimized)
- Read-only access, no approval capabilities

## Frontend Pages

### Consultant Views
- `/dashboard` - Overview of pending recommendations, recent actions, agent status
- `/google-ads` - Google Ads performance metrics, recommendations, action history
- `/seo-content` - Keyword opportunities, content drafts, published articles
- `/settings` - Agent schedules, email config, thresholds

### Client Portal
- `/reporting` - Performance trends (30-day vs 60-day comparison, YoY analysis)
- `/content` - Published blog articles with multilingual versions
- `/actions` - History of executed optimizations with impact metrics

## Backend Structure

```
backend/
├── agents/
│   ├── google_ads/
│   │   ├── analyst.py      # Pulls data from Google Ads API
│   │   ├── analyzer.py     # Claude AI analyzes for opportunities
│   │   └── executor.py     # Executes approved recommendations
│   └── seo_content/
│       ├── researcher.py   # Identifies keyword opportunities
│       ├── writer.py       # Claude AI generates content
│       └── executor.py     # Publishes and delivers content
├── core/
│   ├── scheduler.py        # APScheduler job management
│   ├── supabase.py         # Database operations
│   ├── email.py            # SendGrid/SMTP email delivery
│   └── models.py           # Pydantic data models
└── main.py                 # Entry point (scheduler, executor loop, CLI)
```

## Recommendation Workflow

```
1. Agent runs analysis (scheduled or manual)
2. Claude AI identifies opportunities
3. Recommendations saved with status: "pending"
4. Consultant reviews in dashboard
5. Consultant approves or skips
6. Executor processes approved recommendations
7. Action logged with success/fail status
8. Client sees results in portal
```

## Database Schema (Supabase)

| Table | Purpose |
|-------|---------|
| `profiles` | User accounts with role (consultant/client) |
| `recommendations` | Agent suggestions (pending/approved/executed/skipped) |
| `actions` | Execution log with status and impact metrics |
| `performance_snapshots` | Daily metrics for reporting |
| `content` | Blog articles with multilingual versions |
| `job_runs` | Agent execution history |
| `settings` | Configuration (schedules, emails, thresholds) |

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS 4 |
| Backend | Python 3.10+, Anthropic Claude API, APScheduler |
| Database | Supabase (PostgreSQL) with Row-Level Security |
| Auth | Supabase Auth (email-based) |
| Real-time | Supabase Postgres Changes (live updates) |
| Charts | Recharts |
| Email | SendGrid |
| Ads API | Google Ads API |

## Development

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py              # Run scheduler
python main.py --analyze    # One-off analysis
python main.py --execute    # Process approved recommendations
```

### Environment Variables

**Frontend (.env.local)**
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

**Backend (.env)**
- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_ADS_*` (credentials)
- `SENDGRID_API_KEY`

## Current Status

- Google Ads agent: Functional (analysis + execution)
- SEO Content agent: Functional (generation + delivery)
- Consultant dashboard: Complete with real-time updates
- Client portal: Complete (reporting, content, actions)
- Auth: Working with role-based access
- Multi-client support: Implemented (database migration + UI)

## Multi-Client Architecture

Consultants can manage multiple businesses, each with their own:
- Google Ads account (customer ID + refresh token)
- Google Search Console property
- Contact information
- Agent settings overrides

### Database Schema
```sql
clients (
  id, name, slug, website_url,
  google_ads_customer_id, google_ads_login_customer_id, google_ads_refresh_token,
  gsc_property_url, contact_email, contact_name,
  settings, active, created_at, updated_at
)

consultant_clients (consultant_id, client_id, role)
```

### Frontend
- Client switcher in sidebar (`/src/components/layout/ClientSwitcher.tsx`)
- Client management page (`/settings/clients`)
- All data scoped by `client_id` URL parameter

### Backend
- `GoogleAdsAPIClient.for_client(client_data)` factory method
- `SupabaseRepository` has client-scoped query methods
- Credentials loaded from database per client

## TODOs

- [ ] Google Search Console API integration (real keyword data)
- [ ] Competitor data API integration (Ahrefs/SEMrush)
- [x] Multi-client support (one consultant, many clients)
- [ ] Approval notifications (email/Slack)
- [ ] PDF report exports
- [ ] Batch approve/skip operations
