'use client';

import { useState, useEffect, useMemo } from 'react';
import { createClient } from '@/lib/supabase/client';
import { RecommendationList } from '@/components/recommendations';
import { Recommendation } from '@/lib/types';

type FilterType = 'all' | 'improve_ad' | 'add_keyword' | 'add_negative' | 'pause_keyword' | 'flag_anomaly';

const filterLabels: Record<FilterType, string> = {
  all: 'All',
  improve_ad: 'Ad Improvements',
  add_keyword: 'New Keywords',
  add_negative: 'Negative Keywords',
  pause_keyword: 'Pause Keywords',
  flag_anomaly: 'Anomalies',
};

interface GoogleAdsClientProps {
  initialRecommendations: Recommendation[];
}

export function GoogleAdsClient({ initialRecommendations }: GoogleAdsClientProps) {
  const [recommendations, setRecommendations] = useState<Recommendation[]>(initialRecommendations);
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');
  const supabase = createClient();

  // Filter recommendations based on selected type
  const filteredRecommendations = useMemo(() => {
    if (activeFilter === 'all') return recommendations;
    return recommendations.filter((r) => r.type === activeFilter);
  }, [recommendations, activeFilter]);

  // Count recommendations by type
  const typeCounts = useMemo(() => {
    const counts: Record<FilterType, number> = {
      all: recommendations.length,
      improve_ad: 0,
      add_keyword: 0,
      add_negative: 0,
      pause_keyword: 0,
      flag_anomaly: 0,
    };
    recommendations.forEach((r) => {
      if (r.type in counts) {
        counts[r.type as FilterType]++;
      }
    });
    return counts;
  }, [recommendations]);

  // Subscribe to realtime updates for Google Ads recommendations
  useEffect(() => {
    const channel = supabase
      .channel('google-ads-recommendations')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'recommendations',
          filter: 'agent=eq.google_ads',
        },
        (payload) => {
          if (payload.eventType === 'INSERT' && payload.new.status === 'pending') {
            setRecommendations((prev) => [payload.new as Recommendation, ...prev]);
          } else if (payload.eventType === 'UPDATE') {
            if (payload.new.status !== 'pending') {
              setRecommendations((prev) => prev.filter((r) => r.id !== payload.new.id));
            }
          }
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [supabase]);

  const handleApprove = async (id: string) => {
    const { error } = await supabase
      .from('recommendations')
      .update({
        status: 'approved',
        reviewed_at: new Date().toISOString(),
      })
      .eq('id', id);

    if (!error) {
      setRecommendations((prev) => prev.filter((r) => r.id !== id));
    }
  };

  const handleSkip = async (id: string) => {
    const { error } = await supabase
      .from('recommendations')
      .update({
        status: 'skipped',
        reviewed_at: new Date().toISOString(),
      })
      .eq('id', id);

    if (!error) {
      setRecommendations((prev) => prev.filter((r) => r.id !== id));
    }
  };

  return (
    <div>
      {/* Filter Tabs */}
      <div className="mb-4 flex flex-wrap gap-2">
        {(Object.keys(filterLabels) as FilterType[]).map((filter) => (
          <button
            key={filter}
            onClick={() => setActiveFilter(filter)}
            className={`rounded-full px-3 py-1.5 text-sm font-medium transition-colors ${
              activeFilter === filter
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {filterLabels[filter]}
            {typeCounts[filter] > 0 && (
              <span
                className={`ml-1.5 rounded-full px-1.5 py-0.5 text-xs ${
                  activeFilter === filter
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-700'
                }`}
              >
                {typeCounts[filter]}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Recommendations List */}
      <RecommendationList
        recommendations={filteredRecommendations}
        onApprove={handleApprove}
        onSkip={handleSkip}
        emptyMessage={
          activeFilter === 'all'
            ? 'No pending Google Ads recommendations. The agent runs daily at 8am.'
            : `No pending ${filterLabels[activeFilter].toLowerCase()} recommendations.`
        }
      />
    </div>
  );
}
