"""empty message

Revision ID: 29898931a306
Revises:
Create Date: 2023-11-19 21:57:32.691104

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '29898931a306'
down_revision = None
branch_labels = None
depends_on = None

# TODO
def upgrade():
#    engine = op.get_bind()
#    inspector = sa.inspect(engine)
#    tables = inspector.get_table_names()
#    if "embeddings" not in tables:
#        op.create_table(
#            "embeddings",
#            sa.Column("package_id", sa.UnicodeText, primary_key=True),
#        )

    pass


def downgrade():
    pass
