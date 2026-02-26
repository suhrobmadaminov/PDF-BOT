"""
Reverse Handler — PDF faylni rasmlarga ajratish.
/reverse buyrug'i va PDF fayl xabarlari uchun handler.
Sahifa oralig'ini qo'llab-quvvatlaydi va ko'p sahifali PDF lar uchun ZIP yaratadi.
"""

from pathlib import Path

from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from config import TEMP_DIR
from utils.helpers import (
    get_user_lang, format_file_size, t, check_rate_limit,
    cleanup_file, cleanup_files, parse_page_range, get_timestamp,
    validate_pdf, safe_answer_callback,
)
from utils.keyboards import get_reverse_format_keyboard, get_close_keyboard
from services.file_optimizer import FileOptimizer
from database import Database


# Sahifa oralig'i kiritish uchun state kaliti
WAITING_PAGE_RANGE = "reverse_waiting_range"
REVERSE_PDF_PATH = "reverse_pdf_path"
REVERSE_FORMAT = "reverse_format"
REVERSE_TOTAL_PAGES = "reverse_total_pages"


async def reverse_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /reverse buyrug'i — PDF ni rasmlarga aylantirish.
    """
    if not update.message or not update.effective_user:
        return

    user = update.effective_user
    lang = await get_user_lang(user.id, context)

    if not await check_rate_limit(update, context):
        return

    try:
        # Agar PDF hozir saqlangan bo'lsa, format tanlashga o'tish
        if context.user_data.get(REVERSE_PDF_PATH):
            pdf_path = context.user_data[REVERSE_PDF_PATH]
            if Path(pdf_path).exists():
                info = await FileOptimizer.get_pdf_info(pdf_path)
                filename = Path(pdf_path).name
                keyboard = get_reverse_format_keyboard(lang)
                await update.message.reply_html(
                    t("reverse_select_fmt", lang,
                      filename=filename,
                      pages=info.get("page_count", "?")),
                    reply_markup=keyboard,
                )
                return

        await update.message.reply_text(t("reverse_prompt", lang))

    except Exception as e:
        logger.error(f"reverse_command xatosi: {e}")
        await update.message.reply_text(t("error_general", lang))


async def handle_pdf_document(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Foydalanuvchi PDF fayl yuborganda ishlaydi.
    PDF ni temp papkaga yuklaydi va format tanlash menyusini ko'rsatadi.
    """
    if not update.message or not update.effective_user:
        return

    user = update.effective_user
    message = update.message
    lang = await get_user_lang(user.id, context)
    db: Database = context.bot_data.get("db")

    if not await check_rate_limit(update, context):
        return

    try:
        # Bloklangan foydalanuvchi
        if db and await db.is_banned(user.id):
            await message.reply_text(t("error_banned", lang))
            return

        document = message.document
        if not document:
            return

        # PDF tekshiruvi
        valid, error = validate_pdf(
            document.mime_type,
            document.file_name,
            document.file_size or 0,
        )

        if not valid:
            await message.reply_text(t("error_not_pdf", lang))
            return

        # Fayl hajmi tekshiruvi
        if (document.file_size or 0) > 50 * 1024 * 1024:
            await message.reply_text(
                t("error_file_too_large", lang,
                  max_size="50 MB",
                  file_size=format_file_size(document.file_size or 0))
            )
            return

        # PDF ni yuklash
        status_msg = await message.reply_text(t("progress_uploading", lang))

        try:
            tg_file = await context.bot.get_file(document.file_id)
            pdf_filename = document.file_name or f"doc_{get_timestamp()}.pdf"
            local_path = TEMP_DIR / f"pdf_{user.id}_{get_timestamp()}.pdf"
            await tg_file.download_to_drive(str(local_path))
        except Exception as e:
            logger.error(f"PDF yuklab olishda xato: {e}")
            await status_msg.edit_text(t("error_download", lang))
            return

        pdf_size = local_path.stat().st_size
        logger.info(f"PDF yuklandi: {local_path.name}, {pdf_size:,} bayt")

        # PDF ma'lumotlarini olish
        info = await FileOptimizer.get_pdf_info(local_path)
        page_count = info.get("page_count", 0)

        if page_count == 0:
            await status_msg.edit_text(t("error_general", lang))
            await cleanup_file(local_path)
            return

        # PDF yo'lini saqlash
        # Eski PDF ni tozalash (agar bor bo'lsa)
        old_pdf = context.user_data.get(REVERSE_PDF_PATH)
        if old_pdf and old_pdf != str(local_path):
            await cleanup_file(old_pdf)

        context.user_data[REVERSE_PDF_PATH] = str(local_path)
        context.user_data[REVERSE_TOTAL_PAGES] = page_count

        # Format tanlash menyusi
        keyboard = get_reverse_format_keyboard(lang)
        await status_msg.edit_text(
            t("reverse_select_fmt", lang,
              filename=pdf_filename,
              pages=page_count),
            reply_markup=keyboard,
            parse_mode="HTML",
        )

        # Statistika
        if db:
            await db.update_last_active(user.id)

    except Exception as e:
        logger.error(f"handle_pdf_document xatosi: {e}")
        try:
            await message.reply_text(t("error_general", lang))
        except Exception:
            pass


