"""
Admin Handler — bot administratori uchun boshqaruv buyruqlari.
Statistika, broadcast, ban/unban, cleanup va log ko'rish.
Faqat ADMIN_IDS da ko'rsatilgan foydalanuvchilar uchun.
"""

import os
import asyncio
from pathlib import Path
from datetime import datetime

from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from config import ADMIN_IDS, TEMP_DIR, LOG_DIR
from utils.helpers import get_user_lang, t, is_admin, format_file_size, format_datetime
from utils.keyboards import get_admin_keyboard
from database import Database


def admin_only(func):
    """
    Admin faqat decorator — faqat adminlar foydalana oladigan handler uchun.
    Admin bo'lmasa xabar yuboriladi.
    """
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user:
            return
        user_id = update.effective_user.id
        if not is_admin(user_id):
            lang = await get_user_lang(user_id, context)
            if update.message:
                await update.message.reply_text(t("admin_only", lang))
            elif update.callback_query:
                await update.callback_query.answer(
                    t("admin_only", "uz"), show_alert=True
                )
            return
        return await func(update, context)
    wrapper.__name__ = func.__name__
    return wrapper


@admin_only
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /admin buyrug'i — admin panel va statistikani ko'rsatish.
    """
    if not update.message:
        return

    user = update.effective_user
    lang = await get_user_lang(user.id, context)
    db: Database = context.bot_data.get("db")

    try:
        stats = {}
        if db:
            stats = await db.get_global_stats()

        top_actions_text = ""
        for item in stats.get("top_actions", []):
            top_actions_text += f"  • {item['action']}: {item['count']}\n"

        panel_text = t(
            "admin_panel", lang,
            total_users=stats.get("total_users", 0),
            active_today=stats.get("active_today", 0),
            total_pdfs=stats.get("total_pdfs", 0),
            pdfs_today=stats.get("pdfs_today", 0),
            banned_users=stats.get("banned_users", 0),
            top_actions=top_actions_text or "  Hali statistika yo'q",
        )

        keyboard = get_admin_keyboard(lang)
        await update.message.reply_html(panel_text, reply_markup=keyboard)

        logger.info(f"Admin panel: {user.id}")

    except Exception as e:
        logger.error(f"admin_command xatosi: {e}")
        await update.message.reply_text(t("error_general", lang))


@admin_only
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /broadcast [matn] — barcha foydalanuvchilarga xabar yuborish.
    """
    if not update.message or not update.effective_user:
        return

    user = update.effective_user
    lang = await get_user_lang(user.id, context)
    db: Database = context.bot_data.get("db")

    # Matn tekshiruvi
    message_text = " ".join(context.args) if context.args else ""
    if not message_text:
        await update.message.reply_text(t("broadcast_usage", lang))
        return

    try:
        if not db:
            await update.message.reply_text(t("error_general", lang))
            return

        all_users = await db.get_all_users()
        total = len(all_users)

        status_msg = await update.message.reply_text(
            f"{t('broadcast_started', lang)} (0/{total})"
        )

        sent = 0
        failed = 0

        for i, user_data in enumerate(all_users):
            # Bloklangan va admin foydalanuvchilarni o'tkazib yuborish
            if user_data.get("is_banned"):
                failed += 1
                continue

            try:
                await context.bot.send_message(
                    chat_id=user_data["user_id"],
                    text=f"📢 {message_text}",
                )
                sent += 1
                # Telegram flood limit: 30 xabar/sekund
                await asyncio.sleep(0.05)
            except Exception as e:
                failed += 1
                logger.debug(f"Broadcast xatosi (user={user_data['user_id']}): {e}")

            # Har 50 ta foydalanuvchida progress yangilash
            if (i + 1) % 50 == 0:
                try:
                    await status_msg.edit_text(
                        f"{t('broadcast_started', lang)} ({i+1}/{total})"
                    )
                except Exception:
                    pass

        # Natija
        result = t("broadcast_done", lang, sent=sent, failed=failed)
        await status_msg.edit_text(result)

        logger.info(f"Broadcast yakunlandi: {sent} yuborildi, {failed} xato")

    except Exception as e:
        logger.error(f"broadcast_command xatosi: {e}")
        await update.message.reply_text(t("error_general", lang))


