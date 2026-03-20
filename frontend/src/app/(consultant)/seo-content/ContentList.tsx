'use client';

import { useState } from 'react';
import { createClient } from '@/lib/supabase/client';
import { Content } from '@/lib/types';
import { Button, Badge, Modal } from '@/components/ui';
import { formatRelativeTime } from '@/lib/utils';
import { Eye, Send, FileText } from 'lucide-react';

interface ContentListProps {
  initialContent: Content[];
}

export function ContentList({ initialContent }: ContentListProps) {
  const [content, setContent] = useState<Content[]>(initialContent);
  const [previewContent, setPreviewContent] = useState<Content | null>(null);
  const [previewLang, setPreviewLang] = useState<'en' | 'fr' | 'nl'>('en');
  const [sending, setSending] = useState<string | null>(null);
  const supabase = createClient();

  const handleSendToClient = async (item: Content) => {
    setSending(item.id);

    // Update status to approved (backend will pick up and send email)
    const { error } = await supabase
      .from('content')
      .update({
        status: 'approved',
        updated_at: new Date().toISOString(),
      })
      .eq('id', item.id);

    if (!error) {
      setContent((prev) =>
        prev.map((c) =>
          c.id === item.id ? { ...c, status: 'approved' as const } : c
        )
      );
    }

    setSending(null);
  };

  const getTitle = (item: Content, lang: 'en' | 'fr' | 'nl') => {
    switch (lang) {
      case 'en':
        return item.title_en;
      case 'fr':
        return item.title_fr;
      case 'nl':
        return item.title_nl;
    }
  };

  const getContent = (item: Content, lang: 'en' | 'fr' | 'nl') => {
    switch (lang) {
      case 'en':
        return item.content_en;
      case 'fr':
        return item.content_fr;
      case 'nl':
        return item.content_nl;
    }
  };

  if (content.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <FileText className="h-12 w-12 text-gray-300" />
        <p className="mt-4 text-sm text-gray-500">
          No content drafts yet. Approve keyword opportunities to generate articles.
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-3">
        {content.map((item) => (
          <div
            key={item.id}
            className="flex items-center justify-between rounded-lg border border-gray-200 p-3"
          >
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <p className="truncate font-medium text-gray-900">
                  {item.title_en || item.keyword}
                </p>
                <Badge
                  variant={item.status === 'draft' ? 'warning' : 'info'}
                >
                  {item.status}
                </Badge>
              </div>
              <p className="mt-0.5 text-xs text-gray-500">
                {item.keyword} • {formatRelativeTime(item.created_at)}
              </p>
              <div className="mt-1 flex gap-1">
                {item.content_en && <Badge variant="default">EN</Badge>}
                {item.content_fr && <Badge variant="default">FR</Badge>}
                {item.content_nl && <Badge variant="default">NL</Badge>}
              </div>
            </div>
            <div className="ml-4 flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setPreviewContent(item)}
              >
                <Eye className="h-4 w-4" />
              </Button>
              {item.status === 'draft' && (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => handleSendToClient(item)}
                  loading={sending === item.id}
                >
                  <Send className="mr-1 h-4 w-4" />
                  Approve
                </Button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Preview Modal */}
      <Modal
        isOpen={!!previewContent}
        onClose={() => setPreviewContent(null)}
        title="Content Preview"
        size="xl"
      >
        {previewContent && (
          <div>
            <div className="mb-4 flex gap-2">
              {(['en', 'fr', 'nl'] as const).map((lang) => (
                <button
                  key={lang}
                  onClick={() => setPreviewLang(lang)}
                  className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                    previewLang === lang
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {lang.toUpperCase()}
                </button>
              ))}
            </div>
            <div className="rounded-lg bg-gray-50 p-4">
              <h3 className="text-lg font-semibold text-gray-900">
                {getTitle(previewContent, previewLang) || 'No title'}
              </h3>
              <div className="prose prose-sm mt-4 max-h-96 overflow-y-auto">
                {getContent(previewContent, previewLang) || 'No content'}
              </div>
            </div>
          </div>
        )}
      </Modal>
    </>
  );
}
