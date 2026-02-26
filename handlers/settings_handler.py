"""
Sozlamalar Handler — PDF sifati, sahifa o'lchami, yo'nalish va chegara sozlamalari.
/quality, /pagesize, /orientation, /margin buyruqlari.
"""

from loguru import logger
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from utils.helpers import get_user_lang, t, check_rate_limit
from utils.keyboards import (
    get_quality_keyboard, get_pagesize_keyboard,
    get_orientation_keyboard, get_margin_keyboard,
)
from database import Database


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Umumiy sozlamalar menyusini ko'rsatish.
    """
    if not update.message or not update.effective_user:
        return

    user = update.effective_user
    lang = await get_user_lang(user.id, context)
    db: Database = context.bot_data.get("db")

    settings = {"quality": "high", "pagesize": "A4", "orientation": "portrait", "margin": "small"}
    if db:
        user_settings = await db.get_settings(user.id)
        settings.update(user_settings)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎚️ Sifat", callback_data="q_men"),
            InlineKeyboardButton("📏 Sahifa", callback_data="ps_men"),
        ],
        [
            InlineKeyboardButton("🔄 Yo'nalish", callback_data="or_men"),
            InlineKeyboardButton("📐 Chegara", callback_data="mg_men"),
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

    await update.message.reply_html(text, reply_markup=keyboard)


# ── Sifat sozlamalari ─────────────────────────────────────────────────────────

async def quality_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /quality buyrug'i — PDF sifat darajasini tanlash menyusi.
    """
    if not update.message or not update.effective_user:
        return

    user = update.effective_user
    lang = await get_user_lang(user.id, context)

    if not await check_rate_limit(update, context):
        return

    db: Database = context.bot_data.get("db")

    try:
        current_quality = "high"
        if db:
            settings = await db.get_settings(user.id)
            current_quality = settings.get("quality", "high")

        keyboard = get_quality_keyboard(lang, current_quality)
        await update.message.reply_html(
            t("quality_select", lang),
            reply_markup=keyboard,
        )
    except Exception as e:
        logger.error(f"quality_command xatosi: {e}")
        await update.message.reply_text(t("error_general", lang))


# ── Sahifa o'lchami sozlamalari ───────────────────────────────────────────────

async def pagesize_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /pagesize buyrug'i — PDF sahifa o'lchamini tanlash menyusi.
    """
    if not update.message or not update.effective_user:
        return

    user = update.effective_user
    lang = await get_user_lang(user.id, context)

    if not await check_rate_limit(update, context):
        return

    db: Database = context.bot_data.get("db")

    try:
        current = "A4"
        if db:
            settings = await db.get_settings(user.id)
            current = settings.get("pagesize", "A4")

        keyboard = get_pagesize_keyboard(lang, current)
        await update.message.reply_html(
            t("pagesize_select", lang),
            reply_markup=keyboard,
        )
    except Exception as e:
        logger.error(f"pagesize_command xatosi: {e}")
        await update.message.reply_text(t("error_general", lang))


# ── Yo'nalish sozlamalari ─────────────────────────────────────────────────────

async def orientation_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /orientation buyrug'i — sahifa yo'nalishini tanlash menyusi.
    """
    if not update.message or not update.effective_user:
        return

    user = update.effective_user
    lang = await get_user_lang(user.id, context)

    if not await check_rate_limit(update, context):
        return

    db: Database = context.bot_data.get("db")

    try:
        current = "portrait"
        if db:
            settings = await db.get_settings(user.id)
            current = settings.get("orientation", "portrait")

        keyboard = get_orientation_keyboard(lang, current)
        await update.message.reply_html(
            t("orientation_select", lang),
            reply_markup=keyboard,
        )
    except Exception as e:
        logger.error(f"orientation_command xatosi: {e}")
        await update.message.reply_text(t("error_general", lang))


# ── Chegara sozlamalari ───────────────────────────────────────────────────────

