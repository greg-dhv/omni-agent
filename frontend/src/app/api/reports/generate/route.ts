import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execAsync = promisify(exec);

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const period = searchParams.get('period') || 'last_month';

  // Validate period
  const validPeriods = ['last_month', 'this_month', 'last_30_days'];
  if (!validPeriods.includes(period)) {
    return NextResponse.json(
      { error: 'Invalid period. Use: last_month, this_month, or last_30_days' },
      { status: 400 }
    );
  }

  try {
    // Path to backend directory
    const backendDir = path.join(process.cwd(), '..', 'backend');

    // Generate report JSON
    const { stdout: reportJson } = await execAsync(
      `python3 generate_report.py --period ${period} --json`,
      { cwd: backendDir, timeout: 60000 }
    );

    const report = JSON.parse(reportJson);

    // Generate HTML separately (we need to call Python again for HTML)
    const { stdout: htmlOutput } = await execAsync(
      `python3 -c "
from agents.reporting import ReportGenerator, create_monthly_report_email
from core.supabase import SupabaseRepository
import json

repo = SupabaseRepository()
client_settings = repo.get_setting('client_email') or {}
client_name = client_settings.get('name', 'Client')

report = ${JSON.stringify(report).replace(/'/g, "\\'")}
html = create_monthly_report_email(report, client_name)
print(html)
"`,
      { cwd: backendDir, timeout: 30000, maxBuffer: 10 * 1024 * 1024 }
    );

    return NextResponse.json({
      report,
      html: htmlOutput,
    });
  } catch (error) {
    console.error('Report generation error:', error);
    const message = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json(
      { error: `Failed to generate report: ${message}` },
      { status: 500 }
    );
  }
}
