"""
Yordamchi funksiyalar moduli — umumiy ishlatiluvchi yordamchilar.
Rate limiter, fayl hajmi formatlash, progress bar va boshqalar.
"""

import os
import time
import asyncio
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Any

from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

from config import (
    ADMIN_IDS,
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_WINDOW,
    MAX_FILE_SIZE,
    ALLOWED_MIME_TYPES,
    ALLOWED_EXTENSIONS,
)
from locales import get_text


# ── Rate Limiter ──────────────────────────────────────────────────────────────

class RateLimiter:
    """
    Foydalanuvchilar uchun so'rovlar sonini cheklovchi sinf.
    Har foydalanuvchi uchun vaqt oynasida maksimal so'rovlar soni nazorat qilinadi.
    """

    def __init__(self, max_requests: int = RATE_LIMIT_REQUESTS, window: int = RATE_LIMIT_WINDOW):
        """
        Args:
            max_requests: Vaqt oynasida maksimal so'rovlar soni
            window:       Vaqt oynasi (sekund)
        """
        self.max_requests = max_requests
        self.window = window
        # {user_id: [timestamp1, timestamp2, ...]}
        self._requests: dict[int, list[float]] = defaultdict(list)

    def is_allowed(self, user_id: int) -> tuple[bool, int]:
        """
        Foydalanuvchi so'rov yuborishga ruxsat bor-yo'qligini tekshirish.

        Args:
            user_id: Telegram foydalanuvchi IDsi

        Returns:
            (ruxsat_bor, kutish_vaqti_sekund)
        """
        now = time.time()
        # Eski so'rovlarni tozalash (vaqt oynasidan tashqaridagilar)
        self._requests[user_id] = [
            ts for ts in self._requests[user_id]
            if now - ts < self.window
        ]

        if len(self._requests[user_id]) >= self.max_requests:
            # Qachon ruxsat berilishini hisoblash
            oldest = min(self._requests[user_id])
            wait_seconds = int(self.window - (now - oldest)) + 1
            return False, wait_seconds

        # So'rovni qayd etish
        self._requests[user_id].append(now)
        return True, 0

    def reset(self, user_id: int) -> None:
        """Foydalanuvchi so'rovlar tarixini tozalash."""
        self._requests.pop(user_id, None)


# Global rate limiter obyekti
rate_limiter = RateLimiter()


# ── Foydalanuvchi til olish ────────────────────────────────────────────────────

