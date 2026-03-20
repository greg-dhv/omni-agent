import { createClient } from '@/lib/supabase/server';
import { GoogleAdsClient } from './GoogleAdsClient';
import { GoogleAdsMetrics } from './GoogleAdsMetrics';

export default async function GoogleAdsPage() {
  const supabase = await createClient();

  // Fetch pending Google Ads recommendations
  const { data: recommendations } = await supabase
    .from('recommendations')
    .select('*')
    .eq('agent', 'google_ads')
    .eq('status', 'pending')
    .order('priority', { ascending: false })
    .order('created_at', { ascending: false });

  // Fetch recent Google Ads actions
  const { data: recentActions } = await supabase
    .from('actions')
    .select('*')
    .eq('agent', 'google_ads')
    .order('executed_at', { ascending: false })
    .limit(10);

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Google Ads</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage recommendations and view performance
        </p>
      </div>

      {/* Metrics with Timeline Selector */}
      <GoogleAdsMetrics />

      {/* Recommendations */}
      <GoogleAdsClient initialRecommendations={recommendations || []} />
    </div>
  );
}
