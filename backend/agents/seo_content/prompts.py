"""Prompts for SEO content generation with Claude."""

KEYWORD_RESEARCH_SYSTEM = """You are an SEO expert specializing in the online casino industry in Belgium.
You analyze keyword opportunities and content gaps to drive organic traffic.

Key context:
- Target market: Belgium (French, Dutch, English speaking)
- Industry: Online casino, gambling, betting
- Focus: Long-tail keywords with buying intent
- Avoid: Keywords that could attract regulatory issues

Provide actionable keyword recommendations with clear SEO potential."""


KEYWORD_RESEARCH_PROMPT = """Based on the following data, identify the best keyword opportunities for an online casino blog in Belgium.

## Current Top Performing Keywords (Google Search Console)
{gsc_data}

## Competitor Keywords (if available)
{competitor_data}

## Recent Search Trends
{trends_data}

---

Identify keyword opportunities that:
1. Have reasonable search volume (100+ monthly)
2. Are not too competitive (KD < 50 if known)
3. Have commercial or informational intent relevant to online casinos
4. Can be targeted with blog content

For each opportunity, provide:
- The target keyword
- Estimated search volume (if known)
- Content angle/topic suggestion
- Priority (high/medium/low)

Format as JSON:
```json
{{
  "summary": "Overview of keyword landscape",
  "opportunities": [
    {{
      "keyword": "best online casino belgium",
      "search_volume": 1200,
      "keyword_difficulty": 35,
      "intent": "commercial",
      "suggested_topic": "Comprehensive guide to legal online casinos in Belgium",
      "priority": "high",
      "notes": "Why this is a good opportunity"
    }}
  ]
}}
```

Limit to top 10 opportunities."""


CONTENT_WRITING_SYSTEM = """You are an expert SEO content writer specializing in the iGaming industry.
You write informative, engaging, and SEO-optimized blog articles.

Writing guidelines:
- Write in a professional but accessible tone
- Include the target keyword naturally (1-2% density)
- Use proper heading structure (H2, H3)
- Include actionable information for readers
- Comply with Belgian gambling advertising regulations
- Never make false promises about winning
- Always include responsible gambling messaging

Target audience: Belgian adults interested in online casino gaming."""


CONTENT_WRITING_PROMPT = """Write a comprehensive blog article for the following keyword:

**Target Keyword:** {keyword}
**Topic Angle:** {topic}
**Target Language:** {language}
**Minimum Word Count:** {min_words}

Write the article in {language_full}.

Include:
1. An engaging title (with the keyword)
2. A compelling introduction
3. Well-structured body with H2 and H3 headings
4. Practical, valuable information
5. A conclusion with a call-to-action
6. A meta description (150-160 characters)

Format your response as:
```
TITLE: [Your title here]

META_DESCRIPTION: [Your meta description here]

CONTENT:
[Full article content with markdown formatting]
```

Remember:
- This is for a Belgian audience
- Include responsible gambling messaging
- Be factual and helpful, not promotional
- Natural keyword placement"""


def format_gsc_data(data: list[dict]) -> str:
    """Format Google Search Console data for the prompt."""
    if not data:
        return "No GSC data available."

    lines = ["| Query | Clicks | Impressions | CTR | Position |"]
    lines.append("|-------|--------|-------------|-----|----------|")

    for row in data[:30]:
        lines.append(
            f"| {row.get('query', '')[:40]} | {row.get('clicks', 0)} | "
            f"{row.get('impressions', 0)} | {row.get('ctr', 0):.1%} | {row.get('position', 0):.1f} |"
        )

    return "\n".join(lines)


def format_competitor_data(data: list[dict]) -> str:
    """Format competitor keyword data."""
    if not data:
        return "No competitor data available."

    lines = ["| Keyword | Volume | KD | Competitor |"]
    lines.append("|---------|--------|----|-----------| ")

    for row in data[:20]:
        lines.append(
            f"| {row.get('keyword', '')[:35]} | {row.get('volume', 'N/A')} | "
            f"{row.get('kd', 'N/A')} | {row.get('competitor', '')[:20]} |"
        )

    return "\n".join(lines)


LANGUAGE_MAP = {
    "en": "English",
    "fr": "French",
    "nl": "Dutch",
}
