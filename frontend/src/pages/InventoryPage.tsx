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
  const [showBulk, setShowBulk] = useState(false);
  const [saving, setSaving] = useState(false);
  const [bulkLoading, setBulkLoading] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [bulkCsv, setBulkCsv] = useState('');

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

  const bulkUpload = async () => {
    if (!bulkCsv.trim()) return;
    setBulkLoading(true);
    setFeedback('');
    try {
      const lines = bulkCsv.trim().split('\n').map(l => l.trim()).filter(Boolean);
      if (lines.length < 2) throw new Error('CSV needs a header row and at least one data row');
      const headers = lines[0].split(',').map(h => h.trim().toLowerCase().replace(/[^a-z_]/g, ''));
      const items = lines.slice(1).map(line => {
        const vals = line.split(',').map(v => v.trim());
        const obj: any = {};
        headers.forEach((h, i) => {
          if (h === 'sku') obj.sku = vals[i];
          else if (h === 'name') obj.name = vals[i];
          else if (h === 'quantity' || h === 'quantity_on_hand') obj.quantity_on_hand = parseInt(vals[i]) || 0;
          else if (h === 'price' || h === 'unit_cost') obj.unit_cost = parseFloat(vals[i]) || 0;
          else if (h === 'category') obj.category = vals[i];
        });
        return obj;
      }).filter(i => i.sku && i.name);
      const res = await api.post(`/inventory/bulk?company_id=${selectedCompany}`, items);
      setFeedback(`Bulk upload complete: ${res.data?.length || items.length} items imported`);
      setBulkCsv('');
      setShowBulk(false);
      fetchItems();
      setTimeout(() => setFeedback(''), 5000);
    } catch (err: any) {
      const detail = err?.response?.data?.detail || err?.message || 'Bulk upload failed';
      setFeedback(Array.isArray(detail) ? detail.map((d: any) => d.msg || d).join(' ') : detail);
    } finally {
      setBulkLoading(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => setBulkCsv(ev.target?.result as string);
    reader.readAsText(file);
  };

  return (
    <>
      <Header
        title="Inventory"
        actions={
          selectedCompany && (
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button className="btn-secondary" onClick={() => setShowBulk(!showBulk)} style={{ whiteSpace: 'nowrap' }}>
                📦 Bulk Upload
              </button>
              <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
                {showForm ? 'Cancel' : '+ Add Item'}
              </button>
            </div>
          )
        }
      />

      {/* Feedback Banner */}
      {feedback && (
        <div style={{
          padding: '0.75rem 1rem', marginBottom: '1rem', borderRadius: '8px',
          background: feedback.includes('complete') || feedback.includes('success') ? 'rgba(13, 204, 175, 0.1)' : 'rgba(239, 68, 68, 0.1)',
          border: `1px solid ${feedback.includes('complete') || feedback.includes('success') ? 'var(--turquoise-dark)' : 'var(--danger)'}`,
          color: feedback.includes('complete') || feedback.includes('success') ? 'var(--turquoise-dark)' : 'var(--danger)',
          fontSize: '0.85rem', fontWeight: 600,
        }}>{feedback}</div>
      )}

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

      {/* Bulk Upload Modal */}
      {showBulk && selectedCompany && (
        <div className="card mb-lg" style={{ padding: '1.25rem', border: '1px solid var(--turquoise-dark)' }}>
          <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>📦 Bulk Upload Inventory</h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
            Paste CSV data or upload a .csv file. Format: <code style={{ fontSize: '0.75rem' }}>sku,name,quantity,price[,category]</code>
          </p>
          <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem', alignItems: 'center' }}>
            <label className="btn-secondary" style={{ cursor: 'pointer', display: 'inline-block', padding: '0.5rem 1rem', fontSize: '0.85rem' }}>
              📁 Choose CSV File
              <input type="file" accept=".csv,.txt" onChange={handleFileUpload} style={{ display: 'none' }} />
            </label>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>or paste below</span>
          </div>
          <textarea
            placeholder={"sku,name,quantity,price,category\nWDG-001,Widget Alpha,500,12.99,Widgets\nWDG-002,Widget Beta,300,8.49,Widgets"}
            value={bulkCsv}
            onChange={(e) => setBulkCsv(e.target.value)}
            style={{
              width: '100%', minHeight: '150px', fontFamily: 'SF Mono, Fira Code, monospace',
              fontSize: '0.8rem', padding: '0.75rem', marginBottom: '0.75rem', resize: 'vertical',
              background: 'var(--bg)', color: 'var(--text-primary)', borderRadius: '8px',
              border: '1px solid var(--card-border)',
            }}
          />
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <button className="btn-primary" onClick={bulkUpload} disabled={bulkLoading || !bulkCsv.trim()}>
              {bulkLoading ? 'Uploading...' : 'Upload'}
            </button>
            <button className="btn-secondary" onClick={() => { setShowBulk(false); setBulkCsv(''); }}>Cancel</button>
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