async def handle_reverse_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Reverse format tanlash callback handleri.
    rev_jpg, rev_png, rev_zip, rev_cancel
    """
    query = update.callback_query
    if not query or not update.effective_user:
        return

    await query.answer()
    user = update.effective_user
    data = query.data
    lang = await get_user_lang(user.id, context)
    db: Database = context.bot_data.get("db")

    if data == "rev_cancel":
        # Bekor qilish
        pdf_path = context.user_data.pop(REVERSE_PDF_PATH, None)
        context.user_data.pop(REVERSE_FORMAT, None)
        context.user_data.pop(REVERSE_TOTAL_PAGES, None)
        context.user_data.pop(WAITING_PAGE_RANGE, None)

        if pdf_path:
            await cleanup_file(pdf_path)

        await query.edit_message_text("❌ Bekor qilindi.")
        return

    # PDF yo'lini tekshirish
    pdf_path = context.user_data.get(REVERSE_PDF_PATH)
    if not pdf_path or not Path(pdf_path).exists():
        await query.edit_message_text(t("reverse_no_pdf", lang))
        return

    # Format aniqlash
    format_map = {
        "rev_jpg": "jpg",
        "rev_png": "png",
        "rev_zip": "jpg",  # ZIP uchun JPG formatida
    }
    out_format = format_map.get(data, "jpg")
    use_zip = (data == "rev_zip")

    context.user_data[REVERSE_FORMAT] = out_format
    context.user_data["reverse_use_zip"] = use_zip

    # Barcha sahifalarni darhol konvertatsiya qilish (sahifa so'rovini skip qilish)
    total_pages = context.user_data.get(REVERSE_TOTAL_PAGES, 1)
    page_indices = list(range(total_pages))

    # Keyboard xabarini o'chirish
    try:
        await query.delete_message()
    except Exception:
        pass

    await _do_reverse_conversion(
        update, context, pdf_path, page_indices, lang, db
    )


async def handle_page_range_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Sahifa oralig'i kiritilganda ishlaydi.
    Foydalanuvchi '1-3, 5, 7-10' kabi matn yuboradi.
    """
    if not update.message or not update.effective_user:
        return

    user = update.effective_user
    message = update.message
    lang = await get_user_lang(user.id, context)
    db: Database = context.bot_data.get("db")

    # Sahifa oralig'i kutilmayaptimi?
    if not context.user_data.get(WAITING_PAGE_RANGE):
        return

    pdf_path = context.user_data.get(REVERSE_PDF_PATH)
    if not pdf_path or not Path(pdf_path).exists():
        await message.reply_text(t("reverse_no_pdf", lang))
        return

    try:
        total_pages = context.user_data.get(REVERSE_TOTAL_PAGES, 1)
        range_text = message.text.strip()

        # /all buyrug'i — barcha sahifalar
        if range_text.lower() in ("/all", "all", ""):
            page_indices = list(range(total_pages))
        else:
            page_indices = parse_page_range(range_text, total_pages)

        if page_indices is None:
            await message.reply_text(t("reverse_invalid_range", lang))
            return

        # State ni tozalash
        context.user_data.pop(WAITING_PAGE_RANGE, None)

        # Konvertatsiyani boshlash
        await _do_reverse_conversion(
            update, context, pdf_path, page_indices, lang, db
        )

    except Exception as e:
        logger.error(f"handle_page_range_input xatosi: {e}")
        await message.reply_text(t("error_general", lang))
        context.user_data.pop(WAITING_PAGE_RANGE, None)


