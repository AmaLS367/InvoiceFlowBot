from alembic import op

revision = "0002_user_languages"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS user_languages(
            user_id INTEGER PRIMARY KEY,
            locale TEXT NOT NULL
        );
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS user_languages;")
