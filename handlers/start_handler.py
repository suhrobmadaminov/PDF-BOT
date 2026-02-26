"""
Start va Help Handler — foydalanuvchilarni kutib olish va yo'riqnoma berish.
/start, /help buyruqlari va yangi foydalanuvchilarni ma'lumotlar bazasiga qo'shish.
"""

from loguru import logger
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from utils.helpers import get_user_lang, get_user_info, t, is_admin, check_rate_limit
from utils.keyboards import get_language_keyboard, get_main_keyboard
from database import Database


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /start buyrug'i handleri.
    Foydalanuvchini ma'lumotlar bazasiga qo'shadi (yoki mavjudni yangilaydi)
    va xush kelibsiz xabar yuboradi.
    """
    if not update.message or not update.effective_user:
        return

    user = update.effective_user
    db: Database = context.bot_data.get("db")

    try:
        # Foydalanuvchini ma'lumotlar bazasiga qo'shish yoki yangilash
        if db:
            user_data = await db.get_or_create_user(
                user_id=user.id,
                username=user.username,
                full_name=user.full_name,
            )

            # Bloklangan foydalanuvchini tekshirish
            if user_data and user_data.get("is_banned"):
                lang = user_data.get("lang", "uz")
                await update.message.reply_text(t("error_banned", lang))
                return

            # Tilni cache ga saqlash
            lang = user_data.get("lang", "uz") if user_data else "uz"
            context.user_data["lang"] = lang

            # Statistikaga yozish
            await db.log_action(user.id, "start_command")
        else:
            lang = "uz"

        # Eski persistent klaviaturani olib tashlash
        rm_msg = await update.message.reply_text(
            "\u200b", reply_markup=ReplyKeyboardRemove()
        )
        try:
            await rm_msg.delete()
        except Exception:
            pass

        # Xush kelibsiz xabar yuborish (inline keyboard bilan)
        first_name = user.first_name or user.full_name
        welcome_text = t("welcome", lang, name=first_name)

        await update.message.reply_html(
            welcome_text,
            reply_markup=get_main_keyboard(lang),
        )

        logger.info(f"Foydalanuvchi /start: {user.id} (@{user.username})")

    except Exception as e:
        logger.error(f"start_command xatosi (user={user.id}): {e}")
        try:
            await update.message.reply_text(
                "Xush kelibsiz! Rasm yuboring yoki /help yozing."
            )
        except Exception:
            pass


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /help buyrug'i handleri.
    Bot funksiyalari haqida to'liq yo'riqnoma beradi.
    """
    if not update.message or not update.effective_user:
        return

    user = update.effective_user

    # Rate limit tekshirish
    if not await check_rate_limit(update, context):
        return

    try:
        db: Database = context.bot_data.get("db")
        lang = await get_user_lang(user.id, context)

        if db:
            await db.update_last_active(user.id)

        help_text = t("help", lang)
        await update.message.reply_html(help_text)

        logger.debug(f"Foydalanuvchi /help: {user.id}")

    except Exception as e:
        logger.error(f"help_command xatosi: {e}")
        try:
            await update.message.reply_text(t("error_general", "uz"))
        except Exception:
            pass


async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /lang buyrug'i handleri.
    Foydalanuvchi interfeys tilini o'zgartirish uchun.
    """
    if not update.message or not update.effective_user:
        return

    user = update.effective_user

    # Rate limit tekshirish
    if not await check_rate_limit(update, context):
        return

    try:
        lang = await get_user_lang(user.id, context)
        keyboard = get_language_keyboard()
        await update.message.reply_html(
            t("lang_select", lang),
            reply_markup=keyboard,
        )
    except Exception as e:
        logger.error(f"lang_command xatosi: {e}")


async def handle_lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Til tanlash callback handleri.
    Foydalanuvchi til tugmasini bosganida ishlaydi.
    """
    query = update.callback_query
    if not query or not update.effective_user:
        return

    await query.answer()
    user = update.effective_user
    data = query.data  # 'lang_uz', 'lang_ru', 'lang_en'

    try:
        new_lang = data.split("_")[1]  # 'uz', 'ru', 'en'
        valid_langs = {"uz", "ru", "en"}
        if new_lang not in valid_langs:
            return

        # Ma'lumotlar bazasida yangilash
        db: Database = context.bot_data.get("db")
        if db:
            await db.update_user_lang(user.id, new_lang)

        # Cache ni yangilash
        context.user_data["lang"] = new_lang

        # Tasdiqlash xabari
        confirmation = t("lang_set", new_lang)
        await query.edit_message_text(confirmation)

        logger.info(f"Til o'zgardi: user={user.id}, lang={new_lang}")

    except Exception as e:
        logger.error(f"handle_lang_callback xatosi: {e}")
        try:
            await query.edit_message_text(t("error_general", "uz"))
        except Exception:
            pass


