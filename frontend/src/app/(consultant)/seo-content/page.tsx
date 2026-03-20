import { createClient } from '@/lib/supabase/server';
import { Card, CardHeader, CardTitle, CardContent, Badge } from '@/components/ui';
import { SEOContentClient } from './SEOContentClient';
import { ContentList } from './ContentList';
import { FileText, Search, Send } from 'lucide-react';

export default async function SEOContentPage() {
  const supabase = await createClient();

  // Fetch pending SEO recommendations
  const { data: recommendations } = await supabase
    .from('recommendations')
    .select('*')
    .eq('agent', 'seo_content')
    .eq('status', 'pending')
    .order('priority', { ascending: false })
    .order('created_at', { ascending: false });

  // Fetch content drafts
  const { data: drafts } = await supabase
    .from('content')
    .select('*')
    .in('status', ['draft', 'approved'])
    .order('created_at', { ascending: false });

  // Fetch sent content
  const { data: sentContent } = await supabase
    .from('content')
    .select('*')
    .eq('status', 'sent')
    .order('sent_at', { ascending: false })
    .limit(10);

  // Stats
  const { count: draftCount } = await supabase
    .from('content')
    .select('*', { count: 'exact', head: true })
    .eq('status', 'draft');

  const { count: sentCount } = await supabase
    .from('content')
    .select('*', { count: 'exact', head: true })
    .eq('status', 'sent');

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">SEO & Content</h1>
        <p className="mt-1 text-sm text-gray-500">
          Keyword opportunities and blog article generation
        </p>
      </div>

      {/* Stats */}
      <div className="mb-8 grid gap-4 sm:grid-cols-3">
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-blue-50 p-2">
              <Search className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Keyword Opportunities</p>
              <p className="text-2xl font-semibold text-gray-900">
                {recommendations?.length || 0}
              </p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-yellow-50 p-2">
              <FileText className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Drafts Ready</p>
              <p className="text-2xl font-semibold text-gray-900">
                {draftCount || 0}
              </p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-green-50 p-2">
              <Send className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Sent to Client</p>
              <p className="text-2xl font-semibold text-gray-900">
                {sentCount || 0}
              </p>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* Keyword Opportunities */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Keyword Opportunities</CardTitle>
            <Badge variant="info">{recommendations?.length || 0} pending</Badge>
          </CardHeader>
          <CardContent>
            <SEOContentClient initialRecommendations={recommendations || []} />
          </CardContent>
        </Card>

        {/* Content Drafts */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Content Drafts</CardTitle>
            <Badge variant="warning">{drafts?.length || 0} drafts</Badge>
          </CardHeader>
          <CardContent>
            <ContentList initialContent={drafts || []} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
