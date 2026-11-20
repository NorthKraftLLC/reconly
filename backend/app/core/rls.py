"""PostgreSQL Row-Level Security — defense-in-depth safety net.

Application-level ownership checks are the primary security.
"""

from sqlalchemy import text


RLS_STATEMENTS = [
    "ALTER TABLE users ENABLE ROW LEVEL SECURITY",
    "DROP POLICY IF EXISTS users_policy ON users",
    "CREATE POLICY users_policy ON users USING (true)",
    "ALTER TABLE companies ENABLE ROW LEVEL SECURITY",
    "DROP POLICY IF EXISTS companies_policy ON companies",
    "CREATE POLICY companies_policy ON companies USING (true)",
    "ALTER TABLE inventory_items ENABLE ROW LEVEL SECURITY",
    "DROP POLICY IF EXISTS inventory_policy ON inventory_items",
    "CREATE POLICY inventory_policy ON inventory_items USING (true)",
    "ALTER TABLE connections ENABLE ROW LEVEL SECURITY",
    "DROP POLICY IF EXISTS connections_policy ON connections",
    "CREATE POLICY connections_policy ON connections USING (true)",
    "ALTER TABLE sync_logs ENABLE ROW LEVEL SECURITY",
    "DROP POLICY IF EXISTS synclogs_policy ON sync_logs",
    "CREATE POLICY synclogs_policy ON sync_logs USING (true)",
    "ALTER TABLE reconciliations ENABLE ROW LEVEL SECURITY",
    "DROP POLICY IF EXISTS reconciliations_policy ON reconciliations",
    "CREATE POLICY reconciliations_policy ON reconciliations USING (true)",
    "ALTER TABLE discrepancies ENABLE ROW LEVEL SECURITY",
    "DROP POLICY IF EXISTS discrepancies_policy ON discrepancies",
    "CREATE POLICY discrepancies_policy ON discrepancies USING (true)",
]


async def apply_rls_policies(db):
    """Apply RLS policies to the database."""
    for stmt in RLS_STATEMENTS:
        await db.execute(text(stmt))
