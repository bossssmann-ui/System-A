"""
SQLite слой для хранения и работы с тендерами.
"""
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class TenderDB:
    """Работа с БД тендеров."""

    def __init__(self, db_path: str = "tenders.db"):
        """
        Инициализирует подключение к БД и создаёт схему.

        Args:
            db_path: Путь к файлу SQLite
        """
        self.db_path = db_path
        self._init_schema()

    def _init_schema(self) -> None:
        """Создаёт таблицы если их нет."""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS tenders (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            law TEXT NOT NULL,
            customer TEXT,
            amount INTEGER,
            region TEXT,
            deadline TEXT,
            link TEXT UNIQUE,
            description TEXT,
            fetched_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_fetched_at ON tenders(fetched_at DESC);
        CREATE INDEX IF NOT EXISTS idx_amount ON tenders(amount DESC);
        CREATE INDEX IF NOT EXISTS idx_law ON tenders(law);
        """

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(schema_sql)
                conn.commit()
            logger.info(f"Инициализирована БД: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Ошибка инициализации БД: {e}")
            raise

    def upsert_tender(self, tender: Dict[str, Any]) -> bool:
        """
        Вставляет или обновляет тендер в БД.

        Args:
            tender: Словарь с полями: id, title, law, customer, amount, region, deadline, link, description

        Returns:
            True если вставлена новая запись, False если обновлена
        """
        required_fields = ["id", "title", "law", "link"]
        if not all(field in tender for field in required_fields):
            logger.warning(f"Неполные данные тендера: {tender}")
            return False

        now = datetime.utcnow().isoformat()

        sql = """
        INSERT INTO tenders (id, title, law, customer, amount, region, deadline, link, description, fetched_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            updated_at = excluded.updated_at,
            title = excluded.title,
            amount = excluded.amount,
            deadline = excluded.deadline
        """

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    sql,
                    (
                        tender.get("id"),
                        tender.get("title"),
                        tender.get("law"),
                        tender.get("customer"),
                        tender.get("amount"),
                        tender.get("region"),
                        tender.get("deadline"),
                        tender.get("link"),
                        tender.get("description"),
                        now,
                        now,
                    ),
                )
                conn.commit()
                inserted = cursor.rowcount > 0
                logger.debug(f"Тендер {tender['id']}: {'вставлен' if inserted else 'обновлён'}")
                return inserted
        except sqlite3.IntegrityError:
            logger.debug(f"Дубликат тендера {tender['id']}")
            return False
        except sqlite3.Error as e:
            logger.error(f"Ошибка при вставке тендера {tender['id']}: {e}")
            raise

    def get_recent_new_tenders(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Возвращает топ-N новых тендеров по сумме.

        Args:
            limit: Сколько записей вернуть

        Returns:
            Список словарей с тендерами
        """
        sql = """
        SELECT id, title, law, customer, amount, region, deadline, link, description
        FROM tenders
        ORDER BY amount DESC NULLS LAST, fetched_at DESC
        LIMIT ?
        """

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(sql, (limit,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Ошибка при чтении из БД: {e}")
            raise

    def get_tender_count(self) -> int:
        """
        Возвращает общее количество тендеров в БД.

        Returns:
            Количество записей
        """
        sql = "SELECT COUNT(*) FROM tenders"

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                result = cursor.fetchone()
                return result[0] if result else 0
        except sqlite3.Error as e:
            logger.error(f"Ошибка при подсчёте тендеров: {e}")
            raise
