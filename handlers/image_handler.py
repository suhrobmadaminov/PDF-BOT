"""
Rasm Handler — foydalanuvchi yuborgan rasmlarni qabul qilish va qayta ishlash.
Bitta rasm → inline klaviatura ko'rsatish.
Ko'p rasmli rejimda → to'plamga qo'shish.
Tahrirlash rejimida → amallarni qo'llash.
"""

import os
from pathlib import Path
from datetime import datetime

from loguru import logger
from telegram import Update, Message
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler

from config import TEMP_DIR, MAX_FILE_SIZE, MAX_IMAGES_PER_SESSION
from utils.helpers import (
    get_user_lang, format_file_size, t, check_rate_limit,
    validate_image, cleanup_file, get_timestamp, safe_answer_callback,
)
from utils.keyboards import (
    get_image_actions_keyboard, get_edit_menu_keyboard,
    get_brightness_keyboard, get_contrast_keyboard,
    get_rotation_keyboard, get_after_edit_keyboard,
)
from services.pdf_converter import PDFConverter
from services.image_editor import ImageEditor
from database import Database


async def _safe_edit_text(query, text: str, **kwargs) -> None:
    """
    Xabarni xavfsiz tahrirlash: photo message bo'lsa o'chirib yangi text yuboradi.
    """
    try:
        await query.edit_message_text(text, **kwargs)
    except Exception as e:
        if "no text" in str(e).lower() or "message to edit" in str(e).lower():
            try:
                await query.message.delete()
            except Exception:
                pass
            await query.message.chat.send_message(text, **kwargs)
        else:
            raise


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Foydalanuvchi rasm yuborganda ishlaydigan asosiy handler.

    Uch holatni qo'llab-quvvatlaydi:
    1. Oddiy holat → inline klaviatura ko'rsatish
    2. Ko'p rasm yig'ish rejimi (collect mode) → to'plamga qo'shish
    3. Bloklangan foydalanuvchi → javob bermaslik
    """
    if not update.message or not update.effective_user:
        return

    user = update.effective_user
    message = update.message

    # Rate limit tekshirish
    if not await check_rate_limit(update, context):
        return

    db: Database = context.bot_data.get("db")

    try:
        # Bloklangan foydalanuvchini tekshirish
        if db and await db.is_banned(user.id):
            lang = await get_user_lang(user.id, context)
            await message.reply_text(t("error_banned", lang))
            return

        # Foydalanuvchini bazaga qo'shish (yangi bo'lsa)
        if db:
            await db.get_or_create_user(user.id, user.username, user.full_name)
            await db.update_last_active(user.id)

        lang = await get_user_lang(user.id, context)

        # Rasm ma'lumotlarini olish
        photo = message.photo
        document = message.document

        if photo:
            # Telegram Photo — eng katta o'lchamni olish
            file_obj = photo[-1]
            file_id = file_obj.file_id
            file_size = file_obj.file_size or 0
            file_name = f"photo_{get_timestamp()}.jpg"
            mime_type = "image/jpeg"
        elif document:
            # Hujjat sifatida yuborilgan rasm
            file_id = document.file_id
            file_size = document.file_size or 0
            file_name = document.file_name or f"image_{get_timestamp()}"
            mime_type = document.mime_type or ""
        else:
            await message.reply_text(t("error_not_image", lang))
            return

        # Format va hajm tekshiruvi
        valid, error_reason = validate_image(mime_type, file_name, file_size)
        if not valid:
            if error_reason == "too_large":
                await message.reply_text(
                    t("error_file_too_large", lang,
                      max_size=format_file_size(MAX_FILE_SIZE),
                      file_size=format_file_size(file_size))
                )
            else:
                await message.reply_text(t("error_invalid_format", lang))
            return

        # Faylni temp papkaga yuklash
        status_msg = await message.reply_text(t("progress_uploading", lang))

        try:
            tg_file = await context.bot.get_file(file_id)
            local_path = TEMP_DIR / f"img_{user.id}_{get_timestamp()}.jpg"
            await tg_file.download_to_drive(str(local_path))
        except Exception as e:
            logger.error(f"Rasm yuklab olishda xato: {e}")
            await status_msg.edit_text(t("error_download", lang))
            return

        # Yuklangan fayl hajmini tekshirish
        actual_size = local_path.stat().st_size if local_path.exists() else 0
        logger.info(f"Rasm yuklandi: {local_path.name}, {actual_size:,} bayt")

        # Ko'p rasm yig'ish rejimini tekshirish
        if context.user_data.get("collect_mode"):
            await _add_to_collect(
                update, context, local_path, file_name, lang, status_msg
            )
            return

        # Oddiy holat — inline klaviatura ko'rsatish
        # Joriy rasmni session da saqlash
        context.user_data["current_image"] = {
            "original_path":  str(local_path),
            "work_path":      str(local_path),
            "file_id":        file_id,
            "file_name":      file_name,
            "file_size":      actual_size,
            "from_msg_id":    message.message_id,
        }

        # Edit sessiyasini ham tayyorlash
        edit_session = ImageEditor.create_work_session(local_path)
        context.user_data["edit_session"] = edit_session

        size_str = format_file_size(actual_size)
        caption = t("image_actions_caption", lang,
                    filename=file_name, size=size_str)

        keyboard = get_image_actions_keyboard(lang)

        await status_msg.delete()
        await message.reply_text(
            f"📥 {caption}\n\n{t('image_received', lang)}",
            reply_markup=keyboard,
            parse_mode="HTML",
        )

        # Statistikaga yozish
        if db:
            await db.log_action(user.id, "image_received")

    except Exception as e:
        logger.error(f"handle_image xatosi (user={user.id}): {e}")
        try:
            lang = await get_user_lang(user.id, context)
            await message.reply_text(t("error_general", lang))
        except Exception:
            pass


async def _add_to_collect(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    local_path: Path,
    file_name: str,
    lang: str,
    status_msg: Message,
) -> None:
    """
    Ko'p rasm yig'ish rejimida rasmni to'plamga qo'shish.

    Args:
        local_path: Yuklangan rasm lokal yo'li
        file_name:  Rasm fayl nomi
        lang:       Foydalanuvchi tili
        status_msg: Yuklanish status xabari
    """
    user = update.effective_user
    message = update.message

    try:
        collect_images = context.user_data.get("collect_images", [])

        # Maksimal son tekshiruvi
        if len(collect_images) >= MAX_IMAGES_PER_SESSION:
            await status_msg.edit_text(
                t("collect_max_reached", lang, max=MAX_IMAGES_PER_SESSION)
            )
            await cleanup_file(local_path)
            return

        # To'plamga qo'shish
        collect_images.append(str(local_path))
        context.user_data["collect_images"] = collect_images

        count = len(collect_images)
        await status_msg.edit_text(
            t("collect_image_added", lang, count=count, total=count)
        )

        logger.debug(f"Collect: user={user.id}, rasm_soni={count}")

        # DB da sessiyani yangilash
        db: Database = context.bot_data.get("db")
        if db:
            await db.update_session(user.id, images_data=collect_images)

    except Exception as e:
        logger.error(f"_add_to_collect xatosi: {e}")
        await cleanup_file(local_path)
        try:
            await status_msg.edit_text(t("error_general", lang))
        except Exception:
            pass


# ── Rasm harakatlar callback handleri ────────────────────────────────────────

async def handle_image_action_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Rasm ustidagi amallar callback handleri.
    pdf_make, pdf_compress, pdf_ocr, edit_menu, pdf_cancel
    """
    query = update.callback_query
    if not query or not update.effective_user:
        return

    await query.answer()
    user = update.effective_user
    data = query.data

    lang = await get_user_lang(user.id, context)
    db: Database = context.bot_data.get("db")

    # Joriy rasmni olish
    current_image = context.user_data.get("current_image")
    if not current_image and data != "pdf_cancel":
        await query.edit_message_text(t("edit_no_image", lang))
        return

    try:
        if data == "pdf_cancel":
            # Bekor qilish
            await query.edit_message_text("❌ Bekor qilindi.")
            if current_image:
                await cleanup_file(current_image.get("original_path"))
                edit_session = context.user_data.get("edit_session", {})
                work = edit_session.get("work_path")
                if work and work != current_image.get("original_path"):
                    await cleanup_file(work)
            context.user_data.pop("current_image", None)
            context.user_data.pop("edit_session", None)

        elif data == "pdf_make":
            # Oddiy PDF yaratish
            await _make_pdf(update, context, current_image, lang, compress=False)

        elif data == "pdf_compress":
            # Siqib PDF yaratish
            await _make_pdf(update, context, current_image, lang, compress=True)

        elif data == "pdf_ocr":
            # OCR tili tanlash menyusini ko'rsatish
            from utils.keyboards import get_ocr_lang_keyboard
            settings = {}
            if db:
                settings = await db.get_settings(user.id)
            ocr_lang = settings.get("ocr_lang", "en")
            await query.edit_message_text(
                t("ocr_select_lang", lang),
                reply_markup=get_ocr_lang_keyboard(lang, ocr_lang),
            )

        elif data == "edit_menu":
            # Tahrirlash menyusini ko'rsatish
            await _safe_edit_text(
                query,
                t("edit_menu", lang),
                reply_markup=get_edit_menu_keyboard(lang),
            )

        elif data == "collect_done":
            # Ko'p rasmli PDF yaratish tugmasi
            from handlers.pdf_handler import _finish_collect
            await _finish_collect(update, context)

        elif data == "collect_cancel":
            # Ko'p rasmli rejimni bekor qilish
            from handlers.pdf_handler import _cancel_collect
            await _cancel_collect(update, context)

    except Exception as e:
        logger.error(f"handle_image_action_callback xatosi: {e}")
        try:
            await query.edit_message_text(t("error_general", lang))
        except Exception:
            pass


