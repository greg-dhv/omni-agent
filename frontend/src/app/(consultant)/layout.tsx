import { ConsultantNav } from '@/components/layout';
import { createClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';

export default async function ConsultantLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    redirect('/login');
  }

  // Get pending recommendations count
  const { count: pendingCount } = await supabase
    .from('recommendations')
    .select('*', { count: 'exact', head: true })
    .eq('status', 'pending');

  return (
    <div className="flex h-screen bg-gray-50">
      <ConsultantNav pendingCount={pendingCount || 0} />
      <main className="flex-1 overflow-y-auto">
        <div className="p-8">{children}</div>
      </main>
    </div>
  );
}
