'use client';

import { Action } from '@/lib/types';
import { formatRelativeTime, getAgentIcon, getAgentDisplayName } from '@/lib/utils';
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface ActionsTimelineProps {
  actions: Action[];
  maxItems?: number;
}

export function ActionsTimeline({ actions, maxItems = 10 }: ActionsTimelineProps) {
  const displayActions = actions.slice(0, maxItems);

  const getResultIcon = (result: string | null) => {
    switch (result) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'partial':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      default:
        return <CheckCircle className="h-5 w-5 text-gray-400" />;
    }
  };

  if (displayActions.length === 0) {
    return (
      <p className="text-sm text-gray-500">No recent actions</p>
    );
  }

  return (
    <div className="flow-root">
      <ul className="-mb-8">
        {displayActions.map((action, index) => (
          <li key={action.id}>
            <div className="relative pb-8">
              {index !== displayActions.length - 1 && (
                <span
                  className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-gray-200"
                  aria-hidden="true"
                />
              )}
              <div className="relative flex space-x-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100">
                  {getResultIcon(action.result)}
                </div>
                <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1">
                  <div>
                    <p className="text-sm text-gray-900">
                      <span className="mr-1">{getAgentIcon(action.agent)}</span>
                      {action.title || action.action_type}
                    </p>
                    {action.description && (
                      <p className="mt-0.5 text-sm text-gray-500">
                        {action.description}
                      </p>
                    )}
                    {action.impact && (
                      <p className="mt-0.5 text-sm font-medium text-green-600">
                        {action.impact}
                      </p>
                    )}
                  </div>
                  <div className="whitespace-nowrap text-right text-sm text-gray-500">
                    {formatRelativeTime(action.executed_at)}
                  </div>
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
