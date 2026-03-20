# Omni Agent Platform

AI-powered marketing operations platform for Google Ads optimization and SEO content generation.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        NEXT.JS DASHBOARD                        │
│              (TypeScript + Tailwind CSS 4)                      │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐              │
│   │ Overview│ │ Google  │ │ SEO &   │ │ Settings│              │
│   │         │ │ Ads     │ │ Content │ │         │              │
│   └─────────┘ └─────────┘ └─────────┘ └─────────┘              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        SUPABASE                                 │
│   • Postgres database                                           │
│   • Realtime subscriptions                                      │
│   • Row Level Security                                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PYTHON AGENTS                                │
│   ┌──────────────┐    ┌──────────────┐                         │
│   │  Google Ads  │    │  SEO Content │                         │
│   │    Agent     │    │    Agent     │                         │
│   └──────────────┘    └──────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

## Features

### Google Ads Agent
- Daily analysis of campaign, keyword, and ad performance
- Claude AI identifies optimization opportunities:
  - High cost, low conversion keywords
  - Negative keyword opportunities
  - Underperforming ads
  - Budget pacing issues
- Human approval required before execution
- Automatic execution via Google Ads API

### SEO Content Agent
- Weekly keyword opportunity research
- Multilingual blog article generation (EN, FR, NL)
- Human approval at each step
- Email delivery to clients

## Setup

### Prerequisites
- Node.js 18+
- Python 3.10+
- Supabase account
- Google Ads API credentials
- Anthropic API key

### 1. Clone and Install

```bash
cd ai-ops

# Frontend
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local with your Supabase credentials

# Backend
cd ../backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
```

### 2. Set Up Supabase

1. Create a new Supabase project
2. Run the SQL migrations in order:
   ```sql
   -- Run in Supabase SQL Editor
   -- First: supabase/migrations/001_initial_schema.sql
   -- Then: supabase/migrations/002_row_level_security.sql
   ```
3. Copy your project URL and keys to the environment files

### 3. Google Ads API Setup

1. Create a Google Cloud project
2. Enable the Google Ads API
3. Create OAuth2 credentials
4. Get a developer token from Google Ads
5. Generate a refresh token
6. Update `backend/config/google-ads.yaml`

### 4. Create Your First User

```sql
-- In Supabase SQL Editor, after a user signs up:
UPDATE profiles SET role = 'consultant' WHERE email = 'your-email@example.com';
```

## Running

### Development

```bash
# Terminal 1: Frontend
cd frontend
npm run dev

# Terminal 2: Backend
cd backend
source venv/bin/activate
python main.py
```

### Production

Frontend can be deployed to Vercel. Backend should run as a systemd service or Docker container.

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
```

### Backend (.env)
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=xxx
ANTHROPIC_API_KEY=xxx
GOOGLE_ADS_CUSTOMER_ID=xxx
SENDGRID_API_KEY=xxx
```

## Agent Schedules

| Agent | Default Schedule | Timezone |
|-------|-----------------|----------|
| Google Ads | Daily at 8:00 AM | Europe/Brussels |
| SEO Content | Weekly Monday 9:00 AM | Europe/Brussels |

Schedules can be configured in the Settings page.

## User Roles

| Role | Access |
|------|--------|
| Consultant | Full access: approvals, settings, all data |
| Client | Read-only: reporting, action history, content library |

## License

Private - All rights reserved.
