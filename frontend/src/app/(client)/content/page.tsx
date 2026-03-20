import { createClient } from '@/lib/supabase/server';
import { Card, CardHeader, CardTitle, CardContent, Badge } from '@/components/ui';
import { formatDate, formatRelativeTime } from '@/lib/utils';
import { FileText, Globe, ExternalLink } from 'lucide-react';
import { ContentViewer } from './ContentViewer';

export default async function ContentPage() {
  const supabase = await createClient();

  // Fetch sent/published content
  const { data: content } = await supabase
    .from('content')
    .select('*')
    .in('status', ['sent', 'published'])
    .order('sent_at', { ascending: false });

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Content Library</h1>
        <p className="mt-1 text-sm text-gray-500">
          Blog articles created for your website
        </p>
      </div>

      {content?.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <FileText className="mx-auto h-12 w-12 text-gray-300" />
            <p className="mt-4 text-gray-500">No content delivered yet</p>
            <p className="mt-1 text-sm text-gray-400">
              New articles will appear here once they&apos;re ready
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {content?.map((item) => (
            <Card key={item.id} className="overflow-hidden">
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-4">
                <div className="flex items-center gap-2">
                  <Globe className="h-5 w-5 text-white/80" />
                  <span className="text-sm font-medium text-white/80">
                    {item.keyword}
                  </span>
                </div>
              </div>
              <CardContent className="pt-4">
                <h3 className="font-semibold text-gray-900 line-clamp-2">
                  {item.title_en || item.keyword}
                </h3>
                <div className="mt-2 flex flex-wrap gap-1">
                  {item.content_en && <Badge variant="default">EN</Badge>}
                  {item.content_fr && <Badge variant="default">FR</Badge>}
                  {item.content_nl && <Badge variant="default">NL</Badge>}
                </div>
                <div className="mt-3 flex items-center justify-between">
                  <p className="text-xs text-gray-500">
                    {item.sent_at
                      ? `Sent ${formatRelativeTime(item.sent_at)}`
                      : formatDate(item.created_at)}
                  </p>
                  <Badge
                    variant={item.status === 'published' ? 'success' : 'info'}
                  >
                    {item.status}
                  </Badge>
                </div>
                {item.published_url && (
                  <a
                    href={item.published_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-3 flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700"
                  >
                    <ExternalLink className="h-4 w-4" />
                    View Published
                  </a>
                )}
                <ContentViewer content={item} />
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
