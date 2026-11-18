import { Link, useLocation } from 'react-router-dom';

interface SidebarProps {
  user: { email: string; first_name?: string } | null;
  onLogout: () => void;
}

const navItems = [
  { path: '/', label: 'Dashboard', icon: '◆' },
  { path: '/companies', label: 'Companies', icon: '◈' },
  { path: '/inventory', label: 'Inventory', icon: '▪' },
  { path: '/reconciliations', label: 'Reconciliations', icon: '⬡' },
];

export default function Sidebar({ user, onLogout }: SidebarProps) {
  const location = useLocation();

  return (
    <aside style={{
      width: '260px',
      minWidth: '260px',
      background: 'linear-gradient(180deg, #0B1D33 0%, #0F2642 100%)',
      color: '#C8D6E5',
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      borderRight: '1px solid rgba(37, 99, 235, 0.1)',
    }}>
      {/* Logo Area */}
      <div style={{
        padding: '1.75rem 1.5rem 1.5rem',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1rem',
            boxShadow: '0 0 16px rgba(37, 99, 235, 0.3)',
          }}>⬡</div>
          <div>
            <h2 style={{
              fontSize: '1.1rem',
              fontWeight: 800,
              color: '#FFFFFF',
              letterSpacing: '-0.02em',
              margin: 0,
              lineHeight: 1.2,
            }}>Reconly</h2>
            <p style={{
              fontSize: '0.65rem',
              color: '#2563EB',
              textTransform: 'uppercase',
              letterSpacing: '0.1em',
              margin: 0,
              fontWeight: 600,
            }}>Inventory Pro</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{
        flex: 1,
        padding: '1rem 0.75rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '2px',
      }}>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path ||
            (item.path !== '/' && location.pathname.startsWith(item.path));

          return (
            <Link
              key={item.path}
              to={item.path}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                textDecoration: 'none',
                color: isActive ? '#60A5FA' : '#8A9BB0',
                background: isActive ? 'rgba(37, 99, 235, 0.12)' : 'transparent',
                fontWeight: isActive ? 600 : 500,
                fontSize: '0.9rem',
                transition: 'all 150ms ease',
                position: 'relative',
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  e.currentTarget.style.background = 'rgba(255,255,255,0.04)';
                  e.currentTarget.style.color = '#C8D6E5';
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.color = '#8A9BB0';
                }
              }}
            >
              {isActive && (
                <div style={{
                  position: 'absolute',
                  left: 0,
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: '3px',
                  height: '20px',
                  background: '#2563EB',
                  borderRadius: '0 2px 2px 0',
                }} />
              )}
              <span style={{ fontSize: '1rem', width: '20px', textAlign: 'center' }}>{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Bottom User Section */}
      <div style={{
        borderTop: '1px solid rgba(255,255,255,0.06)',
        padding: '1rem 1.25rem',
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          marginBottom: '0.75rem',
          padding: '0.6rem',
          background: 'rgba(255,255,255,0.03)',
          borderRadius: '8px',
        }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            background: 'linear-gradient(135deg, #1A3D5C, #2563EB)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '0.8rem',
            fontWeight: 700,
            color: '#FFFFFF',
          }}>
            {user?.first_name?.charAt(0)?.toUpperCase() || user?.email?.charAt(0)?.toUpperCase() || '?'}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <p style={{
              fontSize: '0.8rem',
              fontWeight: 600,
              color: '#E2E8F0',
              margin: 0,
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}>
              {user?.first_name || user?.email?.split('@')[0] || 'User'}
            </p>
            <p style={{
              fontSize: '0.65rem',
              color: '#8A9BB0',
              margin: 0,
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}>
              {user?.email}
            </p>
          </div>
        </div>
        <button
          onClick={onLogout}
          style={{
            width: '100%',
            padding: '0.55rem',
            background: 'rgba(239, 68, 68, 0.08)',
            border: '1px solid rgba(239, 68, 68, 0.15)',
            borderRadius: '8px',
            color: '#F87171',
            cursor: 'pointer',
            fontSize: '0.8rem',
            fontWeight: 500,
            transition: 'all 150ms ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(239, 68, 68, 0.15)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'rgba(239, 68, 68, 0.08)';
          }}
        >
          Sign Out
        </button>
      </div>
    </aside>
  );
}
