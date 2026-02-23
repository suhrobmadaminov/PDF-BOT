"""
Start va Help Handler — foydalanuvchilarni kutib olish va yo'riqnoma berish.
/start, /help buyruqlari va yangi foydalanuvchilarni ma'lumotlar bazasiga qo'shish.
"""

from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from utils.helpers import get_user_lang, get_user_info, t, is_admin, check_rate_limit
from utils.keyboards import get_language_keyboard
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

        # Xush kelibsiz xabar yuborish
        first_name = user.first_name or user.full_name
        welcome_text = t("welcome", lang, name=first_name)

        await update.message.reply_html(welcome_text)

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
    ]
