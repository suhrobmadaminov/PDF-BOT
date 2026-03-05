"""
Ma'lumotlar bazasi moduli — SQLite + aiosqlite orqali barcha CRUD operatsiyalar.
Jadvallar: users, sessions, pdf_history, statistics, settings
"""

import json
import aiosqlite
from datetime import datetime, timedelta
from loguru import logger
from config import DATABASE_PATH, DEFAULT_SETTINGS


class Database:
    """Asinxron SQLite ma'lumotlar bazasi boshqaruvchisi."""

    def __init__(self):
        """Database obyektini boshlang'ich holatga keltirish."""
        self.db_path = str(DATABASE_PATH)
        self._conn: aiosqlite.Connection | None = None

    async def init(self) -> None:
        """
        Ma'lumotlar bazasini ishga tushirish va barcha jadvallarni yaratish.
        Agar jadvallar mavjud bo'lsa, ular o'zgartirilmaydi.
        """
        try:
            self._conn = await aiosqlite.connect(self.db_path)
            # Foreign key qo'llab-quvvatlashni yoqish
            await self._conn.execute("PRAGMA foreign_keys = ON")
            # WAL rejimi — yozish va o'qishni parallel bajarish
            await self._conn.execute("PRAGMA journal_mode = WAL")
            await self._conn.commit()
            await self._create_tables()
            logger.info(f"Ma'lumotlar bazasi ulandi: {self.db_path}")
        except Exception as e:
            logger.error(f"Ma'lumotlar bazasini ishga tushirishda xato: {e}")
            raise

    async def _create_tables(self) -> None:
        """Barcha jadvallarni yaratish."""
        async with self._conn.executescript("""
            -- Foydalanuvchilar jadvali
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER UNIQUE NOT NULL,
                username    TEXT,
                full_name   TEXT,
                lang        TEXT DEFAULT 'uz',
                joined_at   TEXT NOT NULL,
                is_banned   INTEGER DEFAULT 0,
                last_active TEXT
            );

            -- Foydalanuvchi sessiyalari (ko'p rasmli rejim uchun)
            CREATE TABLE IF NOT EXISTS sessions (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       INTEGER UNIQUE NOT NULL,
                mode          TEXT DEFAULT 'idle',
                images_data   TEXT DEFAULT '[]',
                images_count  INTEGER DEFAULT 0,
                created_at    TEXT NOT NULL,
                updated_at    TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );

            -- PDF tarix jadvali
            CREATE TABLE IF NOT EXISTS pdf_history (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                file_id     TEXT NOT NULL,
                file_name   TEXT NOT NULL,
                file_size   INTEGER DEFAULT 0,
                pages       INTEGER DEFAULT 1,
                created_at  TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );

            -- Statistika jadvali
            CREATE TABLE IF NOT EXISTS statistics (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                extra_data  TEXT,
                timestamp   TEXT NOT NULL
            );

            -- Foydalanuvchi sozlamalari jadvali
            CREATE TABLE IF NOT EXISTS settings (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER UNIQUE NOT NULL,
                quality     TEXT DEFAULT 'high',
                pagesize    TEXT DEFAULT 'A4',
                orientation TEXT DEFAULT 'portrait',
                margin      TEXT DEFAULT 'small',
                ocr_lang    TEXT DEFAULT 'en',
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );

            -- Indekslar — tezroq qidirish uchun
            CREATE INDEX IF NOT EXISTS idx_users_user_id      ON users(user_id);
            CREATE INDEX IF NOT EXISTS idx_sessions_user_id   ON sessions(user_id);
            CREATE INDEX IF NOT EXISTS idx_history_user_id    ON pdf_history(user_id);
            CREATE INDEX IF NOT EXISTS idx_stats_user_id      ON statistics(user_id);
            CREATE INDEX IF NOT EXISTS idx_stats_timestamp    ON statistics(timestamp);
            CREATE INDEX IF NOT EXISTS idx_stats_action       ON statistics(action_type);
        """):
            pass
        await self._conn.commit()
        logger.debug("Barcha jadvallar yaratildi yoki mavjud")

    async def close(self) -> None:
        """Ma'lumotlar bazasi ulanishini yopish."""
        if self._conn:
            await self._conn.close()
            self._conn = None
            logger.info("Ma'lumotlar bazasi ulanishi yopildi")

    # ── Foydalanuvchi metodlari ────────────────────────────────────────────────

    async def get_or_create_user(
        self,
        user_id: int,
        username: str | None,
        full_name: str,
    ) -> dict:
        """
        Foydalanuvchini olish yoki yangi yaratish.

        Args:
            user_id:   Telegram foydalanuvchi IDsi
            username:  Telegram username (@username)
            full_name: To'liq ism

        Returns:
            Foydalanuvchi ma'lumotlari lug'ati
        """
        now = datetime.utcnow().isoformat()
        try:
            # Mavjud foydalanuvchini yangilash (username yoki ism o'zgargan bo'lishi mumkin)
            await self._conn.execute(
                """
                INSERT INTO users (user_id, username, full_name, joined_at, last_active)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username    = excluded.username,
                    full_name   = excluded.full_name,
                    last_active = excluded.last_active
                """,
                (user_id, username, full_name, now, now),
            )
            await self._conn.commit()

            # Default sozlamalarni yaratish (agar yo'q bo'lsa)
            await self._conn.execute(
                """
                INSERT OR IGNORE INTO settings (user_id, quality, pagesize, orientation, margin, ocr_lang)
                VALUES (?, 'high', 'A4', 'portrait', 'small', 'en')
                """,
                (user_id,),
            )
            await self._conn.commit()

            return await self.get_user(user_id)
        except Exception as e:
            logger.error(f"get_or_create_user xatosi (user_id={user_id}): {e}")
            raise

    async def get_user(self, user_id: int) -> dict | None:
        """
        Foydalanuvchi ma'lumotlarini olish.

        Args:
            user_id: Telegram foydalanuvchi IDsi

        Returns:
            Foydalanuvchi lug'ati yoki None (topilmasa)
        """
        try:
            async with self._conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    cols = [d[0] for d in cursor.description]
                    return dict(zip(cols, row))
                return None
        except Exception as e:
            logger.error(f"get_user xatosi (user_id={user_id}): {e}")
            return None

    async def update_user_lang(self, user_id: int, lang: str) -> None:
        """Foydalanuvchi interfeys tilini yangilash."""
        try:
            await self._conn.execute(
                "UPDATE users SET lang = ? WHERE user_id = ?",
                (lang, user_id),
            )
            await self._conn.commit()
        except Exception as e:
            logger.error(f"update_user_lang xatosi: {e}")

    async def update_last_active(self, user_id: int) -> None:
        """Foydalanuvchining oxirgi faollik vaqtini yangilash."""
        try:
            now = datetime.utcnow().isoformat()
            await self._conn.execute(
                "UPDATE users SET last_active = ? WHERE user_id = ?",
                (now, user_id),
            )
            await self._conn.commit()
        except Exception as e:
            logger.error(f"update_last_active xatosi: {e}")

    async def ban_user(self, user_id: int) -> bool:
        """Foydalanuvchini bloklash."""
        try:
            await self._conn.execute(
                "UPDATE users SET is_banned = 1 WHERE user_id = ?",
                (user_id,),
            )
            await self._conn.commit()
            logger.info(f"Foydalanuvchi bloklandi: {user_id}")
            return True
        except Exception as e:
            logger.error(f"ban_user xatosi: {e}")
            return False

    async def unban_user(self, user_id: int) -> bool:
        """Foydalanuvchini blokdan chiqarish."""
        try:
            await self._conn.execute(
                "UPDATE users SET is_banned = 0 WHERE user_id = ?",
                (user_id,),
            )
            await self._conn.commit()
            logger.info(f"Foydalanuvchi blokdan chiqarildi: {user_id}")
            return True
        except Exception as e:
            logger.error(f"unban_user xatosi: {e}")
            return False

    async def is_banned(self, user_id: int) -> bool:
        """Foydalanuvchi bloklangan-bloklashmaganligini tekshirish."""
        try:
            async with self._conn.execute(
                "SELECT is_banned FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return bool(row and row[0])
        except Exception as e:
            logger.error(f"is_banned xatosi: {e}")
            return False

    async def get_all_users(self) -> list[dict]:
        """Barcha foydalanuvchilarni olish (broadcast uchun)."""
        try:
            async with self._conn.execute(
                "SELECT user_id, username, full_name, lang, is_banned FROM users"
            ) as cursor:
                rows = await cursor.fetchall()
                cols = [d[0] for d in cursor.description]
                return [dict(zip(cols, row)) for row in rows]
        except Exception as e:
            logger.error(f"get_all_users xatosi: {e}")
            return []

    async def get_active_users_today(self) -> int:
        """Bugungi aktiv foydalanuvchilar sonini olish."""
        try:
            today = datetime.utcnow().date().isoformat()
            async with self._conn.execute(
                "SELECT COUNT(*) FROM users WHERE last_active LIKE ?",
                (f"{today}%",),
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
        except Exception as e:
            logger.error(f"get_active_users_today xatosi: {e}")
            return 0

    # ── Sessiya metodlari ─────────────────────────────────────────────────────

    async def create_session(self, user_id: int, mode: str = "collecting") -> None:
        """
        Foydalanuvchi sessiyasini yaratish yoki yangilash.

        Args:
            user_id: Telegram foydalanuvchi IDsi
            mode:    Sessiya rejimi ('collecting', 'editing', 'idle')
        """
        now = datetime.utcnow().isoformat()
        try:
            await self._conn.execute(
                """
                INSERT INTO sessions (user_id, mode, images_data, images_count, created_at, updated_at)
                VALUES (?, ?, '[]', 0, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    mode       = excluded.mode,
                    images_data = '[]',
                    images_count = 0,
                    updated_at = excluded.updated_at
                """,
                (user_id, mode, now, now),
            )
            await self._conn.commit()
        except Exception as e:
            logger.error(f"create_session xatosi: {e}")

    async def get_session(self, user_id: int) -> dict | None:
        """Foydalanuvchi sessiyasini olish."""
        try:
            async with self._conn.execute(
                "SELECT * FROM sessions WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    cols = [d[0] for d in cursor.description]
                    data = dict(zip(cols, row))
                    # images_data ni ro'yxatga o'tkazish
                    try:
                        data["images_data"] = json.loads(data["images_data"] or "[]")
                    except json.JSONDecodeError:
                        data["images_data"] = []
                    return data
                return None
        except Exception as e:
            logger.error(f"get_session xatosi: {e}")
            return None

    async def update_session(
        self,
        user_id: int,
        mode: str | None = None,
        images_data: list | None = None,
    ) -> None:
        """Sessiya ma'lumotlarini yangilash."""
        now = datetime.utcnow().isoformat()
        try:
            updates = []
            params = []

            if mode is not None:
                updates.append("mode = ?")
                params.append(mode)

            if images_data is not None:
                updates.append("images_data = ?")
                updates.append("images_count = ?")
                params.append(json.dumps(images_data))
                params.append(len(images_data))

            if not updates:
                return

            updates.append("updated_at = ?")
            params.append(now)
            params.append(user_id)

            sql = f"UPDATE sessions SET {', '.join(updates)} WHERE user_id = ?"
            await self._conn.execute(sql, params)
            await self._conn.commit()
        except Exception as e:
            logger.error(f"update_session xatosi: {e}")

    async def delete_session(self, user_id: int) -> None:
        """Foydalanuvchi sessiyasini o'chirish."""
        try:
            await self._conn.execute(
                "DELETE FROM sessions WHERE user_id = ?", (user_id,)
            )
            await self._conn.commit()
        except Exception as e:
            logger.error(f"delete_session xatosi: {e}")

    # ── PDF Tarix metodlari ───────────────────────────────────────────────────

    async def add_history(
        self,
        user_id: int,
        file_id: str,
        file_name: str,
        file_size: int,
        pages: int = 1,
    ) -> int:
        """
        PDF tarixga qo'shish. Eski yozuvlar avtomatik o'chiriladi
        (faqat oxirgi MAX_HISTORY_COUNT ta saqlanadi).

        Returns:
            Yangi yozuv ID si
        """
        from config import MAX_HISTORY_COUNT
        now = datetime.utcnow().isoformat()
        try:
            cursor = await self._conn.execute(
                """
                INSERT INTO pdf_history (user_id, file_id, file_name, file_size, pages, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, file_id, file_name, file_size, pages, now),
            )
            new_id = cursor.lastrowid
            await self._conn.commit()

            # Eski yozuvlarni o'chirish (faqat oxirgi 5 ta saqlansin)
            await self._conn.execute(
                """
                DELETE FROM pdf_history
                WHERE user_id = ? AND id NOT IN (
                    SELECT id FROM pdf_history
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                )
                """,
                (user_id, user_id, MAX_HISTORY_COUNT),
            )
            await self._conn.commit()
            return new_id
        except Exception as e:
            logger.error(f"add_history xatosi: {e}")
            return -1

    async def get_history(self, user_id: int) -> list[dict]:
        """Foydalanuvchining PDF tarixini olish (yangilaridan eskisigacha)."""
        try:
            async with self._conn.execute(
                """
                SELECT id, file_id, file_name, file_size, pages, created_at
                FROM pdf_history
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                cols = [d[0] for d in cursor.description]
                return [dict(zip(cols, row)) for row in rows]
        except Exception as e:
            logger.error(f"get_history xatosi: {e}")
            return []

    async def delete_history_item(self, history_id: int, user_id: int) -> bool:
        """Tarixdan bitta PDF ni o'chirish (faqat o'z tarixin o'chira oladi)."""
        try:
            await self._conn.execute(
                "DELETE FROM pdf_history WHERE id = ? AND user_id = ?",
                (history_id, user_id),
            )
            await self._conn.commit()
            return True
        except Exception as e:
            logger.error(f"delete_history_item xatosi: {e}")
            return False

    async def cleanup_old_history_files(self, days: int) -> int:
        """
        Ko'rsatilgan kundan eski PDF tarix yozuvlarini o'chirish.

        Args:
            days: Necha kundan eski yozuvlar o'chirilsin

        Returns:
            O'chirilgan yozuvlar soni
        """
        try:
            cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
            cursor = await self._conn.execute(
                "DELETE FROM pdf_history WHERE created_at < ?", (cutoff,)
            )
            await self._conn.commit()
            count = cursor.rowcount
            if count > 0:
                logger.info(f"Eski tarix tozalandi: {count} ta yozuv o'chirildi")
            return count
        except Exception as e:
            logger.error(f"cleanup_old_history_files xatosi: {e}")
            return 0

    # ── Statistika metodlari ──────────────────────────────────────────────────

    async def log_action(
        self,
        user_id: int,
        action_type: str,
        extra_data: str | None = None,
    ) -> None:
        """
        Foydalanuvchi harakatini statistika jadvaliga yozish.

        Args:
            user_id:     Telegram foydalanuvchi IDsi
            action_type: Harakat turi (masalan: 'pdf_created', 'ocr_used')
            extra_data:  Qo'shimcha ma'lumot (JSON satr)
        """
        now = datetime.utcnow().isoformat()
        try:
            await self._conn.execute(
                """
                INSERT INTO statistics (user_id, action_type, extra_data, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, action_type, extra_data, now),
            )
            await self._conn.commit()
        except Exception as e:
            logger.error(f"log_action xatosi: {e}")

    async def get_global_stats(self) -> dict:
        """Umumiy bot statistikasini olish."""
        try:
            today = datetime.utcnow().date().isoformat()
            stats = {}

            # Jami foydalanuvchilar
            async with self._conn.execute(
                "SELECT COUNT(*) FROM users"
            ) as cursor:
                row = await cursor.fetchone()
                stats["total_users"] = row[0] if row else 0

            # Bugungi aktiv foydalanuvchilar
            async with self._conn.execute(
                "SELECT COUNT(*) FROM users WHERE last_active LIKE ?",
                (f"{today}%",),
            ) as cursor:
                row = await cursor.fetchone()
                stats["active_today"] = row[0] if row else 0

            # Jami yaratilgan PDF lar
            async with self._conn.execute(
                "SELECT COUNT(*) FROM statistics WHERE action_type = 'pdf_created'"
            ) as cursor:
                row = await cursor.fetchone()
                stats["total_pdfs"] = row[0] if row else 0

            # Bugungi PDF lar
            async with self._conn.execute(
                "SELECT COUNT(*) FROM statistics WHERE action_type = 'pdf_created' AND timestamp LIKE ?",
                (f"{today}%",),
            ) as cursor:
                row = await cursor.fetchone()
                stats["pdfs_today"] = row[0] if row else 0

            # Bloklangan foydalanuvchilar
            async with self._conn.execute(
                "SELECT COUNT(*) FROM users WHERE is_banned = 1"
            ) as cursor:
                row = await cursor.fetchone()
                stats["banned_users"] = row[0] if row else 0

            # Eng ko'p ishlatiladigan funksiyalar (top 5)
            async with self._conn.execute(
                """
                SELECT action_type, COUNT(*) as cnt
                FROM statistics
                GROUP BY action_type
                ORDER BY cnt DESC
                LIMIT 5
                """
            ) as cursor:
                rows = await cursor.fetchall()
                stats["top_actions"] = [{"action": r[0], "count": r[1]} for r in rows]

            return stats
        except Exception as e:
            logger.error(f"get_global_stats xatosi: {e}")
            return {}

    async def get_user_stats(self, user_id: int) -> dict:
        """Bitta foydalanuvchi statistikasini olish."""
        try:
            stats = {}

            user = await self.get_user(user_id)
            stats["user"] = user

            # Yaratilgan PDF lar soni
            async with self._conn.execute(
                "SELECT COUNT(*) FROM statistics WHERE user_id = ? AND action_type = 'pdf_created'",
                (user_id,),
            ) as cursor:
                row = await cursor.fetchone()
                stats["total_pdfs"] = row[0] if row else 0

            # OCR ishlatilgan marta
            async with self._conn.execute(
                "SELECT COUNT(*) FROM statistics WHERE user_id = ? AND action_type = 'ocr_used'",
                (user_id,),
            ) as cursor:
                row = await cursor.fetchone()
                stats["ocr_count"] = row[0] if row else 0

            # Reverse ishlatilgan marta
            async with self._conn.execute(
                "SELECT COUNT(*) FROM statistics WHERE user_id = ? AND action_type = 'reverse_used'",
                (user_id,),
            ) as cursor:
                row = await cursor.fetchone()
                stats["reverse_count"] = row[0] if row else 0

            # Tarix soni
            async with self._conn.execute(
                "SELECT COUNT(*) FROM pdf_history WHERE user_id = ?",
                (user_id,),
            ) as cursor:
                row = await cursor.fetchone()
                stats["history_count"] = row[0] if row else 0

            return stats
        except Exception as e:
            logger.error(f"get_user_stats xatosi: {e}")
            return {}

    # ── Sozlamalar metodlari ──────────────────────────────────────────────────

    async def get_settings(self, user_id: int) -> dict:
        """Foydalanuvchi sozlamalarini olish."""
        try:
            async with self._conn.execute(
                "SELECT * FROM settings WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    cols = [d[0] for d in cursor.description]
                    return dict(zip(cols, row))
                # Default sozlamalar qaytarish
                return {**DEFAULT_SETTINGS, "user_id": user_id}
        except Exception as e:
            logger.error(f"get_settings xatosi: {e}")
            return {**DEFAULT_SETTINGS, "user_id": user_id}

    async def update_settings(self, user_id: int, **kwargs) -> None:
        """
        Foydalanuvchi sozlamalarini yangilash.

        Args:
            user_id: Telegram foydalanuvchi IDsi
            **kwargs: Yangilanadigan sozlamalar (masalan: quality='low')
        """
        allowed_keys = {"quality", "pagesize", "orientation", "margin", "ocr_lang"}
        filtered = {k: v for k, v in kwargs.items() if k in allowed_keys}

        if not filtered:
            return

        try:
            # Avval users jadvalida mavjudligini ta'minlash (FOREIGN KEY uchun)
            now = datetime.utcnow().isoformat()
            await self._conn.execute(
                """
                INSERT OR IGNORE INTO users (user_id, username, full_name, joined_at, last_active)
                VALUES (?, NULL, '', ?, ?)
                """,
                (user_id, now, now),
            )

            # Avval mavjudligini tekshirish va yaratish
            await self._conn.execute(
                """
                INSERT OR IGNORE INTO settings (user_id, quality, pagesize, orientation, margin, ocr_lang)
                VALUES (?, 'high', 'A4', 'portrait', 'small', 'en')
                """,
                (user_id,),
            )

            sets = ", ".join(f"{k} = ?" for k in filtered.keys())
            values = list(filtered.values()) + [user_id]
            await self._conn.execute(
                f"UPDATE settings SET {sets} WHERE user_id = ?", values
            )
            await self._conn.commit()
        except Exception as e:
            logger.error(f"update_settings xatosi: {e}")

    # ── Admin metodlari ───────────────────────────────────────────────────────

    async def get_last_errors(self, limit: int = 50) -> list[dict]:
        """Oxirgi xatolarni olish (log fayldan emas, statistika jadvalidan)."""
        try:
            async with self._conn.execute(
                """
                SELECT user_id, action_type, extra_data, timestamp
                FROM statistics
                WHERE action_type LIKE 'error_%'
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,),
            ) as cursor:
                rows = await cursor.fetchall()
                cols = [d[0] for d in cursor.description]
                return [dict(zip(cols, row)) for row in rows]
        except Exception as e:
            logger.error(f"get_last_errors xatosi: {e}")
            return []

    async def search_user(self, query: str) -> list[dict]:
        """Foydalanuvchini ID yoki username bo'yicha qidirish."""
        try:
            # ID bo'yicha qidirish
            if query.lstrip("-").isdigit():
                user_id = int(query)
                async with self._conn.execute(
                    "SELECT * FROM users WHERE user_id = ?", (user_id,)
                ) as cursor:
                    rows = await cursor.fetchall()
                    cols = [d[0] for d in cursor.description]
                    return [dict(zip(cols, row)) for row in rows]
            else:
                # Username bo'yicha qidirish
                async with self._conn.execute(
                    "SELECT * FROM users WHERE username LIKE ?",
                    (f"%{query}%",),
                ) as cursor:
                    rows = await cursor.fetchall()
                    cols = [d[0] for d in cursor.description]
                    return [dict(zip(cols, row)) for row in rows]
        except Exception as e:
            logger.error(f"search_user xatosi: {e}")
            return []
