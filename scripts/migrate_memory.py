import sqlite3
from pathlib import Path


def migrate():
    db_path = Path("storage/database/qualiprompt.db")
    if not db_path.exists():
        print("Nenhum banco existente para migrar.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=30000")

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memory_associations'")
    if not cursor.fetchone():
        print("Tabela memory_associations nao existe. Nada a migrar.")
        conn.close()
        return

    cursor.execute("PRAGMA table_info(memory_associations)")
    columns = [col[1] for col in cursor.fetchall()]

    if "model_version" not in columns:
        cursor.execute(
            "ALTER TABLE memory_associations ADD COLUMN model_version TEXT DEFAULT 'legacy'"
        )
        print("Coluna model_version adicionada.")

    conn.commit()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_associations_new (
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
        INSERT OR IGNORE INTO memory_associations_new
        (id, template_name, domain, has_constraints, has_examples, goal_length_category,
         model_version, best_prompt, best_score, usage_count, last_used, created_at, updated_at)
        SELECT id, template_name, domain, has_constraints, has_examples, goal_length_category,
               COALESCE(model_version, 'legacy'), best_prompt, best_score, usage_count,
               last_used, created_at, updated_at
        FROM memory_associations
    """)

    cursor.execute("DROP TABLE memory_associations")
    cursor.execute("ALTER TABLE memory_associations_new RENAME TO memory_associations")

    conn.commit()
    conn.close()
    print("Migracao concluida com sucesso.")


if __name__ == "__main__":
    migrate()
