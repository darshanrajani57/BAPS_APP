import axios from 'axios';
import type { Member, Session, Attendance, Seva, ApiResponse } from '../../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Add request interceptor for debugging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error('API Error Response:', error.response.status, error.response.data);
    } else if (error.request) {
      console.error('API Request Error: No response received. Is the backend running?');
      console.error('Backend URL:', API_BASE_URL);
    } else {
      console.error('API Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// Members API
export const membersApi = {
  getAll: async (): Promise<Member[]> => {
    const response = await apiClient.get<ApiResponse<Member[]>>('/members');
    return response.data.data || [];
  },
  getById: async (id: number): Promise<Member> => {
    const response = await apiClient.get<ApiResponse<Member>>(`/members/${id}`);
    if (!response.data.data) throw new Error('Member not found');
    return response.data.data;
  },
  create: async (member: Partial<Member>): Promise<Member> => {
    const response = await apiClient.post<ApiResponse<Member> & { id?: number }>('/members', member);
    // Backend returns { status: 'success', message: '...', id: ... }
    if (response.data.status === 'success' && response.data.id) {
      // Fetch the created member to get full details
      return await membersApi.getById(response.data.id);
    }
    if (response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Failed to create member');
  },
  update: async (id: number, member: Partial<Member>): Promise<void> => {
    await apiClient.put<ApiResponse<void>>(`/members/${id}`, member);
  },
  delete: async (id: number): Promise<void> => {
    await apiClient.delete<ApiResponse<void>>(`/members/${id}`);
  },
};

// Sessions API
export const sessionsApi = {
  getAll: async (): Promise<Session[]> => {
    const response = await apiClient.get<ApiResponse<Session[]>>('/sessions');
    return response.data.data || [];
  },
  getById: async (id: string): Promise<Session> => {
    const response = await apiClient.get<ApiResponse<Session>>(`/sessions/${id}`);
    if (!response.data.data) throw new Error('Session not found');
    return response.data.data;
  },
  getReport: async (id: string): Promise<{ session: any; report: any; role_summary: any }> => {
    const response = await apiClient.get<ApiResponse<any>>(`/sessions/${id}/report`);
    return response.data.data || { session: null, report: {}, role_summary: {} };
  },
  create: async (session: { date: string; start_time: string; end_time?: string }): Promise<Session> => {
    const response = await apiClient.post<ApiResponse<Session> & { id?: string }>('/sessions', session);
    // Backend returns { status: 'success', message: '...', id: '...' }
    if (response.data.status === 'success' && response.data.id) {
      // Fetch the created session to get full details
      return await sessionsApi.getById(response.data.id);
    }
    if (response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Failed to create session');
  },
  end: async (id: string): Promise<void> => {
    await apiClient.put<ApiResponse<void>>(`/sessions/${id}/end`);
  },
};

// Attendance API
export const attendanceApi = {
  getBySession: async (sessionId: string): Promise<Attendance[]> => {
    const response = await apiClient.get<ApiResponse<Attendance[]>>(`/sessions/${sessionId}/attendance`);
    return response.data.data || [];
  },
  update: async (sessionId: string, memberId: number, status: 'Present' | 'Absent', samparkName?: string): Promise<void> => {
    await apiClient.post<ApiResponse<void>>(`/sessions/${sessionId}/attendance`, {
      member_id: memberId,
      status,
      sampark_name: samparkName,
    });
  },
};

// Sevas API
export const sevasApi = {
  getAll: async (): Promise<Seva[]> => {
    const response = await apiClient.get<ApiResponse<Seva[]>>('/sevas');
    return response.data.data || [];
  },
  create: async (seva: { name: string; seva_type?: string }): Promise<Seva> => {
    const response = await apiClient.post<ApiResponse<Seva> & { id?: string }>('/sevas', seva);
    // Backend returns { status: 'success', message: '...', id: '...' }
    if (response.data.status === 'success' && response.data.id) {
      // Fetch all sevas and find the one we just created
      const sevas = await sevasApi.getAll();
      const created = sevas.find(s => s.id === response.data.id);
      if (created) return created;
    }
    if (response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Failed to create seva');
  },
  update: async (id: string, seva: { name?: string; seva_type?: string }): Promise<void> => {
    await apiClient.put<ApiResponse<void>>(`/sevas/${id}`, seva);
  },
  delete: async (id: string): Promise<void> => {
    await apiClient.delete<ApiResponse<void>>(`/sevas/${id}`);
  },
  // Seva members
  getMembers: async (seva_id: string): Promise<Array<{ id: number; name: string }>> => {
    const response = await apiClient.get<ApiResponse<any[]>>(`/sevas/${seva_id}/members`);
    return response.data.data || [];
  },
  addMember: async (seva_id: string, member_id: number): Promise<void> => {
    await apiClient.post(`/sevas/${seva_id}/members`, { member_id });
  },
  removeMember: async (seva_id: string, member_id: number): Promise<void> => {
    await apiClient.delete(`/sevas/${seva_id}/members/${member_id}`);
  },
};

// Assignments API
export const assignmentsApi = {
  getAll: async (): Promise<Array<{ id: number; member_id: number; sampark_name: string }>> => {
    const response = await apiClient.get<ApiResponse<any[]>>('/assignments');
    return response.data.data || [];
  },
  create: async (member_id: number, sampark_name: string): Promise<void> => {
    await apiClient.post('/assignments', { member_id, sampark_name });
  },
  deleteForMember: async (member_id: number): Promise<void> => {
    // Backend deletes existing assignment by member_id on create; if necessary add endpoint to delete
    await apiClient.post('/assignments', { member_id, sampark_name: null });
  },  // Suggestions for a yuvak
  getSuggestions: async (member_id: number): Promise<Array<{ id: number; name: string; score: number }>> => {
    const response = await apiClient.get<ApiResponse<any[]>>(`/members/${member_id}/suggestions`);
    return response.data.data || [];
  },
  // Assigned yuvaks for a sampark/karyakar
  getAssignedForSampark: async (member_id: number): Promise<Array<{ id: number; name: string }>> => {
    const response = await apiClient.get<ApiResponse<any[]>>(`/members/${member_id}/assigned`);
    return response.data.data || [];
  },
  // Assigned counts for sampark-like members
  getAssignedCounts: async (): Promise<Array<{ id: number; name: string; count: number }>> => {
    const response = await apiClient.get<ApiResponse<any[]>>('/members/assigned_counts');
    return response.data.data || [];
  },};

export default apiClient;