async def get_user_lang(
    user_id: int,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    """
    Foydalanuvchi tilini olish (cache → database).

    Args:
        user_id:  Telegram foydalanuvchi IDsi
        context:  Telegram context

    Returns:
        Til kodi ('uz', 'ru', 'en')
    """
    # Cache dan tekshirish
    if context.user_data.get("lang"):
        return context.user_data["lang"]

    # Ma'lumotlar bazasidan olish
    try:
        db = context.bot_data.get("db")
        if db:
            user = await db.get_user(user_id)
            if user and user.get("lang"):
                context.user_data["lang"] = user["lang"]
                return user["lang"]
    except Exception as e:
        logger.warning(f"get_user_lang xatosi: {e}")

    return "uz"  # Default til


def t(key: str, lang: str, **kwargs) -> str:
    """
    Qisqa yordamchi — matn olish uchun.

    Args:
        key:    Matn kaliti
        lang:   Til kodi
        **kwargs: Formatlash parametrlari

    Returns:
        Formatlangan matn
    """
    return get_text(key, lang, **kwargs)


# ── Fayl hajmi formatlash ─────────────────────────────────────────────────────

def format_file_size(size_bytes: int) -> str:
    """
    Fayl hajmini inson o'qiy oladigan formatga o'tkazish.

    Args:
        size_bytes: Fayl hajmi (bayt)

    Returns:
        Formatlangan satr ('1.23 MB', '456 KB', va h.k.)
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


# ── Progress bar ──────────────────────────────────────────────────────────────

def create_progress_bar(current: int, total: int, width: int = 10) -> str:
    """
    Matnli progress bar yaratish.

    Args:
        current: Joriy qiymat
        total:   Jami qiymat
        width:   Bar kengligi (belgi soni)

    Returns:
        Progress bar satri, masalan: '████░░░░░░'
    """
    if total <= 0:
        return "░" * width

    filled = int(width * current / total)
    filled = min(filled, width)
    bar = "█" * filled + "░" * (width - filled)
    return bar


def progress_text(current: int, total: int, width: int = 8) -> str:
    """
    Progress bar va foiz ko'rsatkichini birlashtirgan matn.

    Returns:
        Masalan: '[████░░░░] 50%'
    """
    percent = int(100 * current / total) if total > 0 else 0
    bar = create_progress_bar(current, total, width)
    return f"[{bar}] {percent}%"


# ── Admin tekshiruvi ──────────────────────────────────────────────────────────

def is_admin(user_id: int) -> bool:
    """
    Foydalanuvchi admin ekanligini tekshirish.

    Args:
        user_id: Telegram foydalanuvchi IDsi

    Returns:
        True — admin, False — oddiy foydalanuvchi
    """
    return user_id in ADMIN_IDS


# ── Fayl validatsiyasi ────────────────────────────────────────────────────────

def validate_image(
    mime_type: str | None,
    file_name: str | None,
    file_size: int,
) -> tuple[bool, str]:
    """
    Rasm faylini format va hajm bo'yicha tekshirish.

    Args:
        mime_type: MIME turi
        file_name: Fayl nomi
        file_size: Fayl hajmi (bayt)

    Returns:
        (yaroqli, xato_sababi) — yaroqli bo'lsa ('', '')
    """
    # Format tekshiruvi
    ext_valid = False
    if file_name:
        ext = Path(file_name).suffix.lower()
        ext_valid = ext in ALLOWED_EXTENSIONS

    mime_valid = mime_type and mime_type.lower() in ALLOWED_MIME_TYPES

    if not (ext_valid or mime_valid):
        return False, "invalid_format"

    # Hajm tekshiruvi
    if file_size > MAX_FILE_SIZE:
        return False, "too_large"

    return True, ""


def validate_pdf(
    mime_type: str | None,
    file_name: str | None,
    file_size: int,
) -> tuple[bool, str]:
    """
    PDF faylini tekshirish.

    Returns:
        (yaroqli, xato_sababi)
    """
    pdf_mimes = {"application/pdf"}
    is_pdf = (
        (mime_type and mime_type.lower() in pdf_mimes)
        or (file_name and file_name.lower().endswith(".pdf"))
    )

    if not is_pdf:
        return False, "not_pdf"

    # PDF uchun hajm limiti kattaroq (50MB)
    if file_size > 50 * 1024 * 1024:
        return False, "too_large"

    return True, ""


# ── Vaqtinchalik fayl tozalash ────────────────────────────────────────────────

async def cleanup_file(file_path: str | Path | None) -> None:
    """
    Vaqtinchalik faylni xavfsiz o'chirish.

    Args:
        file_path: O'chiriladigan fayl yo'li
    """
    if not file_path:
        return
    try:
        path = Path(file_path)
        if path.exists() and path.is_file():
            path.unlink()
            logger.debug(f"Vaqtinchalik fayl o'chirildi: {path.name}")
    except Exception as e:
        logger.warning(f"Fayl o'chirishda xato ({file_path}): {e}")


async def cleanup_files(file_paths: list[str | Path]) -> None:
    """
    Bir nechta vaqtinchalik fayllarni tozalash.

    Args:
        file_paths: O'chiriladigan fayl yo'llari ro'yxati
    """
    tasks = [cleanup_file(fp) for fp in file_paths]
    await asyncio.gather(*tasks, return_exceptions=True)


def cleanup_dir_files(directory: Path, older_than_minutes: int = 60) -> int:
    """
    Papkadagi eski fayllarni sinxron ravishda tozalash.

    Args:
        directory:          Tozalanadigan papka
        older_than_minutes: Necha daqiqadan eski fayllar o'chirilsin

    Returns:
        O'chirilgan fayllar soni
    """
    if not directory.exists():
        return 0

    count = 0
    cutoff = time.time() - (older_than_minutes * 60)

    try:
        for file_path in directory.iterdir():
            if file_path.is_file():
                try:
                    if file_path.stat().st_mtime < cutoff:
                        file_path.unlink()
                        count += 1
                except Exception as e:
                    logger.warning(f"Fayl o'chirishda xato: {e}")
    except Exception as e:
        logger.error(f"Papka tozalashda xato: {e}")

    return count


# ── Sana formatlash ───────────────────────────────────────────────────────────

def format_datetime(dt_str: str | None) -> str:
    """
    ISO formatdagi sana-vaqtni inson o'qiy oladigan formatga o'tkazish.

    Args:
        dt_str: ISO format sana satri

    Returns:
        Formatlangan sana ('12.05.2024 14:30')
    """
    if not dt_str:
        return "—"
    try:
        dt = datetime.fromisoformat(dt_str.split(".")[0])
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return dt_str[:16] if dt_str else "—"


def get_timestamp() -> str:
    """Joriy vaqt timestampini string sifatida olish (fayl nomlari uchun)."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# ── Sahifa oralig'ini tahlil qilish ──────────────────────────────────────────

def parse_page_range(range_str: str, max_pages: int) -> list[int] | None:
    """
    Sahifa oralig'i satrini sahifa raqamlari ro'yxatiga o'tkazish.

    Args:
        range_str:  Oraliq satri, masalan: '1-3, 5, 7-10'
        max_pages:  Maksimal sahifa soni

    Returns:
        Sahifa raqamlari ro'yxati (0-indexed) yoki None (xato bo'lsa)

    Misol:
        parse_page_range('1-3, 5', 10) → [0, 1, 2, 4]
    """
    if not range_str or range_str.strip().lower() in ("all", "/all", ""):
        return list(range(max_pages))

    pages = set()
    try:
        parts = range_str.replace(" ", "").split(",")
        for part in parts:
            if "-" in part:
                start_str, end_str = part.split("-", 1)
                start = int(start_str) - 1  # 0-indexed ga o'tkazish
                end = int(end_str) - 1
                if start < 0 or end < start or end >= max_pages:
                    return None
                pages.update(range(start, end + 1))
            else:
                page = int(part) - 1  # 0-indexed
                if page < 0 or page >= max_pages:
                    return None
                pages.add(page)
        return sorted(pages) if pages else None
    except (ValueError, IndexError):
        return None


# ── Savol tartibi olish ───────────────────────────────────────────────────────

def parse_order(order_str: str, max_count: int) -> list[int] | None:
    """
    Rasm tartib satrini indekslar ro'yxatiga o'tkazish.

    Args:
        order_str:  Tartib satri, masalan: '3,1,2,4' (1-indexed)
        max_count:  Maksimal rasm soni

    Returns:
        0-indexed indekslar ro'yxati yoki None (xato bo'lsa)
    """
    try:
        parts = order_str.replace(" ", "").split(",")
        if len(parts) != max_count:
            return None

        indices = []
        seen = set()
        for part in parts:
            idx = int(part) - 1  # 0-indexed
            if idx < 0 or idx >= max_count or idx in seen:
                return None
            indices.append(idx)
            seen.add(idx)

        return indices
    except (ValueError, AttributeError):
        return None


# ── Rate limit decorator ──────────────────────────────────────────────────────

async def check_rate_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Rate limit tekshirish va xabar yuborish.

    Returns:
        True — ruxsat bor, False — limit oshib ketgan
    """
    if not update.effective_user:
        return True

    user_id = update.effective_user.id

    # Adminlar uchun limit yo'q
    if is_admin(user_id):
        return True

    allowed, wait_seconds = rate_limiter.is_allowed(user_id)

    if not allowed:
        lang = await get_user_lang(user_id, context)
        msg = t("error_rate_limit", lang, seconds=wait_seconds)
        try:
            if update.message:
                await update.message.reply_text(msg)
            elif update.callback_query:
                await update.callback_query.answer(
                    f"Iltimos {wait_seconds}s kuting!", show_alert=True
                )
        except Exception:
            pass
        return False

    return True


# ── Foydalanuvchi ma'lumotlarini olish ────────────────────────────────────────

def get_user_info(update: Update) -> dict[str, Any]:
    """
    Update dan foydalanuvchi ma'lumotlarini olish.

    Returns:
        {user_id, username, full_name, first_name}
    """
    user = update.effective_user
    if not user:
        return {}
    return {
        "user_id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "first_name": user.first_name or user.full_name,
    }


# ── Fayl nomi generatsiya qilish ──────────────────────────────────────────────

def generate_pdf_filename(prefix: str = "converted") -> str:
    """
    PDF fayl nomini generatsiya qilish.

    Args:
        prefix: Prefiks ('converted', 'ocr', 'merged')

    Returns:
        Fayl nomi, masalan: 'converted_20240512_143022.pdf'
    """
    return f"{prefix}_{get_timestamp()}.pdf"


def generate_zip_filename() -> str:
    """ZIP fayl nomini generatsiya qilish."""
    return f"pages_{get_timestamp()}.zip"


# ── Xabar tahrirlash ─────────────────────────────────────────────────────────

async def safe_edit_message(
    message: Any,
    new_text: str,
    reply_markup: Any = None,
    parse_mode: str = "HTML",
) -> None:
    """
    Xabarni xavfsiz ravishda tahrirlash (xato bo'lsa jim o'tkazish).

    Args:
        message:      Tahrirlaniladigan xabar
        new_text:     Yangi matn
        reply_markup: Tugmalar (ixtiyoriy)
        parse_mode:   HTML yoki MarkdownV2
    """
    try:
        if reply_markup is not None:
            await message.edit_text(
                new_text, reply_markup=reply_markup, parse_mode=parse_mode
            )
        else:
            await message.edit_text(new_text, parse_mode=parse_mode)
    except Exception as e:
        # Xabar o'zgarmagan yoki o'chirilgan bo'lishi mumkin
        if "message is not modified" not in str(e).lower():
            logger.debug(f"safe_edit_message xatosi: {e}")


async def safe_answer_callback(
    callback_query: Any,
    text: str = "",
    show_alert: bool = False,
) -> None:
    """
    Callback query ni xavfsiz javoblash.

    Args:
        callback_query: Callback query obyekti
        text:           Ko'rsatiladigan matn (qisqa)
        show_alert:     Alert oyna ko'rsatish
    """
    try:
        await callback_query.answer(text=text, show_alert=show_alert)
    except Exception as e:
        logger.debug(f"safe_answer_callback xatosi: {e}")


# ── Foiz hisoblash ────────────────────────────────────────────────────────────

def calc_savings_percent(original: int, compressed: int) -> int:
    """
    Tejash foizini hisoblash.

    Args:
        original:   Asl hajm (bayt)
        compressed: Siqilgan hajm (bayt)

    Returns:
        Tejash foizi (0-100)
    """
    if original <= 0:
        return 0
    saved = original - compressed
    percent = int(saved * 100 / original)
    return max(0, min(100, percent))


# ── Telegram fayl hajmini olish ───────────────────────────────────────────────

def get_file_size_from_path(file_path: str | Path) -> int:
    """
    Fayl yo'lidan hajmni olish.

    Returns:
        Fayl hajmi (bayt), xato bo'lsa 0
    """
    try:
        return Path(file_path).stat().st_size
    except Exception:
        return 0
