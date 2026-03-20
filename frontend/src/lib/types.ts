// Database types for AI Ops Platform

export type UserRole = 'consultant' | 'client';

export type AgentType = 'google_ads' | 'seo_content' | 'competitor';

// Client (business) that you manage
export interface Client {
  id: string;
  name: string;
  slug: string;
  website_url: string | null;
  google_ads_customer_id: string | null;
  google_ads_login_customer_id: string | null;
  google_ads_refresh_token: string | null;
  gsc_property_url: string | null;
  contact_email: string | null;
  contact_name: string | null;
  settings: Record<string, unknown>;
  business_context: BusinessContext | null;
  active: boolean;
  created_at: string;
  updated_at: string;
}

// Business context for AI analysis
export interface BusinessContext {
  industry?: string;
  country?: string;
  description?: string;
  target_audience?: string;
  key_products?: string[];
  competitors?: string[];
  kpis?: string[];
  notes?: string;
  ad_copy_restrictions?: string[];
}

export type RecommendationStatus = 'pending' | 'approved' | 'skipped' | 'executed' | 'failed';

export type Priority = 'high' | 'medium' | 'low';

export type ContentStatus = 'draft' | 'approved' | 'sent' | 'published';

export type JobStatus = 'running' | 'completed' | 'failed';

export interface Profile {
  id: string;
  email: string | null;
  full_name: string | null;
  role: UserRole;
  company_name: string | null;
  avatar_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface Recommendation {
  id: string;
  client_id: string | null;
  agent: AgentType;
  type: string;
  status: RecommendationStatus;
  priority: Priority;
  title: string;
  summary: string | null;
  details: Record<string, unknown>;
  created_at: string;
  reviewed_at: string | null;
  reviewed_by: string | null;
  executed_at: string | null;
}

export interface Action {
  id: string;
  recommendation_id: string | null;
  agent: AgentType;
  action_type: string;
  title: string | null;
  description: string | null;
  impact: string | null;
  result: 'success' | 'failed' | 'partial' | null;
  error_message: string | null;
  metadata: Record<string, unknown>;
  executed_at: string;
}

export interface PerformanceSnapshot {
  id: string;
  date: string;
  source: 'google_ads' | 'organic' | 'meta_ads';
  metrics: {
    cost?: number;
    clicks?: number;
    impressions?: number;
    conversions?: number;
    ctr?: number;
    cpc?: number;
    cost_per_conversion?: number;
  };
  created_at: string;
}

export interface Content {
  id: string;
  recommendation_id: string | null;
  keyword: string | null;
  keyword_en: string | null;
  keyword_fr: string | null;
  keyword_nl: string | null;
  slug: string | null;
  title_en: string | null;
  title_fr: string | null;
  title_nl: string | null;
  content_en: string | null;
  content_fr: string | null;
  content_nl: string | null;
  meta_description_en: string | null;
  meta_description_fr: string | null;
  meta_description_nl: string | null;
  recommendation_details: {
    keyword?: string;
    intent?: string;
    search_volume?: number;
    current_position?: number;
    opportunity_type?: string;
    suggested_topic?: string;
    notes?: string;
    keyword_difficulty?: number;
  } | null;
  status: ContentStatus;
  sent_to: string | null;
  sent_at: string | null;
  published_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface JobRun {
  id: string;
  agent: AgentType;
  status: JobStatus;
  started_at: string;
  completed_at: string | null;
  summary: Record<string, unknown>;
  error_message: string | null;
}

export interface Settings {
  key: string;
  value: Record<string, unknown>;
  updated_at: string;
}

// Dashboard stats
export interface DashboardStats {
  pendingCount: number;
  executedToday: number;
  totalSavings: number;
  lastRunTime: string | null;
}

// Google Ads specific recommendation details
export interface GoogleAdsRecommendationDetails {
  campaign_id?: string;
  campaign_name?: string;
  ad_group_id?: string;
  ad_group_name?: string;
  keyword_id?: string;
  keyword_text?: string;
  cost?: number;
  clicks?: number;
  impressions?: number;
  conversions?: number;
  ctr?: number;
  cpc?: number;
  suggested_action?: string;
}

// SEO Content specific recommendation details
export interface SEOContentRecommendationDetails {
  keyword?: string;
  search_volume?: number;
  keyword_difficulty?: number;
  current_position?: number;
  opportunity_score?: number;
  suggested_topics?: string[];
}
