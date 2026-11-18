import { useState, useEffect } from 'react';
import Header from '../components/Header';
import api from '../services/api';

export default function InventoryPage() {
  const [items, setItems] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [companies, setCompanies] = useState<any[]>([]);
  const [selectedCompany, setSelectedCompany] = useState('');
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState('');
  const [sku, setSku] = useState('');
  const [qty, setQty] = useState('');
  const [cost, setCost] = useState('');
  const [category, setCategory] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState('');

  const fetchCompanies = async () => {
    const res = await api.get('/companies/');
    setCompanies(res.data);
    if (res.data.length > 0) setSelectedCompany(res.data[0].id);
  };

  const fetchItems = async () => {
    if (!selectedCompany) return;
    setLoading(true);
    const res = await api.get('/inventory/', { params: { company_id: selectedCompany, search: search || undefined } });
    setItems(res.data);
    setLoading(false);
  };

  useEffect(() => { fetchCompanies(); }, []);
  useEffect(() => { fetchItems(); }, [selectedCompany, search]);

  const addItem = async () => {
    if (!name.trim() || !sku.trim()) return;
    setSaving(true);
    setFeedback('');
    try {
      await api.post('/inventory/', {
        company_id: selectedCompany,
        name: name.trim(),
        sku: sku.trim(),
        quantity_on_hand: parseInt(qty) || 0,
        unit_cost: parseFloat(cost) || 0,
        category: category.trim() || undefined,
      });
      setName(''); setSku(''); setQty(''); setCost(''); setCategory('');
      setShowForm(false);
      setFeedback('Item added successfully');
      fetchItems();
      setTimeout(() => setFeedback(''), 3000);
    } catch {
      setFeedback('Failed to add item');
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <Header
        title="Inventory"
        actions={
          selectedCompany && (
            <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
              {showForm ? 'Cancel' : '+ Add Item'}
            </button>
          )
        }
      />

      {/* Company Selector */}
      <div style={{ marginBottom: '1.25rem' }}>
        <select
          value={selectedCompany}
          onChange={(e) => setSelectedCompany(e.target.value)}
          style={{ maxWidth: '320px' }}
        >
          <option value="">Select a company...</option>
          {companies.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
      </div>

      {/* Add Item Form */}
      {showForm && selectedCompany && (
        <div className="card mb-lg" style={{ padding: '1.25rem' }}>
          <h3 style={{ fontSize: '1rem', marginBottom: '1rem' }}>New Inventory Item</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.3rem' }}>SKU *</label>
              <input placeholder="SKU-001" value={sku} onChange={(e) => setSku(e.target.value)} />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.3rem' }}>Name *</label>
              <input placeholder="Widget A" value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.3rem' }}>Qty on Hand</label>
              <input type="number" placeholder="0" value={qty} onChange={(e) => setQty(e.target.value)} />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.3rem' }}>Unit Cost ($)</label>
              <input type="number" step="0.01" placeholder="0.00" value={cost} onChange={(e) => setCost(e.target.value)} />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.3rem' }}>Category</label>
              <input placeholder="Electronics" value={category} onChange={(e) => setCategory(e.target.value)} />
            </div>
          </div>
          <div style={{ marginTop: '1rem', display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <button className="btn-primary" onClick={addItem} disabled={saving || !name.trim() || !sku.trim()}>
              {saving ? 'Adding...' : 'Add Item'}
            </button>
            {feedback && (
              <span style={{
                fontSize: '0.85rem',
                color: feedback.includes('success') ? 'var(--turquoise-dark)' : 'var(--danger)',
              }}>{feedback}</span>
            )}
          </div>
        </div>
      )}

      {/* Search */}
      {selectedCompany && (
        <div style={{ marginBottom: '1rem' }}>
          <input
            placeholder="Search by name or SKU..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ maxWidth: '320px' }}
          />
        </div>
      )}

      {/* Items Table */}
      {loading ? (
        <div className="table-wrapper">
          <div style={{ padding: '2rem', textAlign: 'center' }}>
            <div className="spinner" style={{ margin: '0 auto' }} />
          </div>
        </div>
      ) : !selectedCompany ? (
        <div className="empty-state">
          <div className="empty-state-icon">▪</div>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Select a company</h3>
          <p style={{ color: 'var(--text-muted)' }}>Choose a company above to view its inventory.</p>
        </div>
      ) : items.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">▪</div>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>No inventory items</h3>
          <p style={{ color: 'var(--text-muted)' }}>
            {search ? 'No items match your search.' : 'Add your first item to start tracking inventory.'}
          </p>
        </div>
      ) : (
        <div className="table-wrapper" style={{ overflowX: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th>SKU</th>
                <th>Name</th>
                <th style={{ textAlign: 'right' }}>Qty on Hand</th>
                <th style={{ textAlign: 'right' }}>Unit Cost</th>
                <th style={{ textAlign: 'right' }}>Total Value</th>
                <th>Category</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td>
                    <code style={{
                      background: 'var(--bg)',
                      padding: '0.15rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.8rem',
                      fontFamily: 'SF Mono, Fira Code, monospace',
                      color: 'var(--text-secondary)',
                    }}>{item.sku}</code>
                  </td>
                  <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{item.name}</td>
                  <td style={{ textAlign: 'right', fontWeight: 600 }}>{item.quantity_on_hand}</td>
                  <td style={{ textAlign: 'right' }}>${Number(item.unit_cost).toFixed(2)}</td>
                  <td style={{ textAlign: 'right', fontWeight: 600, color: 'var(--text-primary)' }}>
                    ${(Number(item.unit_cost) * item.quantity_on_hand).toFixed(2)}
                  </td>
                  <td>
                    {item.category ? (
                      <span className="badge badge-neutral">{item.category}</span>
                    ) : <span className="text-muted">—</span>}
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
