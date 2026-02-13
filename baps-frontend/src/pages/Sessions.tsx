import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Clock, Calendar, CheckCircle, XCircle, ArrowRight } from 'lucide-react';
import { sessionsApi } from '../lib/api/client';
import type { Session } from '../types';

export default function Sessions() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const data = await sessionsApi.getAll();
      // Sort by date descending
      const sorted = data.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
      setSessions(sorted);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const activeSessions = sessions.filter((s) => s.status === 'ACTIVE');
  const endedSessions = sessions.filter((s) => s.status === 'ENDED');

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Sessions</h1>
          <p className="mt-2 text-gray-600">Manage attendance sessions</p>
        </div>
        <Link
          to="/sessions/create"
          className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus size={20} className="mr-2" />
          Create Session
        </Link>
      </div>

      {/* Active Sessions */}
      {activeSessions.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
            Active Sessions ({activeSessions.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {activeSessions.map((session) => (
              <SessionCard key={session.id} session={session} formatDate={formatDate} />
            ))}
          </div>
        </div>
      )}

      {/* Ended Sessions */}
      {endedSessions.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <XCircle size={20} className="mr-2 text-gray-400" />
            Ended Sessions ({endedSessions.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {endedSessions.map((session) => (
              <SessionCard key={session.id} session={session} formatDate={formatDate} />
            ))}
          </div>
        </div>
      )}

      {sessions.length === 0 && (
        <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
          <Calendar className="mx-auto text-gray-400" size={48} />
          <h3 className="mt-4 text-lg font-medium text-gray-900">No sessions yet</h3>
          <p className="mt-2 text-gray-600">Create your first session to get started</p>
          <Link
            to="/sessions/create"
            className="mt-4 inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            <Plus size={20} className="mr-2" />
            Create Session
          </Link>
        </div>
      )}
    </div>
  );
}

function SessionCard({ session, formatDate }: { session: Session; formatDate: (date: string) => string }) {
  const isActive = session.status === 'ACTIVE';

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{formatDate(session.date)}</h3>
          <div className="flex items-center mt-2 text-sm text-gray-600">
            <Clock size={14} className="mr-1" />
            {session.start_time}
            {session.end_time && ` - ${session.end_time}`}
          </div>
        </div>
        <span
          className={`px-3 py-1 text-xs font-medium rounded-full ${
            isActive
              ? 'bg-green-100 text-green-800'
              : 'bg-gray-100 text-gray-800'
          }`}
        >
          {session.status}
        </span>
      </div>
      <div className="mt-4 flex items-center gap-2">
        <Link
          to={`/sessions/${session.id}`}
          className="flex-1 text-primary-600 hover:text-primary-700 font-medium"
        >
          View Details
        </Link>
        {!isActive && (
          <Link to={`/sessions/${session.id}/report`} className="px-3 py-2 border rounded text-sm bg-gray-50 hover:bg-gray-100">Report</Link>
        )}
      </div>
    </div>
  );
}
