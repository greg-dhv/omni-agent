'use client';

import { useState, useEffect } from 'react';
import { createClient } from '@/lib/supabase/client';
import { Card, CardHeader, CardTitle, CardContent, Button } from '@/components/ui';
import { Save, Clock, Mail, Building2, ChevronRight } from 'lucide-react';
import Link from 'next/link';

interface ScheduleSettings {
  enabled: boolean;
  cron: string;
  timezone: string;
}

interface EmailSettings {
  from_name: string;
  from_email: string;
}

export default function SettingsPage() {
  const [googleAdsSchedule, setGoogleAdsSchedule] = useState<ScheduleSettings>({
    enabled: true,
    cron: '0 8 * * *',
    timezone: 'Europe/Brussels',
  });
  const [seoSchedule, setSeoSchedule] = useState<ScheduleSettings>({
    enabled: true,
    cron: '0 9 * * 1',
    timezone: 'Europe/Brussels',
  });
  const [emailSettings, setEmailSettings] = useState<EmailSettings>({
    from_name: 'AI Ops',
    from_email: 'noreply@example.com',
  });
  const [clientCount, setClientCount] = useState(0);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const supabase = createClient();

  useEffect(() => {
    loadSettings();
    loadClientCount();
  }, []);

  const loadSettings = async () => {
    const { data } = await supabase.from('settings').select('*');

    if (data) {
      data.forEach((setting) => {
        switch (setting.key) {
          case 'google_ads_schedule':
            setGoogleAdsSchedule(setting.value as ScheduleSettings);
            break;
          case 'seo_content_schedule':
            setSeoSchedule(setting.value as ScheduleSettings);
            break;
          case 'email_settings':
            setEmailSettings(setting.value as EmailSettings);
            break;
        }
      });
    }
  };

  const loadClientCount = async () => {
    const { count } = await supabase
      .from('clients')
      .select('*', { count: 'exact', head: true })
      .eq('active', true);
    setClientCount(count || 0);
  };

  const saveSettings = async () => {
    setSaving(true);
    setMessage(null);

    try {
      const updates = [
        { key: 'google_ads_schedule', value: googleAdsSchedule },
        { key: 'seo_content_schedule', value: seoSchedule },
        { key: 'email_settings', value: emailSettings },
      ];

      for (const update of updates) {
        const { error } = await supabase
          .from('settings')
          .upsert(
            { key: update.key, value: update.value, updated_at: new Date().toISOString() },
            { onConflict: 'key' }
          );

        if (error) throw error;
      }

      setMessage({ type: 'success', text: 'Settings saved successfully!' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save settings. Please try again.' });
    }

    setSaving(false);
  };

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="mt-1 text-sm text-gray-500">
            Configure agent schedules and notifications
          </p>
        </div>
        <Button onClick={saveSettings} loading={saving}>
          <Save className="mr-2 h-4 w-4" />
          Save Changes
        </Button>
      </div>

      {message && (
        <div
          className={`mb-6 rounded-lg p-4 ${
            message.type === 'success'
              ? 'bg-green-50 text-green-700'
              : 'bg-red-50 text-red-700'
          }`}
        >
          {message.text}
        </div>
      )}

      <div className="space-y-6">
        {/* Clients Management Link */}
        <Link href="/settings/clients">
          <Card className="cursor-pointer transition-colors hover:bg-gray-50">
            <CardContent className="flex items-center justify-between py-5">
              <div className="flex items-center gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100">
                  <Building2 className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">Manage Clients</h3>
                  <p className="text-sm text-gray-500">
                    {clientCount} {clientCount === 1 ? 'client' : 'clients'} configured
                  </p>
                </div>
              </div>
              <ChevronRight className="h-5 w-5 text-gray-400" />
            </CardContent>
          </Card>
        </Link>

        {/* Agent Schedules */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Agent Schedules
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Google Ads Schedule */}
            <div>
              <div className="flex items-center justify-between">
                <label className="font-medium text-gray-900">Google Ads Agent</label>
                <label className="relative inline-flex cursor-pointer items-center">
                  <input
                    type="checkbox"
                    checked={googleAdsSchedule.enabled}
                    onChange={(e) =>
                      setGoogleAdsSchedule({ ...googleAdsSchedule, enabled: e.target.checked })
                    }
                    className="peer sr-only"
                  />
                  <div className="peer h-6 w-11 rounded-full bg-gray-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-blue-600 peer-checked:after:translate-x-full peer-checked:after:border-white"></div>
                </label>
              </div>
              <p className="mt-1 text-sm text-gray-500">
                Runs daily at 8:00 AM (Europe/Brussels)
              </p>
            </div>

            {/* SEO Content Schedule */}
            <div>
              <div className="flex items-center justify-between">
                <label className="font-medium text-gray-900">SEO & Content Agent</label>
                <label className="relative inline-flex cursor-pointer items-center">
                  <input
                    type="checkbox"
                    checked={seoSchedule.enabled}
                    onChange={(e) =>
                      setSeoSchedule({ ...seoSchedule, enabled: e.target.checked })
                    }
                    className="peer sr-only"
                  />
                  <div className="peer h-6 w-11 rounded-full bg-gray-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-blue-600 peer-checked:after:translate-x-full peer-checked:after:border-white"></div>
                </label>
              </div>
              <p className="mt-1 text-sm text-gray-500">
                Runs weekly on Mondays at 9:00 AM (Europe/Brussels)
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Email Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mail className="h-5 w-5" />
              Email Settings
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                From Name
              </label>
              <input
                type="text"
                value={emailSettings.from_name}
                onChange={(e) =>
                  setEmailSettings({ ...emailSettings, from_name: e.target.value })
                }
                placeholder="Omni Agent"
                className="mt-1 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                From Email
              </label>
              <input
                type="email"
                value={emailSettings.from_email}
                onChange={(e) =>
                  setEmailSettings({ ...emailSettings, from_email: e.target.value })
                }
                placeholder="noreply@yourdomain.com"
                className="mt-1 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
