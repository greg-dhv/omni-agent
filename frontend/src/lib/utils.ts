import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { format, formatDistanceToNow, parseISO } from 'date-fns';

// Tailwind class merging utility
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Format currency (EUR)
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-BE', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount);
}

// Format percentage
export function formatPercent(value: number, decimals = 1): string {
  return `${value.toFixed(decimals)}%`;
}

// Format number with thousands separator
export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-BE').format(value);
}

// Format date
export function formatDate(dateString: string, formatStr = 'MMM d, yyyy'): string {
  return format(parseISO(dateString), formatStr);
}

// Format relative time (e.g., "2 hours ago")
export function formatRelativeTime(dateString: string): string {
  return formatDistanceToNow(parseISO(dateString), { addSuffix: true });
}

// Get priority color class
export function getPriorityColor(priority: string): string {
  switch (priority) {
    case 'high':
      return 'text-red-600 bg-red-50 border-red-200';
    case 'medium':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    case 'low':
      return 'text-green-600 bg-green-50 border-green-200';
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200';
  }
}

// Get status color class
export function getStatusColor(status: string): string {
  switch (status) {
    case 'pending':
      return 'text-blue-600 bg-blue-50 border-blue-200';
    case 'approved':
      return 'text-purple-600 bg-purple-50 border-purple-200';
    case 'executed':
      return 'text-green-600 bg-green-50 border-green-200';
    case 'skipped':
      return 'text-gray-600 bg-gray-50 border-gray-200';
    case 'failed':
      return 'text-red-600 bg-red-50 border-red-200';
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200';
  }
}

// Get agent display name
export function getAgentDisplayName(agent: string): string {
  switch (agent) {
    case 'google_ads':
      return 'Google Ads';
    case 'seo_content':
      return 'SEO & Content';
    case 'competitor':
      return 'Competitor Analysis';
    default:
      return agent;
  }
}

// Get agent icon
export function getAgentIcon(agent: string): string {
  switch (agent) {
    case 'google_ads':
      return '🎰';
    case 'seo_content':
      return '🔍';
    case 'competitor':
      return '📊';
    default:
      return '🤖';
  }
}

// Truncate text
export function truncate(text: string, length: number): string {
  if (text.length <= length) return text;
  return text.slice(0, length) + '...';
}

// Calculate percentage change
export function calculateChange(current: number, previous: number): {
  value: number;
  direction: 'up' | 'down' | 'neutral';
} {
  if (previous === 0) {
    return { value: 0, direction: 'neutral' };
  }
  const change = ((current - previous) / previous) * 100;
  return {
    value: Math.abs(change),
    direction: change > 0 ? 'up' : change < 0 ? 'down' : 'neutral',
  };
}
