'use client';

import { useState, useEffect } from 'react';
import { createClient } from '@/lib/supabase/client';
import { Card } from '@/components/ui';
import { formatCurrency, formatNumber } from '@/lib/utils';
import { subDays, subMonths, startOfMonth, endOfMonth, format } from 'date-fns';

type TimeRange = 'yesterday' | '7days' | '30days' | 'lastMonth';

interface Metrics {
  cost: number;
  clicks: number;
  conversions: number;
  impressions: number;
  ctr: number;
  cpc: number;
}

function getDateRange(range: TimeRange): { startDate: string; endDate: string } {
  const today = new Date();

  switch (range) {
    case 'yesterday': {
      const yesterday = subDays(today, 1);
      return {
        startDate: format(yesterday, 'yyyy-MM-dd'),
        endDate: format(yesterday, 'yyyy-MM-dd'),
      };
    }
    case '7days': {
      return {
        startDate: format(subDays(today, 7), 'yyyy-MM-dd'),
        endDate: format(subDays(today, 1), 'yyyy-MM-dd'),
      };
    }
    case '30days': {
      return {
        startDate: format(subDays(today, 30), 'yyyy-MM-dd'),
        endDate: format(subDays(today, 1), 'yyyy-MM-dd'),
      };
    }
    case 'lastMonth': {
      const lastMonth = subMonths(today, 1);
      return {
        startDate: format(startOfMonth(lastMonth), 'yyyy-MM-dd'),
        endDate: format(endOfMonth(lastMonth), 'yyyy-MM-dd'),
      };
    }
  }
}

export function GoogleAdsMetrics() {
  const [timeRange, setTimeRange] = useState<TimeRange>('30days');
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [dataInfo, setDataInfo] = useState<{ daysAvailable: number; startDate: string; endDate: string } | null>(null);

  useEffect(() => {
    fetchMetrics();
  }, [timeRange]);

  async function fetchMetrics() {
    setLoading(true);
    const supabase = createClient();
    const { startDate, endDate } = getDateRange(timeRange);

    // Query daily snapshots within the date range
    const { data: snapshots, error } = await supabase
      .from('performance_snapshots')
      .select('*')
      .eq('source', 'google_ads')
      .gte('date', startDate)
      .lte('date', endDate)
      .order('date', { ascending: true });

    if (error) {
      console.error('Error fetching snapshots:', error);
      setMetrics(null);
      setDataInfo(null);
      setLoading(false);
      return;
    }

    if (snapshots && snapshots.length > 0) {
      // Aggregate daily metrics
      const aggregated = snapshots.reduce(
        (acc, snapshot) => {
          const m = snapshot.metrics || {};
          return {
            cost: acc.cost + (m.cost || 0),
            clicks: acc.clicks + (m.clicks || 0),
            conversions: acc.conversions + (m.conversions || 0),
            impressions: acc.impressions + (m.impressions || 0),
          };
        },
        { cost: 0, clicks: 0, conversions: 0, impressions: 0 }
      );

      // Calculate derived metrics
      setMetrics({
        ...aggregated,
        ctr: aggregated.impressions > 0 ? (aggregated.clicks / aggregated.impressions) * 100 : 0,
        cpc: aggregated.clicks > 0 ? aggregated.cost / aggregated.clicks : 0,
      });

      setDataInfo({
        daysAvailable: snapshots.length,
        startDate: snapshots[0].date,
        endDate: snapshots[snapshots.length - 1].date,
      });
    } else {
      setMetrics(null);
      setDataInfo(null);
    }

    setLoading(false);
  }

  const timeRangeLabels: Record<TimeRange, string> = {
    yesterday: 'Yesterday',
    '7days': 'Last 7 Days',
    '30days': 'Last 30 Days',
    lastMonth: 'Last Month',
  };

  const avgCostPerConversion = metrics && metrics.conversions > 0
    ? metrics.cost / metrics.conversions
    : 0;

  return (
    <div className="mb-8">
      {/* Timeline Selector */}
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-medium text-gray-900">Performance Overview</h2>
        <div className="flex gap-1 rounded-lg bg-gray-100 p-1">
          {(Object.keys(timeRangeLabels) as TimeRange[]).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                timeRange === range
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {timeRangeLabels[range]}
            </button>
          ))}
        </div>
      </div>

      {/* Metrics Cards */}
      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="animate-pulse p-4">
              <div className="h-4 w-24 rounded bg-gray-200" />
              <div className="mt-2 h-8 w-32 rounded bg-gray-200" />
            </Card>
          ))}
        </div>
      ) : metrics ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Card className="p-4">
            <p className="text-sm font-medium text-gray-500">
              Total Spend ({timeRangeLabels[timeRange]})
            </p>
            <p className="mt-1 text-2xl font-semibold text-gray-900">
              {formatCurrency(metrics.cost)}
            </p>
          </Card>
          <Card className="p-4">
            <p className="text-sm font-medium text-gray-500">Conversions</p>
            <p className="mt-1 text-2xl font-semibold text-gray-900">
              {formatNumber(metrics.conversions)}
            </p>
          </Card>
          <Card className="p-4">
            <p className="text-sm font-medium text-gray-500">Avg. Cost/Conv</p>
            <p className="mt-1 text-2xl font-semibold text-gray-900">
              {formatCurrency(avgCostPerConversion)}
            </p>
          </Card>
          <Card className="p-4">
            <p className="text-sm font-medium text-gray-500">Clicks</p>
            <p className="mt-1 text-2xl font-semibold text-gray-900">
              {formatNumber(metrics.clicks)}
            </p>
          </Card>
        </div>
      ) : (
        <Card className="p-8 text-center">
          <p className="text-gray-500">
            No performance data available for this period. Run an analysis to populate data.
          </p>
        </Card>
      )}

      {/* Data info */}
      {dataInfo && (
        <p className="mt-2 text-xs text-gray-400">
          Showing {dataInfo.daysAvailable} days of data ({dataInfo.startDate} to {dataInfo.endDate})
        </p>
      )}
    </div>
  );
}
