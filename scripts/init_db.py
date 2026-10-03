import sqlite3
from pathlib import Path

DB_PATH = Path("storage/database/qualiprompt.db")


def init_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_name TEXT NOT NULL,
            domain TEXT,
            has_constraints BOOLEAN DEFAULT 0,
            has_examples BOOLEAN DEFAULT 0,
            goal_length_category TEXT,
            model_version TEXT DEFAULT 'legacy',
            best_prompt TEXT NOT NULL,
            best_score REAL NOT NULL,
            usage_count INTEGER DEFAULT 0,
            last_used DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(template_name, domain, has_constraints, has_examples, goal_length_category, model_version)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_signature TEXT,
            old_score REAL,
            new_score REAL,
            improvement REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Migrate existing table if needed
    cursor.execute("PRAGMA table_info(memory_associations)")
    columns = [col[1] for col in cursor.fetchall()]
    if "model_version" not in columns:
        try:
            cursor.execute("ALTER TABLE memory_associations ADD COLUMN model_version TEXT DEFAULT 'legacy'")
        except sqlite3.OperationalError:
            pass

    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=30000")

    conn.commit()
    conn.close()
    print("Database initialized successfully")


if __name__ == "__main__":
    init_database()
