import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import { writeFile, unlink } from 'fs/promises';
import { randomUUID } from 'crypto';

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

  const backendDir = path.join(process.cwd(), '..', 'backend');
  const tempFile = path.join('/tmp', `report_${randomUUID()}.json`);

  try {
    // Generate report JSON
    const { stdout: reportJson } = await execAsync(
      `python3 generate_report.py --period ${period} --json`,
      { cwd: backendDir, timeout: 120000, maxBuffer: 10 * 1024 * 1024 }
    );

    const report = JSON.parse(reportJson);

    // Write report to temp file for Python to read
    await writeFile(tempFile, JSON.stringify(report));

    // Generate HTML using temp file
    const { stdout: htmlOutput } = await execAsync(
      `python3 -c "
import json
from agents.reporting import create_monthly_report_email
from core.supabase import SupabaseRepository

with open('${tempFile}', 'r') as f:
    report = json.load(f)

repo = SupabaseRepository()
client_settings = repo.get_setting('client_email') or {}
client_name = client_settings.get('name', 'Client')

html = create_monthly_report_email(report, client_name)
print(html)
"`,
      { cwd: backendDir, timeout: 30000, maxBuffer: 10 * 1024 * 1024 }
    );

    // Clean up temp file
    await unlink(tempFile).catch(() => {});

    return NextResponse.json({
      report,
      html: htmlOutput,
    });
  } catch (error) {
    // Clean up temp file on error
    await unlink(tempFile).catch(() => {});

    console.error('Report generation error:', error);
    const message = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json(
      { error: `Failed to generate report: ${message}` },
      { status: 500 }
    );
  }
}
