import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui';
import { ReportsClient } from './ReportsClient';
import { FileText, Calendar, Send } from 'lucide-react';

export default function ReportsPage() {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Monthly Reports</h1>
        <p className="mt-1 text-sm text-gray-500">
          Generate and send performance reports to your clients
        </p>
      </div>

      {/* Stats */}
      <div className="mb-8 grid gap-4 sm:grid-cols-3">
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-blue-50 p-2">
              <FileText className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Report Type</p>
              <p className="text-lg font-semibold text-gray-900">Google Ads</p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-purple-50 p-2">
              <Calendar className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Period</p>
              <p className="text-lg font-semibold text-gray-900">Monthly</p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-green-50 p-2">
              <Send className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Delivery</p>
              <p className="text-lg font-semibold text-gray-900">Email</p>
            </div>
          </div>
        </Card>
      </div>

      <ReportsClient />
    </div>
  );
}
