"""add_rls_policy

Revision ID: 8c92134eadae
Revises: fa66029cc22f
Create Date: 2026-06-11 10:56:44.877872

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '8c92134eadae'
down_revision: Union[str, Sequence[str], None] = 'fa66029cc22f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE document ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY tenant_isolation ON document "
        "USING (current_setting('app.current_tenant',true) = tenant_id)"
    )

    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY tenant_isolation ON users "
        "USING (current_setting('app.current_tenant',true) = tenant_id)"
    )

    op.execute("ALTER TABLE tenant ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY tenant_isolation ON tenant "
        "USING (current_setting('app.current_tenant',true) = id)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON document")
    op.execute("ALTER TABLE document DISABLE ROW LEVEL SECURITY")

    op.execute("DROP POLICY IF EXISTS tenant_isolation ON users")
    op.execute("ALTER TABLE users DISABLE ROW LEVEL SECURITY")

    op.execute("DROP POLICY IF EXISTS tenant_isolation ON tenant")
    op.execute("ALTER TABLE tenant DISABLE ROW LEVEL SECURITY")