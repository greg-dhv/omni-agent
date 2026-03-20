"""Prompts for Google Ads analysis with Claude."""


def get_system_prompt(client_context: dict = None) -> str:
    """Generate a dynamic system prompt based on client context.

    Args:
        client_context: Dict with business context from client record.
            Expected keys: industry, country, description, target_audience,
            key_products, kpis, notes, ad_copy_restrictions

    Returns:
        Customized system prompt for Claude.
    """
    if not client_context:
        # Default fallback
        return DEFAULT_SYSTEM_PROMPT

    industry = client_context.get("industry", "general business")
    country = client_context.get("country", "")
    description = client_context.get("description", "")
    target_audience = client_context.get("target_audience", "")
    key_products = client_context.get("key_products", [])
    kpis = client_context.get("kpis", ["conversions", "cost_per_conversion"])
    notes = client_context.get("notes", "")
    ad_copy_restrictions = client_context.get("ad_copy_restrictions", [])

    products_str = ", ".join(key_products) if key_products else "various products/services"
    kpis_str = ", ".join(kpis) if kpis else "Conversions, Cost per Conversion"
    location_str = f" in {country}" if country else ""

    # Build ad copy restrictions section
    restrictions_section = ""
    if ad_copy_restrictions:
        restrictions_str = "\n  ".join(f"- {r}" for r in ad_copy_restrictions)
        restrictions_section = f"""

Ad Copy Restrictions (IMPORTANT for ad improvement suggestions):
  {restrictions_str}"""
    elif industry.lower() in ["casino", "gambling", "online gaming", "betting", "igaming"]:
        # Default restrictions for gambling industry
        restrictions_section = """

Ad Copy Restrictions (IMPORTANT for ad improvement suggestions):
  - No guaranteed wins or sure bets
  - No specific bonus amounts (e.g., "€100 bonus")
  - No misleading claims about odds or returns
  - Must include responsible gambling messaging consideration
  - Avoid superlatives like "best" or "biggest" without substantiation"""

    prompt = f"""You are an expert Google Ads analyst specializing in {industry}{location_str}.
You analyze campaign performance data and provide actionable recommendations to improve ROAS.

Key context:
- Business: {description or f'{industry} client'}
- Target audience: {target_audience or 'Not specified'}
- Key products/services: {products_str}
- Primary KPIs: {kpis_str}
{f'- Notes: {notes}' if notes else ''}{restrictions_section}
- All recommendations will be reviewed by a human before execution

Your analysis should be thorough but focused on high-impact opportunities."""

    return prompt


DEFAULT_SYSTEM_PROMPT = """You are an expert Google Ads analyst.
You analyze campaign performance data and provide actionable recommendations to improve ROAS.

Key context:
- Primary KPIs: Conversions, Cost per Conversion
- All recommendations will be reviewed by a human before execution

Your analysis should be thorough but focused on high-impact opportunities."""

# Keep for backwards compatibility
SYSTEM_PROMPT = DEFAULT_SYSTEM_PROMPT


ANALYSIS_PROMPT = """Analyze the following Google Ads performance data from the last {days} days and provide recommendations.

## Campaign Performance
{campaign_data}

## Keyword Performance (Top 50 by spend)
{keyword_data}

## Search Terms (Top 50 by spend)
{search_term_data}

## Ad Performance (with Ad Strength)
{ad_data}

## Converting Search Terms (potential new keywords)
{converting_search_terms}

---

Based on this data, identify:

1. **High Cost, Low/Zero Conversion Keywords**
   - Keywords spending more than €{high_cost_threshold} with 0 conversions
   - Should these be paused?

2. **Negative Keyword Opportunities**
   - Search terms that are irrelevant or have poor conversion rates
   - Include the exact search term text

3. **Low CTR Ads**
   - Ads with CTR below {low_ctr_threshold}% that should be reviewed
   - Suggest what might be improved

4. **Ad Strength Improvements**
   - Ads with POOR or AVERAGE ad strength that need improvement
   - For each weak ad, suggest 2-3 NEW headline variations and 1-2 NEW description variations
   - Headlines must be ≤30 characters, descriptions ≤90 characters
   - Be specific: don't repeat existing headlines, create fresh alternatives
   - Consider the business context and target audience
   - Note: For regulated industries, avoid prohibited claims (e.g., guaranteed wins, specific bonuses)

5. **New Keyword Opportunities**
   - Converting search terms with status "NONE" (not yet added as keywords)
   - Prioritize by: conversion volume, CPA efficiency, relevance to business
   - Suggest match type (exact/phrase) based on the search term pattern
   - Only recommend terms that show clear conversion intent

6. **Budget Pacing Issues**
   - Campaigns over or under spending vs expected

7. **General Anomalies**
   - Unusual patterns or sudden changes worth flagging

For each recommendation, provide:
- A clear, specific action
- The rationale with supporting numbers
- Priority level (high/medium/low)
- The exact IDs needed to execute

Format your response as JSON with this structure:
```json
{{
  "summary": "Brief overview of account health and key findings",
  "recommendations": [
    {{
      "type": "pause_keyword" | "add_negative" | "pause_ad" | "improve_ad" | "add_keyword" | "adjust_budget" | "flag_anomaly",
      "priority": "high" | "medium" | "low",
      "title": "Short action title",
      "summary": "Why this recommendation",
      "details": {{
        "campaign_id": "...",
        "campaign_name": "...",
        "ad_group_id": "...",
        "ad_group_name": "...",
        "keyword_id": "...",
        "keyword_text": "...",
        "search_term": "...",
        "ad_id": "...",
        "ad_strength": "POOR",
        "current_headlines": ["...", "..."],
        "current_descriptions": ["...", "..."],
        "suggested_headlines": ["New headline 1", "New headline 2"],
        "suggested_descriptions": ["New description text here"],
        "suggested_match_type": "EXACT" | "PHRASE",
        "cost": 123.45,
        "conversions": 0,
        "clicks": 50,
        "ctr": 1.5,
        "cpa": 25.50,
        "suggested_action": "pause" | "add_negative_exact" | "add_negative_phrase" | "add_keyword" | "update_ad"
      }}
    }}
  ]
}}
```

Only include fields in "details" that are relevant to the specific recommendation type.
Limit to the top 25 most impactful recommendations."""