async def _make_pdf(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    current_image: dict,
    lang: str,
    compress: bool = False,
) -> None:
    """
    Bitta rasmdan PDF yaratish va yuborish.

    Args:
        current_image: Joriy rasm ma'lumotlari
        lang:          Foydalanuvchi tili
        compress:      Siqish kerakmi
    """
    query = update.callback_query
    user = update.effective_user
    db: Database = context.bot_data.get("db")

    try:
        # Sozlamalarni olish
        settings = {"quality": "high", "pagesize": "A4",
                    "orientation": "portrait", "margin": "small"}
        if db:
            user_settings = await db.get_settings(user.id)
            settings.update(user_settings)

        # Progress xabari
        if compress:
            await query.edit_message_text(t("pdf_compressing", lang))
        else:
            await query.edit_message_text(t("pdf_creating", lang))

        # Rasm yo'li — edit sessiyasidan olish (tahrirlangan bo'lsa)
        edit_session = context.user_data.get("edit_session", {})
        image_path = edit_session.get("work_path") or current_image.get("original_path")

        if not image_path or not Path(image_path).exists():
            await query.edit_message_text(t("error_general", lang))
            return

        # PDF yaratish
        output_path = PDFConverter.generate_output_path("doc")

        success, err = await PDFConverter.convert_single_image(
            image_path, output_path, settings
        )

        if not success:
            await query.edit_message_text(t("pdf_error", lang))
            return

        original_size = Path(image_path).stat().st_size
        pdf_size = output_path.stat().st_size

        # Siqish kerak bo'lsa
        if compress:
            compress_quality = settings.get("quality", "medium")
            compressed_path = PDFConverter.generate_output_path("compressed")
            comp_ok, orig_sz, comp_sz = await PDFConverter.compress_pdf(
                output_path, compressed_path, compress_quality
            )
            if comp_ok:
                try:
                    output_path.unlink(missing_ok=True)
                except Exception:
                    pass
                output_path = compressed_path
                pdf_size = comp_sz

        # Telegram 50MB limitini tekshirish
        from config import TELEGRAM_MAX_FILE_SIZE
        if pdf_size > TELEGRAM_MAX_FILE_SIZE * 0.9:
            from utils.helpers import format_file_size
            await query.edit_message_text(
                t("pdf_too_large", lang, size=format_file_size(pdf_size))
            )
            await cleanup_file(output_path)
            return

        # PDF ni yuborish
        page_count = await PDFConverter.get_pdf_page_count(output_path)

        await query.edit_message_text(t("progress_sending", lang))

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

        # PDF xabarini o'chirish (keyboard xabari)
        try:
            await query.delete_message()
        except Exception:
            pass

        logger.info(f"PDF yuborildi: user={user.id}, hajm={pdf_size:,}")

        # Vaqtinchalik fayllarni tozalash
        await cleanup_file(current_image.get("original_path"))
        edit_session = context.user_data.get("edit_session", {})
        work = edit_session.get("work_path")
        if work and work != current_image.get("original_path"):
            await cleanup_file(work)
        await cleanup_file(output_path)

        context.user_data.pop("current_image", None)
        context.user_data.pop("edit_session", None)

    except Exception as e:
        logger.error(f"_make_pdf xatosi: {e}")
        try:
            await query.edit_message_text(t("pdf_error", lang))
        except Exception:
            pass


