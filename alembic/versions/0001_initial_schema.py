from __future__ import annotations

from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS invoices(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            supplier TEXT,
            client TEXT,
            doc_number TEXT,
            date TEXT,
            date_iso TEXT,
            total_sum REAL,
            raw_text TEXT,
            source_path TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS invoice_items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            idx INTEGER NOT NULL,
            code TEXT,
            name TEXT,
            qty REAL,
            price REAL,
            total REAL,
            FOREIGN KEY(invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
        );
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS comments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
        );
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS invoice_drafts(
            user_id INTEGER PRIMARY KEY,
            payload TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS invoice_drafts;")
    op.execute("DROP TABLE IF EXISTS comments;")
    op.execute("DROP TABLE IF EXISTS invoice_items;")
    op.execute("DROP TABLE IF EXISTS invoices;")
