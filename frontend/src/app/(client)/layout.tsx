import { ClientNav } from '@/components/layout';
import { createClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';

export default async function ClientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    redirect('/login');
  }

  // Get profile for company name
  const { data: profile } = await supabase
    .from('profiles')
    .select('company_name')
    .eq('id', user.id)
    .single();

  return (
    <div className="flex h-screen bg-gray-50">
      <ClientNav companyName={profile?.company_name || undefined} />
      <main className="flex-1 overflow-y-auto">
        <div className="p-8">{children}</div>
      </main>
    </div>
  );
}
