import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { sessionsApi } from '../lib/api/client';
import { ArrowLeft } from 'lucide-react';

export default function SessionReport() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState<any | null>(null);
  const [report, setReport] = useState<any>({ Present: [], Absent: [] });
  const [roleSummary, setRoleSummary] = useState<Record<string, { Present: number; Absent: number }>>({});

  useEffect(() => {
    if (!id) return;
    loadReport();
  }, [id]);

  const loadReport = async () => {
    setLoading(true);
    try {
      const res = await sessionsApi.getReport(id!);
      setSession(res.session);
      setReport(res.report || { Present: [], Absent: [] });
      setRoleSummary(res.role_summary || {});
    } catch (err) {
      console.error('Failed to load session report:', err);
      alert('Failed to load session report');
    } finally {
      setLoading(false);
    }
  };

  const exportCsv = () => {
    const lines: string[] = [];
    lines.push('Status,Name,Role');
    report.Present.forEach((p: any) => lines.push(`Present,${p.name},${p.role}`));
    report.Absent.forEach((a: any) => lines.push(`Absent,${a.name},${a.role}`));
    const csv = lines.join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `session-${id}-report.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) return <div className="p-6">Loading...</div>;

  if (!session) return <div className="p-6">Session not found</div>;

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Session Report</h1>
          <p className="text-sm text-gray-600">{new Date(session.date).toLocaleDateString()}</p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => navigate(-1)} className="btn-secondary flex items-center">
            <ArrowLeft size={16} className="mr-2" /> Back
          </button>
          <button onClick={exportCsv} className="btn-primary">Export CSV</button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <h2 className="text-lg font-semibold">Role Summary</h2>
        <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.keys(roleSummary).length === 0 ? (
            <div className="text-sm text-gray-500">No role summary available</div>
          ) : (
            Object.entries(roleSummary).map(([role, counts]) => (
              <div key={role} className="p-3 border rounded">
                <div className="font-medium">{role}</div>
                <div className="text-sm text-gray-600">Present: {counts.Present}</div>
                <div className="text-sm text-gray-600">Absent: {counts.Absent}</div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <h2 className="text-lg font-semibold">Present ({report.Present.length})</h2>
          <div className="mt-2 space-y-1">
            {report.Present.map((p: any) => (
              <div key={p.name} className="text-sm">
                <Link to={`/members/${p.id}`} className="text-primary-600 hover:underline">{p.name}</Link>
                <span className="text-xs text-gray-500 ml-2">{p.role}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <h2 className="text-lg font-semibold">Absent ({report.Absent.length})</h2>
          <div className="mt-2 space-y-1">
            {report.Absent.map((a: any) => (
              <div key={a.name} className="text-sm">
                <Link to={`/members/${a.id}`} className="text-primary-600 hover:underline">{a.name}</Link>
                <span className="text-xs text-gray-500 ml-2">{a.role}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
