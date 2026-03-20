"""SEO Content Writer - generates blog articles in multiple languages."""

import logging
import os
import re
from datetime import datetime
from typing import Any

import anthropic
from dotenv import load_dotenv

from .prompts import CONTENT_WRITING_SYSTEM, CONTENT_WRITING_PROMPT, LANGUAGE_MAP
from core.models import Content, ContentStatus
from core.supabase import SupabaseRepository

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SEOContentWriter:
    """Writes SEO-optimized blog content using Claude."""

    def __init__(self):
        self.claude = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.repo = SupabaseRepository()

    def _parse_article_response(self, response_text: str) -> dict[str, str]:
        """Parse the structured article response from Claude.

        Args:
            response_text: Raw response text.

        Returns:
            Dict with title, meta_description, and content.
        """
        result = {"title": "", "meta_description": "", "content": ""}

        # Extract title
        title_match = re.search(r"TITLE:\s*(.+?)(?:\n|META_DESCRIPTION:)", response_text, re.DOTALL)
        if title_match:
            result["title"] = title_match.group(1).strip()

        # Extract meta description
        meta_match = re.search(r"META_DESCRIPTION:\s*(.+?)(?:\n\n|CONTENT:)", response_text, re.DOTALL)
        if meta_match:
            result["meta_description"] = meta_match.group(1).strip()

        # Extract content
        content_match = re.search(r"CONTENT:\s*(.+)", response_text, re.DOTALL)
        if content_match:
            result["content"] = content_match.group(1).strip()

        return result

    async def write_article(
        self,
        keyword: str,
        topic: str,
        language: str = "en",
        min_words: int = 1500,
    ) -> dict[str, str]:
        """Write an article for a specific keyword and language.

        Args:
            keyword: Target keyword.
            topic: Suggested topic/angle.
            language: Language code (en, fr, nl).
            min_words: Minimum word count.

        Returns:
            Dict with title, meta_description, and content.
        """
        language_full = LANGUAGE_MAP.get(language, "English")

        prompt = CONTENT_WRITING_PROMPT.format(
            keyword=keyword,
            topic=topic,
            language=language,
            language_full=language_full,
            min_words=min_words,
        )

        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,  # Longer for full articles
            system=CONTENT_WRITING_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )

        return self._parse_article_response(response.content[0].text)

    async def translate_keyword(self, keyword: str, target_language: str) -> str:
        """Translate a keyword to the target language.

        Args:
            keyword: Original keyword (usually in English or detected language).
            target_language: Target language code (en, fr, nl).

        Returns:
            Translated keyword suitable for SEO.
        """
        language_full = LANGUAGE_MAP.get(target_language, "English")

        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": f"""Translate this SEO keyword to {language_full}.

Keyword: "{keyword}"

Provide ONLY the translated keyword, nothing else. Keep it natural for search - how would someone in {language_full} search for this?
If the keyword is already in {language_full}, return it as-is."""
            }],
        )

        return response.content[0].text.strip().strip('"')

    async def write_multilingual_article(
        self,
        keyword: str,
        topic: str,
        languages: list[str] = None,
        min_words: int = 1500,
    ) -> Content:
        """Write an article in multiple languages.

        Args:
            keyword: Target keyword.
            topic: Suggested topic/angle.
            languages: List of language codes.
            min_words: Minimum word count per language.

        Returns:
            Content object with all language versions.
        """
        if languages is None:
            languages = ["en", "fr", "nl"]

        logger.info(f"Writing article for '{keyword}' in {len(languages)} languages...")

        content = Content(
            keyword=keyword,
            slug=keyword.lower().replace(" ", "-")[:50],
            status=ContentStatus.DRAFT,
        )

        # Translate keywords for each language
        translated_keywords = {}
        for lang in languages:
            logger.info(f"Translating keyword to {lang}...")
            translated_keywords[lang] = await self.translate_keyword(keyword, lang)
            logger.info(f"  {lang}: {translated_keywords[lang]}")

        for lang in languages:
            lang_keyword = translated_keywords[lang]
            logger.info(f"Writing {lang} version for keyword: {lang_keyword}...")
            article = await self.write_article(lang_keyword, topic, lang, min_words)

            if lang == "en":
                content.title_en = article["title"]
                content.content_en = article["content"]
                content.meta_description_en = article["meta_description"]
                content.keyword_en = lang_keyword
            elif lang == "fr":
                content.title_fr = article["title"]
                content.content_fr = article["content"]
                content.meta_description_fr = article["meta_description"]
                content.keyword_fr = lang_keyword
            elif lang == "nl":
                content.title_nl = article["title"]
                content.content_nl = article["content"]
                content.meta_description_nl = article["meta_description"]
                content.keyword_nl = lang_keyword

        return content

    async def generate_content_for_recommendation(
        self, recommendation: dict
    ) -> Content:
        """Generate content for an approved keyword recommendation.

        Args:
            recommendation: The approved keyword recommendation.

        Returns:
            Content object ready for database.
        """
        details = recommendation.get("details", {})
        keyword = details.get("keyword", recommendation.get("title", "").replace("Target keyword: ", ""))
        topic = details.get("suggested_topic", "Comprehensive guide")

        # Get language settings
        settings = self.repo.get_setting("seo_content") or {}
        languages = settings.get("languages", ["en", "fr", "nl"])
        min_words = settings.get("min_word_count", 1500)

        content = await self.write_multilingual_article(
            keyword=keyword,
            topic=topic,
            languages=languages,
            min_words=min_words,
        )

        content.recommendation_id = recommendation.get("id")
        # Store the original recommendation details for context in emails
        content.recommendation_details = details

        return content