def format_campaign_data(campaigns: list[dict]) -> str:
    """Format campaign data for the prompt."""
    if not campaigns:
        return "No campaign data available."

    lines = ["| Campaign | Cost | Clicks | Conv | CTR | CPC | CPA |"]
    lines.append("|----------|------|--------|------|-----|-----|-----|")

    for c in campaigns[:20]:  # Top 20 campaigns
        cpa = f"€{c['cost_per_conversion']:.2f}" if c.get('cost_per_conversion') else "N/A"
        lines.append(
            f"| {c['campaign_name'][:30]} | €{c['cost']:.2f} | {c['clicks']} | "
            f"{c['conversions']:.1f} | {c['ctr']:.2f}% | €{c['avg_cpc']:.2f} | {cpa} |"
        )

    return "\n".join(lines)


def format_keyword_data(keywords: list[dict]) -> str:
    """Format keyword data for the prompt."""
    if not keywords:
        return "No keyword data available."

    lines = ["| Keyword | Match | Cost | Clicks | Conv | CTR | CPA |"]
    lines.append("|---------|-------|------|--------|------|-----|-----|")

    for k in keywords[:50]:  # Top 50 keywords
        cpa = f"€{k['cost_per_conversion']:.2f}" if k.get('cost_per_conversion') else "N/A"
        lines.append(
            f"| {k['keyword_text'][:25]} | {k['match_type'][:5]} | €{k['cost']:.2f} | "
            f"{k['clicks']} | {k['conversions']:.1f} | {k['ctr']:.2f}% | {cpa} |"
        )
        # Include IDs as hidden comment for Claude to reference
        lines.append(f"<!-- campaign_id:{k['campaign_id']} ad_group_id:{k['ad_group_id']} keyword_id:{k['keyword_id']} -->")

    return "\n".join(lines)


def format_search_term_data(search_terms: list[dict]) -> str:
    """Format search term data for the prompt."""
    if not search_terms:
        return "No search term data available."

    lines = ["| Search Term | Campaign | Cost | Clicks | Conv |"]
    lines.append("|-------------|----------|------|--------|------|")

    for st in search_terms[:50]:  # Top 50 search terms
        lines.append(
            f"| {st['search_term'][:35]} | {st['campaign_name'][:20]} | "
            f"€{st['cost']:.2f} | {st['clicks']} | {st['conversions']:.1f} |"
        )
        lines.append(f"<!-- campaign_id:{st['campaign_id']} ad_group_id:{st['ad_group_id']} -->")

    return "\n".join(lines)


def format_ad_data(ads: list[dict]) -> str:
    """Format ad data for the prompt with ad strength."""
    if not ads:
        return "No ad data available."

    lines = ["| Ad Group | Ad Strength | Headlines | CTR | Clicks | Conv |"]
    lines.append("|----------|-------------|-----------|-----|--------|------|")

    for a in ads[:30]:  # Top 30 ads
        headlines = a.get('headlines', [])
        descriptions = a.get('descriptions', [])
        headlines_preview = " | ".join(headlines[:2])[:35]
        ad_strength = a.get('ad_strength', 'UNKNOWN')

        lines.append(
            f"| {a['ad_group_name'][:18]} | {ad_strength[:8]} | {headlines_preview} | "
            f"{a['ctr']:.2f}% | {a['clicks']} | {a['conversions']:.1f} |"
        )
        # Include full ad details for Claude to suggest improvements
        lines.append(f"<!-- campaign_id:{a['campaign_id']} ad_group_id:{a['ad_group_id']} ad_id:{a['ad_id']} -->")
        lines.append(f"<!-- headlines:{headlines} -->")
        lines.append(f"<!-- descriptions:{descriptions} -->")

    return "\n".join(lines)


def format_converting_search_terms(search_terms: list[dict]) -> str:
    """Format converting search terms for keyword discovery."""
    if not search_terms:
        return "No converting search terms available."

    # Filter to only show terms not yet added as keywords
    not_added = [st for st in search_terms if st.get('status') == 'NONE']

    if not not_added:
        return "All converting search terms are already added as keywords."

    lines = ["| Search Term | Campaign | Conv | CPA | Status |"]
    lines.append("|-------------|----------|------|-----|--------|")

    for st in not_added[:30]:  # Top 30 not-added terms
        cpa = f"€{st['cpa']:.2f}" if st.get('cpa') else "N/A"
        lines.append(
            f"| {st['search_term'][:35]} | {st['campaign_name'][:18]} | "
            f"{st['conversions']:.1f} | {cpa} | {st['status']} |"
        )
        lines.append(f"<!-- campaign_id:{st['campaign_id']} ad_group_id:{st['ad_group_id']} -->")

    return "\n".join(lines)
