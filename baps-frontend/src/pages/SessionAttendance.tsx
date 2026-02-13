import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, CheckCircle, XCircle, Search, Filter, Save } from 'lucide-react';
import { sessionsApi, attendanceApi, membersApi } from '../lib/api/client';
import type { Session, Member, Attendance } from '../types';

export default function SessionAttendance() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [session, setSession] = useState<Session | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [attendance, setAttendance] = useState<Record<number, 'Present' | 'Absent'>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (id) {
      loadData();
    }
  }, [id]);

  const loadData = async () => {
    if (!id) return;
    try {
      const [sessionData, membersData, attendanceData] = await Promise.all([
        sessionsApi.getById(id),
        membersApi.getAll(),
        attendanceApi.getBySession(id),
      ]);

      setSession(sessionData);
      setMembers(membersData);

      // Initialize attendance map
      const attendanceMap: Record<number, 'Present' | 'Absent'> = {};
      membersData.forEach((member) => {
        const att = attendanceData.find((a) => a.member_id === member.id);
        attendanceMap[member.id] = att?.status || 'Absent';
      });
      setAttendance(attendanceMap);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleAttendance = (memberId: number) => {
    if (session?.status === 'ENDED') return;
    setAttendance((prev) => ({
      ...prev,
      [memberId]: prev[memberId] === 'Present' ? 'Absent' : 'Present',
    }));
  };

  const handleSave = async () => {
    if (!id) return;
    setSaving(true);
    try {
      const promises = Object.entries(attendance).map(([memberId, status]) =>
        attendanceApi.update(id, parseInt(memberId), status)
      );
      await Promise.all(promises);
      alert('Attendance saved successfully!');
    } catch (error) {
      console.error('Failed to save attendance:', error);
      alert('Failed to save attendance. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleEndSession = async () => {
    if (!id || !confirm('Are you sure you want to end this session?')) return;
    try {
      await sessionsApi.end(id);
      await loadData();
    } catch (error) {
      console.error('Failed to end session:', error);
      alert('Failed to end session. Please try again.');
    }
  };

  const filteredMembers = members.filter((member) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      member.name?.toLowerCase().includes(query) ||
      member.member_type?.toLowerCase().includes(query) ||
      String(member.phone || '').toLowerCase().includes(query)
    );
  });

  const presentCount = Object.values(attendance).filter((status) => status === 'Present').length;
  const absentCount = Object.values(attendance).filter((status) => status === 'Absent').length;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!session) {
    return <div>Session not found</div>;
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate('/sessions')}
        className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
      >
        <ArrowLeft size={20} className="mr-2" />
        Back to Sessions
      </button>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Session Attendance</h1>
            <p className="mt-1 text-gray-600">
              {new Date(session.date).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-600">Status</div>
            <span
              className={`inline-block px-3 py-1 text-sm font-medium rounded-full ${
                session.status === 'ACTIVE'
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {session.status}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-green-50 rounded-lg p-4">
            <div className="text-sm text-gray-600">Present</div>
            <div className="text-2xl font-bold text-green-600">{presentCount}</div>
          </div>
          <div className="bg-red-50 rounded-lg p-4">
            <div className="text-sm text-gray-600">Absent</div>
            <div className="text-2xl font-bold text-red-600">{absentCount}</div>
          </div>
        </div>

        {session.status === 'ACTIVE' && (
          <div className="flex items-center space-x-4">
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
            >
              <Save size={20} className="mr-2" />
              {saving ? 'Saving...' : 'Save Attendance'}
            </button>
            <button
              onClick={handleEndSession}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              End Session
            </button>
          </div>
        )}
      </div>

      {/* Search */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search members..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Members List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredMembers.map((member) => (
                <tr
                  key={member.id}
                  className={`hover:bg-gray-50 cursor-pointer ${
                    session.status === 'ENDED' ? 'opacity-75' : ''
                  }`}
                  onClick={() => handleToggleAttendance(member.id!)}
                >
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">{member.name}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                      {member.member_type || 'N/A'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-center">
                    {attendance[member.id!] === 'Present' ? (
                      <CheckCircle className="inline text-green-500" size={24} />
                    ) : (
                      <XCircle className="inline text-red-500" size={24} />
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
