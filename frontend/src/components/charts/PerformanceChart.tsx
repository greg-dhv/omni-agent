'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { format, parseISO } from 'date-fns';
import { formatCurrency } from '@/lib/utils';

interface DataPoint {
  date: string;
  conversions?: number;
  cost?: number;
  clicks?: number;
  impressions?: number;
  cost_per_conversion?: number;
}

interface PerformanceChartProps {
  data: DataPoint[];
  metrics?: ('conversions' | 'cost' | 'clicks' | 'cost_per_conversion')[];
  height?: number;
}

const metricConfig = {
  conversions: { color: '#3B82F6', name: 'Conversions' },
  cost: { color: '#EF4444', name: 'Cost' },
  clicks: { color: '#10B981', name: 'Clicks' },
  cost_per_conversion: { color: '#F59E0B', name: 'Cost/Conv' },
};

export function PerformanceChart({
  data,
  metrics = ['conversions', 'cost_per_conversion'],
  height = 300,
}: PerformanceChartProps) {
  const formatXAxis = (dateString: string) => {
    return format(parseISO(dateString), 'MMM d');
  };

  const formatTooltipValue = (value: number, name: string) => {
    if (name === 'Cost' || name === 'Cost/Conv') {
      return formatCurrency(value);
    }
    return value.toLocaleString();
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
        <XAxis
          dataKey="date"
          tickFormatter={formatXAxis}
          stroke="#9CA3AF"
          fontSize={12}
        />
        <YAxis stroke="#9CA3AF" fontSize={12} />
        <Tooltip
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #E5E7EB',
            borderRadius: '8px',
          }}
          formatter={formatTooltipValue}
          labelFormatter={(label) => format(parseISO(label as string), 'MMM d, yyyy')}
        />
        <Legend />
        {metrics.map((metric) => (
          <Line
            key={metric}
            type="monotone"
            dataKey={metric}
            name={metricConfig[metric].name}
            stroke={metricConfig[metric].color}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
