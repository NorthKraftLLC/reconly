import { useState, useEffect } from 'react';
import Header from '../components/Header';
import api from '../services/api';

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<any[]>([]);
  const [name, setName] = useState('');
  const [industry, setIndustry] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState('');

  const fetch = async () => {
    const res = await api.get('/companies/');
    setCompanies(res.data);
    setLoading(false);
  };

  useEffect(() => { fetch(); }, []);

  const addCompany = async () => {
    if (!name.trim()) return;
    setSaving(true);
    setFeedback('');
    try {
      await api.post('/companies/', { name: name.trim(), industry: industry.trim() || undefined });
      setName('');
      setIndustry('');
      setFeedback('Company added successfully');
      fetch();
      setTimeout(() => setFeedback(''), 3000);
    } catch {
      setFeedback('Failed to add company');
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <Header title="Companies" />

      {/* Add Company Form */}
      <div className="card mb-lg" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-end' }}>
          <div style={{ flex: 1 }}>
            <label style={{
              display: 'block',
              fontSize: '0.75rem',
              fontWeight: 600,
              color: 'var(--text-muted)',
              marginBottom: '0.35rem',
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
            }}>Company Name</label>
            <input
              placeholder="Acme Corp"
              value={name}
              onChange={(e) => setName(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && addCompany()}
            />
          </div>
          <div style={{ flex: 1 }}>
            <label style={{
              display: 'block',
              fontSize: '0.75rem',
              fontWeight: 600,
              color: 'var(--text-muted)',
              marginBottom: '0.35rem',
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
            }}>Industry <span style={{ fontWeight: 400, textTransform: 'none' }}>(optional)</span></label>
            <input
              placeholder="Retail, Manufacturing, etc."
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
            />
          </div>
          <button
            className="btn-primary"
            onClick={addCompany}
            disabled={saving || !name.trim()}
            style={{ minWidth: '140px', opacity: saving || !name.trim() ? 0.6 : 1 }}
          >
            {saving ? 'Adding...' : '+ Add Company'}
          </button>
        </div>
        {feedback && (
          <div style={{
            marginTop: '0.75rem',
            padding: '0.6rem 0.85rem',
            borderRadius: '8px',
            fontSize: '0.85rem',
            background: feedback.includes('success') ? 'var(--success-bg)' : 'var(--danger-bg)',
            color: feedback.includes('success') ? 'var(--turquoise-dark)' : 'var(--danger)',
          }}>
            {feedback}
          </div>
        )}
      </div>

      {/* Companies List */}
      {loading ? (
        <div style={{ display: 'grid', gap: '0.75rem' }}>
          {[1, 2, 3].map((i) => (
            <div key={i} className="card" style={{ height: '60px' }}>
              <div className="loading-shimmer" style={{ width: '60%', height: '18px', marginBottom: '8px' }} />
              <div className="loading-shimmer" style={{ width: '40%', height: '14px' }} />
            </div>
          ))}
        </div>
      ) : companies.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">◈</div>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>No companies yet</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Add your first company above to start tracking inventory.
          </p>
        </div>
      ) : (
        <div className="table-wrapper" style={{ overflowX: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th>Company</th>
                <th>Slug</th>
                <th>Industry</th>
                <th style={{ textAlign: 'right' }}>Created</th>
              </tr>
            </thead>
            <tbody>
              {companies.map((c) => (
                <tr key={c.id}>
                  <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{c.name}</td>
                  <td>
                    <code style={{
                      background: 'var(--bg)',
                      padding: '0.15rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.8rem',
                      fontFamily: 'SF Mono, Fira Code, monospace',
                    }}>{c.slug}</code>
                  </td>
                  <td>{c.industry || <span className="text-muted">—</span>}</td>
                  <td style={{ textAlign: 'right', fontSize: '0.85rem' }}>
                    {c.created_at ? new Date(c.created_at).toLocaleDateString() : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
