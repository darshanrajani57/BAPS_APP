import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { membersApi, assignmentsApi } from '../../lib/api/client';
import type { Member } from '../../types';

export default function MemberDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [member, setMember] = useState<Member | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState<Partial<Member>>({});
  const [samparkName, setSamparkName] = useState('');
  const [originalForm, setOriginalForm] = useState<Partial<Member>>({});
  const [suggestions, setSuggestions] = useState<Array<{ id: number; name: string; score: number }>>([]);
  const [assignedList, setAssignedList] = useState<Array<{ id: number; name: string }>>([]);
  const [assignmentEditing, setAssignmentEditing] = useState(false);
  const [candidates, setCandidates] = useState<Array<{ id: number; name: string }>>([]);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [filterQuery, setFilterQuery] = useState('');
  // Sort order for the dropdown 'Others' list and for assigned yuvaks
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [assignedSortOrder, setAssignedSortOrder] = useState<'asc' | 'desc'>('asc');
  // Map of candidate id -> assigned yuvaks count
  const [assignedCounts, setAssignedCounts] = useState<Record<number, number>>({});
  // Add/remove assigned yuvaks UI state
  const [showAddYuvak, setShowAddYuvak] = useState(false);
  const [yuvakCandidates, setYuvakCandidates] = useState<Array<{ id: number; name: string }>>([]);
  const [addFilter, setAddFilter] = useState('');

  useEffect(() => {
    if (!id) return;
    loadMember();
    loadAssignment();
    loadSuggestions();
    loadAssignedForSampark();
    loadCandidates();
    loadAssignedCounts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  useEffect(() => {
    // Close dropdown on escape or outside click
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') setDropdownOpen(false); };
    const onDocClick = (e: MouseEvent) => {
      // @ts-ignore - using closest for simple click outside detection
      if (!(e.target as any)?.closest || !(e.target as any).closest('.sampark-dropdown')) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('keydown', onKey);
    document.addEventListener('click', onDocClick);
    return () => { document.removeEventListener('keydown', onKey); document.removeEventListener('click', onDocClick); };
  }, []);

  const loadCandidates = async () => {
    try {
      const all = await membersApi.getAll();
      const c = all
        .filter(m => {
          const role = (m.member_type || '').toLowerCase();
          return ['sampark karyakar', 'karyakar', 'sanchalak', 'sampark'].includes(role);
        })
        .map(m => ({ id: m.id, name: m.name }));
      setCandidates(c);
    } catch (err) {
      console.error('Failed to load sampark candidates:', err);
    }
  };

  const loadYuvakCandidates = async () => {
    try {
      const all = await membersApi.getAll();
      const y = all
        .filter(m => (m.member_type || '').toLowerCase() === 'yuvak')
        .map(m => ({ id: m.id, name: m.name }));
      setYuvakCandidates(y);
    } catch (err) {
      console.error('Failed to load yuvak candidates:', err);
    }
  }; 

  const loadSuggestions = async () => {
    try {
      if (!id) return;
      const res = await assignmentsApi.getSuggestions(Number(id));
      setSuggestions(res);
    } catch (err) {
      console.error('Failed to load suggestions:', err);
    }
  };

  const loadAssignedForSampark = async () => {
    try {
      if (!id) return;
      const res = await assignmentsApi.getAssignedForSampark(Number(id));
      setAssignedList(res);
    } catch (err) {
      console.error('Failed to load assigned list:', err);
    }
  };

  const loadAssignedCounts = async () => {
    try {
      const res = await assignmentsApi.getAssignedCounts();
      const map: Record<number, number> = {};
      res.forEach((r: { id: number; name: string; count: number }) => { map[r.id] = r.count; });
      setAssignedCounts(map);
    } catch (err) {
      console.error('Failed to load assigned counts:', err);
    }
  };

  const handleAddYuvak = async (memberId: number) => {
    if (!member) return;
    try {
      await assignmentsApi.create(memberId, member.name);
      alert('Yuvak assigned');
      setShowAddYuvak(false);
      loadAssignedForSampark();
      loadAssignedCounts();
      loadYuvakCandidates();
    } catch (err) {
      console.error('Failed to add yuvak:', err);
      alert('Failed to add yuvak');
    }
  };

  const handleRemoveAssigned = async (memberId: number) => {
    try {
      // Ensure we only remove assignments that belong to this Sampark
      const all = await assignmentsApi.getAll();
      const assignment = all.find(a => a.member_id === memberId);
      if (!assignment) {
        alert('No assignment found for this member');
        return;
      }
      if (!member || assignment.sampark_name !== member.name) {
        alert('You can only remove yuvaks assigned to this Sampark');
        return;
      }

      const assignedMemberName = (assignment as any).member_name || yuvakCandidates.find(y => y.id === memberId)?.name || 'this yuvak';
      if (!confirm(`Remove ${assignedMemberName} from ${member.name}?`)) return;

      await assignmentsApi.deleteForMember(memberId);
      alert('Yuvak unassigned');
      loadAssignedForSampark();
      loadAssignedCounts();
      loadYuvakCandidates();
    } catch (err) {
      console.error('Failed to remove assigned yuvak:', err);
      alert('Failed to remove yuvak');
    }
  };

  const handleChangeMemberRole = async (memberId: number, newRole: string) => {
    try {
      // If changing away from Yuvak, confirm because this will unassign them
      if (newRole.toLowerCase() !== 'yuvak') {
        if (!confirm('Changing role will unassign this Yuvak. Continue?')) {
          // reload to reset any UI element (select) back to actual data
          loadAssignedForSampark();
          loadYuvakCandidates();
          return;
        }
      }

      await membersApi.update(memberId, { member_type: newRole });
      alert('Member role updated');
      // if changed away from Yuvak, unassign them
      if (newRole.toLowerCase() !== 'yuvak') {
        await assignmentsApi.deleteForMember(memberId);
      }
      loadAssignedForSampark();
      loadAssignedCounts();
      loadYuvakCandidates();
    } catch (err) {
      console.error('Failed to change member role:', err);
      alert('Failed to change role');
    }
  };

  const loadMember = async () => {
    try {
      const data = await membersApi.getById(Number(id));
      setMember(data);
      const initialForm: Partial<Member> = {
        name: data.name,
        phone: data.phone,
        family_phone: (data as any).family_phone,
        dob: (data as any).dob,
        address: data.address,
        member_type: data.member_type,
        category: data.category,
        status: (data as any).status,
        study: (data as any).study,
        college_timing: (data as any).college_timing,
        college_holiday: (data as any).college_holiday,
        job: (data as any).job,
        job_timing: (data as any).job_timing,
        job_holiday: (data as any).job_holiday,
        remark: (data as any).remark,
      };
      setForm(initialForm);
      setOriginalForm(initialForm);
    } catch (err) {
      console.error('Failed to load member:', err);
      alert('Failed to load member.');
    } finally {
      setLoading(false);
    }
  };

  const loadAssignment = async () => {
    try {
      const all = await assignmentsApi.getAll();
      const assign = all.find(a => a.member_id === Number(id));
      setSamparkName(assign ? assign.sampark_name : '');
    } catch (err) {
      console.error('Failed to load assignments:', err);
    }
  };

  const handleSave = async () => {
    if (!member) return;
    setSaving(true);
    try {
      await membersApi.update(member.id, form);
      alert('Member updated');
      setEditing(false);
      loadMember();
      loadSuggestions();
      loadAssignedForSampark();
    } catch (err) {
      console.error('Failed to save member:', err);
      alert('Failed to save member');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setForm(originalForm);
    setEditing(false);
  };

  const handleStartEdit = () => {
    setOriginalForm(form);
    setEditing(true);
  };

  const handleAssign = async () => {
    if (!member) return;
    try {
      await assignmentsApi.create(member.id, samparkName);
      alert('Assignment saved');
      setAssignmentEditing(false);
      loadAssignment();
      loadAssignedForSampark();
      loadAssignedCounts();
    } catch (err) {
      console.error('Failed to save assignment:', err);
      alert('Failed to save assignment');
    }
  };

  const handleQuickAssign = async (sampark: string) => {
    if (!member) return;
    try {
      await assignmentsApi.create(member.id, sampark);
      alert(`Assigned ${sampark}`);
      setSamparkName(sampark);
      setAssignmentEditing(false);
      loadAssignment();
      loadAssignedForSampark();
      loadAssignedCounts();
      // refresh yuvak candidates in case someone's role changed
      loadYuvakCandidates();
    } catch (err) {
      console.error('Failed to quick assign:', err);
      alert('Failed to assign');
    }
  };

  if (loading) return <div className="p-6">Loading...</div>;
  if (!member) return <div className="p-6">Member not found</div>;

  // Helpers for status
  const isJob = form.status === 'Job';
  const isCollege = form.status === 'College';
  const isYuvak = (member?.member_type || '').toLowerCase() === 'yuvak';
  const isSamparkLike = ['sampark karyakar', 'karyakar', 'sanchalak', 'sampark'].includes((member?.member_type || '').toLowerCase());
  // Find candidate object for the currently assigned sampark name (if any) to create a link
  const assignedCandidate = candidates.find(c => c.name === samparkName);

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Member Detail</h1>
          <p className="text-sm text-gray-600">Edit member and manage assignments</p>
        </div>
        <div className="flex items-center gap-3">
          {!editing ? (
            <button onClick={handleStartEdit} className="btn-primary">Edit</button>
          ) : (
            <>
              <button onClick={handleSave} disabled={saving} className="btn-primary">{saving ? 'Saving...' : 'Save'}</button>
              <button onClick={handleCancel} className="btn-secondary">Cancel</button>
            </>
          )}
          <button onClick={() => navigate('/members')} className="btn-secondary">Back</button>
          <button onClick={async () => {
            if (!member) return;
            if (!confirm(`Delete member ${member.name}? This will remove their assignments and attendance.`)) return;
            try {
              await membersApi.delete(member.id);
              alert('Member deleted');
              navigate('/members');
            } catch (err) {
              console.error('Failed to delete member:', err);
              alert('Failed to delete member');
            }
          }} className="btn-danger">Delete</button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Name</label>
            <input disabled={!editing} value={form.name || ''} onChange={(e) => setForm({ ...form, name: e.target.value })} className="mt-1 w-full" />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Role</label>
            <select disabled={!editing} value={form.member_type || ''} onChange={(e) => setForm({ ...form, member_type: e.target.value })} className="mt-1 w-full">
              <option value="">-- Select --</option>
              <option>Yuvak</option>
              <option>Sampark Karyakar</option>
              <option>Karyakar</option>
              <option>Sanchalak</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Phone</label>
            <input disabled={!editing} value={form.phone || ''} onChange={(e) => setForm({ ...form, phone: e.target.value })} className="mt-1 w-full" />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Family Phone</label>
            <input disabled={!editing} value={(form as any).family_phone || ''} onChange={(e) => setForm({ ...form, family_phone: e.target.value })} className="mt-1 w-full" />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Category</label>
            <input disabled={!editing} value={form.category || ''} onChange={(e) => setForm({ ...form, category: e.target.value })} className="mt-1 w-full" />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Date of Birth</label>
            <input disabled={!editing} value={(form.dob || '').toString()} onChange={(e) => setForm({ ...form, dob: e.target.value })} className="mt-1 w-full" />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700">Address</label>
            <input disabled={!editing} value={form.address || ''} onChange={(e) => setForm({ ...form, address: e.target.value })} className="mt-1 w-full" />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Status</label>
            <select disabled={!editing} value={(form.status as string) || ''} onChange={(e) => setForm({ ...form, status: e.target.value })} className="mt-1 w-full">
              <option value="">-- Select --</option>
              <option value="Job">Job</option>
              <option value="College">College</option>
            </select>
          </div>

          {/* Job section */}
          {isJob && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700">Job</label>
                <input disabled={!editing} value={(form as any).job || ''} onChange={(e) => setForm({ ...form, job: e.target.value })} className="mt-1 w-full" />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Job Timing</label>
                <input disabled={!editing} value={(form as any).job_timing || ''} onChange={(e) => setForm({ ...form, job_timing: e.target.value })} className="mt-1 w-full" />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Job Holiday</label>
                <select disabled={!editing} value={(form as any).job_holiday || ''} onChange={(e) => setForm({ ...form, job_holiday: e.target.value })} className="mt-1 w-full">
                  <option value="">-- Select --</option>
                  <option>Monday</option>
                  <option>Tuesday</option>
                  <option>Wednesday</option>
                  <option>Thursday</option>
                  <option>Friday</option>
                  <option>Saturday</option>
                  <option>Sunday</option>
                </select>
              </div>
            </>
          )}

          {/* College section */}
          {isCollege && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700">Study</label>
                <input disabled={!editing} value={(form as any).study || ''} onChange={(e) => setForm({ ...form, study: e.target.value })} className="mt-1 w-full" />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">College Timing</label>
                <input disabled={!editing} value={(form as any).college_timing || ''} onChange={(e) => setForm({ ...form, college_timing: e.target.value })} className="mt-1 w-full" />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">College Holiday</label>
                <select disabled={!editing} value={(form as any).college_holiday || ''} onChange={(e) => setForm({ ...form, college_holiday: e.target.value })} className="mt-1 w-full">
                  <option value="">-- Select --</option>
                  <option>Monday</option>
                  <option>Tuesday</option>
                  <option>Wednesday</option>
                  <option>Thursday</option>
                  <option>Friday</option>
                  <option>Saturday</option>
                  <option>Sunday</option>
                </select>
              </div>
            </>
          )}

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700">Remark</label>
            <textarea disabled={!editing} value={(form as any).remark || ''} onChange={(e) => setForm({ ...form, remark: e.target.value })} className="mt-1 w-full" />
          </div>
        </div>
      </div>

        {(isYuvak || assignedList.length > 0) && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <h2 className="text-lg font-semibold">Assignment (Sampark)</h2>

            {isYuvak && (
              <div className="mt-2 grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
                {assignmentEditing ? (
                  <>
                    <div className="md:col-span-2 relative sampark-dropdown">
<div className="flex items-center justify-between mb-1">
                      <label className="block text-sm font-medium text-gray-700">Select Sampark</label>
                      <div className="flex items-center gap-2">
                        <button type="button" onClick={() => setSortOrder('asc')} className={`text-xs px-2 py-1 rounded ${sortOrder === 'asc' ? 'bg-blue-600 text-white' : 'border bg-white'}`}>
                          A→Z
                        </button>
                        <button type="button" onClick={() => setSortOrder('desc')} className={`text-xs px-2 py-1 rounded ${sortOrder === 'desc' ? 'bg-blue-600 text-white' : 'border bg-white'}`}>
                          Z→A
                        </button>
                      </div>
                    </div>
                      <input
                        className="mt-1 w-full border rounded px-3 py-2"
                        placeholder="Search or pick a Sampark..."
                        value={filterQuery || samparkName}
                        onChange={(e) => { setFilterQuery(e.target.value); setDropdownOpen(true); }}
                        onClick={() => setDropdownOpen(true)}
                      />

                      <div className={`absolute z-20 mt-1 w-full bg-white border rounded shadow max-h-60 overflow-auto ${dropdownOpen ? '' : 'hidden'}`}>
                        {/* Suggested group (top 5) and Others */}
                        {(() => {
                          const topSuggestions = suggestions.slice(0, 5);
                          // suggested: keep order of top suggestions and apply filter
                          const suggested = topSuggestions
                            .filter(s => s.name.toLowerCase().includes((filterQuery || '').toLowerCase()))
                            .map(s => ({ id: s.id, name: s.name }))
                            .sort((a, b) => sortOrder === 'asc' ? a.name.localeCompare(b.name) : b.name.localeCompare(a.name));
                          const suggestedIds = new Set(topSuggestions.map(s => s.id));
                          // others: exclude top suggestions, apply filter and sort alphabetically
                          const other = candidates
                            .filter(c => !suggestedIds.has(c.id) && c.name.toLowerCase().includes((filterQuery || '').toLowerCase()))
                            .sort((a, b) => sortOrder === 'asc' ? a.name.localeCompare(b.name) : b.name.localeCompare(a.name));
                          return (
                            <div>
                              {suggested.length > 0 && (
                                <div>
                                  <div className="px-3 py-2 text-xs text-gray-500">Suggested</div>
                                  {suggested.map(c => {
                                    const count = assignedCounts[c.id] || 0;
                                    return (
                                      <div key={c.id} className="px-3 py-2 hover:bg-gray-50 flex items-center justify-between cursor-pointer" onClick={() => { setSamparkName(c.name); setFilterQuery(''); setDropdownOpen(false); }}>
                                        <div className="flex items-center gap-2">
                                          <span className="inline-block w-2 h-2 bg-green-500 rounded-full" />
                                          <span className="text-sm">{c.name}</span>
                                          <span className={`ml-2 text-xs px-2 py-0.5 rounded-full ${count > 0 ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'}`}>{count}</span>
                                        </div>
                                        <div className="text-xs text-gray-500">Use</div>
                                      </div>
                                    );
                                  })}
                                </div>
                              )}

                              {/* Others */}
                              <div>
                                <div className="px-3 py-2 text-xs text-gray-500">Others</div>
                                {other.map(c => {
                                  const count = assignedCounts[c.id] || 0;
                                  return (
                                    <div key={c.id} className="px-3 py-2 hover:bg-gray-50 flex items-center justify-between cursor-pointer" onClick={() => { setSamparkName(c.name); setFilterQuery(''); setDropdownOpen(false); }}>
                                      <div className="flex items-center gap-2">
                                        <div className="text-sm">{c.name}</div>
                                        <span className={`ml-2 text-xs px-2 py-0.5 rounded-full ${count > 0 ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'}`}>{count}</span>
                                      </div>
                                    </div>
                                  );
                                })}
                              </div>
                            </div>
                          );
                        })()}
                      </div>
                    </div>
                    <div>
                      <div className="flex flex-col gap-2">
                        <button className="btn-primary w-full" onClick={handleAssign}>Save</button>
                        <button className="btn-secondary w-full" onClick={() => { setAssignmentEditing(false); loadAssignment(); }}>Cancel</button>
                      </div>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="md:col-span-2">
                      {samparkName ? (
                        assignedCandidate ? (
                          <div className="text-sm">Assigned: <a className="text-primary-600 hover:underline" href={`/members/${assignedCandidate.id}`}>{samparkName}</a></div>
                        ) : (
                          <div className="text-sm">Assigned: {samparkName}</div>
                        )
                      ) : (
                        <div className="text-sm text-gray-400">No Sampark assigned</div>
                      )}
                    </div>
                    <div>
                      <button className="btn-secondary" onClick={() => setAssignmentEditing(true)}>Edit Assignment</button>
                    </div>
                  </>
                )}
              </div>
            )}



            {/* Assigned list if current is sampark */}
            {(isSamparkLike || assignedList.length > 0) && (
              <div className="mt-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium">Assigned Yuvaks</h3>
                  <div className="flex items-center gap-2">
                    <button type="button" onClick={() => setAssignedSortOrder('asc')} className={`text-xs px-2 py-1 rounded ${assignedSortOrder === 'asc' ? 'bg-blue-600 text-white' : 'border bg-white'}`}>
                      A→Z
                    </button>
                    <button type="button" onClick={() => setAssignedSortOrder('desc')} className={`text-xs px-2 py-1 rounded ${assignedSortOrder === 'desc' ? 'bg-blue-600 text-white' : 'border bg-white'}`}>
                      Z→A
                    </button>
                    {isSamparkLike && (
                      <button type="button" onClick={() => { setShowAddYuvak(!showAddYuvak); loadYuvakCandidates(); }} className="text-xs px-2 py-1 rounded border bg-white">
                        {showAddYuvak ? 'Close' : 'Add Yuvak'}
                      </button>
                    )}
                  </div>
                </div>

                {showAddYuvak && (
                  <div className="mt-2 border rounded p-3 bg-gray-50">
                    <div className="flex gap-2 items-center mb-2">
                      <input placeholder="Search Yuvaks..." value={addFilter} onChange={(e) => setAddFilter(e.target.value)} className="w-full px-2 py-1 border rounded" />
                    </div>
                    <div className="max-h-48 overflow-auto">
                      {yuvakCandidates.filter(y => y.name.toLowerCase().includes(addFilter.toLowerCase())).map(y => (
                        <div key={y.id} className="flex items-center justify-between px-2 py-1 hover:bg-white">
                          <div className="text-sm">{y.name}</div>
                          <div className="flex items-center gap-2">
                            <button className="text-xs px-2 py-1 rounded bg-green-100 text-green-700" onClick={() => handleAddYuvak(y.id)}>Add</button>
                            <a href={`/members/${y.id}`} className="text-xs text-gray-600 hover:text-primary-700">Edit</a>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="mt-2 grid gap-2">
                  {assignedList.slice().sort((x, y) => assignedSortOrder === 'asc' ? x.name.localeCompare(y.name) : y.name.localeCompare(x.name)).map((a) => (
                    <div key={a.id} className="py-1 text-sm flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div>• <a className="text-primary-600 hover:underline" href={`/members/${a.id}`}>{a.name}</a></div>
                        {/* Quick role selector for assigned member */}
                        <div>
                          <select defaultValue="Yuvak" onChange={(e) => handleChangeMemberRole(a.id, e.target.value)} className="text-xs border rounded px-2 py-0.5">
                            <option>Yuvak</option>
                            <option>Sampark Karyakar</option>
                            <option>Karyakar</option>
                            <option>Sanchalak</option>
                          </select>
                        </div>
                      </div>
                      <div>
                        <button className="text-xs px-2 py-1 rounded bg-red-100 text-red-700" onClick={() => handleRemoveAssigned(a.id)}>Remove</button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>
        )}
    </div>
  );
}
