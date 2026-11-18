import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import api from '../services/api';

export default function ReconciliationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [rec, setRec] = useState<any>(null);
  const [discrepancies, setDiscrepancies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'discrepancies' | 'matched'>('discrepancies');

  useEffect(() => {
    (async () => {
      const [recRes, discRes] = await Promise.all([
        api.get(`/reconciliations/${id}`),
        api.get(`/reconciliations/${id}/discrepancies`),
      ]);
      setRec(recRes.data);
      setDiscrepancies(discRes.data);
      setLoading(false);
    })();
  }, [id]);

  const formatStatus = (status: string) => {
    return status.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  };

  const severityBadge = (severity: string) => {
    switch (severity) {
      case 'critical': return 'badge-danger';
      case 'high': return 'badge-warning';
      case 'medium': return 'badge-info';
      default: return 'badge-success';
    }
  };

  if (loading) {
    return (
      <>
        <div className="page-header">
          <h1>Loading...</h1>
        </div>
        <div className="card" style={{ height: '200px' }}>
          <div className="loading-shimmer" style={{ width: '40%', height: '20px', marginBottom: '12px' }} />
          <div className="loading-shimmer" style={{ width: '70%', height: '16px' }} />
        </div>
      </>
    );
  }

  if (!rec) return <div className="empty-state">Reconciliation not found.</div>;

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button
            className="btn-secondary"
            onClick={() => navigate('/reconciliations')}
            style={{ padding: '0.5rem 0.75rem', fontSize: '0.85rem' }}
          >
            ← Back
          </button>
          <div>
            <h1 style={{ marginBottom: '0.2rem' }}>{rec.name}</h1>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
              Created {rec.created_at ? new Date(rec.created_at).toLocaleString() : '—'}
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <a
            href={`/api/v1/reports/${id}/pdf`}
            download
            className="btn-secondary"
          >PDF</a>
          <a
            href={`/api/v1/reports/${id}/csv`}
            download
            className="btn-secondary"
          >CSV</a>
          <a
            href={`/api/v1/reports/${id}/excel`}
            download
            className="btn-secondary"
          >Excel</a>
        </div>
      </div>

      {/* Summary Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
        gap: '1rem',
        marginBottom: '1.5rem',
      }}>
        <StatCard label="Total Items" value={rec.total_items} color="#2563EB" />
        <StatCard label="Matched" value={rec.matched_items} color="#3B82F6" />
        <StatCard label="Discrepancies" value={rec.discrepancies_found} color="#FF6B2C" accent />
        <StatCard label="Status" value={formatStatus(rec.status)} color="#0B1D33" />
      </div>

      {/* Tabs */}
      <div style={{
        display: 'flex',
        gap: '0',
        marginBottom: '1.25rem',
        borderBottom: '2px solid var(--border)',
      }}>
        <button
          onClick={() => setActiveTab('discrepancies')}
          style={{
            padding: '0.65rem 1.25rem',
            background: 'none',
            border: 'none',
            borderBottom: activeTab === 'discrepancies' ? '2px solid var(--turquoise)' : '2px solid transparent',
            marginBottom: '-2px',
            fontWeight: activeTab === 'discrepancies' ? 600 : 500,
            color: activeTab === 'discrepancies' ? 'var(--turquoise-dark)' : 'var(--text-muted)',
            cursor: 'pointer',
            fontSize: '0.9rem',
            transition: 'all 150ms ease',
          }}
        >
          Discrepancies ({discrepancies.length})
        </button>
        <button
          onClick={() => setActiveTab('matched')}
          style={{
            padding: '0.65rem 1.25rem',
            background: 'none',
            border: 'none',
            borderBottom: activeTab === 'matched' ? '2px solid var(--turquoise)' : '2px solid transparent',
            marginBottom: '-2px',
            fontWeight: activeTab === 'matched' ? 600 : 500,
            color: activeTab === 'matched' ? 'var(--turquoise-dark)' : 'var(--text-muted)',
            cursor: 'pointer',
            fontSize: '0.9rem',
            transition: 'all 150ms ease',
          }}
        >
          Matched Items
        </button>
      </div>

      {/* Discrepancies Table */}
      {activeTab === 'discrepancies' && (
        <div className="table-wrapper" style={{ overflowX: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th>SKU</th>
                <th>Item</th>
                <th style={{ textAlign: 'right' }}>System Qty</th>
                <th style={{ textAlign: 'right' }}>Source Qty</th>
                <th style={{ textAlign: 'right' }}>Diff</th>
                <th>Type</th>
                <th>Severity</th>
                <th>Explanation</th>
                <th style={{ textAlign: 'center' }}>Resolved</th>
              </tr>
            </thead>
            <tbody>
              {discrepancies.map((d) => (
                <tr key={d.id}>
                  <td>
                    <code style={{
                      background: 'var(--bg)',
                      padding: '0.15rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.8rem',
                      fontFamily: 'SF Mono, Fira Code, monospace',
                    }}>{d.item_sku || '—'}</code>
                  </td>
                  <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{d.item_name}</td>
                  <td style={{ textAlign: 'right' }}>{d.system_quantity}</td>
                  <td style={{ textAlign: 'right' }}>{d.source_quantity}</td>
                  <td style={{
                    textAlign: 'right',
                    fontWeight: 700,
                    color: d.quantity_difference < 0 ? 'var(--danger)' : d.quantity_difference > 0 ? 'var(--orange)' : 'var(--text-primary)',
                  }}>{d.quantity_difference > 0 ? '+' : ''}{d.quantity_difference}</td>
                  <td>
                    <span className="badge badge-neutral">
                      {d.discrepancy_type.replace('_', ' ')}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${severityBadge(d.severity)}`}>
                      {d.severity.toUpperCase()}
                    </span>
                  </td>
                  <td className="truncate" style={{ maxWidth: '250px', fontSize: '0.85rem' }}>
                    {d.explanation}
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    {d.resolved
                      ? <span className="badge badge-success" style={{ fontSize: '0.7rem' }}>✓ Resolved</span>
                      : <span className="badge badge-neutral" style={{ fontSize: '0.7rem' }}>Pending</span>
                    }
                  </td>
                </tr>
              ))}
              {discrepancies.length === 0 && (
                <tr>
                  <td colSpan={9}>
                    <div className="empty-state">
                      <div className="empty-state-icon" style={{ fontSize: '2.5rem' }}>✓</div>
                      <h3 style={{ color: 'var(--turquoise-dark)', marginBottom: '0.25rem', fontSize: '1.1rem' }}>Perfect match!</h3>
                      <p>No discrepancies found. All items reconciled successfully.</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'matched' && (
        <div className="empty-state">
          <div className="empty-state-icon">✓</div>
          <h3 style={{ color: 'var(--turquoise-dark)', marginBottom: '0.5rem' }}>
            {rec.matched_items} items matched perfectly
          </h3>
          <p style={{ color: 'var(--text-muted)' }}>
            These items had matching quantities between system and source data.
          </p>
        </div>
      )}
    </>
  );
}

function StatCard({ label, value, color, accent = false }: {
  label: string;
  value: string | number;
  color: string;
  accent?: boolean;
}) {
  return (
    <div style={{
      background: accent ? `${color}15` : 'var(--surface)',
      borderRadius: 'var(--radius-lg)',
      padding: '1.25rem',
      boxShadow: accent ? `0 0 20px ${color}20` : 'var(--shadow-sm)',
      border: `1px solid ${accent ? `${color}30` : 'var(--border-light)'}`,
    }}>
      <p style={{
        fontSize: '0.75rem',
        color: accent ? color : 'var(--text-muted)',
        marginBottom: '0.4rem',
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: '0.04em',
      }}>{label}</p>
      <p style={{
        fontSize: '1.75rem',
        fontWeight: 800,
        color: accent ? color : 'var(--text-primary)',
        margin: 0,
        letterSpacing: '-0.02em',
        lineHeight: 1.1,
      }}>
        {typeof value === 'string' ? value.charAt(0).toUpperCase() + value.slice(1) : value}
      </p>
    </div>
  );
}
