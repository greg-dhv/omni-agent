'use client';

import { Recommendation } from '@/lib/types';
import { RecommendationCard } from './RecommendationCard';
import { Inbox } from 'lucide-react';

interface RecommendationListProps {
  recommendations: Recommendation[];
  onApprove: (id: string) => Promise<void>;
  onSkip: (id: string) => Promise<void>;
  loading?: boolean;
  emptyMessage?: string;
}

export function RecommendationList({
  recommendations,
  onApprove,
  onSkip,
  loading = false,
  emptyMessage = 'No recommendations to review',
}: RecommendationListProps) {
  if (recommendations.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-300 bg-gray-50 py-12">
        <Inbox className="h-12 w-12 text-gray-400" />
        <p className="mt-4 text-sm text-gray-500">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {recommendations.map((recommendation) => (
        <RecommendationCard
          key={recommendation.id}
          recommendation={recommendation}
          onApprove={onApprove}
          onSkip={onSkip}
          loading={loading}
        />
      ))}
    </div>
  );
}