# ── OCR callback handleri ────────────────────────────────────────────────────

async def handle_ocr_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    OCR til tanlash va OCR PDF yaratish callback handleri.
    ocr_uz, ocr_ru, ocr_en, ocr_ar
    """
    query = update.callback_query
    if not query or not update.effective_user:
        return

    await query.answer()
    user = update.effective_user
    data = query.data
    lang = await get_user_lang(user.id, context)
    db: Database = context.bot_data.get("db")

    current_image = context.user_data.get("current_image")
    if not current_image:
        await query.edit_message_text(t("edit_no_image", lang))
        return

    if data == "ocr_cancel":
        await query.edit_message_text("❌ Bekor qilindi.")
        return

    # Til kodi (ocr_uz → uz)
    ocr_lang = data.split("_")[1] if "_" in data else "en"
    valid_ocr_langs = {"uz", "ru", "en", "ar"}
    if ocr_lang not in valid_ocr_langs:
        return

    try:
        # OCR tilini sozlamalarda saqlash
        if db:
            await db.update_settings(user.id, ocr_lang=ocr_lang)

        # OCR PDF yaratish
        await query.edit_message_text(t("ocr_creating", lang))

        from services.ocr_service import OCRService

        edit_session = context.user_data.get("edit_session", {})
        image_path = edit_session.get("work_path") or current_image.get("original_path")

        if not image_path or not Path(image_path).exists():
            await query.edit_message_text(t("error_general", lang))
            return

        output_path = PDFConverter.generate_output_path("ocr")

        success, char_count = await OCRService.create_searchable_pdf(
            image_path, output_path, ocr_lang
        )

        if not success:
            await query.edit_message_text(t("ocr_error", lang, error="PDF yaratilmadi"))
            return

        pdf_size = output_path.stat().st_size
        page_count = await PDFConverter.get_pdf_page_count(output_path)

        # Natija xabari
        if char_count > 0:
            caption = t("ocr_success", lang, chars=char_count)
        else:
            caption = t("ocr_no_text", lang)

        await query.edit_message_text(t("progress_sending", lang))

        with open(output_path, "rb") as pdf_file:
            sent_doc = await update.effective_chat.send_document(
                document=pdf_file,
                filename=output_path.name,
                caption=caption,
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
            await db.log_action(user.id, "ocr_used")

        try:
            await query.delete_message()
        except Exception:
            pass

        # Tozalash
        await cleanup_file(current_image.get("original_path"))
        work = context.user_data.get("edit_session", {}).get("work_path")
        if work and work != current_image.get("original_path"):
            await cleanup_file(work)
        await cleanup_file(output_path)

        context.user_data.pop("current_image", None)
        context.user_data.pop("edit_session", None)

    except Exception as e:
        logger.error(f"handle_ocr_callback xatosi: {e}")
        try:
            await query.edit_message_text(t("ocr_error", lang, error=str(e)))
        except Exception:
            pass


# ── Tahrirlash callback handlerlari ──────────────────────────────────────────

async def handle_edit_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Rasm tahrirlash amallari callback handleri.
    ed_bri_menu, ed_con_menu, ed_rot_menu, ed_gray, ed_sharp,
    ed_a4, ed_reset, ed_done, ed_bri_*, ed_con_*, ed_rot_*
    """
    query = update.callback_query
    if not query or not update.effective_user:
        return

    await query.answer()
    user = update.effective_user
    data = query.data
    lang = await get_user_lang(user.id, context)

    # Joriy rasmni tekshirish
    current_image = context.user_data.get("current_image")
    if not current_image:
        await query.edit_message_text(t("edit_no_image", lang))
        return

    # Edit sessiyasini tekshirish
    edit_session = context.user_data.get("edit_session")
    if not edit_session:
        edit_session = ImageEditor.create_work_session(current_image["original_path"])
        context.user_data["edit_session"] = edit_session

    try:
        # Asosiy menyu ko'rsatish
        if data == "edit_menu":
            await _safe_edit_text(
                query,
                t("edit_menu", lang),
                reply_markup=get_edit_menu_keyboard(lang),
            )
            return

        # Pastki menyular
        if data == "ed_bri_menu":
            await query.edit_message_text(
                t("edit_brightness", lang),
                reply_markup=get_brightness_keyboard(lang),
            )
            return

        if data == "ed_con_menu":
            await query.edit_message_text(
                t("edit_contrast", lang),
                reply_markup=get_contrast_keyboard(lang),
            )
            return

        if data == "ed_rot_menu":
            from utils.keyboards import get_rotation_keyboard
            await query.edit_message_text(
                "🔄 Aylantirish burchagini tanlang:",
                reply_markup=get_rotation_keyboard(lang),
            )
            return

        # Qaytarish (reset)
        if data == "ed_reset":
            success = await ImageEditor.reset_to_original(
                edit_session["original_path"],
                edit_session["work_path"],
            )
            if success:
                edit_session["edits_applied"] = []
                await query.edit_message_text(
                    t("edit_reset", lang),
                    reply_markup=get_edit_menu_keyboard(lang),
                )
            return

        # Tugallash — PDF yaratish
        if data == "ed_done":
            # Ish nusxasini current_image ga ko'chirish
            current_image["work_path"] = edit_session["work_path"]
            await _make_pdf(update, context, current_image, lang, compress=False)
            return

        # Amallar qo'llash
        await query.edit_message_text(t("edit_applying", lang))

        success = await ImageEditor.apply_edit(edit_session["work_path"], data)

        if success:
            edit_session["edits_applied"].append(data)

            # Preview rasmni yuborish
            await _send_edit_preview(update, context, edit_session, lang)
        else:
            await query.edit_message_text(
                t("error_general", lang)
            )

    except Exception as e:
        err_str = str(e).lower()
        if "not modified" in err_str or "message is not modified" in err_str:
            return
        logger.error(f"handle_edit_callback xatosi: {e}")
        try:
            await query.edit_message_text(t("error_general", lang))
        except Exception:
            pass


