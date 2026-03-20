import { createClient } from '@/lib/supabase/server';
import { StatCard, Card, CardHeader, CardTitle, CardContent } from '@/components/ui';
import { RecommendationList } from '@/components/recommendations';
import { ActionsTimeline } from '@/components/charts';
import { formatCurrency, formatRelativeTime } from '@/lib/utils';
import { Megaphone, Search, Clock, CheckCircle } from 'lucide-react';
import { DashboardClient } from './DashboardClient';

export default async function DashboardPage() {
  const supabase = await createClient();

  // Fetch pending recommendations
  const { data: pendingRecommendations } = await supabase
    .from('recommendations')
    .select('*')
    .eq('status', 'pending')
    .order('priority', { ascending: false })
    .order('created_at', { ascending: false })
    .limit(10);

  // Fetch recent actions
  const { data: recentActions } = await supabase
    .from('actions')
    .select('*')
    .order('executed_at', { ascending: false })
    .limit(5);

  // Fetch stats
  const { count: pendingCount } = await supabase
    .from('recommendations')
    .select('*', { count: 'exact', head: true })
    .eq('status', 'pending');

  const today = new Date().toISOString().split('T')[0];
  const { count: executedToday } = await supabase
    .from('actions')
    .select('*', { count: 'exact', head: true })
    .gte('executed_at', today);

  // Get last job run
  const { data: lastJob } = await supabase
    .from('job_runs')
    .select('*')
    .eq('status', 'completed')
    .order('completed_at', { ascending: false })
    .limit(1)
    .single();

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Overview of your AI operations
        </p>
      </div>

      {/* Stats */}
      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Pending Recommendations"
          value={String(pendingCount || 0)}
          icon={<Clock className="h-5 w-5" />}
        />
        <StatCard
          title="Executed Today"
          value={String(executedToday || 0)}
          icon={<CheckCircle className="h-5 w-5" />}
        />
        <StatCard
          title="Google Ads Agent"
          value={lastJob?.agent === 'google_ads' ? 'Active' : 'Idle'}
          icon={<Megaphone className="h-5 w-5" />}
        />
        <StatCard
          title="SEO Agent"
          value={lastJob?.agent === 'seo_content' ? 'Active' : 'Idle'}
          icon={<Search className="h-5 w-5" />}
        />
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        {/* Pending Recommendations */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Pending Recommendations</CardTitle>
            </CardHeader>
            <CardContent>
              <DashboardClient
                initialRecommendations={pendingRecommendations || []}
              />
            </CardContent>
          </Card>
        </div>

        {/* Recent Actions */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Recent Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <ActionsTimeline actions={recentActions || []} maxItems={5} />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
