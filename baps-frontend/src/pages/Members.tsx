import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, Filter, Edit, Phone, MapPin } from 'lucide-react';
import { membersApi, assignmentsApi } from '../lib/api/client';
import type { Member } from '../types';

export default function Members() {
  const [members, setMembers] = useState<Member[]>([]);
  const [filteredMembers, setFilteredMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  // Map of member id -> assigned yuvaks count (for sampark-like members)
  const [assignedCounts, setAssignedCounts] = useState<Record<number, number>>({});

  // Add Member modal state
  const [showAddMember, setShowAddMember] = useState(false);
  const [newMember, setNewMember] = useState<Partial<Member>>({ name: '', phone: '', member_type: '', category: '', address: '', status: '' });

  useEffect(() => {
    loadMembers();
  }, []);

  useEffect(() => {
    filterMembers();
  }, [members, searchQuery, roleFilter]);

  const loadMembers = async () => {
    try {
      const data = await membersApi.getAll();
      setMembers(data);
      setFilteredMembers(data);
      // load assigned counts after members are fetched
      loadAssignedCounts();
    } catch (error) {
      console.error('Failed to load members:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterMembers = () => {
    let filtered = [...members];

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (m) =>
          m.name?.toLowerCase().includes(query) ||
          m.phone?.includes(query) ||
          m.address?.toLowerCase().includes(query) ||
          m.member_type?.toLowerCase().includes(query)
      );
    }

    if (roleFilter) {
      filtered = filtered.filter((m) => m.member_type === roleFilter);
    }

    setFilteredMembers(filtered);
  };

  const roles = Array.from(new Set(members.map((m) => m.member_type).filter(Boolean)));

  // Helper to display phone without trailing .0 and ensure string
  const formatPhone = (phone?: any) => {
    if (phone === undefined || phone === null || phone === '') return 'N/A';
    try {
      const s = String(phone);
      return s.replace(/\.0+$/, '');
    } catch (err) {
      return 'N/A';
    }
  };

  const loadAssignedCounts = async () => {
    try {
      const res = await assignmentsApi.getAssignedCounts();
      const map: Record<number, number> = {};
      res.forEach((r: { id: number; count: number }) => { map[r.id] = r.count; });
      setAssignedCounts(map);
    } catch (err) {
      console.error('Failed to load assigned counts:', err);
    }
  };

  const handleCreateMember = async () => {
    if (!newMember.name || newMember.name.trim() === '') {
      alert('Please enter a name.');
      return;
    }
    try {
      const created = await membersApi.create(newMember);
      alert(`Member ${created.name} created`);
      setShowAddMember(false);
      setNewMember({ name: '', phone: '', member_type: '', category: '', address: '', status: '' });
      // reload members and counts
      loadMembers();
      loadAssignedCounts();
    } catch (err) {
      console.error('Failed to create member:', err);
      alert('Failed to create member');
    }
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
          <h1 className="text-3xl font-bold text-gray-900">Members</h1>
          <p className="mt-2 text-gray-600">Manage and view all members</p>
        </div>
        <div>
          <button onClick={() => setShowAddMember(true)} className="btn-primary">Add Member</button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search by name, phone, or address..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent appearance-none bg-white"
            >
              <option value="">All Roles</option>
              {roles.map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Add Member Modal */}
      {showAddMember && (
        <div className="fixed inset-0 z-40 flex items-center justify-center">
          <div className="absolute inset-0 bg-black opacity-40" onClick={() => setShowAddMember(false)} />
          <div className="bg-white rounded-lg shadow-lg p-6 z-50 w-full max-w-md">
            <h2 className="text-lg font-semibold mb-4">Add Member</h2>
            <div className="space-y-3">
              <div>
                <label className="block text-sm text-gray-700">Name</label>
                <input value={newMember.name} onChange={(e) => setNewMember({ ...newMember, name: e.target.value })} className="mt-1 w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm text-gray-700">Phone</label>
                <input value={newMember.phone} onChange={(e) => setNewMember({ ...newMember, phone: e.target.value })} className="mt-1 w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm text-gray-700">Role</label>
                <select value={newMember.member_type} onChange={(e) => setNewMember({ ...newMember, member_type: e.target.value })} className="mt-1 w-full border rounded px-3 py-2">
                  <option value="">-- Select --</option>
                  <option>Yuvak</option>
                  <option>Sampark Karyakar</option>
                  <option>Karyakar</option>
                  <option>Sanchalak</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-700">Category</label>
                <input value={newMember.category} onChange={(e) => setNewMember({ ...newMember, category: e.target.value })} className="mt-1 w-full border rounded px-3 py-2" />
              </div>
              <div className="flex items-center justify-end gap-2 mt-4">
                <button className="btn-secondary" onClick={() => setShowAddMember(false)}>Cancel</button>
                <button className="btn-primary" onClick={handleCreateMember}>Create</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Results count */}
      <div className="text-sm text-gray-600">
        Showing {filteredMembers.length} of {members.length} members
      </div>

      {/* Members Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Phone
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Address
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredMembers.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                    No members found
                  </td>
                </tr>
              ) : (
                filteredMembers.map((member) => (
                  <tr key={member.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        <Link to={`/members/${member.id}`} className="text-primary-600 hover:underline">{member.name}</Link>
                      </div>
                      {member.category && (
                        <div className="text-sm text-gray-500">Category: {member.category}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                      <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                        {member.member_type || 'N/A'}
                      </span>
                      {(['sampark karyakar','karyakar','sanchalak','sampark'].includes((member.member_type||'').toLowerCase())) && (
                        <a href={`/members/${member.id}`} className="text-xs inline-flex items-center text-gray-600 hover:text-primary-700">
                          <span className={`ml-2 text-xs px-2 py-0.5 rounded-full ${ (assignedCounts[member.id] || 0) > 0 ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600' }`}>{assignedCounts[member.id] || 0}</span>
                        </a>
                      )}
                    </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center text-sm text-gray-900">
                        <Phone size={14} className="mr-1 text-gray-400" />
                        {formatPhone(member.phone)}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center text-sm text-gray-900">
                        <MapPin size={14} className="mr-1 text-gray-400 flex-shrink-0" />
                        <span className="truncate max-w-xs">{member.address || 'N/A'}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium flex items-center gap-3">
                      <Link to={`/members/${member.id}`} className="text-primary-600 hover:text-primary-900 flex items-center">
                        <Edit size={16} className="mr-1" />
                        Edit
                      </Link>
                      <button
                        className="text-red-600 hover:text-red-800 text-sm px-2 py-1 rounded border border-red-100"
                        onClick={async () => {
                          if (!confirm(`Delete member ${member.name}? This will remove their assignments and attendance.`)) return;
                          try {
                            await membersApi.delete(member.id);
                            alert('Member deleted');
                            // reload list and assigned counts
                            loadMembers();
                            loadAssignedCounts();
                          } catch (err) {
                            console.error('Failed to delete member:', err);
                            alert('Failed to delete member');
                          }
                        }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
