import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execAsync = promisify(exec);

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const period = body.period || 'last_month';

    // Validate period
    const validPeriods = ['last_month', 'this_month', 'last_30_days'];
    if (!validPeriods.includes(period)) {
      return NextResponse.json(
        { error: 'Invalid period. Use: last_month, this_month, or last_30_days' },
        { status: 400 }
      );
    }

    // Path to backend directory
    const backendDir = path.join(process.cwd(), '..', 'backend');

    // Generate and send report
    const { stdout, stderr } = await execAsync(
      `python3 generate_report.py --period ${period} --send`,
      { cwd: backendDir, timeout: 120000 }
    );

    if (stderr && !stderr.includes('Warning')) {
      console.error('Report send stderr:', stderr);
    }

    return NextResponse.json({
      success: true,
      message: stdout.trim(),
    });
  } catch (error) {
    console.error('Report send error:', error);
    const message = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json(
      { error: `Failed to send report: ${message}` },
      { status: 500 }
    );
  }
}
