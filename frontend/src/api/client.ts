import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({ baseURL: API_URL });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface TokenResponse {
  access_token: string;
  token_type: string;
  patient_id: string;
  patient_name: string;
}

export interface Summary {
  document_count: number;
  visit_count: number;
  active_alerts: number;
  medication_count: number;
  lab_count: number;
  recent_doc_type: string | null;
}

export interface Alert {
  id: string;
  alert_type: string;
  severity: string;
  details: Record<string, unknown> | null;
  resolved: boolean;
  created_at: string;
}

export interface Document {
  id: string;
  filename: string;
  doc_type: string;
  ocr_quality: number;
  uploaded_at: string;
}

export interface TimelineEvent {
  id: string;
  event_type: string;
  event_date: string | null;
  payload: Record<string, unknown> | null;
  visit_id: string | null;
}

export interface LabTrendPoint {
  date: string | null;
  value: number;
  unit: string | null;
}

export interface LabTrend {
  test_name: string;
  trend: string;
  points: LabTrendPoint[];
}

export interface EvidenceItem {
  document_id: string | null;
  snippet: string;
  visit_date: string | null;
}

export interface ChatResponse {
  answer: string;
  evidence: EvidenceItem[];
  confidence: number;
  disclaimer: string;
}

export interface UploadResult {
  message: string;
  document_id: string;
  doc_type: string;
  ocr_quality: number;
  alerts_triggered: string[];
}

export const authApi = {
  register: (email: string, password: string, name: string) =>
    api.post<TokenResponse>('/auth/register', { email, password, name }),
  login: (email: string, password: string) =>
    api.post<TokenResponse>('/auth/login', { email, password }),
};

export const dataApi = {
  upload: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return api.post<UploadResult>('/upload', form);
  },
  documents: () => api.get<Document[]>('/documents'),
  deleteDocument: (id: string) => api.delete<void>(`/documents/${id}`),
  timeline: () => api.get<TimelineEvent[]>('/timeline'),
  alerts: () => api.get<Alert[]>('/alerts'),
  summary: () => api.get<Summary>('/summary'),
  labTrends: (test: string) => api.get<LabTrend>(`/lab-trends?test=${test}`),
  chat: (question: string) => api.post<ChatResponse>('/chat', { question }),
};
