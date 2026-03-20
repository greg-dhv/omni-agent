'use client';

import { useState, useEffect } from 'react';
import { createClient } from '@/lib/supabase/client';
import { Client } from '@/lib/types';
import {
  Building2,
  Plus,
  Pencil,
  Trash2,
  ExternalLink,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import Link from 'next/link';

export default function ClientsPage() {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingClient, setEditingClient] = useState<Client | null>(null);

  useEffect(() => {
    fetchClients();
  }, []);

  async function fetchClients() {
    const supabase = createClient();
    const { data, error } = await supabase
      .from('clients')
      .select('*')
      .order('name');

    if (data && !error) {
      setClients(data);
    }
    setLoading(false);
  }

  async function handleDelete(client: Client) {
    if (!confirm(`Are you sure you want to delete "${client.name}"? This will also delete all associated data.`)) {
      return;
    }

    const supabase = createClient();
    const { error } = await supabase
      .from('clients')
      .delete()
      .eq('id', client.id);

    if (!error) {
      setClients(clients.filter(c => c.id !== client.id));
    }
  }

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Clients</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage the businesses you work with
          </p>
        </div>
        <button
          onClick={() => {
            setEditingClient(null);
            setShowForm(true);
          }}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          <Plus className="h-4 w-4" />
          Add Client
        </button>
      </div>

      {showForm && (
        <ClientForm
          client={editingClient}
          onClose={() => {
            setShowForm(false);
            setEditingClient(null);
          }}
          onSave={() => {
            setShowForm(false);
            setEditingClient(null);
            fetchClients();
          }}
        />
      )}

      {clients.length === 0 ? (
        <div className="rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
          <Building2 className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">No clients yet</h3>
          <p className="mt-2 text-sm text-gray-500">
            Add your first client to get started with agent automation.
          </p>
          <button
            onClick={() => setShowForm(true)}
            className="mt-4 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            <Plus className="h-4 w-4" />
            Add Client
          </button>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {clients.map((client) => (
            <div
              key={client.id}
              className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100 text-blue-600">
                    <Building2 className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">{client.name}</h3>
                    {client.website_url && (
                      <a
                        href={client.website_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-sm text-gray-500 hover:text-blue-600"
                      >
                        {client.website_url.replace(/^https?:\/\//, '')}
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-1">
                  <button
                    onClick={() => {
                      setEditingClient(client);
                      setShowForm(true);
                    }}
                    className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
                  >
                    <Pencil className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(client)}
                    className="rounded p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-600"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>

              <div className="mt-4 space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  {client.google_ads_customer_id ? (
                    <>
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span className="text-gray-600">Google Ads connected</span>
                    </>
                  ) : (
                    <>
                      <XCircle className="h-4 w-4 text-gray-300" />
                      <span className="text-gray-400">Google Ads not configured</span>
                    </>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  {client.gsc_property_url ? (
                    <>
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span className="text-gray-600">Search Console connected</span>
                    </>
                  ) : (
                    <>
                      <XCircle className="h-4 w-4 text-gray-300" />
                      <span className="text-gray-400">Search Console not configured</span>
                    </>
                  )}
                </div>
              </div>

              {client.contact_email && (
                <div className="mt-4 border-t border-gray-100 pt-3 text-sm text-gray-500">
                  Contact: {client.contact_name || client.contact_email}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Client form component
interface ClientFormProps {
  client: Client | null;
  onClose: () => void;
  onSave: () => void;
}

function ClientForm({ client, onClose, onSave }: ClientFormProps) {
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    name: client?.name || '',
    slug: client?.slug || '',
    website_url: client?.website_url || '',
    google_ads_customer_id: client?.google_ads_customer_id || '',
    google_ads_login_customer_id: client?.google_ads_login_customer_id || '',
    google_ads_refresh_token: client?.google_ads_refresh_token || '',
    gsc_property_url: client?.gsc_property_url || '',
    contact_name: client?.contact_name || '',
    contact_email: client?.contact_email || '',
    business_context: {
      industry: (client?.business_context as Record<string, unknown>)?.industry as string || '',
      country: (client?.business_context as Record<string, unknown>)?.country as string || '',
      description: (client?.business_context as Record<string, unknown>)?.description as string || '',
      target_audience: (client?.business_context as Record<string, unknown>)?.target_audience as string || '',
      key_products: (client?.business_context as Record<string, unknown>)?.key_products as string[] || [],
      kpis: (client?.business_context as Record<string, unknown>)?.kpis as string[] || [],
      notes: (client?.business_context as Record<string, unknown>)?.notes as string || '',
    },
  });
  const [keyProductsInput, setKeyProductsInput] = useState(
    formData.business_context.key_products?.join(', ') || ''
  );
  const [kpisInput, setKpisInput] = useState(
    formData.business_context.kpis?.join(', ') || ''
  );

  // Auto-generate slug from name
  useEffect(() => {
    if (!client) {
      const slug = formData.name
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-|-$/g, '');
      setFormData(prev => ({ ...prev, slug }));
    }
  }, [formData.name, client]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);

    const supabase = createClient();

    if (client) {
      // Update existing client
      const { error } = await supabase
        .from('clients')
        .update(formData)
        .eq('id', client.id);

      if (!error) {
        onSave();
      } else {
        console.error('Error updating client:', error);
        alert('Error updating client: ' + error.message);
      }
    } else {
      // Create new client
      const { data: newClient, error } = await supabase
        .from('clients')
        .insert(formData)
        .select()
        .single();

      if (!error && newClient) {
        // Link current user as consultant for this client
        const { data: { user } } = await supabase.auth.getUser();
        if (user) {
          await supabase
            .from('consultant_clients')
            .insert({
              consultant_id: user.id,
              client_id: newClient.id,
              role: 'owner'
            });
        }
        onSave();
      } else {
        console.error('Error creating client:', error);
        alert('Error creating client: ' + (error?.message || 'Unknown error'));
      }
    }

    setSaving(false);
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-medium text-gray-900">
        {client ? 'Edit Client' : 'Add New Client'}
      </h2>

      <form onSubmit={handleSubmit} className="mt-4 space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Business Name *
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="mt-1 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="Acme Inc"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Slug *
            </label>
            <input
              type="text"
              required
              value={formData.slug}
              onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
              className="mt-1 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="acme-inc"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Website URL
            </label>
            <input
              type="url"
              value={formData.website_url}
              onChange={(e) => setFormData({ ...formData, website_url: e.target.value })}
              className="mt-1 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="https://example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Contact Email
            </label>
            <input
              type="email"
              value={formData.contact_email}
              onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
              className="mt-1 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="contact@example.com"
            />
          </div>
        </div>

        <div className="border-t border-gray-100 pt-4">
          <h3 className="text-sm font-medium text-gray-900">Google Ads</h3>
          <div className="mt-3 grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Customer ID
              </label>
              <input
                type="text"
                value={formData.google_ads_customer_id}
                onChange={(e) => setFormData({ ...formData, google_ads_customer_id: e.target.value.replace(/-/g, '') })}
                className="mt-1 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="1234567890"
              />
              <p className="mt-1 text-xs text-gray-500">Without dashes</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Manager Account ID (MCC)
              </label>
              <input
                type="text"
                value={formData.google_ads_login_customer_id}
                onChange={(e) => setFormData({ ...formData, google_ads_login_customer_id: e.target.value.replace(/-/g, '') })}
                className="mt-1 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="9876543210"
              />
            </div>

            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700">
                Refresh Token
              </label>
              <input
                type="password"
                value={formData.google_ads_refresh_token}
                onChange={(e) => setFormData({ ...formData, google_ads_refresh_token: e.target.value })}
                className="mt-1 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="OAuth refresh token"
              />
            </div>
          </div>
        </div>

        <div className="border-t border-gray-100 pt-4">
          <h3 className="text-sm font-medium text-gray-900">Google Search Console</h3>
          <div className="mt-3">
            <label className="block text-sm font-medium text-gray-700">
              Property URL
            </label>
            <input
              type="text"
              value={formData.gsc_property_url}
              onChange={(e) => setFormData({ ...formData, gsc_property_url: e.target.value })}
              className="mt-1 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="sc-domain:example.com"
            />
          </div>
        </div>

        <div className="border-t border-gray-100 pt-4">
          <h3 className="text-sm font-medium text-gray-900">Business Context (for AI Analysis)</h3>
          <p className="mt-1 text-xs text-gray-500">This helps the AI understand your business and provide better recommendations</p>
          <div className="mt-3 grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Industry
              </label>
              <input
                type="text"
                value={formData.business_context.industry}
                onChange={(e) => setFormData({
                  ...formData,
                  business_context: { ...formData.business_context, industry: e.target.value }
                })}
                className="mt-1 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="e.g., Online Gaming, E-commerce, SaaS"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Country/Region
              </label>
              <input
                type="text"
                value={formData.business_context.country}
                onChange={(e) => setFormData({
                  ...formData,
                  business_context: { ...formData.business_context, country: e.target.value }
                })}
                className="mt-1 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="e.g., Belgium, Netherlands"
              />
            </div>

            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700">
                Business Description
              </label>
              <textarea
                value={formData.business_context.description}
                onChange={(e) => setFormData({
                  ...formData,
                  business_context: { ...formData.business_context, description: e.target.value }
                })}
                rows={2}
                className="mt-1 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="Brief description of the business..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Target Audience
              </label>
              <input
                type="text"
                value={formData.business_context.target_audience}
                onChange={(e) => setFormData({
                  ...formData,
                  business_context: { ...formData.business_context, target_audience: e.target.value }
                })}
                className="mt-1 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="e.g., Adults 25-55, Small business owners"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Key Products/Services
              </label>
              <input
                type="text"
                value={keyProductsInput}
                onChange={(e) => {
                  setKeyProductsInput(e.target.value);
                  setFormData({
                    ...formData,
                    business_context: {
                      ...formData.business_context,
                      key_products: e.target.value.split(',').map(s => s.trim()).filter(Boolean)
                    }
                  });
                }}
                className="mt-1 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="Comma-separated: slots, live casino, sports"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Key KPIs
              </label>
              <input
                type="text"
                value={kpisInput}
                onChange={(e) => {
                  setKpisInput(e.target.value);
                  setFormData({
                    ...formData,
                    business_context: {
                      ...formData.business_context,
                      kpis: e.target.value.split(',').map(s => s.trim()).filter(Boolean)
                    }
                  });
                }}
                className="mt-1 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="Comma-separated: conversions, ROAS, CPA"
              />
            </div>

            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700">
                Additional Notes
              </label>
              <textarea
                value={formData.business_context.notes}
                onChange={(e) => setFormData({
                  ...formData,
                  business_context: { ...formData.business_context, notes: e.target.value }
                })}
                rows={2}
                className="mt-1 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="Any other context for AI analysis (e.g., high CPCs typical, seasonal business...)"
              />
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3 border-t border-gray-100 pt-4">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={saving}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : client ? 'Update Client' : 'Add Client'}
          </button>
        </div>
      </form>
    </div>
  );
}
