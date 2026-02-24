"""
Image to PDF Pro Bot — Asosiy kirish nuqtasi.
Barcha handlerlarni ro'yxatga oladi, APScheduler ni ishga tushiradi va botni yuritadi.
"""

import sys
import asyncio
from pathlib import Path

from loguru import logger
from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
)

# Config va database
from config import (
    BOT_TOKEN, LOG_LEVEL, LOG_FILE, LOG_ERROR_FILE,
    TEMP_DIR, HISTORY_DIR, CLEANUP_HOUR, CLEANUP_MINUTE, HISTORY_DAYS,
)
from database import Database

# Handlerlar
from handlers.start_handler import (
    get_start_handlers, handle_lang_callback, handle_close_callback
)
from handlers.image_handler import get_image_handlers
from handlers.pdf_handler import get_pdf_handlers
from handlers.settings_handler import get_settings_handlers
from handlers.admin_handler import get_admin_handlers
from handlers.reverse_handler import get_reverse_handlers


# ── Logging sozlash ───────────────────────────────────────────────────────────

def setup_logging() -> None:
    """
    Loguru logging tizimini sozlash.
    - Konsolga: renkli, minimal
    - Faylga: to'liq ma'lumot
    - Xato fayliga: faqat xatolar
    """
    # Default handlerlarni olib tashlash
    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
        "{name}:{function}:{line} | {message}"
    )

    # Konsol handler
    logger.add(
        sys.stdout,
        format=log_format,
        level=LOG_LEVEL,
        colorize=True,
    )

    # Asosiy log fayli (rotatsiya bilan)
    logger.add(
        str(LOG_FILE),
        format=file_format,
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
    )

    # Xatolar log fayli
    logger.add(
        str(LOG_ERROR_FILE),
        format=file_format,
        level="ERROR",
        rotation="5 MB",
        retention="60 days",
        encoding="utf-8",
    )

    logger.info("Logging tizimi sozlandi")


# ── APScheduler yordamida avtomatik tozalash ──────────────────────────────────

def setup_scheduler(application: Application) -> None:
    """
    APScheduler ni sozlash — har kecha eski fayllarni tozalash.

    Args:
        application: Telegram Application obyekti
    """
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger

        scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")

        async def cleanup_job():
            """Har kecha ishlaydigan tozalash vazifasi."""
            try:
                logger.info("Avtomatik tozalash boshlandi...")

                # Temp fayllarni tozalash (2 soatdan eski)
                from utils.helpers import cleanup_dir_files
                temp_count = cleanup_dir_files(TEMP_DIR, older_than_minutes=120)

                # PDF tarix eski yozuvlarni tozalash
                db: Database = application.bot_data.get("db")
                if db:
                    hist_count = await db.cleanup_old_history_files(HISTORY_DAYS)
                else:
                    hist_count = 0

                logger.info(
                    f"Avtomatik tozalash: temp={temp_count}, history={hist_count}"
                )
            except Exception as e:
                logger.error(f"Avtomatik tozalash xatosi: {e}")

        # Har kecha CLEANUP_HOUR:CLEANUP_MINUTE da ishlash
        scheduler.add_job(
            cleanup_job,
            trigger=CronTrigger(hour=CLEANUP_HOUR, minute=CLEANUP_MINUTE),
            id="daily_cleanup",
            name="Daily cleanup",
            replace_existing=True,
        )

        scheduler.start()
        application.bot_data["scheduler"] = scheduler
        logger.info(
            f"APScheduler ishga tushdi (har kecha {CLEANUP_HOUR:02d}:{CLEANUP_MINUTE:02d} da)"
        )

    except ImportError:
        logger.warning("APScheduler o'rnatilmagan — avtomatik tozalash o'chirilgan")
    except Exception as e:
        logger.error(f"Scheduler sozlashda xato: {e}")


# ── Ma'lumotlar bazasini ishga tushirish ──────────────────────────────────────

async def post_init(application: Application) -> None:
    """
    Ilovani ishga tushirgandan keyin bajariladi.
    Ma'lumotlar bazasini va schedulerni sozlaydi.
    """
    # Database ni yaratish va ishga tushirish
    db = Database()
    await db.init()
    application.bot_data["db"] = db
    logger.info("Ma'lumotlar bazasi tayyor")

    # Scheduler
    setup_scheduler(application)

    logger.info("Bot tayyor! Polling boshlandi...")