async def _send_edit_preview(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    edit_session: dict,
    lang: str,
) -> None:
    """
    Tahrirlangan rasmning preview ni yuborish.

    Args:
        edit_session: Tahrirlash sessiyasi ma'lumotlari
        lang:         Foydalanuvchi tili
    """
    try:
        work_path = edit_session.get("work_path")
        if not work_path or not Path(work_path).exists():
            return

        keyboard = get_after_edit_keyboard(lang)

        with open(work_path, "rb") as img_file:
            await update.effective_chat.send_photo(
                photo=img_file,
                caption=f"👁️ {t('edit_preview', lang)}",
                reply_markup=keyboard,
            )

        # Eski xabarni o'chirish
        try:
            if update.callback_query:
                await update.callback_query.delete_message()
        except Exception:
            pass

    except Exception as e:
        logger.error(f"_send_edit_preview xatosi: {e}")


def get_image_handlers() -> list:
    """
    Rasm va tahrirlash handlerlarini ro'yxat sifatida qaytarish.
    """
    return [
        # Rasm xabarlari
        MessageHandler(
            filters.PHOTO | (filters.Document.IMAGE),
            handle_image,
        ),
        # Rasm amallari callback lari
        CallbackQueryHandler(
            handle_image_action_callback,
            pattern=r"^(pdf_make|pdf_compress|pdf_ocr|pdf_cancel|edit_menu|collect_done|collect_cancel)$",
        ),
        # OCR callback lari
        CallbackQueryHandler(
            handle_ocr_callback,
            pattern=r"^ocr_(uz|ru|en|ar|cancel)$",
        ),
        # Tahrirlash callback lari
        CallbackQueryHandler(
            handle_edit_callback,
            pattern=r"^ed_(bri|con|rot|gray|sharp|a4|reset|done|back).*$",
        ),
    ]