@admin_only
async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /ban [user_id] — foydalanuvchini bloklash.
    """
    if not update.message:
        return

    user = update.effective_user
    lang = await get_user_lang(user.id, context)
    db: Database = context.bot_data.get("db")

    args = context.args
    if not args or not args[0].lstrip("-").isdigit():
        await update.message.reply_text(t("ban_usage", lang))
        return

    target_id = int(args[0])

    try:
        if not db:
            return

        target_user = await db.get_user(target_id)
        if not target_user:
            await update.message.reply_text(t("ban_not_found", lang))
            return

        # Admin ni bloklash mumkin emas
        if is_admin(target_id):
            await update.message.reply_text("❌ Admin ni bloklash mumkin emas!")
            return

        success = await db.ban_user(target_id)
        if success:
            await update.message.reply_text(t("ban_done", lang, user_id=target_id))
            logger.info(f"Foydalanuvchi bloklandi: {target_id} (admin={user.id})")
        else:
            await update.message.reply_text(t("error_general", lang))

    except Exception as e:
        logger.error(f"ban_command xatosi: {e}")
        await update.message.reply_text(t("error_general", lang))


@admin_only
async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /unban [user_id] — foydalanuvchini blokdan chiqarish.
    """
    if not update.message:
        return

    user = update.effective_user
    lang = await get_user_lang(user.id, context)
    db: Database = context.bot_data.get("db")

    args = context.args
    if not args or not args[0].lstrip("-").isdigit():
        await update.message.reply_text("Foydalanish: /unban [user_id]")
        return

    target_id = int(args[0])

    try:
        if not db:
            return

        success = await db.unban_user(target_id)
        if success:
            await update.message.reply_text(t("unban_done", lang, user_id=target_id))
            logger.info(f"Blokdan chiqarildi: {target_id}")
        else:
            await update.message.reply_text(t("error_general", lang))

    except Exception as e:
        logger.error(f"unban_command xatosi: {e}")
        await update.message.reply_text(t("error_general", lang))


@admin_only
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /stats [user_id] — bitta foydalanuvchi statistikasini ko'rsatish.
    """
    if not update.message:
        return

    user = update.effective_user
    lang = await get_user_lang(user.id, context)
    db: Database = context.bot_data.get("db")

    args = context.args
    if not args:
        await update.message.reply_text(t("stats_usage", lang))
        return

    # User ID yoki username qidirish
    query_str = args[0].lstrip("@")

    try:
        if not db:
            return

        users = await db.search_user(query_str)
        if not users:
            await update.message.reply_text(t("ban_not_found", lang))
            return

        # Birinchi topilgan foydalanuvchi
        target = users[0]
        target_id = target["user_id"]

        user_stats = await db.get_user_stats(target_id)

        stats_text = t(
            "stats_user", lang,
            user_id=target_id,
            full_name=target.get("full_name", "—"),
            username=target.get("username") or "—",
            lang=target.get("lang", "uz"),
            joined_at=format_datetime(target.get("joined_at")),
            last_active=format_datetime(target.get("last_active")),
            is_banned="Ha ✓" if target.get("is_banned") else "Yo'q",
            total_pdfs=user_stats.get("total_pdfs", 0),
            ocr_count=user_stats.get("ocr_count", 0),
            reverse_count=user_stats.get("reverse_count", 0),
            history_count=user_stats.get("history_count", 0),
        )

        await update.message.reply_html(stats_text)

    except Exception as e:
        logger.error(f"stats_command xatosi: {e}")
        await update.message.reply_text(t("error_general", lang))


@admin_only
async def cleanup_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /cleanup — vaqtinchalik fayllarni qo'lda tozalash.
    """
    if not update.message:
        return

    user = update.effective_user
    lang = await get_user_lang(user.id, context)

    try:
        from utils.helpers import cleanup_dir_files
        count = cleanup_dir_files(TEMP_DIR, older_than_minutes=0)

        await update.message.reply_text(t("cleanup_done", lang, count=count))
        logger.info(f"Admin cleanup: {count} fayl o'chirildi")

    except Exception as e:
        logger.error(f"cleanup_command xatosi: {e}")
        await update.message.reply_text(t("error_general", lang))


