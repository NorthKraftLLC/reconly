import { type ReactNode } from 'react';
import { useAuth } from '../hooks/useAuth';
import Sidebar from './Sidebar';

export default function Layout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar user={user} onLogout={logout} />
      <main style={{
        flex: 1,
        padding: '2rem 2.5rem',
        background: 'var(--bg)',
        minWidth: 0,
        maxHeight: '100vh',
        overflowY: 'auto',
      }}>
        {children}
      </main>
    </div>
  );
}
