"""Email template for monthly reports."""

from typing import Any


def format_currency(value: float) -> str:
    """Format a number as currency."""
    return f"€{value:,.2f}"


def format_number(value: float) -> str:
    """Format a number with thousands separators."""
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.1f}K"
    else:
        return f"{value:,.0f}"


def format_percent(value: float) -> str:
    """Format a number as percentage."""
    return f"{value:.2f}%"


def get_device_icon(device: str) -> str:
    """Get emoji for device type."""
    icons = {
        "MOBILE": "📱",
        "DESKTOP": "💻",
        "TABLET": "📱",
        "CONNECTED_TV": "📺",
        "OTHER": "🔧",
    }
    return icons.get(device, "📊")


def get_gender_icon(gender: str) -> str:
    """Get emoji for gender."""
    icons = {
        "MALE": "👨",
        "FEMALE": "👩",
        "UNDETERMINED": "👤",
    }
    return icons.get(gender, "👤")


def format_age_range(age: str) -> str:
    """Format age range for display."""
    age_labels = {
        "AGE_RANGE_18_24": "18-24",
        "AGE_RANGE_25_34": "25-34",
        "AGE_RANGE_35_44": "35-44",
        "AGE_RANGE_45_54": "45-54",
        "AGE_RANGE_55_64": "55-64",
        "AGE_RANGE_65_UP": "65+",
        "AGE_RANGE_UNDETERMINED": "Unknown",
    }
    return age_labels.get(age, age.replace("AGE_RANGE_", "").replace("_", "-"))


