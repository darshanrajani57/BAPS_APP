import { useEffect, useState } from 'react';
import { Plus, Heart, Edit, Trash2, Calendar } from 'lucide-react';
import { sevasApi, membersApi } from '../lib/api/client';
import type { Seva } from '../types';

export default function Sevas() {
  const [sevas, setSevas] = useState<Seva[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({ name: '', seva_type: '' });
  // Edit modal state
  const [showEditForm, setShowEditForm] = useState(false);
  const [editFormData, setEditFormData] = useState({ name: '', seva_type: '' });
  const [editingSeva, setEditingSeva] = useState<Seva | null>(null);
  // Manage members state
  const [showManageForm, setShowManageForm] = useState(false);
  const [managingSeva, setManagingSeva] = useState<Seva | null>(null);
  const [manageMembers, setManageMembers] = useState<Array<{ id: number; name: string }>>([]);
  const [allMembers, setAllMembers] = useState<Array<{ id: number; name: string }>>([]);
  const [manageSearch, setManageSearch] = useState('');
  // Multi-select additions
  const [selectedToAdd, setSelectedToAdd] = useState<number[]>([]);
  const [isAdding, setIsAdding] = useState(false);

  useEffect(() => {
    loadSevas();
  }, []);

  const loadSevas = async () => {
    try {
      const data = await sevasApi.getAll();
      setSevas(data);
    } catch (error) {
      console.error('Failed to load sevas:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await sevasApi.create(formData);
      setFormData({ name: '', seva_type: '' });
      setShowCreateForm(false);
      loadSevas();
      // Open manage members for the newly created seva
      if (created && created.id) {
        handleStartManage(created);
      }
    } catch (error) {
      console.error('Failed to create seva:', error);
      alert('Failed to create seva. Please try again.');
    }
  };

  // Load all members for search (used when managing members)
  const loadAllMembers = async () => {
    try {
      const members = await membersApi.getAll();
      setAllMembers(members.map(m => ({ id: m.id, name: m.name })));
    } catch (err) {
      console.error('Failed to load members for manage modal:', err);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this seva?')) return;
    try {
      await sevasApi.delete(id);
      loadSevas();
    } catch (error) {
      console.error('Failed to delete seva:', error);
      alert('Failed to delete seva. Please try again.');
    }
  };

  // Start editing an existing seva
  const handleStartEdit = (seva: Seva) => {
    setEditingSeva(seva);
    setEditFormData({ name: seva.name, seva_type: seva.seva_type || '' });
    setShowEditForm(true);
  };

  // Save edits
  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingSeva) return;
    try {
      await sevasApi.update(editingSeva.id, editFormData);
      setShowEditForm(false);
      setEditingSeva(null);
      loadSevas();
    } catch (error) {
      console.error('Failed to update seva:', error);
      alert('Failed to update seva. Please try again.');
    }
  };

  // Manage members handlers
  const handleStartManage = async (seva: Seva) => {
    setManagingSeva(seva);
    setShowManageForm(true);
    await loadAllMembers();
    await loadSevaMembers(seva.id);
  };

  const loadSevaMembers = async (seva_id: string) => {
    try {
      const members = await sevasApi.getMembers(seva_id);
      setManageMembers(members);
    } catch (err) {
      console.error('Failed to load seva members:', err);
    }
  };

  const handleAddMember = async (member_id: number) => {
    if (!managingSeva) return;
    try {
      await sevasApi.addMember(managingSeva.id, member_id);
      await loadSevaMembers(managingSeva.id);
    } catch (err) {
      console.error('Failed to add member to seva:', err);
      alert('Failed to add member');
    }
  };

  const handleRemoveMember = async (member_id: number) => {
    if (!managingSeva) return;
    if (!confirm('Remove this member from the seva?')) return;
    try {
      await sevasApi.removeMember(managingSeva.id, member_id);
      await loadSevaMembers(managingSeva.id);
      await loadSevas();
    } catch (err) {
      console.error('Failed to remove member from seva:', err);
      alert('Failed to remove member');
    }
  };

  // Toggle selection for multi-add
  const toggleSelect = (member_id: number) => {
    setSelectedToAdd(prev => prev.includes(member_id) ? prev.filter(x => x !== member_id) : [...prev, member_id]);
  };

  const handleAddSelected = async () => {
    if (!managingSeva || selectedToAdd.length === 0) return;
    setIsAdding(true);
    try {
      for (const mid of selectedToAdd) {
        // ignore duplicates on server; no need for batching endpoint yet
        await sevasApi.addMember(managingSeva.id, mid);
      }
      setSelectedToAdd([]);
      await loadSevaMembers(managingSeva.id);
      await loadSevas();
    } catch (err) {
      console.error('Failed to add selected members to seva:', err);
      alert('Failed to add selected members');
    } finally {
      setIsAdding(false);
    }
  };

  // Create a new member and immediately add to this seva
  const handleCreateNewMemberInline = async (name: string) => {
    if (!managingSeva || !name || name.trim() === '') return;
    try {
      // create member
      const created = await membersApi.create({ name: name.trim() });
      // add to seva
      await sevasApi.addMember(managingSeva.id, created.id);
      // refresh lists
      await loadAllMembers();
      await loadSevaMembers(managingSeva.id);
      await loadSevas();
      setManageSearch('');
      setSelectedToAdd([]);
    } catch (err) {
      console.error('Failed to create and add member:', err);
      alert('Failed to create member');
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
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
          <h1 className="text-3xl font-bold text-gray-900">Sevas</h1>
          <p className="mt-2 text-gray-600">Manage seva activities</p>
        </div>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus size={20} className="mr-2" />
          {showCreateForm ? 'Cancel' : 'Create Seva'}
        </button>
      </div>

      {/* Create Form */}
      {showCreateForm && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Create New Seva</h2>
          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Seva Name</label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Enter seva name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Seva Type (Optional)</label>
              <input
                type="text"
                value={formData.seva_type}
                onChange={(e) => setFormData({ ...formData, seva_type: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Enter seva type"
              />
            </div>
            <div className="flex items-center space-x-4">
              <button
                type="submit"
                className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                Create Seva
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Edit Form Modal */}
      {showEditForm && editingSeva && (
        <div className="fixed inset-0 z-40 flex items-center justify-center">
          <div className="absolute inset-0 bg-black opacity-40" onClick={() => setShowEditForm(false)} />
          <div className="bg-white rounded-lg shadow-lg p-6 z-50 w-full max-w-md">
            <h2 className="text-lg font-semibold mb-4">Edit Seva</h2>
            <form onSubmit={handleUpdate} className="space-y-4">
              <div>
                <label className="block text-sm text-gray-700">Name</label>
                <input value={editFormData.name} onChange={(e) => setEditFormData({ ...editFormData, name: e.target.value })} className="mt-1 w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm text-gray-700">Seva Type</label>
                <input value={editFormData.seva_type} onChange={(e) => setEditFormData({ ...editFormData, seva_type: e.target.value })} className="mt-1 w-full border rounded px-3 py-2" />
              </div>
              <div className="flex items-center justify-end gap-2 mt-4">
                <button type="button" className="btn-secondary" onClick={() => { setShowEditForm(false); setEditingSeva(null); }}>Cancel</button>
                <button type="submit" className="btn-primary">Save</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Manage Members Modal */}
      {showManageForm && managingSeva && (
        <div className="fixed inset-0 z-40 flex items-center justify-center">
          <div className="absolute inset-0 bg-black opacity-40" onClick={() => setShowManageForm(false)} />
          <div className="bg-white rounded-lg shadow-lg p-6 z-50 w-full max-w-2xl">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Manage Members for {managingSeva.name}</h2>
              <button className="text-sm text-gray-600" onClick={() => setShowManageForm(false)}>Close</button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-medium mb-2">Assigned Members</h3>
                <div className="max-h-72 overflow-auto border rounded p-2">
                  {manageMembers.length === 0 ? (
                    <div className="text-sm text-gray-500">No members assigned</div>
                  ) : (
                    manageMembers.map(m => (
                      <div key={m.id} className="flex items-center justify-between py-1">
                        <div className="text-sm">{m.name}</div>
                        <button className="text-xs text-red-600" onClick={() => handleRemoveMember(m.id)}>Remove</button>
                      </div>
                    ))
                  )}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium mb-2">Add Members</h3>

                {/* Selected chips */}
                {selectedToAdd.length > 0 && (
                  <div className="flex gap-2 flex-wrap mb-2">
                    {selectedToAdd.map(id => {
                      const m = allMembers.find(x => x.id === id);
                      return m ? (
                        <div key={id} className="px-2 py-1 bg-blue-50 rounded-full text-sm flex items-center gap-2">
                          <span>{m.name}</span>
                          <button className="text-xs text-gray-600" onClick={() => toggleSelect(id)}>×</button>
                        </div>
                      ) : null;
                    })}
                  </div>
                )}

                <div className="relative">
                  <input
                    placeholder="Search members to add..."
                    value={manageSearch}
                    onChange={(e) => setManageSearch(e.target.value)}
                    className="w-full px-3 py-2 border rounded mb-2"
                  />

                  {/* Dropdown results */}
                  <div className="absolute left-0 right-0 bg-white border rounded shadow mt-1 max-h-56 overflow-auto z-30">
                    {(() => {
                      const assignedIds = new Set(manageMembers.map(m => m.id));
                      const available = allMembers
                        .filter(m => !assignedIds.has(m.id))
                        .filter(m => m.name.toLowerCase().includes(manageSearch.toLowerCase()));

                      if (manageSearch.trim() !== '' && available.length === 0) {
                        return (
                          <div className="p-2 text-sm text-gray-600 flex items-center justify-between">
                            <div>No match found</div>
                            <div>
                              <button className="px-2 py-1 text-xs text-green-700" onClick={() => handleCreateNewMemberInline(manageSearch)}>Create & Add "{manageSearch}"</button>
                            </div>
                          </div>
                        );
                      }

                      return available.slice(0, 50).map(m => (
                        <div key={m.id} className="px-3 py-2 hover:bg-gray-50 flex items-center justify-between">
                          <div className="text-sm">{m.name}</div>
                          <div className="flex items-center gap-2">
                            <button className={`text-xs px-2 py-1 rounded ${selectedToAdd.includes(m.id) ? 'bg-blue-600 text-white' : 'border bg-white'}`} onClick={() => toggleSelect(m.id)}>
                              {selectedToAdd.includes(m.id) ? 'Selected' : 'Select'}
                            </button>
                            <button className="text-xs text-green-600" onClick={() => { setSelectedToAdd([m.id]); handleAddSelected(); }}>Add</button>
                          </div>
                        </div>
                      ));
                    })()}
                  </div>
                </div>

                <div className="flex items-center gap-2 mt-2">
                  <button className="btn-primary" onClick={handleAddSelected} disabled={selectedToAdd.length === 0 || isAdding}>{isAdding ? 'Adding...' : 'Add selected'}</button>
                  <button className="btn-secondary" onClick={() => { setSelectedToAdd([]); setManageSearch(''); }}>Clear</button>
                </div>
              </div>
            </div>

          </div>
        </div>
      )}

      {/* Sevas Grid */}
      {sevas.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
          <Heart className="mx-auto text-gray-400" size={48} />
          <h3 className="mt-4 text-lg font-medium text-gray-900">No sevas yet</h3>
          <p className="mt-2 text-gray-600">Create your first seva to get started</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sevas.map((seva) => (
            <div
              key={seva.id}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">{seva.name}</h3>
                  {seva.seva_type && (
                    <p className="mt-1 text-sm text-gray-600">{seva.seva_type}</p>
                  )}
                </div>
                <Heart className="text-purple-500" size={24} />
              </div>
              <div className="flex items-center text-sm text-gray-600 mb-4">
                <Calendar size={14} className="mr-2" />
                Created: {formatDate(seva.created_date)}
              </div>
              {seva.member_count !== undefined && (
                <div className="text-sm text-gray-600 mb-4">
                  Members: {seva.member_count}
                </div>
              )}
              <div className="flex items-center space-x-2 pt-4 border-t">
                <button onClick={() => handleStartEdit(seva)} className="flex-1 px-3 py-2 text-sm text-primary-600 hover:bg-primary-50 rounded-lg transition-colors">
                  <Edit size={16} className="inline mr-1" />
                  Edit
                </button>
                <button onClick={() => handleStartManage(seva)} className="flex-1 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
                  Manage Members
                </button>
                <button
                  onClick={() => handleDelete(seva.id)}
                  className="flex-1 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <Trash2 size={16} className="inline mr-1" />
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