@admin_only
async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /logs — oxirgi 50 ta xatolikni ko'rsatish (log fayldan).
    """
    if not update.message:
        return

    user = update.effective_user
    lang = await get_user_lang(user.id, context)

    try:
        log_file = LOG_DIR / "errors.log"
        if not log_file.exists():
            await update.message.reply_text(t("logs_empty", lang))
            return

        # Oxirgi 50 qatorni o'qish
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        last_lines = lines[-50:] if len(lines) >= 50 else lines

        if not last_lines:
            await update.message.reply_text(t("logs_empty", lang))
            return

        log_text = t("logs_title", lang, count=len(last_lines))
        log_content = "".join(last_lines)

        # Telegram 4096 belgi limiti
        if len(log_text + log_content) > 4000:
            log_content = log_content[-3500:]

        full_text = f"<pre>{log_text}{log_content}</pre>"

        await update.message.reply_html(full_text)

    except Exception as e:
        logger.error(f"logs_command xatosi: {e}")
        await update.message.reply_text(t("error_general", lang))


# ── Admin panel callback handleri ─────────────────────────────────────────────

@admin_only
async def handle_admin_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Admin panel callback handleri.
    adm_stats, adm_refresh, adm_cleanup, adm_logs, adm_close
    """
    query = update.callback_query
    if not query or not update.effective_user:
        return

    await query.answer()
    user = update.effective_user
    data = query.data
    lang = await get_user_lang(user.id, context)
    db: Database = context.bot_data.get("db")

    try:
        if data in ("adm_stats", "adm_refresh"):
            # Statistikani yangilash
            stats = {}
            if db:
                stats = await db.get_global_stats()

            top_actions_text = ""
            for item in stats.get("top_actions", []):
                top_actions_text += f"  • {item['action']}: {item['count']}\n"

            panel_text = t(
                "admin_panel", lang,
                total_users=stats.get("total_users", 0),
                active_today=stats.get("active_today", 0),
                total_pdfs=stats.get("total_pdfs", 0),
                pdfs_today=stats.get("pdfs_today", 0),
                banned_users=stats.get("banned_users", 0),
                top_actions=top_actions_text or "  Hali statistika yo'q",
            )

            keyboard = get_admin_keyboard(lang)
            await query.edit_message_text(
                panel_text, reply_markup=keyboard, parse_mode="HTML"
            )

        elif data == "adm_cleanup":
            from utils.helpers import cleanup_dir_files
            count = cleanup_dir_files(TEMP_DIR, older_than_minutes=0)
            await query.answer(
                f"✅ {count} ta vaqtinchalik fayl o'chirildi", show_alert=True
            )

        elif data == "adm_logs":
            log_file = LOG_DIR / "errors.log"
            if not log_file.exists():
                await query.answer(t("logs_empty", lang), show_alert=True)
                return

            with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            last_lines = lines[-20:] if len(lines) >= 20 else lines
            log_text = "".join(last_lines) if last_lines else "Bo'sh"

            if len(log_text) > 200:
                log_text = "..." + log_text[-200:]

            await query.answer(log_text[:200], show_alert=True)

        elif data == "adm_close":
            await query.delete_message()

    except Exception as e:
        logger.error(f"handle_admin_callback xatosi: {e}")
        try:
            await query.answer(t("error_general", lang), show_alert=True)
        except Exception:
            pass


def get_admin_handlers() -> list:
    """
    Admin handlerlarini ro'yxat sifatida qaytarish.
    """
    return [
        CommandHandler("admin",     admin_command),
        CommandHandler("broadcast", broadcast_command),
        CommandHandler("ban",       ban_command),
        CommandHandler("unban",     unban_command),
        CommandHandler("stats",     stats_command),
        CommandHandler("cleanup",   cleanup_command),
        CommandHandler("logs",      logs_command),
        # Admin panel callback
        CallbackQueryHandler(
            handle_admin_callback,
            pattern=r"^adm_",
        ),
    ]
