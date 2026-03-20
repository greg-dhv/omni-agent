'use client';

import { cn } from '@/lib/utils';
import {
  formatCurrency,
  formatRelativeTime,
  getPriorityColor,
  getAgentDisplayName,
  getAgentIcon,
} from '@/lib/utils';
import { Recommendation } from '@/lib/types';
import { Badge, Button, Card } from '@/components/ui';
import { Check, X, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';

interface RecommendationCardProps {
  recommendation: Recommendation;
  onApprove: (id: string) => Promise<void>;
  onSkip: (id: string) => Promise<void>;
  loading?: boolean;
}

export function RecommendationCard({
  recommendation,
  onApprove,
  onSkip,
  loading = false,
}: RecommendationCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [actionLoading, setActionLoading] = useState<'approve' | 'skip' | null>(null);

  const handleApprove = async () => {
    setActionLoading('approve');
    await onApprove(recommendation.id);
    setActionLoading(null);
  };

  const handleSkip = async () => {
    setActionLoading('skip');
    await onSkip(recommendation.id);
    setActionLoading(null);
  };

  const details = recommendation.details as Record<string, unknown>;

  return (
    <Card className="overflow-hidden">
      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-3">
            <span className="text-2xl">{getAgentIcon(recommendation.agent)}</span>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-gray-900">
                  {recommendation.title}
                </h3>
                <Badge
                  variant={
                    recommendation.priority === 'high'
                      ? 'danger'
                      : recommendation.priority === 'medium'
                      ? 'warning'
                      : 'default'
                  }
                >
                  {recommendation.priority}
                </Badge>
              </div>
              <p className="mt-1 text-sm text-gray-500">
                {getAgentDisplayName(recommendation.agent)} •{' '}
                {formatRelativeTime(recommendation.created_at)}
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleSkip}
              disabled={loading || actionLoading !== null}
              loading={actionLoading === 'skip'}
            >
              <X className="mr-1 h-4 w-4" />
              Skip
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={handleApprove}
              disabled={loading || actionLoading !== null}
              loading={actionLoading === 'approve'}
            >
              <Check className="mr-1 h-4 w-4" />
              Approve
            </Button>
          </div>
        </div>

        {/* Summary */}
        {recommendation.summary && (
          <p className="mt-3 text-sm text-gray-600">{recommendation.summary}</p>
        )}

        {/* Quick stats for Google Ads */}
        {recommendation.agent === 'google_ads' && details && (
          <div className="mt-3 flex flex-wrap gap-4 text-sm">
            {details.cost !== undefined && (
              <div>
                <span className="text-gray-500">Cost:</span>{' '}
                <span className="font-medium text-gray-900">
                  {formatCurrency(details.cost as number)}
                </span>
              </div>
            )}
            {details.conversions !== undefined && (
              <div>
                <span className="text-gray-500">Conversions:</span>{' '}
                <span className="font-medium text-gray-900">
                  {details.conversions as number}
                </span>
              </div>
            )}
            {details.ctr !== undefined && (
              <div>
                <span className="text-gray-500">CTR:</span>{' '}
                <span className="font-medium text-gray-900">
                  {(details.ctr as number).toFixed(2)}%
                </span>
              </div>
            )}
          </div>
        )}

        {/* Expand/collapse details */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="mt-3 flex items-center text-sm text-blue-600 hover:text-blue-700"
        >
          {expanded ? (
            <>
              <ChevronUp className="mr-1 h-4 w-4" />
              Hide details
            </>
          ) : (
            <>
              <ChevronDown className="mr-1 h-4 w-4" />
              Show details
            </>
          )}
        </button>

        {/* Expanded details */}
        {expanded && (
          <div className="mt-3 rounded-lg bg-gray-50 p-3">
            <pre className="text-xs text-gray-600 overflow-x-auto">
              {JSON.stringify(details, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </Card>
  );
}