async def _do_reverse_conversion(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    pdf_path: str,
    page_indices: list[int],
    lang: str,
    db,
) -> None:
    """
    PDF → Rasm konvertatsiyasini amalga oshirish.

    Args:
        pdf_path:     PDF fayl yo'li
        page_indices: Konvertatsiya qilinadigan sahifa indekslari (0-indexed)
        lang:         Foydalanuvchi tili
        db:           Database obyekti
    """
    user = update.effective_user
    out_format = context.user_data.get(REVERSE_FORMAT, "jpg")
    use_zip = context.user_data.get("reverse_use_zip", False)

    status_msg = await update.effective_chat.send_message(
        t("reverse_processing", lang)
    )

    image_paths = []
    zip_path = None

    try:
        # PDF → Rasmlar
        image_paths = await FileOptimizer.pdf_to_images(
            pdf_path,
            output_format=out_format,
            dpi=150,
            page_indices=page_indices,
        )

        if not image_paths:
            await status_msg.edit_text(t("reverse_error", lang, error="Rasm yaratilmadi"))
            return

        page_count = len(image_paths)

        # ZIP yaratish kerakmi?
        should_zip = use_zip or page_count > 5

        if should_zip:
            # ZIP arxiv yaratish
            zip_filename = f"pages_{get_timestamp()}.zip"
            zip_path = TEMP_DIR / zip_filename

            zip_ok = await FileOptimizer.create_zip_from_images(image_paths, zip_path)

            if not zip_ok:
                await status_msg.edit_text(t("reverse_error", lang, error="ZIP yaratilmadi"))
                return

            zip_size = zip_path.stat().st_size
            await status_msg.edit_text(t("progress_sending", lang))

            # ZIP ni yuborish
            with open(zip_path, "rb") as zf:
                await update.effective_chat.send_document(
                    document=zf,
                    filename=zip_filename,
                    caption=t("reverse_zip_done", lang, pages=page_count),
                )

            logger.info(f"ZIP yuborildi: {page_count} rasm, {zip_size:,} bayt")

        else:
            # Alohida rasmlarni yuborish
            await status_msg.edit_text(t("progress_sending", lang))

            for i, img_path in enumerate(image_paths):
                try:
                    with open(img_path, "rb") as img_file:
                        await update.effective_chat.send_photo(
                            photo=img_file,
                            caption=f"📄 Sahifa {page_indices[i] + 1}"
                            if i < len(page_indices) else f"📄 Sahifa {i+1}",
                        )
                except Exception as e:
                    logger.warning(f"Rasm yuborishda xato ({img_path}): {e}")

            logger.info(f"Rasmlar yuborildi: {page_count} ta")

        # Status xabarini o'chirish
        try:
            await status_msg.delete()
        except Exception:
            pass

        # Statistika
        if db:
            await db.log_action(user.id, "reverse_used")

    except Exception as e:
        logger.error(f"_do_reverse_conversion xatosi: {e}")
        try:
            await status_msg.edit_text(t("reverse_error", lang, error=str(e)))
        except Exception:
            pass
    finally:
        # Vaqtinchalik fayllarni tozalash
        await cleanup_files(image_paths)
        if zip_path:
            await cleanup_file(zip_path)
        await cleanup_file(pdf_path)

        # State ni tozalash
        context.user_data.pop(REVERSE_PDF_PATH, None)
        context.user_data.pop(REVERSE_FORMAT, None)
        context.user_data.pop(REVERSE_TOTAL_PAGES, None)
        context.user_data.pop("reverse_use_zip", None)


def get_reverse_handlers() -> list:
    """
    Reverse (PDF→Rasm) handlerlarini ro'yxat sifatida qaytarish.
    """
    return [
        CommandHandler("reverse", reverse_command),
        # PDF hujjatlar
        MessageHandler(
            filters.Document.PDF,
            handle_pdf_document,
        ),
        # Format tanlash callback lari
        CallbackQueryHandler(
            handle_reverse_callback,
            pattern=r"^rev_(jpg|png|zip|cancel)$",
        ),
    ]
