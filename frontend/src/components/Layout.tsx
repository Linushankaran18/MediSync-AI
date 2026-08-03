import { Link, useLocation } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../hooks/useAuth';
import { dataApi } from '../api/client';

const links = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/upload', label: 'Upload' },
  { to: '/timeline', label: 'Timeline' },
  { to: '/charts', label: 'Trends' },
  { to: '/chat', label: 'Ask AI' },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const { patientName, logout } = useAuth();
  const location = useLocation();
  const { data: alerts } = useQuery({ queryKey: ['alerts'], queryFn: () => dataApi.alerts().then((r) => r.data) });
  const activeAlertCount = alerts?.filter((a) => !a.resolved).length ?? 0;

  return (
    <div className="min-h-screen">
      <nav className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <span className="text-xl font-bold text-blue-600">MedIntel AI</span>
            <div className="hidden md:flex gap-4">
              {links.map((l) => (
                <Link
                  key={l.to}
                  to={l.to}
                  className={`relative text-sm font-medium ${
                    location.pathname === l.to ? 'text-blue-600' : 'text-slate-600 hover:text-blue-600'
                  }`}
                >
                  {l.label}
                  {l.to === '/dashboard' && activeAlertCount > 0 && (
                    <span className="absolute -top-2 -right-3 bg-red-600 text-white text-[10px] font-bold rounded-full w-4 h-4 flex items-center justify-center">
                      {activeAlertCount}
                    </span>
                  )}
                </Link>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-500">{patientName}</span>
            <button
              onClick={logout}
              className="text-sm text-slate-600 hover:text-red-600"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>
      <main className="max-w-6xl mx-auto px-4 py-8">{children}</main>
    </div>
  );
}
