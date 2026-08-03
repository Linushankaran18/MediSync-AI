import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const links = [
  { to: '/', label: 'Upload' },
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/timeline', label: 'Timeline' },
  { to: '/charts', label: 'Charts' },
  { to: '/chat', label: 'Chat' },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const { patientName, logout } = useAuth();
  const location = useLocation();

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
                  className={`text-sm font-medium ${
                    location.pathname === l.to ? 'text-blue-600' : 'text-slate-600 hover:text-blue-600'
                  }`}
                >
                  {l.label}
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
