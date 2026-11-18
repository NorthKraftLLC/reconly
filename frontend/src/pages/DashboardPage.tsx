import { useState, useEffect } from 'react';
import Header from '../components/Header';
import api from '../services/api';

interface StatData {
  totalItems: number;
  activeReconciliations: number;
  openDiscrepancies: number;
  companiesCount: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<StatData>({
    totalItems: 0,
    activeReconciliations: 0,
    openDiscrepancies: 0,
    companiesCount: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [companiesRes, recsRes] = await Promise.all([
          api.get('/companies/'),
          api.get('/reconciliations/'),
        ]);

        const companies = companiesRes.data || [];
        const recs = recsRes.data || [];

        setStats({
          companiesCount: companies.length,
          totalItems: recs.reduce((sum: number, r: any) => sum + (r.total_items || 0), 0),
          activeReconciliations: recs.filter((r: any) => r.status === 'in_progress').length,
          openDiscrepancies: recs.reduce((sum: number, r: any) => sum + (r.discrepancies_found || 0), 0),
        });
      } catch {
        // Stats remain at defaults
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const statCards = [
    {
      title: 'Companies',
      value: loading ? '—' : stats.companiesCount,
      subtitle: 'Tracked in your system',
      icon: '◈',
      variant: '' as const,
      color: '#2563EB',
    },
    {
      title: 'Items Reconciled',
      value: loading ? '—' : stats.totalItems.toLocaleString(),
      subtitle: 'Across all reconciliations',
      icon: '▪',
      variant: '' as const,
      color: '#3B82F6',
    },
    {
      title: 'Active Reconciliations',
      value: loading ? '—' : stats.activeReconciliations,
      subtitle: 'Currently in progress',
      icon: '⬡',
      variant: stats.activeReconciliations > 0 ? 'warning' : '',
      color: stats.activeReconciliations > 0 ? '#FF6B2C' : '#2563EB',
    },
    {
      title: 'Open Discrepancies',
      value: loading ? '—' : stats.openDiscrepancies,
      subtitle: 'Need your attention',
      icon: '⚠',
      variant: stats.openDiscrepancies > 0 ? 'danger' : '',
      color: stats.openDiscrepancies > 0 ? '#EF4444' : '#2563EB',
    },
  ];

  return (
    <>
      <Header title="Dashboard" />

      {/* Stat Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '1.25rem',
        marginBottom: '2rem',
      }}>
        {statCards.map((stat) => (
          <div
            key={stat.title}
            className="card card-hover"
            style={{ borderTop: `3px solid ${stat.color}` }}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
              <p style={{
                fontSize: '0.8rem',
                color: 'var(--text-muted)',
                marginBottom: 0,
                fontWeight: 500,
              }}>{stat.title}</p>
              <span style={{
                fontSize: '1.25rem',
                opacity: 0.5,
              }}>{stat.icon}</span>
            </div>
            <p style={{
              fontSize: '2rem',
              fontWeight: 800,
              color: 'var(--text-primary)',
              margin: 0,
              letterSpacing: '-0.02em',
              lineHeight: 1.1,
            }}>{stat.value}</p>
            <p style={{
              fontSize: '0.75rem',
              color: 'var(--text-muted)',
              marginTop: '0.35rem',
              marginBottom: 0,
            }}>{stat.subtitle}</p>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '1.25rem',
      }}>
        <QuickActionCard
          icon="⬡"
          title="New Reconciliation"
          description="Start a fresh inventory reconciliation and catch discrepancies instantly."
          link="/reconciliations"
          gradient="linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)"
        />
        <QuickActionCard
          icon="◈"
          title="Add a Company"
          description="Register a new company and start tracking their inventory."
          link="/companies"
          gradient="linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)"
        />
        <QuickActionCard
          icon="▪"
          title="Browse Inventory"
          description="View and manage inventory items across all companies."
          link="/inventory"
          gradient="linear-gradient(135deg, #FF6B2C 0%, #E85A1F 100%)"
        />
      </div>
    </>
  );
}

function QuickActionCard({ icon, title, description, link, gradient }: {
  icon: string;
  title: string;
  description: string;
  link: string;
  gradient: string;
}) {
  return (
    <a href={link} className="card card-hover" style={{ textDecoration: 'none' }}>
      <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
        <div style={{
          width: '44px',
          height: '44px',
          minWidth: '44px',
          borderRadius: '12px',
          background: gradient,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '1.25rem',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        }}>{icon}</div>
        <div>
          <h3 style={{
            fontSize: '1rem',
            fontWeight: 700,
            marginBottom: '0.25rem',
            color: 'var(--text-primary)',
          }}>{title}</h3>
          <p style={{
            fontSize: '0.8rem',
            color: 'var(--text-muted)',
            margin: 0,
            lineHeight: 1.5,
          }}>{description}</p>
        </div>
      </div>
    </a>
  );
}
