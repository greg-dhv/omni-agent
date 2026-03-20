import { createClient } from '@/lib/supabase/server';
import { Card, CardHeader, CardTitle, CardContent, Badge } from '@/components/ui';
import { formatRelativeTime, formatDate, getAgentIcon, getAgentDisplayName } from '@/lib/utils';
import { CheckCircle, XCircle, AlertCircle, Filter } from 'lucide-react';

export default async function ActionsPage() {
  const supabase = await createClient();

  // Fetch all actions
  const { data: actions } = await supabase
    .from('actions')
    .select('*')
    .order('executed_at', { ascending: false })
    .limit(50);

  // Group actions by date
  const groupedActions = actions?.reduce((groups, action) => {
    const date = formatDate(action.executed_at, 'yyyy-MM-dd');
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(action);
    return groups;
  }, {} as Record<string, typeof actions>) || {};

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

  const getResultBadge = (result: string | null) => {
    switch (result) {
      case 'success':
        return <Badge variant="success">Success</Badge>;
      case 'failed':
        return <Badge variant="danger">Failed</Badge>;
      case 'partial':
        return <Badge variant="warning">Partial</Badge>;
      default:
        return <Badge variant="default">Unknown</Badge>;
    }
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Actions History</h1>
        <p className="mt-1 text-sm text-gray-500">
          Complete history of optimizations performed on your account
        </p>
      </div>

      {Object.keys(groupedActions).length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Filter className="mx-auto h-12 w-12 text-gray-300" />
            <p className="mt-4 text-gray-500">No actions performed yet</p>
            <p className="mt-1 text-sm text-gray-400">
              Actions will appear here once optimizations are executed
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {Object.entries(groupedActions).map(([date, dayActions]) => (
            <div key={date}>
              <h2 className="mb-3 text-sm font-medium text-gray-500">
                {formatDate(date, 'EEEE, MMMM d, yyyy')}
              </h2>
              <Card>
                <CardContent className="divide-y divide-gray-100 p-0">
                  {dayActions?.map((action) => (
                    <div key={action.id} className="flex items-start gap-4 p-4">
                      <div className="mt-0.5">
                        {getResultIcon(action.result)}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">{getAgentIcon(action.agent)}</span>
                          <p className="font-medium text-gray-900">
                            {action.title || action.action_type}
                          </p>
                          {getResultBadge(action.result)}
                        </div>
                        {action.description && (
                          <p className="mt-1 text-sm text-gray-600">
                            {action.description}
                          </p>
                        )}
                        {action.impact && (
                          <p className="mt-1 text-sm font-medium text-green-600">
                            {action.impact}
                          </p>
                        )}
                        <p className="mt-1 text-xs text-gray-400">
                          {getAgentDisplayName(action.agent)} •{' '}
                          {formatRelativeTime(action.executed_at)}
                        </p>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
