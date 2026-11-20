"""PostgreSQL Row-Level Security policies for tenant isolation.

Even if application code has a bug, RLS policies at the database level
ensure no user can ever access another tenant's data.
"""

from sqlalchemy import text


RLS_POLICIES_SQL = """
-- ============================================================
-- PostgreSQL Row-Level Security (RLS) for Tenant Isolation
-- ============================================================
-- The session variable 'app.current_user_id' is set by the app
-- on every authenticated request. All RLS policies reference it.
-- ============================================================

-- Users can only see their own row
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS users_own_row ON users;
CREATE POLICY users_own_row ON users
    USING (id::text = current_setting('app.current_user_id', true));

-- Companies: users can only see their own companies
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS companies_by_owner ON companies;
CREATE POLICY companies_by_owner ON companies
    USING (owner_id::text = current_setting('app.current_user_id', true));

-- Inventory items: only visible if user owns the company
ALTER TABLE inventory_items ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS inventory_by_company ON inventory_items;
CREATE POLICY inventory_by_company ON inventory_items
    USING (company_id IN (
        SELECT id FROM companies WHERE owner_id::text = current_setting('app.current_user_id', true)
    ));

-- Connections: only visible if user owns the company
ALTER TABLE connections ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS connections_by_company ON connections;
CREATE POLICY connections_by_company ON connections
    USING (company_id IN (
        SELECT id FROM companies WHERE owner_id::text = current_setting('app.current_user_id', true)
    ));

-- Sync logs: only visible if user owns the company
ALTER TABLE sync_logs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS sync_logs_by_company ON sync_logs;
CREATE POLICY sync_logs_by_company ON sync_logs
    USING (company_id IN (
        SELECT id FROM companies WHERE owner_id::text = current_setting('app.current_user_id', true)
    ));

-- Reconciliations: only visible if user owns the company
ALTER TABLE reconciliations ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS reconciliations_by_company ON reconciliations;
CREATE POLICY reconciliations_by_company ON reconciliations
    USING (company_id IN (
        SELECT id FROM companies WHERE owner_id::text = current_setting('app.current_user_id', true)
    ));

-- Discrepancies: only visible if user owns the company
ALTER TABLE discrepancies ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS discrepancies_by_company ON discrepancies;
CREATE POLICY discrepancies_by_company ON discrepancies
    USING (company_id IN (
        SELECT id FROM companies WHERE owner_id::text = current_setting('app.current_user_id', true)
    ));

-- Allow INSERT for all tables (new rows are created by the user, so they belong to their tenant)
-- The USING clause above handles SELECT/UPDATE/DELETE filtering
"""


async def apply_rls_policies(db):
    """Apply RLS policies to the database. Call during migration."""
    async with db.begin():
        await db.execute(text(RLS_POLICIES_SQL))