async def handle_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Asosiy menyu inline tugmalari callback handleri.
    menu_collect, menu_history, menu_settings, menu_help

    Eslatma: callback query da update.message = None, shuning uchun
    barcha xabarlar update.effective_chat.send_message() orqali yuboriladi.
    """
    query = update.callback_query
    if not query or not update.effective_user:
        return

    await query.answer()
    user = update.effective_user
    data = query.data
    lang = await get_user_lang(user.id, context)
    db: Database = context.bot_data.get("db")

    # Menyu xabarini o'chirish
    try:
        await query.delete_message()
    except Exception:
        pass

    try:
        if data == "menu_collect":
            # Collect rejimini boshlash
            from config import MAX_IMAGES_PER_SESSION

            if context.user_data.get("collect_mode"):
                count = len(context.user_data.get("collect_images", []))
                from utils.keyboards import get_collect_done_keyboard
                keyboard = get_collect_done_keyboard(lang, count) if count > 0 else None
                await update.effective_chat.send_message(
                    t("collect_already_active", lang),
                    reply_markup=keyboard,
                )
                return

            context.user_data["collect_mode"] = True
            context.user_data["collect_images"] = []

            if db:
                await db.create_session(user.id, mode="collecting")

            await update.effective_chat.send_message(
                t("collect_started", lang, max_images=MAX_IMAGES_PER_SESSION),
                parse_mode="HTML",
            )

        elif data == "menu_history":
            # Tarix ko'rsatish
            if not db:
                await update.effective_chat.send_message(t("error_general", lang))
                return

            if await db.is_banned(user.id):
                await update.effective_chat.send_message(t("error_banned", lang))
                return

            history = await db.get_history(user.id)

            if not history:
                await update.effective_chat.send_message(t("history_empty", lang))
                return

            from utils.helpers import format_file_size, format_datetime
            from utils.keyboards import get_history_keyboard
            text = t("history_title", lang) + "\n\n"
            for item in history:
                text += t(
                    "history_item", lang,
                    name=item.get("file_name", "document.pdf"),
                    size=format_file_size(item.get("file_size", 0)),
                    date=format_datetime(item.get("created_at")),
                    pages=item.get("pages", 1),
                ) + "\n"

            keyboard = get_history_keyboard(history, lang)
            await update.effective_chat.send_message(
                text, reply_markup=keyboard, parse_mode="HTML"
            )

        elif data == "menu_settings":
            # Sozlamalar ko'rsatish
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            settings = {"quality": "high", "pagesize": "A4",
                        "orientation": "portrait", "margin": "small"}
            if db:
                user_settings = await db.get_settings(user.id)
                settings.update(user_settings)

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🎚️ Sifat",    callback_data="q_men"),
                    InlineKeyboardButton("📏 Sahifa",   callback_data="ps_men"),
                ],
                [
                    InlineKeyboardButton("🔄 Yo'nalish", callback_data="or_men"),
                    InlineKeyboardButton("📐 Chegara",  callback_data="mg_men"),
                ],
                [InlineKeyboardButton("❌ Yopish", callback_data="settings_close")],
            ])
            text = (
                f"⚙️ <b>Sozlamalar</b>\n\n"
                f"🎚️ Sifat: <b>{settings.get('quality', 'high')}</b>\n"
                f"📏 Sahifa: <b>{settings.get('pagesize', 'A4')}</b>\n"
                f"🔄 Yo'nalish: <b>{settings.get('orientation', 'portrait')}</b>\n"
                f"📐 Chegara: <b>{settings.get('margin', 'small')}</b>\n\n"
                f"O'zgartirish uchun tugmani bosing:"
            )
            await update.effective_chat.send_message(
                text, reply_markup=keyboard, parse_mode="HTML"
            )

        elif data == "menu_help":
            # Yordam ko'rsatish
            await update.effective_chat.send_message(
                t("help", lang), parse_mode="HTML"
            )

    except Exception as e:
        logger.error(f"handle_menu_callback xatosi: {e}")
        try:
            await update.effective_chat.send_message(t("error_general", lang))
        except Exception:
            pass


async def handle_close_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Xabarni yopish callback handleri ('close_msg', 'settings_close').
    """
    query = update.callback_query
    if not query:
        return
    try:
        await query.answer()
        await query.delete_message()
    except Exception:
        try:
            await query.answer("Yopildi")
        except Exception:
            pass


def get_start_handlers() -> list:
    """
    Start va help handlerlarini ro'yxat sifatida qaytarish.
    main.py da handler qo'shish uchun ishlatiladi.
    """
    return [
        CommandHandler("start", start_command),
        CommandHandler("help",  help_command),
        CommandHandler("lang",  lang_command),
        # Asosiy menyu inline callback lari
        CallbackQueryHandler(
            handle_menu_callback,
            pattern=r"^menu_(collect|history|settings|help)$",
        ),
    ]
