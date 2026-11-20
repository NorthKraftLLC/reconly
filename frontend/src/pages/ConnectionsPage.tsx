import React, { useState, useEffect } from 'react';
import api from '../services/api';

type ConnectorType = { type: string; name: string; description: string };
type ConnectionRole = 'supplier' | 'pos' | 'store' | 'warehouse' | 'erp' | 'marketplace' | 'custom';
type Connection = {
    id: string;
    name: string;
    connection_type: string;
    role: string;
    company_id: string;
    is_active: boolean;
    last_sync_at: string | null;
    last_sync_status: string | null;
    items_count: number | null;
    created_at: string;
};
type SyncResult = {
    sync_id: string;
    status: string;
    items_fetched: number;
    items_imported: number;
    items_updated: number;
    items_failed: number;
    error: string | null;
};

const ROLES: { value: ConnectionRole; label: string; desc: string }[] = [
    { value: 'supplier', label: 'Supplier', desc: 'External supplier inventory feed' },
    { value: 'pos', label: 'Point of Sale', desc: 'Square, Clover, Toast, etc.' },
    { value: 'store', label: 'Store', desc: 'Physical/online store inventory' },
    { value: 'warehouse', label: 'Warehouse', desc: 'WMS system' },
    { value: 'erp', label: 'ERP', desc: 'QuickBooks, NetSuite, SAP' },
    { value: 'marketplace', label: 'Marketplace', desc: 'Amazon, Walmart, eBay' },
    { value: 'custom', label: 'Custom', desc: 'Other data source' },
];