async def margin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /margin buyrug'i — PDF chegara o'lchamini tanlash menyusi.
    """
    if not update.message or not update.effective_user:
        return

    user = update.effective_user
    lang = await get_user_lang(user.id, context)

    if not await check_rate_limit(update, context):
        return

    db: Database = context.bot_data.get("db")

    try:
        current = "small"
        if db:
            settings = await db.get_settings(user.id)
            current = settings.get("margin", "small")

        keyboard = get_margin_keyboard(lang, current)
        await update.message.reply_html(
            t("margin_select", lang),
            reply_markup=keyboard,
        )
    except Exception as e:
        logger.error(f"margin_command xatosi: {e}")
        await update.message.reply_text(t("error_general", lang))


# ── Sozlamalar Callback Handlerlari ───────────────────────────────────────────

async def handle_settings_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Barcha sozlamalar uchun callback handler.
    q_* (sifat), ps_* (sahifa), or_* (yo'nalish), mg_* (chegara)
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
        # ── Menyu tugmalari (settings_command dan ochilgan) ──
        if data == "q_men":
            settings = {}
            if db:
                settings = await db.get_settings(user.id)
            await query.edit_message_text(
                t("quality_select", lang),
                reply_markup=get_quality_keyboard(lang, settings.get("quality", "high")),
            )
            return

        elif data == "ps_men":
            settings = {}
            if db:
                settings = await db.get_settings(user.id)
            await query.edit_message_text(
                t("pagesize_select", lang),
                reply_markup=get_pagesize_keyboard(lang, settings.get("pagesize", "A4")),
            )
            return

        elif data == "or_men":
            settings = {}
            if db:
                settings = await db.get_settings(user.id)
            await query.edit_message_text(
                t("orientation_select", lang),
                reply_markup=get_orientation_keyboard(lang, settings.get("orientation", "portrait")),
            )
            return

        elif data == "mg_men":
            settings = {}
            if db:
                settings = await db.get_settings(user.id)
            await query.edit_message_text(
                t("margin_select", lang),
                reply_markup=get_margin_keyboard(lang, settings.get("margin", "small")),
            )
            return

        # ── Sifat tanlash ──
        if data.startswith("q_"):
            quality_map = {
                "q_low": "low",
                "q_med": "medium",
                "q_hi":  "high",
                "q_ult": "ultra",
            }
            quality = quality_map.get(data)
            if quality and db:
                await db.update_settings(user.id, quality=quality)
                from config import QUALITY_SETTINGS
                label = QUALITY_SETTINGS.get(quality, {}).get("label", quality)
                await query.edit_message_text(
                    t("quality_set", lang, quality=label),
                    reply_markup=get_quality_keyboard(lang, quality),
                )
                logger.debug(f"Sifat o'rnatildi: user={user.id}, quality={quality}")

        # ── Sahifa o'lchami tanlash ──
        elif data.startswith("ps_"):
            size_map = {
                "ps_A3":  "A3",
                "ps_A4":  "A4",
                "ps_A5":  "A5",
                "ps_Let": "Letter",
                "ps_Leg": "Legal",
                "ps_Ori": "Original",
            }
            size = size_map.get(data)
            if size and db:
                await db.update_settings(user.id, pagesize=size)
                await query.edit_message_text(
                    t("pagesize_set", lang, size=size),
                    reply_markup=get_pagesize_keyboard(lang, size),
                )
                logger.debug(f"Sahifa o'lchami: user={user.id}, size={size}")

        # ── Yo'nalish tanlash ──
        elif data.startswith("or_"):
            orient_map = {
                "or_por": "portrait",
                "or_lan": "landscape",
                "or_aut": "auto",
            }
            orient = orient_map.get(data)
            if orient and db:
                await db.update_settings(user.id, orientation=orient)
                orient_labels = {
                    "portrait":  "Vertikal (Portrait)",
                    "landscape": "Gorizontal (Landscape)",
                    "auto":      "Avtomatik",
                }
                label = orient_labels.get(orient, orient)
                await query.edit_message_text(
                    t("orientation_set", lang, orientation=label),
                    reply_markup=get_orientation_keyboard(lang, orient),
                )

        # ── Chegara tanlash ──
        elif data.startswith("mg_"):
            margin_map = {
                "mg_non": "none",
                "mg_sml": "small",
                "mg_med": "medium",
                "mg_lrg": "large",
            }
            margin = margin_map.get(data)
            if margin and db:
                await db.update_settings(user.id, margin=margin)
                margin_labels = {
                    "none":   "Yo'q",
                    "small":  "Kichik",
                    "medium": "O'rta",
                    "large":  "Katta",
                }
                label = margin_labels.get(margin, margin)
                await query.edit_message_text(
                    t("margin_set", lang, margin=label),
                    reply_markup=get_margin_keyboard(lang, margin),
                )

        # ── Yopish ──
        elif data == "settings_close":
            await query.delete_message()

    except Exception as e:
        logger.error(f"handle_settings_callback xatosi: {e}")
        try:
            await query.edit_message_text(t("error_general", lang))
        except Exception:
            pass


def get_settings_handlers() -> list:
    """
    Sozlamalar handlerlarini ro'yxat sifatida qaytarish.
    """
    return [
        CommandHandler("quality",     quality_command),
        CommandHandler("pagesize",    pagesize_command),
        CommandHandler("orientation", orientation_command),
        CommandHandler("margin",      margin_command),
        # Sozlamalar callback lari
        CallbackQueryHandler(
            handle_settings_callback,
            pattern=r"^(q_|ps_|or_|mg_|settings_close)",
        ),
    ]
