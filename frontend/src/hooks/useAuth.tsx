import { createContext, useContext, useState, type ReactNode } from 'react';

interface AuthState {
  token: string | null;
  patientId: string | null;
  patientName: string | null;
  login: (token: string, patientId: string, patientName: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [patientId, setPatientId] = useState(localStorage.getItem('patientId'));
  const [patientName, setPatientName] = useState(localStorage.getItem('patientName'));

  const login = (t: string, pid: string, name: string) => {
    localStorage.setItem('token', t);
    localStorage.setItem('patientId', pid);
    localStorage.setItem('patientName', name);
    setToken(t);
    setPatientId(pid);
    setPatientName(name);
  };

  const logout = () => {
    localStorage.clear();
    setToken(null);
    setPatientId(null);
    setPatientName(null);
  };

  return (
    <AuthContext.Provider value={{ token, patientId, patientName, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
