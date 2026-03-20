'use client';

import { useState } from 'react';
import { Content } from '@/lib/types';
import { Button, Modal } from '@/components/ui';
import { Eye } from 'lucide-react';

interface ContentViewerProps {
  content: Content;
}

export function ContentViewer({ content }: ContentViewerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [lang, setLang] = useState<'en' | 'fr' | 'nl'>('en');

  const getTitle = (l: 'en' | 'fr' | 'nl') => {
    switch (l) {
      case 'en':
        return content.title_en;
      case 'fr':
        return content.title_fr;
      case 'nl':
        return content.title_nl;
    }
  };

  const getBody = (l: 'en' | 'fr' | 'nl') => {
    switch (l) {
      case 'en':
        return content.content_en;
      case 'fr':
        return content.content_fr;
      case 'nl':
        return content.content_nl;
    }
  };

  const getMeta = (l: 'en' | 'fr' | 'nl') => {
    switch (l) {
      case 'en':
        return content.meta_description_en;
      case 'fr':
        return content.meta_description_fr;
      case 'nl':
        return content.meta_description_nl;
    }
  };

  return (
    <>
      <Button
        variant="outline"
        size="sm"
        className="mt-3 w-full"
        onClick={() => setIsOpen(true)}
      >
        <Eye className="mr-2 h-4 w-4" />
        View Article
      </Button>

      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title={content.keyword || 'Article'}
        size="xl"
      >
        <div>
          {/* Language Tabs */}
          <div className="mb-4 flex gap-2 border-b border-gray-200 pb-4">
            {(['en', 'fr', 'nl'] as const).map((l) => {
              const hasContent = l === 'en' ? content.content_en : l === 'fr' ? content.content_fr : content.content_nl;
              if (!hasContent) return null;
              return (
                <button
                  key={l}
                  onClick={() => setLang(l)}
                  className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                    lang === l
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {l === 'en' ? 'English' : l === 'fr' ? 'French' : 'Dutch'}
                </button>
              );
            })}
          </div>

          {/* Meta Description */}
          {getMeta(lang) && (
            <div className="mb-4 rounded-lg bg-gray-50 p-3">
              <p className="text-xs font-medium uppercase text-gray-500">
                Meta Description
              </p>
              <p className="mt-1 text-sm text-gray-700">{getMeta(lang)}</p>
            </div>
          )}

          {/* Article Content */}
          <div className="rounded-lg border border-gray-200 p-4">
            <h2 className="text-xl font-bold text-gray-900">
              {getTitle(lang) || 'Untitled'}
            </h2>
            <div className="prose prose-sm mt-4 max-h-[60vh] overflow-y-auto">
              <div
                dangerouslySetInnerHTML={{
                  __html: (getBody(lang) || '').replace(/\n/g, '<br />'),
                }}
              />
            </div>
          </div>
        </div>
      </Modal>
    </>
  );
}
