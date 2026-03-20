'use client';

import { useState, useEffect } from 'react';
import { createClient } from '@/lib/supabase/client';
import { RecommendationList } from '@/components/recommendations';
import { Recommendation } from '@/lib/types';

interface DashboardClientProps {
  initialRecommendations: Recommendation[];
}

export function DashboardClient({ initialRecommendations }: DashboardClientProps) {
  const [recommendations, setRecommendations] = useState<Recommendation[]>(initialRecommendations);
  const supabase = createClient();

  // Subscribe to realtime updates
  useEffect(() => {
    const channel = supabase
      .channel('recommendations')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'recommendations',
        },
        (payload) => {
          if (payload.eventType === 'INSERT') {
            setRecommendations((prev) => [payload.new as Recommendation, ...prev]);
          } else if (payload.eventType === 'UPDATE') {
            setRecommendations((prev) =>
              prev.filter((r) => r.id !== payload.new.id || payload.new.status === 'pending')
            );
          } else if (payload.eventType === 'DELETE') {
            setRecommendations((prev) =>
              prev.filter((r) => r.id !== payload.old.id)
            );
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
    <RecommendationList
      recommendations={recommendations}
      onApprove={handleApprove}
      onSkip={handleSkip}
      emptyMessage="No pending recommendations. Your agents will generate new ones on schedule."
    />
  );
}
