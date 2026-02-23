"""
PDF Handler — ko'p rasmli PDF yaratish va tarix boshqaruvi.
/collect, /done, /cancel, /order, /history buyruqlari.
"""

from pathlib import Path

from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from config import TEMP_DIR, MAX_IMAGES_PER_SESSION
from utils.helpers import (
    get_user_lang, format_file_size, t, check_rate_limit,
    cleanup_file, cleanup_files, parse_order, get_timestamp,
    progress_text, safe_answer_callback,
)
from utils.keyboards import get_history_keyboard, get_collect_done_keyboard
from services.pdf_converter import PDFConverter
from database import Database


# ── Ko'p rasmli yig'ish rejimi ────────────────────────────────────────────────

async def collect_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /collect buyrug'i — ko'p rasm yig'ish rejimini boshlash.
    """
    if not update.message or not update.effective_user:
        return

    user = update.effective_user
    lang = await get_user_lang(user.id, context)
    db: Database = context.bot_data.get("db")

    # Rate limit tekshirish
    if not await check_rate_limit(update, context):
        return

    try:
        # Bloklangan foydalanuvchini tekshirish
        if db and await db.is_banned(user.id):
            await update.message.reply_text(t("error_banned", lang))
            return

        # Allaqachon yig'ish rejimida bo'lsa
        if context.user_data.get("collect_mode"):
            count = len(context.user_data.get("collect_images", []))
            keyboard = get_collect_done_keyboard(lang, count) if count > 0 else None
            await update.message.reply_text(
                t("collect_already_active", lang),
                reply_markup=keyboard,
            )
            return

        # Yig'ish rejimini boshlash
        context.user_data["collect_mode"] = True
        context.user_data["collect_images"] = []

        # Ma'lumotlar bazasida sessiya yaratish
        if db:
            await db.create_session(user.id, mode="collecting")

        await update.message.reply_html(
            t("collect_started", lang, max_images=MAX_IMAGES_PER_SESSION)
        )

        logger.info(f"Collect rejim boshlandi: user={user.id}")

    except Exception as e:
        logger.error(f"collect_command xatosi: {e}")
        await update.message.reply_text(t("error_general", lang))


async def done_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /done buyrug'i — yig'ish rejimini tugatib, PDF yaratish.
    """
    if not update.message or not update.effective_user:
        return

    user = update.effective_user
    lang = await get_user_lang(user.id, context)

    try:
        await _finish_collect(update, context)
    except Exception as e:
        logger.error(f"done_command xatosi: {e}")
        await update.message.reply_text(t("error_general", lang))


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /cancel buyrug'i — joriy rejimni bekor qilish.
    """
    if not update.message or not update.effective_user:
        return

    user = update.effective_user
    lang = await get_user_lang(user.id, context)

    try:
        await _cancel_collect(update, context)
    except Exception as e:
        logger.error(f"cancel_command xatosi: {e}")
        await update.message.reply_text(t("error_general", lang))


async def order_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /order buyrug'i — yig'ilgan rasmlar tartibini o'zgartirish.
    Foydalanish: /order 3,1,2,4
    """
    if not update.message or not update.effective_user:
        return

    user = update.effective_user
    lang = await get_user_lang(user.id, context)

    try:
        collect_images = context.user_data.get("collect_images", [])

        # Rasmlar yo'qligi tekshiruvi
        if not collect_images:
            await update.message.reply_text(t("order_no_images", lang))
            return

        # Buyruq argumentini olish
        args = context.args
        if not args:
            # Yordam ko'rsatish
            image_list = "\n".join(
                f"  {i+1}. {Path(p).name}"
                for i, p in enumerate(collect_images)
            )
            await update.message.reply_html(
                t("order_help", lang, image_list=image_list)
            )
            return

        order_str = " ".join(args)
        new_order = parse_order(order_str, len(collect_images))

        if new_order is None:
            await update.message.reply_text(t("order_invalid", lang))
            return

        # Tartibni o'zgartirish
        reordered = [collect_images[i] for i in new_order]
        context.user_data["collect_images"] = reordered

        # DB da yangilash
        db: Database = context.bot_data.get("db")
        if db:
            await db.update_session(user.id, images_data=reordered)

        count = len(reordered)
        await update.message.reply_text(
            f"{t('order_applied', lang)}\n\n"
            + "\n".join(f"  {i+1}. {Path(p).name}" for i, p in enumerate(reordered))
        )

        logger.debug(f"Rasm tartibi o'zgartirildi: user={user.id}")

    except Exception as e:
        logger.error(f"order_command xatosi: {e}")
        await update.message.reply_text(t("error_general", lang))


