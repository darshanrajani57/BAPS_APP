import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Calendar, FileText } from 'lucide-react';
import { sessionsApi } from '../lib/api/client';

// Backend base (remove /api suffix from API_BASE_URL)
const BACKEND_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:5000').replace(/\/api$/, '');

export default function Reports() {
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    setLoading(true);
    try {
      const all = await sessionsApi.getAll();
      // show only ended sessions (reports available)
      const ended = all.filter(s => s.status === 'ENDED').sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
      setSessions(ended);
    } catch (err) {
      console.error('Failed to load sessions for reports:', err);
      alert('Failed to load sessions for reports');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-6">Loading...</div>;

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Reports</h1>
          <p className="text-sm text-gray-600">View session reports and exports</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold">Session Reports</h2>
          <div className="text-sm text-gray-500">Ended sessions only</div>
        </div>

        {sessions.length === 0 ? (
          <div className="text-sm text-gray-500">No ended sessions to report on</div>
        ) : (
          <div className="grid grid-cols-1 gap-2">
            {sessions.map(s => (
              <div key={s.id} className="flex items-center justify-between p-3 border rounded">
                <div>
                  <div className="font-medium">{new Date(s.date).toLocaleDateString()}</div>
                  <div className="text-sm text-gray-500">{s.start_time}{s.end_time ? ` - ${s.end_time}` : ''}</div>
                </div>
                <div className="flex items-center gap-2">
                  <Link to={`/sessions/${s.id}/report`} className="px-3 py-2 border rounded text-sm bg-gray-50 hover:bg-gray-100">View Report</Link>
                  <a href={`${BACKEND_BASE}/reports/session/${s.id}/pdf`} target="_blank" rel="noreferrer" className="px-3 py-2 border rounded text-sm bg-gray-50 hover:bg-gray-100">PDF</a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <h2 className="text-lg font-semibold">Monthly Reports</h2>
        <p className="text-sm text-gray-500 mt-2">Generate month-range attendance summaries</p>
        <div className="mt-3">
          <Link to="/reports/monthly" className="px-3 py-2 border rounded text-sm bg-gray-50 hover:bg-gray-100 inline-block">View Monthly Reports</Link>
        </div>
        {sessions.length === 0 && (
          <div className="mt-3 text-sm text-gray-500">No ended sessions available — monthly reports will be generated once sessions are ended.</div>
        )}
      </div>
    </div>
  );
}