export default function ConnectionsPage() {
    const [connections, setConnections] = useState<Connection[]>([]);
    const [types, setTypes] = useState<ConnectorType[]>([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [syncing, setSyncing] = useState<Record<string, boolean>>({});
    const [result, setResult] = useState<SyncResult | null>(null);
    const [error, setError] = useState('');
    const [testing, setTesting] = useState<string | null>(null);
    const [testResult, setTestResult] = useState<{ ok: boolean; message: string } | null>(null);
    const [testConnId, setTestConnId] = useState<string | null>(null);

    // Form state
    const [formName, setFormName] = useState('');
    const [formType, setFormType] = useState('csv_import');
    const [formRole, setFormRole] = useState<ConnectionRole>('supplier');
    const [formCompanyId, setFormCompanyId] = useState('');
    const [formCredentials, setFormCredentials] = useState('{}');
    const [formConfig, setFormConfig] = useState('{}');
    const [csvFile, setCsvFile] = useState<File | null>(null);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [connsRes, typesRes] = await Promise.all([
                api.get('/integrations/'),
                api.get('/integrations/types'),
            ]);
            setConnections(connsRes.data);
            setTypes(typesRes.data.types);
        } catch (e: any) {
            setError(e.response?.data?.detail || 'Failed to load connections');
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        try {
            const formData = new FormData();
            formData.append('name', formName);
            formData.append('connection_type', formType);
            formData.append('role', formRole);
            formData.append('company_id', formCompanyId);
            formData.append('credentials', formCredentials);
            formData.append('config', formConfig);

            const createRes = await api.post('/integrations/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });

            setShowForm(false);
            resetForm();
            await loadData();

            // If CSV type and file selected, upload it to the new connection
            if (formType === 'csv_import' && csvFile) {
                const newConnId = createRes.data.id;
                const uploadFormData = new FormData();
                uploadFormData.append('file', csvFile);
                const uploadRes = await api.post(`/integrations/${newConnId}/upload-csv`, uploadFormData, {
                    headers: { 'Content-Type': 'multipart/form-data' },
                });
                alert(`CSV uploaded: ${uploadRes.data.items_parsed} items parsed`);
            }
        } catch (e: any) {
            setError(e.response?.data?.detail || 'Failed to create connection');
        }
    };

    const handleSync = async (id: string) => {
        setSyncing(prev => ({ ...prev, [id]: true }));
        setResult(null);
        setError('');
        try {
            const res = await api.post(`/integrations/${id}/sync`);
            setResult(res.data);
        } catch (e: any) {
            setError(e.response?.data?.detail || 'Sync failed');
        } finally {
            setSyncing(prev => ({ ...prev, [id]: false }));
        }
    };

    const handleTest = async (id: string) => {
        setTesting(id);
        setTestResult(null);
        setError('');
        try {
            const res = await api.post(`/integrations/${id}/test`);
            setTestConnId(id);
            setTestResult(res.data);
        } catch (e: any) {
            setError(e.response?.data?.detail || 'Test failed');
        } finally {
            setTesting(null);
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm('Delete this connection? This cannot be undone.')) return;
        try {
            await api.delete(`/integrations/${id}`);
            await loadData();
        } catch (e: any) {
            setError(e.response?.data?.detail || 'Delete failed');
        }
    };

    const handleCsvUpload = async (e: React.ChangeEvent<HTMLInputElement>, connId: string) => {
        const file = e.target.files?.[0];
        if (!file) return;
        setError('');
        try {
            const formData = new FormData();
            formData.append('file', file);
            const res = await api.post(`/integrations/${connId}/upload-csv`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            alert(`CSV uploaded: ${res.data.items_parsed} items parsed`);
            await loadData();
        } catch (err: any) {
            setError(err.response?.data?.detail || 'CSV upload failed');
        }
    };

    const resetForm = () => {
        setFormName('');
        setFormType('csv_import');
        setFormRole('supplier');
        setFormCompanyId('');
        setFormCredentials('{}');
        setFormConfig('{}');
        setCsvFile(null);
    };

    const statusColor = (status: string | null) => {
        switch (status) {
            case 'success': return '#22c55e';
            case 'failed': return '#ef4444';
            case 'in_progress': return '#f59e0b';
            case 'partial': return '#a855f7';
            default: '#64748b';
        }
    };

    if (loading) return <div className="spinner-center">Loading connections...</div>;

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#FFFFFF', margin: 0 }}>Data Connections</h1>
                    <p style={{ color: '#8A9BB0', margin: '0.5rem 0 0', fontSize: '0.9rem' }}>
                        Connect suppliers, POS systems, stores, and marketplaces to sync inventory automatically
                    </p>
                </div>
                <button
                    onClick={() => setShowForm(!showForm)}
                    style={{
                        padding: '0.7rem 1.5rem',
                        background: 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '10px',
                        fontSize: '0.9rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        boxShadow: '0 4px 16px rgba(37, 99, 235, 0.3)',
                    }}
                >
                    {showForm ? 'Cancel' : '+ Add Connection'}
                </button>
            </div>

            {error && (
                <div style={{
                    background: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid rgba(239, 68, 68, 0.2)',
                    color: '#FCA5A5',
                    padding: '0.75rem 1rem',
                    borderRadius: '10px',
                    marginBottom: '1.25rem',
                    fontSize: '0.85rem',
                }}>
                    {error}
                </div>
            )}

            {result && (
                <div style={{
                    background: result.status === 'success' ? 'rgba(34, 197, 94, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                    border: `1px solid ${result.status === 'success' ? 'rgba(34, 197, 94, 0.2)' : 'rgba(245, 158, 11, 0.2)'}`,
                    color: result.status === 'success' ? '#86EFAC' : '#FCD34D',
                    padding: '1rem',
                    borderRadius: '10px',
                    marginBottom: '1.25rem',
                    fontSize: '0.85rem',
                }}>
                    <strong>Sync Result:</strong> Status: {result.status} | Fetched: {result.items_fetched} | Imported: {result.items_imported} | Updated: {result.items_updated} | Failed: {result.items_failed}
                    {result.error && <div style={{ marginTop: '0.5rem' }}>Error: {result.error}</div>}
                </div>
            )}

            {testResult && testConnId && (
                <div style={{
                    background: testResult.ok ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                    border: `1px solid ${testResult.ok ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)'}`,
                    color: testResult.ok ? '#86EFAC' : '#FCA5A5',
                    padding: '0.75rem 1rem',
                    borderRadius: '10px',
                    marginBottom: '1.25rem',
                    fontSize: '0.85rem',
                }}>
                    <strong>Test Connection:</strong> {testResult.ok ? '✅' : '❌'} {testResult.message}
                </div>
            )}

            {/* Create Connection Form */}
            {showForm && (
                <div style={{
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: '16px',
                    padding: '2rem',
                    marginBottom: '2rem',
                }}>
                    <h3 style={{ color: '#FFFFFF', margin: '0 0 1.5rem', fontSize: '1.1rem' }}>New Connection</h3>
                    <form onSubmit={handleCreate}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                            <div>
                                <label style={labelStyle}>Connection Name</label>
                                <input
                                    required
                                    value={formName}
                                    onChange={e => setFormName(e.target.value)}
                                    placeholder="e.g., Amazon Warehouse East"
                                    style={inputStyle}
                                />
                            </div>
                            <div>
                                <label style={labelStyle}>Company ID</label>
                                <input
                                    required
                                    value={formCompanyId}
                                    onChange={e => setFormCompanyId(e.target.value)}
                                    placeholder="UUID of the company"
                                    style={inputStyle}
                                />
                            </div>
                            <div>
                                <label style={labelStyle}>Integration Type</label>
                                <select value={formType} onChange={e => setFormType(e.target.value)} style={inputStyle}>
                                    {types.map(t => (
                                        <option key={t.type} value={t.type}>{t.name}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label style={labelStyle}>Role</label>
                                <select value={formRole} onChange={e => setFormRole(e.target.value as ConnectionRole)} style={inputStyle}>
                                    {ROLES.map(r => (
                                        <option key={r.value} value={r.value}>{r.label} — {r.desc}</option>
                                    ))}
                                </select>
                            </div>
                        </div>
                        <div style={{ marginBottom: '1rem' }}>
                            <label style={labelStyle}>Credentials (JSON) — API keys, tokens, URLs</label>
                            <textarea
                                value={formCredentials}
                                onChange={e => setFormCredentials(e.target.value)}
                                placeholder={formType === 'shopify' ? '{"shop": "mystore.myshopify.com", "access_token": "shpat_..."}' :
                                    formType === 'square' ? '{"access_token": "sq0atp-...", "location_id": "..."}' :
                                    formType === 'quickbooks' ? '{"access_token": "...", "realm_id": "..."}' :
                                    formType === 'woocommerce' ? '{"store_url": "https://mystore.com", "consumer_key": "...", "consumer_secret": "..."}' :
                                    formType === 'custom_api' ? '{"api_url": "https://api.supplier.com/inventory", "auth_token": "..."}' :
                                    '{}'}
                                rows={3}
                                style={{ ...inputStyle, fontFamily: 'monospace', fontSize: '0.8rem' }}
                            />
                        </div>
                        <div style={{ marginBottom: '1.5rem' }}>
                            <label style={labelStyle}>Config (JSON) — Optional settings</label>
                            <textarea
                                value={formConfig}
                                onChange={e => setFormConfig(e.target.value)}
                                placeholder='{"sync_interval": "daily", "mappings": {...}}'
                                rows={2}
                                style={{ ...inputStyle, fontFamily: 'monospace', fontSize: '0.8rem' }}
                            />
                        </div>
                        {formType === 'csv_import' && (
                            <div style={{ marginBottom: '1.5rem' }}>
                                <label style={labelStyle}>Or upload CSV now (optional)</label>
                                <input type="file" accept=".csv" onChange={e => setCsvFile(e.target.files?.[0] || null)} style={{ ...inputStyle, padding: '0.5rem' }} />
                            </div>
                        )}
                        <button type="submit" style={btnPrimary}>Create Connection</button>
                    </form>
                </div>
            )}

            {/* Connections Grid */}
            {connections.length === 0 ? (
                <div style={{
                    textAlign: 'center',
                    padding: '4rem 2rem',
                    color: '#8A9BB0',
                }}>
                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔗</div>
                    <h3 style={{ color: '#FFFFFF', margin: '0 0 0.5rem' }}>No connections yet</h3>
                    <p style={{ margin: 0, fontSize: '0.9rem' }}>Add your first data source to start syncing inventory automatically.</p>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: '1.25rem' }}>
                    {connections.map(conn => (
                        <div key={conn.id} style={{
                            background: 'rgba(255, 255, 255, 0.03)',
                            border: '1px solid rgba(255, 255, 255, 0.08)',
                            borderRadius: '14px',
                            padding: '1.5rem',
                            transition: 'border-color 150ms',
                        }}
                            onMouseEnter={e => (e.currentTarget.style.borderColor = 'rgba(37, 99, 235, 0.3)')}
                            onMouseLeave={e => (e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.08)')}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                                <div>
                                    <h3 style={{ color: '#FFFFFF', margin: 0, fontSize: '1.05rem' }}>{conn.name}</h3>
                                    <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.4rem' }}>
                                        <span style={{
                                            background: 'rgba(37, 99, 235, 0.15)',
                                            color: '#60A5FA',
                                            padding: '0.2rem 0.6rem',
                                            borderRadius: '6px',
                                            fontSize: '0.7rem',
                                            fontWeight: 600,
                                            textTransform: 'uppercase',
                                        }}>{conn.connection_type.replace('_', ' ')}</span>
                                        <span style={{
                                            background: 'rgba(245, 158, 11, 0.15)',
                                            color: '#FCD34D',
                                            padding: '0.2rem 0.6rem',
                                            borderRadius: '6px',
                                            fontSize: '0.7rem',
                                            fontWeight: 600,
                                            textTransform: 'uppercase',
                                        }}>{conn.role}</span>
                                    </div>
                                </div>
                                <div style={{
                                    width: '10px',
                                    height: '10px',
                                    borderRadius: '50%',
                                    background: statusColor(conn.last_sync_status),
                                    boxShadow: `0 0 8px ${statusColor(conn.last_sync_status)}40`,
                                }} title={`Last sync: ${conn.last_sync_status || 'never'}`} />
                            </div>

                            <div style={{ fontSize: '0.8rem', color: '#8A9BB0', marginBottom: '1rem' }}>
                                {conn.items_count !== null && <div>Items: <strong style={{ color: '#C8D6E5' }}>{conn.items_count}</strong></div>}
                                {conn.last_sync_at && <div>Last sync: <strong style={{ color: '#C8D6E5' }}>{new Date(conn.last_sync_at).toLocaleString()}</strong></div>}
                            </div>

                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                <button
                                    onClick={() => handleSync(conn.id)}
                                    disabled={syncing[conn.id]}
                                    style={{
                                        ...btnSmall,
                                        background: syncing[conn.id] ? 'rgba(37, 99, 235, 0.3)' : 'rgba(37, 99, 235, 0.2)',
                                        cursor: syncing[conn.id] ? 'not-allowed' : 'pointer',
                                    }}
                                >
                                    {syncing[conn.id] ? '⏳ Syncing...' : '⟳ Sync'}
                                </button>
                                <button
                                    onClick={() => handleTest(conn.id)}
                                    disabled={testing === conn.id}
                                    style={{
                                        ...btnSmall,
                                        background: 'rgba(34, 197, 94, 0.2)',
                                        color: '#86EFAC',
                                        cursor: testing === conn.id ? 'not-allowed' : 'pointer',
                                    }}
                                >
                                    {testing === conn.id ? 'Testing...' : '⚡ Test'}
                                </button>
                                {conn.connection_type === 'csv_import' && (
                                    <label style={{ ...btnSmall, background: 'rgba(168, 85, 247, 0.2)', color: '#C084FC', cursor: 'pointer' }}>
                                        📄 CSV
                                        <input type="file" accept=".csv" hidden onChange={e => handleCsvUpload(e, conn.id)} />
                                    </label>
                                )}
                                <button
                                    onClick={() => handleDelete(conn.id)}
                                    style={{ ...btnSmall, background: 'rgba(239, 68, 68, 0.15)', color: '#FCA5A5', marginLeft: 'auto' }}
                                >
                                    ✕
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

const labelStyle: React.CSSProperties = {
    display: 'block',
    fontSize: '0.8rem',
    fontWeight: 500,
    color: '#C8D6E5',
    marginBottom: '0.4rem',
};

const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '0.7rem 1rem',
    borderRadius: '10px',
    border: '1.5px solid rgba(255, 255, 255, 0.1)',
    background: 'rgba(255, 255, 255, 0.04)',
    color: '#FFFFFF',
    fontSize: '0.85rem',
    outline: 'none',
    boxSizing: 'border-box',
};

const btnPrimary: React.CSSProperties = {
    padding: '0.7rem 1.5rem',
    background: 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)',
    color: '#fff',
    border: 'none',
    borderRadius: '10px',
    fontSize: '0.9rem',
    fontWeight: 600,
    cursor: 'pointer',
    boxShadow: '0 4px 16px rgba(37, 99, 235, 0.3)',
};

const btnSmall: React.CSSProperties = {
    padding: '0.4rem 0.8rem',
    border: 'none',
    borderRadius: '8px',
    fontSize: '0.75rem',
    fontWeight: 600,
    color: '#60A5FA',
    transition: 'all 150ms',
};