async def _finish_collect(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Ko'p rasmli yig'ish rejimini tugatish va PDF yaratish.
    /done buyrug'i yoki 'PDF Qil' tugmasi tomonidan chaqiriladi.
    """
    if not update.effective_user:
        return

    user = update.effective_user
    lang = await get_user_lang(user.id, context)
    db: Database = context.bot_data.get("db")

    # Rasmlar ro'yxatini olish
    collect_images = context.user_data.get("collect_images", [])

    if not collect_images:
        if update.message:
            await update.message.reply_text(t("collect_no_images", lang))
        elif update.callback_query:
            await update.callback_query.edit_message_text(
                t("collect_no_images", lang)
            )
        return

    # Yig'ish rejimi faol emasligini tekshirish
    if not context.user_data.get("collect_mode"):
        if update.message:
            await update.message.reply_text(t("collect_not_active", lang))
        return

    try:
        # Progress xabari
        total = len(collect_images)
        status_msg = None

        if update.message:
            status_msg = await update.message.reply_text(
                t("collect_done_creating", lang,
                  bar=progress_text(0, total),
                  percent=0)
            )
        elif update.callback_query:
            await update.callback_query.edit_message_text(
                t("collect_done_creating", lang,
                  bar=progress_text(0, total),
                  percent=0)
            )

        # Sozlamalarni olish
        settings = {"quality": "high", "pagesize": "A4",
                    "orientation": "portrait", "margin": "small"}
        if db:
            user_settings = await db.get_settings(user.id)
            settings.update(user_settings)

        output_path = PDFConverter.generate_output_path("merged")

        # Progress yangilash funksiyasi
        async def update_progress(current: int, total: int):
            try:
                prog = progress_text(current, total)
                percent = int(100 * current / total)
                new_text = t("collect_done_creating", lang,
                              bar=prog, percent=percent)
                if status_msg:
                    await status_msg.edit_text(new_text)
                elif update.callback_query:
                    await update.callback_query.edit_message_text(new_text)
            except Exception:
                pass

        # PDF yaratish
        success, err = await PDFConverter.convert_multiple_images(
            collect_images,
            output_path,
            settings,
            progress_callback=update_progress,
        )

        if not success:
            err_msg = t("pdf_error", lang)
            if status_msg:
                await status_msg.edit_text(err_msg)
            return

        pdf_size = output_path.stat().st_size
        page_count = await PDFConverter.get_pdf_page_count(output_path)

        # PDF ni yuborish
        if status_msg:
            await status_msg.edit_text(t("progress_sending", lang))

        with open(output_path, "rb") as pdf_file:
            sent_doc = await update.effective_chat.send_document(
                document=pdf_file,
                filename=output_path.name,
                caption=t("pdf_ready", lang,
                           size=format_file_size(pdf_size),
                           pages=page_count),
                parse_mode="HTML",
            )

        # Tarixga saqlash
        if db and sent_doc:
            await db.add_history(
                user_id=user.id,
                file_id=sent_doc.document.file_id,
                file_name=output_path.name,
                file_size=pdf_size,
                pages=page_count,
            )
            await db.log_action(user.id, "pdf_created")
            await db.log_action(user.id, "multi_pdf")

        # Status xabarini o'chirish
        if status_msg:
            try:
                await status_msg.delete()
            except Exception:
                pass
        elif update.callback_query:
            try:
                await update.callback_query.delete_message()
            except Exception:
                pass

        logger.info(
            f"Ko'p rasmli PDF yuborildi: user={user.id}, "
            f"rasmlar={total}, pdf_size={pdf_size:,}"
        )

    except Exception as e:
        logger.error(f"_finish_collect xatosi: {e}")
        try:
            err_text = t("pdf_error", lang)
            if update.message:
                await update.message.reply_text(err_text)
            elif update.callback_query:
                await update.callback_query.edit_message_text(err_text)
        except Exception:
            pass
    finally:
        # Har holda state va vaqtinchalik fayllarni tozalash
        images_to_clean = context.user_data.get("collect_images", [])
        await cleanup_files(images_to_clean)
        if 'output_path' in dir() and output_path and output_path.exists():
            await cleanup_file(output_path)

        context.user_data["collect_mode"] = False
        context.user_data["collect_images"] = []

        # DB sessiyasini o'chirish
        if db:
            await db.delete_session(user.id)


async def _cancel_collect(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Ko'p rasmli yig'ish rejimini bekor qilish.
    """
    if not update.effective_user:
        return

    user = update.effective_user
    lang = await get_user_lang(user.id, context)
    db: Database = context.bot_data.get("db")

    # Vaqtinchalik fayllarni tozalash
    images_to_clean = context.user_data.get("collect_images", [])
    await cleanup_files(images_to_clean)

    # State ni tozalash
    context.user_data["collect_mode"] = False
    context.user_data["collect_images"] = []

    # DB sessiyasini o'chirish
    if db:
        await db.delete_session(user.id)

    cancel_text = t("collect_cancelled", lang)
    try:
        if update.message:
            await update.message.reply_text(cancel_text)
        elif update.callback_query:
            await update.callback_query.edit_message_text(cancel_text)
    except Exception as e:
        logger.debug(f"_cancel_collect xabari xatosi: {e}")

    logger.info(f"Collect bekor qilindi: user={user.id}")


# ── PDF Tarix ─────────────────────────────────────────────────────────────────

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /history buyrug'i — foydalanuvchining PDF tarixini ko'rsatish.
    """
    if not update.message or not update.effective_user:
        return

    user = update.effective_user
    lang = await get_user_lang(user.id, context)

    # Rate limit tekshirish
    if not await check_rate_limit(update, context):
        return

    db: Database = context.bot_data.get("db")

    try:
        if not db:
            await update.message.reply_text(t("error_general", lang))
            return

        # Bloklangan foydalanuvchi
        if await db.is_banned(user.id):
            await update.message.reply_text(t("error_banned", lang))
            return

        history = await db.get_history(user.id)

        if not history:
            await update.message.reply_text(t("history_empty", lang))
            return

        # Tarix ro'yxatini ko'rsatish
        text = t("history_title", lang) + "\n\n"
        from utils.helpers import format_datetime

        for i, item in enumerate(history, 1):
            text += t(
                "history_item", lang,
                name=item.get("file_name", "document.pdf"),
                size=format_file_size(item.get("file_size", 0)),
                date=format_datetime(item.get("created_at")),
                pages=item.get("pages", 1),
            ) + "\n"

        keyboard = get_history_keyboard(history, lang)
        await update.message.reply_html(text, reply_markup=keyboard)

    except Exception as e:
        logger.error(f"history_command xatosi: {e}")
        await update.message.reply_text(t("error_general", lang))


async def handle_history_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Tarix callback handleri — yuklab olish va o'chirish.
    hi_dl_{id}, hi_rm_{id}, hi_info_{id}, hist_close
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
        if data == "hist_close":
            await query.delete_message()
            return

        parts = data.split("_")
        if len(parts) < 3:
            return

        action = parts[1]        # 'dl' yoki 'rm' yoki 'info'
        item_id_str = parts[2]   # raqam

        if not item_id_str.isdigit():
            return
        item_id = int(item_id_str)

        if not db:
            return

        if action == "dl":
            # Tarixdan yuklab olish
            history = await db.get_history(user.id)
            item = next((h for h in history if h["id"] == item_id), None)

            if not item:
                await query.answer(t("history_not_found", lang), show_alert=True)
                return

            # Telegram file_id orqali qayta yuborish
            file_id = item.get("file_id")
            if not file_id:
                await query.answer(t("history_not_found", lang), show_alert=True)
                return

            from utils.helpers import format_datetime
            await update.effective_chat.send_document(
                document=file_id,
                caption=(
                    f"📄 {item.get('file_name', 'document.pdf')}\n"
                    f"📦 {format_file_size(item.get('file_size', 0))}\n"
                    f"📅 {format_datetime(item.get('created_at'))}"
                ),
            )

        elif action == "rm":
            # Tarixdan o'chirish
            success = await db.delete_history_item(item_id, user.id)
            if success:
                await query.answer(t("history_deleted", lang), show_alert=False)
                # Tarixni yangilash
                history = await db.get_history(user.id)
                if history:
                    text = t("history_title", lang) + "\n\n"
                    from utils.helpers import format_datetime
                    for item in history:
                        text += t(
                            "history_item", lang,
                            name=item.get("file_name", "document.pdf"),
                            size=format_file_size(item.get("file_size", 0)),
                            date=format_datetime(item.get("created_at")),
                            pages=item.get("pages", 1),
                        ) + "\n"
                    keyboard = get_history_keyboard(history, lang)
                    try:
                        await query.edit_message_text(
                            text, reply_markup=keyboard, parse_mode="HTML"
                        )
                    except Exception:
                        pass
                else:
                    try:
                        await query.edit_message_text(t("history_empty", lang))
                    except Exception:
                        pass
            else:
                await query.answer(t("history_not_found", lang), show_alert=True)

        elif action == "info":
            # Ma'lumot ko'rsatish (hozircha faqat javob)
            history = await db.get_history(user.id)
            item = next((h for h in history if h["id"] == item_id), None)
            if item:
                from utils.helpers import format_datetime
                info = (
                    f"📄 {item.get('file_name', 'document.pdf')}\n"
                    f"📦 Hajm: {format_file_size(item.get('file_size', 0))}\n"
                    f"📃 Sahifalar: {item.get('pages', 1)}\n"
                    f"📅 Sana: {format_datetime(item.get('created_at'))}"
                )
                await query.answer(info, show_alert=True)

    except Exception as e:
        logger.error(f"handle_history_callback xatosi: {e}")
        try:
            await query.answer(t("error_general", lang), show_alert=True)
        except Exception:
            pass


def get_pdf_handlers() -> list:
    """
    PDF va collect handlerlarini ro'yxat sifatida qaytarish.
    """
    return [
        CommandHandler("collect", collect_command),
        CommandHandler("done",    done_command),
        CommandHandler("cancel",  cancel_command),
        CommandHandler("order",   order_command),
        CommandHandler("history", history_command),
        # Tarix callback lari
        CallbackQueryHandler(
            handle_history_callback,
            pattern=r"^(hi_dl_|hi_rm_|hi_info_|hist_close)",
        ),
    ]
