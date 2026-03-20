'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { createClient } from '@/lib/supabase/client';
import { Client } from '@/lib/types';
import { Building2, ChevronDown, Plus } from 'lucide-react';
import { cn } from '@/lib/utils';
import Link from 'next/link';

interface ClientSwitcherProps {
  collapsed?: boolean;
}

export function ClientSwitcher({ collapsed = false }: ClientSwitcherProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [clients, setClients] = useState<Client[]>([]);
  const [currentClient, setCurrentClient] = useState<Client | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  // Get client from URL or localStorage
  const clientId = searchParams.get('client') ||
    (typeof window !== 'undefined' ? localStorage.getItem('selectedClientId') : null);

  useEffect(() => {
    async function fetchClients() {
      const supabase = createClient();
      const { data, error } = await supabase
        .from('clients')
        .select('*')
        .eq('active', true)
        .order('name');

      if (data && !error) {
        setClients(data);

        // Set current client
        if (clientId) {
          const selected = data.find(c => c.id === clientId);
          if (selected) {
            setCurrentClient(selected);
          } else if (data.length > 0) {
            setCurrentClient(data[0]);
            localStorage.setItem('selectedClientId', data[0].id);
          }
        } else if (data.length > 0) {
          setCurrentClient(data[0]);
          localStorage.setItem('selectedClientId', data[0].id);
        }
      }
      setLoading(false);
    }

    fetchClients();
  }, [clientId]);

  const handleSelectClient = (client: Client) => {
    setCurrentClient(client);
    localStorage.setItem('selectedClientId', client.id);
    setIsOpen(false);

    // Update URL with client parameter
    const url = new URL(window.location.href);
    url.searchParams.set('client', client.id);
    router.push(url.pathname + url.search);
  };

  if (loading) {
    return (
      <div className={cn(
        'mx-3 mb-4 animate-pulse rounded-lg bg-gray-100 p-3',
        collapsed && 'mx-2 p-2'
      )}>
        <div className="h-5 w-24 rounded bg-gray-200" />
      </div>
    );
  }

  if (clients.length === 0) {
    return (
      <Link
        href="/settings/clients/new"
        className={cn(
          'mx-3 mb-4 flex items-center gap-2 rounded-lg border-2 border-dashed border-gray-300 p-3 text-sm text-gray-500 hover:border-blue-400 hover:text-blue-600',
          collapsed && 'mx-2 justify-center p-2'
        )}
      >
        <Plus className="h-4 w-4" />
        {!collapsed && <span>Add Client</span>}
      </Link>
    );
  }

  return (
    <div className={cn('mx-3 mb-4', collapsed && 'mx-2')}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'flex w-full items-center gap-2 rounded-lg bg-gray-100 p-3 text-left hover:bg-gray-200',
          collapsed && 'justify-center p-2'
        )}
      >
        <Building2 className="h-5 w-5 text-gray-600" />
        {!collapsed && (
          <>
            <div className="flex-1 truncate">
              <div className="text-sm font-medium text-gray-900">
                {currentClient?.name || 'Select Client'}
              </div>
              {currentClient?.website_url && (
                <div className="truncate text-xs text-gray-500">
                  {currentClient.website_url.replace(/^https?:\/\//, '')}
                </div>
              )}
            </div>
            <ChevronDown className={cn(
              'h-4 w-4 text-gray-400 transition-transform',
              isOpen && 'rotate-180'
            )} />
          </>
        )}
      </button>

      {isOpen && !collapsed && (
        <div className="absolute z-50 mt-1 w-56 rounded-lg border border-gray-200 bg-white py-1 shadow-lg">
          {clients.map((client) => (
            <button
              key={client.id}
              onClick={() => handleSelectClient(client)}
              className={cn(
                'flex w-full items-center gap-2 px-3 py-2 text-left text-sm hover:bg-gray-50',
                currentClient?.id === client.id && 'bg-blue-50 text-blue-600'
              )}
            >
              <Building2 className="h-4 w-4" />
              <div className="flex-1 truncate">
                <div className="font-medium">{client.name}</div>
                {client.website_url && (
                  <div className="truncate text-xs text-gray-500">
                    {client.website_url.replace(/^https?:\/\//, '')}
                  </div>
                )}
              </div>
            </button>
          ))}

          <div className="my-1 border-t border-gray-100" />

          <Link
            href="/settings/clients"
            className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-gray-600 hover:bg-gray-50"
          >
            <Plus className="h-4 w-4" />
            <span>Manage Clients</span>
          </Link>
        </div>
      )}
    </div>
  );
}
