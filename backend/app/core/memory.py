import hashlib
import json
import random
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple


@dataclass
class MemoryKey:
    template_name: str
    domain: Optional[str]
    has_constraints: bool
    has_examples: bool
    goal_length_category: str
    model_version: str

    def to_tuple(self):
        return (
            self.template_name,
            self.domain,
            self.has_constraints,
            self.has_examples,
            self.goal_length_category,
            self.model_version,
        )

    def to_signature(self) -> str:
        raw = (
            f"{self.template_name}|{self.domain}|"
            f"{self.has_constraints}|{self.has_examples}|"
            f"{self.goal_length_category}|{self.model_version}"
        )
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


class AdaptiveMemory:
    def __init__(
        self,
        db_path: str = "storage/database/qualiprompt.db",
        epsilon: float = 0.2,
        model_version: str = "default",
    ):
        self.db_path = Path(db_path)
        self.epsilon = epsilon
        self.model_version = model_version
        self._ensure_db_exists()
        self._configure_wal()

    def _configure_wal(self):
        conn = self._get_connection()
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA busy_timeout=30000")
        finally:
            conn.close()

    def _get_connection(self):
        return sqlite3.connect(str(self.db_path), timeout=30.0)

    def _ensure_db_exists(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
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
            conn.commit()

    def _extract_key(
        self, template_name: str, user_goal: str, field_values: Dict
    ) -> MemoryKey:
        domain = None
        if "produto" in field_values:
            domain = "product_analysis"
        elif "topic" in field_values:
            domain = "research"
        elif "publico_alvo" in field_values:
            domain = "marketing"

        goal_text = f"{user_goal} {json.dumps(field_values)}".lower()
        has_constraints = any(
            word in goal_text
            for word in ["maximo", "minimo", "limite", "ate", "exatamente", "entre"]
        )
        has_examples = any(
            word in goal_text for word in ["exemplo", "como", "similar", "caso"]
        )

        word_count = len(user_goal.split())
        if word_count < 20:
            length_cat = "short"
        elif word_count < 100:
            length_cat = "medium"
        else:
            length_cat = "long"

        return MemoryKey(
            template_name=template_name,
            domain=domain,
            has_constraints=has_constraints,
            has_examples=has_examples,
            goal_length_category=length_cat,
            model_version=self.model_version,
        )

    def get_best_prompt(
        self, template_name: str, user_goal: str, field_values: Dict
    ) -> Tuple[Optional[str], bool]:
        should_explore = random.random() < self.epsilon

        if should_explore:
            return None, True

        key = self._extract_key(template_name, user_goal, field_values)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT best_prompt, best_score FROM memory_associations
                WHERE template_name = ? AND (domain = ? OR domain IS NULL)
                  AND has_constraints = ? AND has_examples = ?
                  AND goal_length_category = ? AND model_version = ?
                ORDER BY best_score DESC
                LIMIT 1
            """,
                key.to_tuple(),
            )

            row = cursor.fetchone()

            if row:
                cursor.execute(
                    """
                    UPDATE memory_associations
                    SET last_used = ?, usage_count = usage_count + 1
                    WHERE template_name = ? AND (domain = ? OR domain IS NULL)
                      AND has_constraints = ? AND has_examples = ?
                      AND goal_length_category = ? AND model_version = ?
                """,
                    (datetime.now(),) + key.to_tuple(),
                )
                conn.commit()
                return row[0], False

        return None, False

    def update(
        self,
        template_name: str,
        user_goal: str,
        field_values: Dict,
        generated_prompt: str,
        score: float,
    ) -> bool:
        key = self._extract_key(template_name, user_goal, field_values)

        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id, best_score FROM memory_associations
                WHERE template_name = ? AND (domain = ? OR domain IS NULL)
                  AND has_constraints = ? AND has_examples = ?
                  AND goal_length_category = ? AND model_version = ?
            """,
                key.to_tuple(),
            )

            existing = cursor.fetchone()

            if existing:
                existing_id, existing_score = existing

                if score <= existing_score:
                    return False

                cursor.execute(
                    """
                    UPDATE memory_associations
                    SET best_prompt = ?, best_score = ?, updated_at = ?
                    WHERE id = ?
                """,
                    (generated_prompt, score, datetime.now(), existing_id),
                )

                cursor.execute(
                    """
                    INSERT INTO memory_log (key_signature, old_score, new_score, improvement)
                    VALUES (?, ?, ?, ?)
                """,
                    (key.to_signature(), existing_score, score, score - existing_score),
                )

            else:
                cursor.execute(
                    """
                    INSERT INTO memory_associations
                    (template_name, domain, has_constraints, has_examples,
                     goal_length_category, model_version, best_prompt, best_score,
                     usage_count, last_used, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
                """,
                    key.to_tuple()
                    + (
                        generated_prompt,
                        score,
                        datetime.now(),
                        datetime.now(),
                        datetime.now(),
                    ),
                )

            conn.commit()
            return True

    def get_stats(self) -> Dict:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM memory_associations")
            total_entries = cursor.fetchone()[0]

            cursor.execute("SELECT AVG(best_score) FROM memory_associations")
            avg_score = cursor.fetchone()[0] or 0

            cursor.execute(
                "SELECT COUNT(*) FROM memory_log WHERE improvement > 0"
            )
            improvements = cursor.fetchone()[0]

            return {
                "total_entries": total_entries,
                "average_score": round(avg_score, 2),
                "improvements_logged": improvements,
                "epsilon": self.epsilon,
                "model_version": self.model_version,
            }
