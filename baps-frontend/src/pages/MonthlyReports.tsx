import { useEffect, useState } from 'react';
import { Calendar, Download, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
const BACKEND_BASE = API_BASE_URL.replace(/\/api$/, '');

interface MemberAttendance {
  present_dates: string[];
  absence_dates: string[];
  present_count: number;
  absence_count: number;
  role?: string;
}

interface Summary {
  [key: string]: {
    total_members: number;
    present: number;
    absent: number;
  };
}

export default function MonthlyReports() {
  const navigate = useNavigate();
  const [months, setMonths] = useState(1);
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadMonthlyReport();
  }, [months]);

  const loadMonthlyReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/reports/monthly?months=${months}`);
      if (response.data.status === 'success') {
        setData(response.data.data);
      } else {
        setError('Failed to load monthly report');
      }
    } catch (err: any) {
      console.error('Failed to load monthly report:', err);
      setError(err.response?.data?.message || 'Failed to load monthly report');
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = () => {
    window.open(`${BACKEND_BASE}/reports/monthly/pdf?months=${months}`, '_blank');
  };

  return (
    <div className="space-y-6 p-6">
      <button
        onClick={() => navigate('/reports')}
        className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
      >
        <ArrowLeft size={20} className="mr-2" />
        Back to Reports
      </button>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Monthly Reports</h1>
          <p className="text-sm text-gray-600 mt-2">Attendance summary for selected period</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2">
              <Calendar size={18} className="text-gray-600" />
              <span className="text-sm font-medium text-gray-700">Period:</span>
              <select
                value={months}
                onChange={(e) => setMonths(parseInt(e.target.value))}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value={1}>Last 1 Month</option>
                <option value={3}>Last 3 Months</option>
                <option value={6}>Last 6 Months</option>
                <option value={12}>Last 12 Months</option>
              </select>
            </label>
          </div>
          <button
            onClick={downloadPDF}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <Download size={18} />
            Download PDF
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {loading ? (
          <div className="text-center py-8 text-gray-500">Loading report...</div>
        ) : data ? (
          <div className="space-y-6">
            {/* Summary */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h2 className="text-lg font-semibold mb-3">Summary</h2>
              <p className="text-sm text-gray-600 mb-4">
                Period: <strong>{data.start_date}</strong> to <strong>{data.end_date}</strong> ({data.selected_months} month{data.selected_months > 1 ? 's' : ''}) - <strong>{data.total_sessions}</strong> sessions
              </p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(data.summary).map(([category, stats]: [string, any]) => (
                  <div key={category} className="bg-white p-3 rounded border border-gray-200">
                    <div className="text-sm font-medium text-gray-700">{category}</div>
                    <div className="text-xs text-gray-500 mt-1">Members: {stats.total_members}</div>
                    <div className="text-xs text-green-600 mt-1">Present: {stats.present}</div>
                    <div className="text-xs text-red-600">Absent: {stats.absent}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Leadership Report */}
            {Object.keys(data.leadership_absent).length > 0 && (
              <div>
                <h2 className="text-lg font-semibold mb-3">Leadership Attendance</h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left p-3 font-medium text-gray-700">Name</th>
                        <th className="text-left p-3 font-medium text-gray-700">Role</th>
                        <th className="text-left p-3 font-medium text-gray-700">Present</th>
                        <th className="text-left p-3 font-medium text-gray-700">Absent</th>
                        <th className="text-left p-3 font-medium text-gray-700">Absence Dates</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(data.leadership_absent).map(([name, member]: [string, any]) => (
                        <tr key={name} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="p-3">{name}</td>
                          <td className="p-3 text-xs text-gray-600">{member.role}</td>
                          <td className="p-3 text-green-600 font-medium">{member.present_count}</td>
                          <td className="p-3 text-red-600 font-medium">{member.absence_count}</td>
                          <td className="p-3 text-xs text-gray-600">
                            {member.absence_dates.length > 0 ? member.absence_dates.join(', ') : '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Yuvak Report */}
            {Object.keys(data.yuvak_absent).length > 0 && (
              <div>
                <h2 className="text-lg font-semibold mb-3">Yuvak Attendance</h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left p-3 font-medium text-gray-700">Name</th>
                        <th className="text-left p-3 font-medium text-gray-700">Present</th>
                        <th className="text-left p-3 font-medium text-gray-700">Absent</th>
                        <th className="text-left p-3 font-medium text-gray-700">Absence Dates</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(data.yuvak_absent).map(([name, member]: [string, any]) => (
                        <tr key={name} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="p-3">{name}</td>
                          <td className="p-3 text-green-600 font-medium">{member.present_count}</td>
                          <td className="p-3 text-red-600 font-medium">{member.absence_count}</td>
                          <td className="p-3 text-xs text-gray-600">
                            {member.absence_dates.length > 0 ? member.absence_dates.join(', ') : '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {Object.keys(data.leadership_absent).length === 0 && Object.keys(data.yuvak_absent).length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No attendance data available for the selected period.
              </div>
            )}
          </div>
        ) : null}
      </div>
    </div>
  );
}
