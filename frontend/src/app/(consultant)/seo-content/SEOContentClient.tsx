'use client';

import { useState } from 'react';
import { createClient } from '@/lib/supabase/client';
import { RecommendationList } from '@/components/recommendations';
import { Recommendation } from '@/lib/types';

interface SEOContentClientProps {
  initialRecommendations: Recommendation[];
}

export function SEOContentClient({ initialRecommendations }: SEOContentClientProps) {
  const [recommendations, setRecommendations] = useState<Recommendation[]>(initialRecommendations);
  const supabase = createClient();

  const handleApprove = async (id: string) => {
    // Approving a keyword opportunity triggers article generation
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
      emptyMessage="No keyword opportunities found. The agent runs weekly on Mondays."
    />
  );
}
