import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import api from '../services/api';

export default function ReconciliationPage() {
  const navigate = useNavigate();
  const [reconciliations, setReconciliations] = useState<any[]>([]);
  const [companies, setCompanies] = useState<any[]>([]);
  const [selectedCompany, setSelectedCompany] = useState('');
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [modalName, setModalName] = useState('');
  const [modalJson, setModalJson] = useState('');
  const [modalError, setModalError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    (async () => {
      const [compRes, recRes] = await Promise.all([
        api.get('/companies/'),
        api.get('/reconciliations/', { params: { company_id: selectedCompany || '00000000-0000-0000-0000-000000000000' } }),
      ]);
      setCompanies(compRes.data);
      setReconciliations(recRes.data);
      if (compRes.data.length > 0) setSelectedCompany(compRes.data[0].id);
      setLoading(false);
    })();
  }, [selectedCompany]);

  const createReconciliation = async () => {
    if (!selectedCompany || !modalName.trim()) {
      setModalError('Please fill in a name and select a company.');
      return;
    }
    setModalError('');
    setSubmitting(true);
    try {
      let sourceData;
      if (modalJson.trim()) {
        sourceData = JSON.parse(modalJson);
      } else {
        sourceData = { system: [], source: [] };
      }
      const res = await api.post('/reconciliations/', {
        company_id: selectedCompany,
        name: modalName.trim(),
        source_data: sourceData,
      });
      setShowModal(false);
      setModalName('');
      setModalJson('');
      navigate(`/reconciliations/${res.data.id}`);
    } catch (err: any) {
      setModalError(err.response?.data?.detail || 'Failed to create reconciliation. Check your JSON format.');
    } finally {
      setSubmitting(false);
    }
  };

  const formatStatus = (status: string) => {
    return status.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  };

  const statusBadge = (status: string) => {
    switch (status) {
      case 'completed': return 'badge-success';
      case 'in_progress': return 'badge-warning';
      case 'failed': return 'badge-danger';
      default: return 'badge-neutral';
    }
  };

  return (
    <>
      <Header
        title="Reconciliations"
        actions={
          <button className="btn-accent" onClick={() => setShowModal(true)}>
            + New Reconciliation
          </button>
        }
      />

      {/* Company Filter */}
      <div style={{ marginBottom: '1.5rem' }}>
        <select
          value={selectedCompany}
          onChange={(e) => setSelectedCompany(e.target.value)}
          style={{ maxWidth: '320px' }}
        >
          <option value="">All companies</option>
          {companies.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
      </div>

      {/* Reconciliations List */}
      {loading ? (
        <div style={{ display: 'grid', gap: '0.75rem' }}>
          {[1, 2, 3].map((i) => (
            <div key={i} className="card" style={{ height: '80px' }}>
              <div className="loading-shimmer" style={{ width: '50%', height: '18px', marginBottom: '8px' }} />
              <div className="loading-shimmer" style={{ width: '80%', height: '14px' }} />
            </div>
          ))}
        </div>
      ) : reconciliations.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">⬡</div>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>No reconciliations yet</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
            Create your first reconciliation to compare system inventory against source data.
          </p>
          <button className="btn-accent" onClick={() => setShowModal(true)}>
            + New Reconciliation
          </button>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '0.75rem' }}>
          {reconciliations.map((r) => (
            <div
              key={r.id}
              onClick={() => navigate(`/reconciliations/${r.id}`)}
              className="card card-hover"
              style={{ cursor: 'pointer' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ flex: 1 }}>
                  <h3 style={{ fontSize: '1.05rem', marginBottom: '0.35rem' }}>{r.name}</h3>
                  <div style={{ display: 'flex', gap: '1.25rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    <span>{r.total_items} items</span>
                    <span style={{ color: 'var(--turquoise-dark)' }}>{r.matched_items} matched</span>
                    <span style={{ color: r.discrepancies_found > 0 ? 'var(--orange)' : 'var(--text-muted)' }}>
                      {r.discrepancies_found} discrepancies
                    </span>
                    <span>{r.created_at ? new Date(r.created_at).toLocaleDateString() : ''}</span>
                  </div>
                </div>
                <span className={`badge ${statusBadge(r.status)}`}>
                  {formatStatus(r.status)}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={(e) => { if (e.target === e.currentTarget) setShowModal(false); }}>
          <div className="modal-content">
            <div className="modal-header">
              <h3>New Reconciliation</h3>
              <button className="modal-close" onClick={() => setShowModal(false)}>✕</button>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Company
              </label>
              <select
                value={selectedCompany}
                onChange={(e) => setSelectedCompany(e.target.value)}
              >
                <option value="">Select company...</option>
                {companies.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Reconciliation Name
              </label>
              <input
                placeholder={'Reconciliation ' + new Date().toLocaleDateString()}
                value={modalName}
                onChange={(e) => setModalName(e.target.value)}
              />
            </div>

            <div style={{ marginBottom: '1.25rem' }}>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Source Data <span style={{ fontWeight: 400, textTransform: 'none' }}>{'(JSON — optional)'}</span>
              </label>
              <textarea
                placeholder='{"system": [{"sku": "A", "name": "Item A", "qty": 10, "cost": 5.00}], "source": [{"sku": "A", "name": "Item A", "qty": 8, "cost": 5.00}]}'
                value={modalJson}
                onChange={(e) => setModalJson(e.target.value)}
                rows={6}
                style={{
                  fontFamily: 'SF Mono, Fira Code, monospace',
                  fontSize: '0.8rem',
                  width: '100%',
                  padding: '0.75rem 1rem',
                  borderRadius: 'var(--radius-md)',
                  border: '1.5px solid var(--border)',
                  color: 'var(--text-primary)',
                  outline: 'none',
                  resize: 'vertical',
                  background: 'var(--bg-warm)',
                }}
              />
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>
                Paste JSON with <code style={{ background: 'var(--bg)', padding: '1px 4px', borderRadius: '3px' }}>system</code> and <code style={{ background: 'var(--bg)', padding: '1px 4px', borderRadius: '3px' }}>source</code> arrays. Each needs <code style={{ background: 'var(--bg)', padding: '1px 4px', borderRadius: '3px' }}>sku</code>, <code style={{ background: 'var(--bg)', padding: '1px 4px', borderRadius: '3px' }}>name</code>, <code style={{ background: 'var(--bg)', padding: '1px 4px', borderRadius: '3px' }}>qty</code>, <code style={{ background: 'var(--bg)', padding: '1px 4px', borderRadius: '3px' }}>cost</code>.
              </p>
            </div>

            {modalError && (
              <div style={{
                background: 'var(--danger-bg)',
                border: '1px solid rgba(239, 68, 68, 0.2)',
                color: 'var(--danger)',
                padding: '0.65rem 0.85rem',
                borderRadius: '8px',
                marginBottom: '1rem',
                fontSize: '0.85rem',
              }}>
                {modalError}
              </div>
            )}

            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
              <button className="btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
              <button
                className="btn-accent"
                onClick={createReconciliation}
                disabled={submitting}
                style={{ opacity: submitting ? 0.6 : 1 }}
              >
                {submitting ? 'Creating...' : 'Run Reconciliation'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