def create_monthly_report_email(report: dict[str, Any], client_name: str) -> str:
    """Create beautiful HTML email for monthly report.

    Args:
        report: Report data from ReportGenerator.
        client_name: Name of the client.

    Returns:
        HTML email content.
    """
    overview = report.get("overview", {})
    period = report.get("period", {})
    devices = report.get("devices", [])
    audience = report.get("audience", {})
    campaigns = report.get("campaigns", [])

    # Build device rows
    device_rows = ""
    total_device_cost = sum(d.get("cost", 0) for d in devices)
    for device in devices:
        cost = device.get("cost", 0)
        share = (cost / total_device_cost * 100) if total_device_cost > 0 else 0
        device_rows += f"""
        <tr>
            <td style="padding: 12px 16px; border-bottom: 1px solid #e2e8f0;">
                {get_device_icon(device.get('device', ''))} {device.get('device', 'Unknown').title()}
            </td>
            <td style="padding: 12px 16px; border-bottom: 1px solid #e2e8f0; text-align: right;">
                {format_currency(cost)}
            </td>
            <td style="padding: 12px 16px; border-bottom: 1px solid #e2e8f0; text-align: right;">
                {format_number(device.get('clicks', 0))}
            </td>
            <td style="padding: 12px 16px; border-bottom: 1px solid #e2e8f0; text-align: right;">
                {device.get('conversions', 0):.0f}
            </td>
            <td style="padding: 12px 16px; border-bottom: 1px solid #e2e8f0; text-align: right;">
                {share:.1f}%
            </td>
        </tr>
        """

    # Build age rows
    age_rows = ""
    ages = audience.get("age", [])
    if ages:
        total_age_cost = sum(a.get("cost", 0) for a in ages)
        for age in ages[:6]:  # Top 6 age groups
            cost = age.get("cost", 0)
            share = (cost / total_age_cost * 100) if total_age_cost > 0 else 0
            age_rows += f"""
            <tr>
                <td style="padding: 10px 16px; border-bottom: 1px solid #e2e8f0;">
                    {format_age_range(age.get('age_range', ''))}
                </td>
                <td style="padding: 10px 16px; border-bottom: 1px solid #e2e8f0; text-align: right;">
                    {format_currency(cost)}
                </td>
                <td style="padding: 10px 16px; border-bottom: 1px solid #e2e8f0; text-align: right;">
                    {age.get('conversions', 0):.0f}
                </td>
                <td style="padding: 10px 16px; border-bottom: 1px solid #e2e8f0; text-align: right;">
                    {share:.1f}%
                </td>
            </tr>
            """

    # Build gender rows
    gender_rows = ""
    genders = audience.get("gender", [])
    if genders:
        total_gender_cost = sum(g.get("cost", 0) for g in genders)
        for gender in genders:
            cost = gender.get("cost", 0)
            share = (cost / total_gender_cost * 100) if total_gender_cost > 0 else 0
            gender_rows += f"""
            <tr>
                <td style="padding: 10px 16px; border-bottom: 1px solid #e2e8f0;">
                    {get_gender_icon(gender.get('gender', ''))} {gender.get('gender', 'Unknown').title()}
                </td>
                <td style="padding: 10px 16px; border-bottom: 1px solid #e2e8f0; text-align: right;">
                    {format_currency(cost)}
                </td>
                <td style="padding: 10px 16px; border-bottom: 1px solid #e2e8f0; text-align: right;">
                    {gender.get('conversions', 0):.0f}
                </td>
                <td style="padding: 10px 16px; border-bottom: 1px solid #e2e8f0; text-align: right;">
                    {share:.1f}%
                </td>
            </tr>
            """

    # Build location rows
    location_rows = ""
    locations = audience.get("location", [])
    if locations:
        for loc in locations[:5]:
            location_rows += f"""
            <tr>
                <td style="padding: 10px 16px; border-bottom: 1px solid #e2e8f0;">
                    🌍 {loc.get('country', 'Unknown')}
                </td>
                <td style="padding: 10px 16px; border-bottom: 1px solid #e2e8f0; text-align: right;">
                    {format_currency(loc.get('cost', 0))}
                </td>
                <td style="padding: 10px 16px; border-bottom: 1px solid #e2e8f0; text-align: right;">
                    {loc.get('conversions', 0):.0f}
                </td>
            </tr>
            """

    # Build campaign rows
    campaign_rows = ""
    for campaign in campaigns[:5]:
        campaign_rows += f"""
        <tr>
            <td style="padding: 10px 16px; border-bottom: 1px solid #e2e8f0; max-width: 200px; overflow: hidden; text-overflow: ellipsis;">
                {campaign.get('campaign_name', 'Unknown')[:35]}
            </td>
            <td style="padding: 10px 16px; border-bottom: 1px solid #e2e8f0; text-align: right;">
                {format_currency(campaign.get('cost', 0))}
            </td>
            <td style="padding: 10px 16px; border-bottom: 1px solid #e2e8f0; text-align: right;">
                {campaign.get('conversions', 0):.0f}
            </td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f8fafc; color: #1e293b;">
        <div style="max-width: 700px; margin: 0 auto; padding: 20px;">

            <!-- Header -->
            <div style="background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); border-radius: 16px; padding: 40px 30px; text-align: center; margin-bottom: 24px;">
                <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 700;">
                    📊 Monthly Performance Report
                </h1>
                <p style="color: rgba(255,255,255,0.9); margin: 12px 0 0; font-size: 16px;">
                    {period.get('display', 'Last Month')}
                </p>
            </div>

            <!-- Greeting -->
            <div style="background: white; border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <p style="margin: 0; color: #475569; font-size: 16px; line-height: 1.6;">
                    Hi {client_name},
                </p>
                <p style="margin: 12px 0 0; color: #475569; font-size: 16px; line-height: 1.6;">
                    Here's your Google Ads performance summary for the past month. Below you'll find key metrics, device breakdown, and audience insights.
                </p>
            </div>

            <!-- Overview Metrics -->
            <div style="background: white; border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <h2 style="margin: 0 0 20px; font-size: 18px; color: #1e293b; font-weight: 600;">
                    📈 Overview
                </h2>
                <div style="display: table; width: 100%;">
                    <div style="display: table-row;">
                        <!-- Cost -->
                        <div style="display: table-cell; padding: 16px; text-align: center; border-right: 1px solid #e2e8f0;">
                            <div style="font-size: 28px; font-weight: 700; color: #ef4444;">
                                {format_currency(overview.get('cost', 0))}
                            </div>
                            <div style="font-size: 13px; color: #64748b; margin-top: 4px;">Total Spend</div>
                        </div>
                        <!-- Impressions -->
                        <div style="display: table-cell; padding: 16px; text-align: center; border-right: 1px solid #e2e8f0;">
                            <div style="font-size: 28px; font-weight: 700; color: #3b82f6;">
                                {format_number(overview.get('impressions', 0))}
                            </div>
                            <div style="font-size: 13px; color: #64748b; margin-top: 4px;">Impressions</div>
                        </div>
                        <!-- Clicks -->
                        <div style="display: table-cell; padding: 16px; text-align: center;">
                            <div style="font-size: 28px; font-weight: 700; color: #8b5cf6;">
                                {format_number(overview.get('clicks', 0))}
                            </div>
                            <div style="font-size: 13px; color: #64748b; margin-top: 4px;">Clicks</div>
                        </div>
                    </div>
                </div>
                <div style="display: table; width: 100%; margin-top: 16px; border-top: 1px solid #e2e8f0; padding-top: 16px;">
                    <div style="display: table-row;">
                        <!-- Conversions -->
                        <div style="display: table-cell; padding: 16px; text-align: center; border-right: 1px solid #e2e8f0;">
                            <div style="font-size: 28px; font-weight: 700; color: #22c55e;">
                                {overview.get('conversions', 0):.0f}
                            </div>
                            <div style="font-size: 13px; color: #64748b; margin-top: 4px;">Conversions</div>
                        </div>
                        <!-- Conversion Value -->
                        <div style="display: table-cell; padding: 16px; text-align: center; border-right: 1px solid #e2e8f0;">
                            <div style="font-size: 28px; font-weight: 700; color: #22c55e;">
                                {format_currency(overview.get('conversion_value', 0))}
                            </div>
                            <div style="font-size: 13px; color: #64748b; margin-top: 4px;">Conv. Value</div>
                        </div>
                        <!-- ROAS -->
                        <div style="display: table-cell; padding: 16px; text-align: center;">
                            <div style="font-size: 28px; font-weight: 700; color: #f59e0b;">
                                {overview.get('roas', 0):.2f}x
                            </div>
                            <div style="font-size: 13px; color: #64748b; margin-top: 4px;">ROAS</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Device Performance -->
            <div style="background: white; border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <h2 style="margin: 0 0 20px; font-size: 18px; color: #1e293b; font-weight: 600;">
                    📱 Device Performance
                </h2>
                <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                    <thead>
                        <tr style="background: #f8fafc;">
                            <th style="padding: 12px 16px; text-align: left; font-weight: 600; color: #64748b; border-bottom: 2px solid #e2e8f0;">Device</th>
                            <th style="padding: 12px 16px; text-align: right; font-weight: 600; color: #64748b; border-bottom: 2px solid #e2e8f0;">Spend</th>
                            <th style="padding: 12px 16px; text-align: right; font-weight: 600; color: #64748b; border-bottom: 2px solid #e2e8f0;">Clicks</th>
                            <th style="padding: 12px 16px; text-align: right; font-weight: 600; color: #64748b; border-bottom: 2px solid #e2e8f0;">Conv.</th>
                            <th style="padding: 12px 16px; text-align: right; font-weight: 600; color: #64748b; border-bottom: 2px solid #e2e8f0;">Share</th>
                        </tr>
                    </thead>
                    <tbody style="color: #334155;">
                        {device_rows}
                    </tbody>
                </table>
            </div>

            <!-- Audience Section -->
            <div style="background: white; border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <h2 style="margin: 0 0 20px; font-size: 18px; color: #1e293b; font-weight: 600;">
                    👥 Audience Insights
                </h2>

                <!-- Age Distribution -->
                {f'''
                <h3 style="margin: 0 0 12px; font-size: 15px; color: #475569; font-weight: 600;">Age Distribution</h3>
                <table style="width: 100%; border-collapse: collapse; font-size: 14px; margin-bottom: 24px;">
                    <thead>
                        <tr style="background: #f8fafc;">
                            <th style="padding: 10px 16px; text-align: left; font-weight: 600; color: #64748b; border-bottom: 2px solid #e2e8f0;">Age</th>
                            <th style="padding: 10px 16px; text-align: right; font-weight: 600; color: #64748b; border-bottom: 2px solid #e2e8f0;">Spend</th>
                            <th style="padding: 10px 16px; text-align: right; font-weight: 600; color: #64748b; border-bottom: 2px solid #e2e8f0;">Conv.</th>
                            <th style="padding: 10px 16px; text-align: right; font-weight: 600; color: #64748b; border-bottom: 2px solid #e2e8f0;">Share</th>
                        </tr>
                    </thead>
                    <tbody style="color: #334155;">
                        {age_rows}
                    </tbody>
                </table>
                ''' if age_rows else '<p style="color: #94a3b8; font-size: 14px;">Age data not available</p>'}

                <!-- Gender Distribution -->
                {f'''
                <h3 style="margin: 0 0 12px; font-size: 15px; color: #475569; font-weight: 600;">Gender Distribution</h3>
                <table style="width: 100%; border-collapse: collapse; font-size: 14px; margin-bottom: 24px;">
                    <thead>
                        <tr style="background: #f8fafc;">
                            <th style="padding: 10px 16px; text-align: left; font-weight: 600; color: #64748b; border-bottom: 2px solid #e2e8f0;">Gender</th>
                            <th style="padding: 10px 16px; text-align: right; font-weight: 600; color: #64748b; border-bottom: 2px solid #e2e8f0;">Spend</th>
                            <th style="padding: 10px 16px; text-align: right; font-weight: 600; color: #64748b; border-bottom: 2px solid #e2e8f0;">Conv.</th>
                            <th style="padding: 10px 16px; text-align: right; font-weight: 600; color: #64748b; border-bottom: 2px solid #e2e8f0;">Share</th>
                        </tr>
                    </thead>
                    <tbody style="color: #334155;">
                        {gender_rows}
                    </tbody>
                </table>
                ''' if gender_rows else ''}

                <!-- Location Distribution -->
                {f'''
                <h3 style="margin: 0 0 12px; font-size: 15px; color: #475569; font-weight: 600;">Top Locations</h3>
                <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                    <thead>
                        <tr style="background: #f8fafc;">
                            <th style="padding: 10px 16px; text-align: left; font-weight: 600; color: #64748b; border-bottom: 2px solid #e2e8f0;">Location</th>
                            <th style="padding: 10px 16px; text-align: right; font-weight: 600; color: #64748b; border-bottom: 2px solid #e2e8f0;">Spend</th>
                            <th style="padding: 10px 16px; text-align: right; font-weight: 600; color: #64748b; border-bottom: 2px solid #e2e8f0;">Conv.</th>
                        </tr>
                    </thead>
                    <tbody style="color: #334155;">
                        {location_rows}
                    </tbody>
                </table>
                ''' if location_rows else ''}
            </div>

            <!-- Top Campaigns -->
            <div style="background: white; border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <h2 style="margin: 0 0 20px; font-size: 18px; color: #1e293b; font-weight: 600;">
                    🎯 Top Campaigns
                </h2>
                <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                    <thead>
                        <tr style="background: #f8fafc;">
                            <th style="padding: 10px 16px; text-align: left; font-weight: 600; color: #64748b; border-bottom: 2px solid #e2e8f0;">Campaign</th>
                            <th style="padding: 10px 16px; text-align: right; font-weight: 600; color: #64748b; border-bottom: 2px solid #e2e8f0;">Spend</th>
                            <th style="padding: 10px 16px; text-align: right; font-weight: 600; color: #64748b; border-bottom: 2px solid #e2e8f0;">Conv.</th>
                        </tr>
                    </thead>
                    <tbody style="color: #334155;">
                        {campaign_rows}
                    </tbody>
                </table>
            </div>

            <!-- Footer -->
            <div style="text-align: center; padding: 20px; color: #94a3b8; font-size: 13px;">
                <p style="margin: 0;">Generated by AI Ops • Your Marketing Intelligence Platform</p>
                <p style="margin: 8px 0 0;">Report period: {period.get('display', '')}</p>
            </div>

        </div>
    </body>
    </html>
    """
