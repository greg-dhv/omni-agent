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
            {/* Why We Wrote This Section */}
            {previewContent.recommendation_details && (
              <div className="mb-4 rounded-lg bg-indigo-50 border border-indigo-200 p-4">
                <h4 className="font-semibold text-indigo-900 mb-2">Why We Wrote This Article</h4>
                <div className="text-sm text-indigo-800 space-y-1">
                  <p><span className="font-medium">Target Keyword:</span> {previewContent.recommendation_details.keyword}</p>
                  {previewContent.recommendation_details.opportunity_type && (
                    <p><span className="font-medium">Opportunity:</span> {previewContent.recommendation_details.opportunity_type.replace('_', ' ')}</p>
                  )}
                  {previewContent.recommendation_details.current_position && (
                    <p><span className="font-medium">Current Position:</span> #{previewContent.recommendation_details.current_position}</p>
                  )}
                  {previewContent.recommendation_details.search_volume && (
                    <p><span className="font-medium">Search Volume:</span> ~{previewContent.recommendation_details.search_volume}/month</p>
                  )}
                  {previewContent.recommendation_details.intent && (
                    <p><span className="font-medium">Intent:</span> {previewContent.recommendation_details.intent}</p>
                  )}
                  {previewContent.recommendation_details.suggested_topic && (
                    <p><span className="font-medium">Topic Angle:</span> {previewContent.recommendation_details.suggested_topic}</p>
                  )}
                  {previewContent.recommendation_details.notes && (
                    <p><span className="font-medium">Notes:</span> {previewContent.recommendation_details.notes}</p>
                  )}
                </div>
              </div>
            )}

            {/* Language Tabs */}
            <div className="mb-4 flex gap-2">
              {(['en', 'fr', 'nl'] as const).map((lang) => (
                <button
                  key={lang}
                  onClick={() => setPreviewLang(lang)}
                  className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                    previewLang === lang
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {lang === 'en' ? '🇬🇧 English' : lang === 'fr' ? '🇫🇷 Français' : '🇳🇱 Nederlands'}
                </button>
              ))}
            </div>

            {/* Article Content */}
            <div className="rounded-lg bg-white border border-gray-200 p-4">
              {/* Translated Keyword */}
              <div className="mb-3 text-sm text-gray-600">
                <span className="font-medium">Target Keyword ({previewLang.toUpperCase()}):</span>{' '}
                {previewLang === 'en' ? previewContent.keyword_en : previewLang === 'fr' ? previewContent.keyword_fr : previewContent.keyword_nl}
                {' '}
                {!previewContent[`keyword_${previewLang}` as keyof Content] && (
                  <span className="text-gray-400">({previewContent.keyword})</span>
                )}
              </div>

              <h3 className="text-xl font-bold text-gray-900 mb-2">
                {getTitle(previewContent, previewLang) || 'No title'}
              </h3>

              {/* Meta Description */}
              <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded text-sm">
                <span className="font-medium text-amber-800">Meta Description:</span>{' '}
                <span className="text-amber-700">
                  {previewLang === 'en' ? previewContent.meta_description_en : previewLang === 'fr' ? previewContent.meta_description_fr : previewContent.meta_description_nl}
                </span>
              </div>

              {/* Article Body */}
              <div className="prose prose-sm prose-gray max-w-none max-h-96 overflow-y-auto text-gray-800">
                <div className="whitespace-pre-wrap">
                  {getContent(previewContent, previewLang) || 'No content available.'}
                </div>
              </div>

              {/* Copy Hint */}
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded text-sm text-green-800">
                💡 Copy this article content to paste into your blog CMS
              </div>
            </div>
          </div>
        )}
      </Modal>
    </>
  );
}
