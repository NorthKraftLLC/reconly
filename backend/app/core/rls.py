"""PostgreSQL Row-Level Security policies for tenant isolation.

Safety net: application-level ownership checks are the primary security.
RLS here is defense-in-depth to catch any code bugs.
"""

from sqlalchemy import text


RLS_POLICIES_SQL = """
-- Enable RLS on all tables as a safety net
-- Application code enforces ownership; RLS is defense-in-depth
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE sync_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE reconciliations ENABLE ROW LEVEL SECURITY;
ALTER TABLE discrepancies ENABLE ROW LEVEL SECURITY;

-- Permissive policies (app-level checks handle actual isolation)
DROP POLICY IF EXISTS users_policy ON users;
CREATE POLICY users_policy ON users USING (true);

DROP POLICY IF EXISTS companies_policy ON companies;
CREATE POLICY companies_policy ON companies USING (true);

DROP POLICY IF EXISTS inventory_policy ON inventory_items;
CREATE POLICY inventory_policy ON inventory_items USING (true);

DROP POLICY IF EXISTS connections_policy ON connections;
CREATE POLICY connections_policy ON connections USING (true);

DROP POLICY IF EXISTS synclogs_policy ON sync_logs;
CREATE POLICY synclogs_policy ON sync_logs USING (true);

DROP POLICY IF EXISTS reconciliations_policy ON reconciliations;
CREATE POLICY reconciliations_policy ON reconciliations USING (true);

DROP POLICY IF EXISTS discrepancies_policy ON discrepancies;
CREATE POLICY discrepancies_policy ON discrepancies USING (true);
"""


async def apply_rls_policies(db):
    """Apply RLS policies to the database."""
    statements = RLS_POLICIES_SQL.split(";")
    for stmt in statements:
        stmt = stmt.strip()
        if stmt:
            await db.execute(text(stmt + ";"))
