'use client';

import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Button, Badge, Modal } from '@/components/ui';
import { FileText, Eye, Send, RefreshCw, Calendar, TrendingUp, Users, Smartphone } from 'lucide-react';

interface ReportData {
  period: {
    name: string;
    display: string;
    start_date: string;
    end_date: string;
  };
  overview: {
    cost: number;
    impressions: number;
    clicks: number;
    conversions: number;
    conversion_value: number;
    ctr: number;
    cpc: number;
    roas: number;
  };
  devices: Array<{
    device: string;
    cost: number;
    clicks: number;
    conversions: number;
  }>;
  audience: {
    age: Array<{ age_range: string; cost: number; conversions: number }>;
    gender: Array<{ gender: string; cost: number; conversions: number }>;
    location: Array<{ country: string; cost: number; conversions: number }>;
  };
  campaigns: Array<{
    campaign_name: string;
    cost: number;
    conversions: number;
  }>;
}

type PeriodType = 'last_month' | 'this_month' | 'last_30_days';

export function ReportsClient() {
  const [period, setPeriod] = useState<PeriodType>('last_month');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [report, setReport] = useState<ReportData | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const [previewHtml, setPreviewHtml] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const periodLabels: Record<PeriodType, string> = {
    last_month: 'Last Month',
    this_month: 'This Month',
    last_30_days: 'Last 30 Days',
  };

  const formatCurrency = (value: number) => `€${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  const formatNumber = (value: number) => {
    if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
    return value.toLocaleString();
  };

  const generateReport = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`/api/reports/generate?period=${period}`);
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || 'Failed to generate report');
      }
      const data = await response.json();
      setReport(data.report);
      setPreviewHtml(data.html);
      setSuccess('Report generated successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  const sendReport = async () => {
    if (!report) return;

    setSending(true);
    setError(null);

    try {
      const response = await fetch('/api/reports/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ period }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || 'Failed to send report');
      }

      setSuccess('Report sent successfully to client');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send report');
    } finally {
      setSending(false);
    }
  };

  const getDeviceIcon = (device: string) => {
    const icons: Record<string, string> = {
      MOBILE: '📱',
      DESKTOP: '💻',
      TABLET: '📱',
      CONNECTED_TV: '📺',
    };
    return icons[device] || '📊';
  };

  return (
    <div className="space-y-6">
      {/* Controls */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">Period:</span>
            </div>
            <div className="flex gap-2">
              {(Object.keys(periodLabels) as PeriodType[]).map((p) => (
                <button
                  key={p}
                  onClick={() => setPeriod(p)}
                  className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                    period === p
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {periodLabels[p]}
                </button>
              ))}
            </div>
            <div className="ml-auto flex gap-2">
              <Button
                variant="primary"
                onClick={generateReport}
                loading={loading}
                disabled={loading}
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Generate Report
              </Button>
            </div>
          </div>

          {error && (
            <div className="mt-4 rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-700">
              {error}
            </div>
          )}

          {success && (
            <div className="mt-4 rounded-lg bg-green-50 border border-green-200 p-3 text-sm text-green-700">
              {success}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Report Preview */}
      {report && (
        <>
          {/* Overview Cards */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            <Card className="p-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-red-600">{formatCurrency(report.overview.cost)}</p>
                <p className="text-sm text-gray-500 mt-1">Total Spend</p>
              </div>
            </Card>
            <Card className="p-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">{formatNumber(report.overview.impressions)}</p>
                <p className="text-sm text-gray-500 mt-1">Impressions</p>
              </div>
            </Card>
            <Card className="p-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-purple-600">{formatNumber(report.overview.clicks)}</p>
                <p className="text-sm text-gray-500 mt-1">Clicks</p>
              </div>
            </Card>
            <Card className="p-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">{report.overview.conversions.toFixed(0)}</p>
                <p className="text-sm text-gray-500 mt-1">Conversions</p>
              </div>
            </Card>
            <Card className="p-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">{formatCurrency(report.overview.conversion_value)}</p>
                <p className="text-sm text-gray-500 mt-1">Conv. Value</p>
              </div>
            </Card>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            {/* Device Performance */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Smartphone className="h-5 w-5 text-blue-600" />
                  Device Performance
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {report.devices.map((device) => {
                    const totalCost = report.devices.reduce((sum, d) => sum + d.cost, 0);
                    const share = totalCost > 0 ? (device.cost / totalCost) * 100 : 0;
                    return (
                      <div key={device.device} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center gap-3">
                          <span className="text-xl">{getDeviceIcon(device.device)}</span>
                          <span className="font-medium text-gray-900">{device.device.toLowerCase()}</span>
                        </div>
                        <div className="flex items-center gap-4 text-sm">
                          <span className="text-gray-600">{formatCurrency(device.cost)}</span>
                          <span className="text-gray-600">{device.conversions.toFixed(0)} conv</span>
                          <Badge variant="default">{share.toFixed(0)}%</Badge>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Audience Insights */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5 text-purple-600" />
                  Audience Insights
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Gender */}
                  {report.audience.gender.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-gray-500 mb-2">Gender</p>
                      <div className="flex gap-2">
                        {report.audience.gender.map((g) => (
                          <div key={g.gender} className="flex-1 p-3 bg-gray-50 rounded-lg text-center">
                            <p className="text-lg font-semibold text-gray-900">
                              {g.gender === 'MALE' ? '👨' : g.gender === 'FEMALE' ? '👩' : '👤'}
                            </p>
                            <p className="text-sm text-gray-600">{formatCurrency(g.cost)}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Top Locations */}
                  {report.audience.location.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-gray-500 mb-2">Top Locations</p>
                      <div className="space-y-2">
                        {report.audience.location.slice(0, 3).map((loc) => (
                          <div key={loc.country} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                            <span className="text-sm text-gray-700">🌍 {loc.country}</span>
                            <span className="text-sm font-medium text-gray-900">{formatCurrency(loc.cost)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Top Campaigns */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-green-600" />
                Top Campaigns
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {report.campaigns.slice(0, 5).map((campaign, i) => (
                  <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="font-medium text-gray-900 truncate max-w-md">{campaign.campaign_name}</span>
                    <div className="flex items-center gap-4 text-sm">
                      <span className="text-gray-600">{formatCurrency(campaign.cost)}</span>
                      <Badge variant="success">{campaign.conversions.toFixed(0)} conv</Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900">Report Ready</h3>
                  <p className="text-sm text-gray-500">Preview or send this report to your client</p>
                </div>
                <div className="flex gap-3">
                  <Button variant="outline" onClick={() => setShowPreview(true)}>
                    <Eye className="mr-2 h-4 w-4" />
                    Preview Email
                  </Button>
                  <Button variant="primary" onClick={sendReport} loading={sending}>
                    <Send className="mr-2 h-4 w-4" />
                    Send to Client
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {/* Email Preview Modal */}
      <Modal
        isOpen={showPreview}
        onClose={() => setShowPreview(false)}
        title="Email Preview"
        size="xl"
      >
        <div className="bg-gray-100 p-4 rounded-lg max-h-[70vh] overflow-y-auto">
          <div
            className="bg-white rounded-lg shadow"
            dangerouslySetInnerHTML={{ __html: previewHtml }}
          />
        </div>
      </Modal>
    </div>
  );
}
