#!/usr/bin/env python3
"""Generate and optionally send monthly report.

Usage:
    python generate_report.py                    # Generate report JSON
    python generate_report.py --send             # Generate and send via email
    python generate_report.py --period last_30_days  # Specify period
"""

import argparse
import asyncio
import json
import os
import sys

from dotenv import load_dotenv

load_dotenv()

from agents.reporting import ReportGenerator, create_monthly_report_email
from core.email import send_email
from core.supabase import SupabaseRepository


async def main():
    parser = argparse.ArgumentParser(description="Generate monthly report")
    parser.add_argument(
        "--period",
        default="last_month",
        choices=["last_month", "this_month", "last_30_days"],
        help="Report period",
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="Send report via email",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON",
    )
    args = parser.parse_args()

    # Generate report
    generator = ReportGenerator()
    report = generator.generate_report(period=args.period)

    if args.json:
        # Output JSON for API consumption
        print(json.dumps(report, indent=2))
        return

    # Get client info
    repo = SupabaseRepository()
    client_settings = repo.get_setting("client_email") or {}
    client_email = client_settings.get("email")
    client_name = client_settings.get("name", "Client")

    # Generate HTML
    html = create_monthly_report_email(report, client_name)

    if args.send:
        if not client_email:
            print("Error: Client email not configured in settings", file=sys.stderr)
            sys.exit(1)

        email_settings = repo.get_setting("email_settings") or {}

        success = await send_email(
            to_email=client_email,
            to_name=client_name,
            subject=f"Monthly Performance Report - {report['period']['display']}",
            html_content=html,
            from_email=email_settings.get("from_email"),
            from_name=email_settings.get("from_name", "AI Ops"),
            provider=email_settings.get("provider", "sendgrid"),
        )

        if success:
            print(f"Report sent to {client_email}")
        else:
            print("Failed to send report", file=sys.stderr)
            sys.exit(1)
    else:
        # Print summary
        overview = report["overview"]
        print(f"\n{'=' * 60}")
        print(f"MONTHLY REPORT - {report['period']['display']}")
        print(f"{'=' * 60}")
        print(f"\nOverview:")
        print(f"  Cost:           €{overview['cost']:,.2f}")
        print(f"  Impressions:    {overview['impressions']:,}")
        print(f"  Clicks:         {overview['clicks']:,}")
        print(f"  Conversions:    {overview['conversions']:.0f}")
        print(f"  Conv. Value:    €{overview['conversion_value']:,.2f}")
        print(f"  ROAS:           {overview['roas']:.2f}x")

        print(f"\nDevices:")
        for device in report["devices"]:
            print(f"  {device['device']:12} €{device['cost']:>10,.2f}  {device['conversions']:>5.0f} conv")

        print(f"\nTop Campaigns:")
        for campaign in report["campaigns"][:5]:
            name = campaign['campaign_name'][:30]
            print(f"  {name:32} €{campaign['cost']:>10,.2f}  {campaign['conversions']:>5.0f} conv")

        print(f"\n{'=' * 60}")
        print(f"Use --send to email this report to: {client_email or 'Not configured'}")


if __name__ == "__main__":
    asyncio.run(main())
