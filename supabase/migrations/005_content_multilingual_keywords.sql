-- Add translated keywords and recommendation details to content table
-- This allows storing translated keywords for each language and the original recommendation context

-- Add translated keyword columns
ALTER TABLE public.content
ADD COLUMN IF NOT EXISTS keyword_en text,
ADD COLUMN IF NOT EXISTS keyword_fr text,
ADD COLUMN IF NOT EXISTS keyword_nl text,
ADD COLUMN IF NOT EXISTS recommendation_details jsonb;

-- Comment the columns for documentation
COMMENT ON COLUMN public.content.keyword_en IS 'Target keyword translated to English';
COMMENT ON COLUMN public.content.keyword_fr IS 'Target keyword translated to French';
COMMENT ON COLUMN public.content.keyword_nl IS 'Target keyword translated to Dutch';
COMMENT ON COLUMN public.content.recommendation_details IS 'Original recommendation details for context (intent, notes, search_volume, etc.)';
