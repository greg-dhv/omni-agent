import { createClient } from '@/lib/supabase/server';
import { Card, CardHeader, CardTitle, CardContent, StatCard } from '@/components/ui';
import { PerformanceChart, ActionsTimeline } from '@/components/charts';
import { formatCurrency, formatNumber, formatPercent, calculateChange } from '@/lib/utils';
import { TrendingUp, TrendingDown, DollarSign, MousePointer, Target } from 'lucide-react';
import { subDays, format } from 'date-fns';

export default async function ReportingPage() {
  const supabase = await createClient();

  // Fetch last 30 days performance
  const thirtyDaysAgo = format(subDays(new Date(), 30), 'yyyy-MM-dd');
  const sixtyDaysAgo = format(subDays(new Date(), 60), 'yyyy-MM-dd');

  const { data: currentPeriod } = await supabase
    .from('performance_snapshots')
    .select('*')
    .eq('source', 'google_ads')
    .gte('date', thirtyDaysAgo)
    .order('date', { ascending: true });

  const { data: previousPeriod } = await supabase
    .from('performance_snapshots')
    .select('*')
    .eq('source', 'google_ads')
    .gte('date', sixtyDaysAgo)
    .lt('date', thirtyDaysAgo);

  // Fetch recent actions
  const { data: recentActions } = await supabase
    .from('actions')
    .select('*')
    .order('executed_at', { ascending: false })
    .limit(10);

  // Calculate current period totals
  const currentTotals = currentPeriod?.reduce(
    (acc, day) => ({
      cost: acc.cost + (day.metrics?.cost || 0),
      clicks: acc.clicks + (day.metrics?.clicks || 0),
      conversions: acc.conversions + (day.metrics?.conversions || 0),
      impressions: acc.impressions + (day.metrics?.impressions || 0),
    }),
    { cost: 0, clicks: 0, conversions: 0, impressions: 0 }
  ) || { cost: 0, clicks: 0, conversions: 0, impressions: 0 };

  // Calculate previous period totals
  const previousTotals = previousPeriod?.reduce(
    (acc, day) => ({
      cost: acc.cost + (day.metrics?.cost || 0),
      clicks: acc.clicks + (day.metrics?.clicks || 0),
      conversions: acc.conversions + (day.metrics?.conversions || 0),
      impressions: acc.impressions + (day.metrics?.impressions || 0),
    }),
    { cost: 0, clicks: 0, conversions: 0, impressions: 0 }
  ) || { cost: 0, clicks: 0, conversions: 0, impressions: 0 };

  const costPerConversion = currentTotals.conversions > 0
    ? currentTotals.cost / currentTotals.conversions
    : 0;
  const prevCostPerConversion = previousTotals.conversions > 0
    ? previousTotals.cost / previousTotals.conversions
    : 0;

  // Chart data
  const chartData = currentPeriod?.map((day) => ({
    date: day.date,
    conversions: day.metrics?.conversions || 0,
    cost: day.metrics?.cost || 0,
    cost_per_conversion: day.metrics?.conversions > 0
      ? day.metrics.cost / day.metrics.conversions
      : 0,
  })) || [];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Performance Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Last 30 days performance overview
        </p>
      </div>

      {/* Stats Grid */}
      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Conversions"
          value={formatNumber(currentTotals.conversions)}
          change={calculateChange(currentTotals.conversions, previousTotals.conversions)}
          changeLabel="vs prev 30 days"
          icon={<Target className="h-5 w-5" />}
        />
        <StatCard
          title="Cost per Conversion"
          value={formatCurrency(costPerConversion)}
          change={{
            ...calculateChange(costPerConversion, prevCostPerConversion),
            // Flip direction - lower is better for cost
            direction: costPerConversion < prevCostPerConversion ? 'up' : costPerConversion > prevCostPerConversion ? 'down' : 'neutral',
          }}
          changeLabel="vs prev 30 days"
          icon={<DollarSign className="h-5 w-5" />}
        />
        <StatCard
          title="Total Spend"
          value={formatCurrency(currentTotals.cost)}
          change={calculateChange(currentTotals.cost, previousTotals.cost)}
          changeLabel="vs prev 30 days"
          icon={<TrendingUp className="h-5 w-5" />}
        />
        <StatCard
          title="Clicks"
          value={formatNumber(currentTotals.clicks)}
          change={calculateChange(currentTotals.clicks, previousTotals.clicks)}
          changeLabel="vs prev 30 days"
          icon={<MousePointer className="h-5 w-5" />}
        />
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        {/* Performance Chart */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Performance Trend</CardTitle>
            </CardHeader>
            <CardContent>
              {chartData.length > 0 ? (
                <PerformanceChart
                  data={chartData}
                  metrics={['conversions', 'cost_per_conversion']}
                  height={350}
                />
              ) : (
                <div className="flex h-64 items-center justify-center text-gray-500">
                  No performance data available yet
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Recent Optimizations */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Recent Optimizations</CardTitle>
            </CardHeader>
            <CardContent>
              <ActionsTimeline actions={recentActions || []} maxItems={8} />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