async def post_shutdown(application: Application) -> None:
    """
    Bot to'xtaganda chaqiriladi — resurslarni tozalash.
    """
    # Ma'lumotlar bazasini yopish
    db: Database = application.bot_data.get("db")
    if db:
        await db.close()
        logger.info("Ma'lumotlar bazasi yopildi")

    # Schedulerni to'xtatish
    scheduler = application.bot_data.get("scheduler")
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler to'xtatildi")


# ── Xato handler ─────────────────────────────────────────────────────────────

async def error_handler(update: object, context) -> None:
    """
    Global xato handler — barcha tutilmagan xatolar shu yerga keladi.
    """
    from telegram.error import (
        BadRequest, Forbidden, NetworkError, TimedOut, TelegramError, Conflict
    )

    error = context.error

    # Conflict — bir vaqtda ikki instance (deployment paytida odatiy)
    if isinstance(error, Conflict):
        logger.warning(f"Bot conflict (deployment): {error}")
        return

    # Telegram xatolari (odatda muhim emas)
    if isinstance(error, (NetworkError, TimedOut)):
        logger.warning(f"Tarmoq xatosi: {error}")
        return

    if isinstance(error, Forbidden):
        # Foydalanuvchi botni bloklagan
        logger.debug(f"Bot bloklangan: {error}")
        return

    if isinstance(error, BadRequest):
        if "message is not modified" in str(error).lower():
            return
        if "query is too old" in str(error).lower():
            return
        logger.warning(f"BadRequest: {error}")
        return

    # Qolgan barcha xatolar
    logger.error(f"Kutilmagan xato: {error}", exc_info=error)

    # Foydalanuvchiga xabar berish
    if isinstance(update, Update) and update.effective_chat:
        try:
            from locales import get_text
            lang = "uz"
            if update.effective_user and context.user_data.get("lang"):
                lang = context.user_data["lang"]
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=get_text("error_general", lang),
            )
        except Exception:
            pass

    # Xatoni statistikaga yozish
    if isinstance(update, Update) and update.effective_user:
        try:
            db: Database = context.bot_data.get("db")
            if db:
                await db.log_action(
                    update.effective_user.id,
                    "error_occurred",
                    str(error)[:200],
                )
        except Exception:
            pass


# ── Barcha handlerlarni ro'yxatga olish ──────────────────────────────────────

def register_handlers(application: Application) -> None:
    """
    Barcha handlerlarni Application ga ro'yxatga olish.
    Tartib muhim: aniq patternlar avval, umumiylar oxirda.
    """

    # ── 1. Start, Help, Lang handlerlari ──────────────────────────────────────
    for handler in get_start_handlers():
        application.add_handler(handler)

    # Til va yopish callback lari
    application.add_handler(
        CallbackQueryHandler(handle_lang_callback, pattern=r"^lang_(uz|ru|en)$")
    )
    application.add_handler(
        CallbackQueryHandler(handle_close_callback, pattern=r"^(close_msg|settings_close)$")
    )

    # ── 2. Admin handlerlari (kuchli prioritet uchun avval) ───────────────────
    for handler in get_admin_handlers():
        application.add_handler(handler)

    # ── 3. Sozlamalar handlerlari ─────────────────────────────────────────────
    for handler in get_settings_handlers():
        application.add_handler(handler)

    # ── 4. PDF va collect handlerlari ─────────────────────────────────────────
    for handler in get_pdf_handlers():
        application.add_handler(handler)

    # ── 5. Reverse handlerlari ────────────────────────────────────────────────
    for handler in get_reverse_handlers():
        application.add_handler(handler)

    # ── 6. Rasm handlerlari (oxirda, chunki umumiy) ───────────────────────────
    for handler in get_image_handlers():
        application.add_handler(handler)

    # ── 7. Global xato handler ────────────────────────────────────────────────
    application.add_error_handler(error_handler)

    logger.info("Barcha handlerlar ro'yxatga olindi")


# ── Asosiy ishga tushirish funksiyasi ─────────────────────────────────────────

def main() -> None:
    """
    Botni ishga tushirish — asosiy funksiya.
    """
    setup_logging()

    logger.info("=" * 50)
    logger.info("  IMAGE TO PDF PRO BOT ishga tushmoqda...")
    logger.info("=" * 50)

    # Papkalarni tekshirish
    for directory in [TEMP_DIR, HISTORY_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    # Application yaratish
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    # Handlerlarni ro'yxatga olish
    register_handlers(application)

    logger.info("Bot polling boshlandi (Ctrl+C bilan to'xtatish)")

    # Botni ishga tushirish
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
        close_loop=True,
    )


if __name__ == "__main__":
    main()
