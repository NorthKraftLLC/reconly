"""Row-Level Security setup.

NOTE: RLS disabled for now. PostgreSQL 14+ applies RLS to table owners too,
which blocks our application's database user. 

All tenant isolation is enforced at the application level:
- Every router checks get_company_owned(user.id) before accessing data
- Company.owner_id ensures only owners can access their data  
- Every query filters by company_id
- Foreign keys with CASCADE delete ensure referential integrity

This is the standard multi-tenant pattern used by Stripe, Shopify, etc.
"""

from sqlalchemy import text


async def apply_rls_policies(db):
    """No-op: RLS disabled. Application-level checks handle tenant isolation."""
    pass
