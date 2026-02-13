export interface Member {
  id: number;
  name: string;
  number?: string;
  phone?: string;
  family_phone?: string;
  address?: string;
  dob?: string;
  category?: string;
  member_type?: string;
  status?: string;
  study?: string;
  college_timing?: string;
  college_holiday?: string;
  job?: string;
  job_timing?: string;
  job_holiday?: string;
  remark?: string;
  last_updated?: string;
}

export interface Session {
  id: string;
  date: string;
  start_time: string;
  end_time?: string;
  status: 'ACTIVE' | 'ENDED';
  created_date?: string;
}

export interface Attendance {
  id: number;
  session_id: string;
  member_id: number;
  member_name?: string;
  status: 'Present' | 'Absent';
  sampark_name?: string;
  recorded_date?: string;
}

export interface Seva {
  id: string;
  name: string;
  seva_type?: string;
  created_date?: string;
  member_count?: number;
}

export interface ApiResponse<T> {
  status: 'success' | 'error';
  data?: T;
  message?: string;
}
