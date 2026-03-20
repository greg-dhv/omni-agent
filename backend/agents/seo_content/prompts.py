"""Prompts for SEO content generation with Claude."""

KEYWORD_RESEARCH_SYSTEM = """You are an SEO expert specializing in the online casino industry in Belgium.
You analyze keyword opportunities and content gaps to drive organic traffic.

Key context:
- Target market: Belgium (French, Dutch, English speaking)
- Industry: Online casino, gambling, betting
- Focus: Long-tail keywords with buying intent
- Avoid: Keywords that could attract regulatory issues

Provide actionable keyword recommendations with clear SEO potential."""


KEYWORD_RESEARCH_PROMPT = """Based on the following data, identify the best keyword opportunities for content creation.

## Google Search Console Data
{gsc_data}

## Competitor Keywords (if available)
{competitor_data}

## Additional Keywords to Consider
{trends_data}

---

Analyze the GSC data and identify the best opportunities. Focus on:

**Quick Wins (Position 4-10):** These keywords are close to top 3. Recommend content improvements or internal linking.

**Low Hanging Fruit (Position 11-20):** These are close to page 1. Recommend content expansion or new supporting articles.

**CTR Opportunities:** Good rankings but low CTR. Recommend title/meta description improvements.

**Striking Distance (Position 21-30):** Need dedicated content to reach page 1.

For each opportunity, provide:
- The target keyword (use exact keyword from GSC if available)
- Current position (from GSC data)
- Estimated search volume (estimate based on impressions)
- Recommended action (optimize existing content, create new content, improve meta)
- Content angle/topic suggestion
- Priority (high/medium/low)

Format as JSON:
```json
{{
  "summary": "Overview of opportunities found",
  "opportunities": [
    {{
      "keyword": "keyword from gsc",
      "current_position": 8.5,
      "search_volume": 500,
      "keyword_difficulty": 30,
      "intent": "informational",
      "opportunity_type": "quick_win",
      "action": "Optimize existing content, add more depth",
      "suggested_topic": "Expand the existing article with more details about X",
      "priority": "high",
      "notes": "Currently ranking #8, with optimization can reach top 3"
    }}
  ]
}}
```

Prioritize GSC data opportunities over seed keywords. Limit to top 15 opportunities."""


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


def format_gsc_data(data: dict) -> str:
    """Format Google Search Console opportunity data for the prompt."""
    if not data:
        return "No GSC data available."

    lines = []

    # Quick wins - position 4-10
    if data.get("quick_wins"):
        lines.append("### Quick Wins (Position 4-10, optimize for top 3)")
        lines.append("| Keyword | Position | Impressions | Clicks | CTR |")
        lines.append("|---------|----------|-------------|--------|-----|")
        for row in data["quick_wins"][:10]:
            lines.append(
                f"| {row.get('keyword', '')[:40]} | {row.get('position', 0)} | "
                f"{row.get('impressions', 0)} | {row.get('clicks', 0)} | {row.get('ctr', 0)}% |"
            )
        lines.append("")

    # Low hanging fruit - position 11-20
    if data.get("low_hanging_fruit"):
        lines.append("### Low Hanging Fruit (Position 11-20, push to page 1)")
        lines.append("| Keyword | Position | Impressions | Clicks | CTR |")
        lines.append("|---------|----------|-------------|--------|-----|")
        for row in data["low_hanging_fruit"][:10]:
            lines.append(
                f"| {row.get('keyword', '')[:40]} | {row.get('position', 0)} | "
                f"{row.get('impressions', 0)} | {row.get('clicks', 0)} | {row.get('ctr', 0)}% |"
            )
        lines.append("")

    # CTR opportunities
    if data.get("ctr_opportunities"):
        lines.append("### CTR Opportunities (Good position but low CTR - improve snippets)")
        lines.append("| Keyword | Position | Impressions | Clicks | CTR |")
        lines.append("|---------|----------|-------------|--------|-----|")
        for row in data["ctr_opportunities"][:10]:
            lines.append(
                f"| {row.get('keyword', '')[:40]} | {row.get('position', 0)} | "
                f"{row.get('impressions', 0)} | {row.get('clicks', 0)} | {row.get('ctr', 0)}% |"
            )
        lines.append("")

    # Striking distance - position 21-30
    if data.get("striking_distance"):
        lines.append("### Striking Distance (Position 21-30, needs dedicated content)")
        lines.append("| Keyword | Position | Impressions | Clicks | CTR |")
        lines.append("|---------|----------|-------------|--------|-----|")
        for row in data["striking_distance"][:10]:
            lines.append(
                f"| {row.get('keyword', '')[:40]} | {row.get('position', 0)} | "
                f"{row.get('impressions', 0)} | {row.get('clicks', 0)} | {row.get('ctr', 0)}% |"
            )

    if not lines:
        return "No keyword opportunities found in GSC data."

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
