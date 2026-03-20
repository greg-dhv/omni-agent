-- Add business context field to clients for dynamic AI prompts

ALTER TABLE public.clients
ADD COLUMN IF NOT EXISTS business_context jsonb DEFAULT '{}';

-- business_context structure:
-- {
--   "industry": "online casino",
--   "country": "Belgium",
--   "language": "nl",
--   "description": "Belgian online casino focused on slots and live dealer games",
--   "target_audience": "Adults 25-55 interested in online gambling",
--   "key_products": ["slots", "live casino", "sports betting"],
--   "competitors": ["betway", "unibet", "ladbrokes"],
--   "kpis": ["conversions", "cost_per_conversion", "roas"],
--   "notes": "CPCs are high (€5-15), focus on deposit conversions"
-- }

COMMENT ON COLUMN public.clients.business_context IS 'Business context for AI analysis prompts - industry, target audience, KPIs, etc.';
