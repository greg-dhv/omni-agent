import { cn } from '@/lib/utils';
import { ArrowDown, ArrowUp, Minus } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string;
  change?: {
    value: number;
    direction: 'up' | 'down' | 'neutral';
  };
  changeLabel?: string;
  icon?: React.ReactNode;
  className?: string;
}

export function StatCard({
  title,
  value,
  change,
  changeLabel = 'vs last period',
  icon,
  className,
}: StatCardProps) {
  return (
    <div className={cn('rounded-xl border border-gray-200 bg-white p-6', className)}>
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-gray-500">{title}</p>
        {icon && <div className="text-gray-400">{icon}</div>}
      </div>
      <p className="mt-2 text-3xl font-semibold text-gray-900">{value}</p>
      {change && (
        <div className="mt-2 flex items-center text-sm">
          {change.direction === 'up' && (
            <ArrowUp className="mr-1 h-4 w-4 text-green-500" />
          )}
          {change.direction === 'down' && (
            <ArrowDown className="mr-1 h-4 w-4 text-red-500" />
          )}
          {change.direction === 'neutral' && (
            <Minus className="mr-1 h-4 w-4 text-gray-400" />
          )}
          <span
            className={cn(
              change.direction === 'up' && 'text-green-600',
              change.direction === 'down' && 'text-red-600',
              change.direction === 'neutral' && 'text-gray-500'
            )}
          >
            {change.value.toFixed(1)}%
          </span>
          <span className="ml-1 text-gray-500">{changeLabel}</span>
        </div>
      )}
    </div>
  );
}
