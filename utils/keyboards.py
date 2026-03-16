"""
Tugmalar (Inline Keyboard) moduli — barcha inline klaviaturalar shu yerda.
Har bir funksiya uchun alohida klaviatura factory funksiyasi mavjud.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from locales import get_text


def _t(key: str, lang: str, **kwargs) -> str:
    """Qisqa yordamchi — matn olish."""
    return get_text(key, lang, **kwargs)


# ── Asosiy menyu (Inline) ─────────────────────────────────────────────────────

def get_main_keyboard(lang: str) -> InlineKeyboardMarkup:
    """
    Xush kelibsiz xabarga biriktirilgan asosiy navigatsiya klaviaturasi.

    Args:
        lang: Foydalanuvchi tili

    Returns:
        InlineKeyboardMarkup
    """
    keyboard = [
        [
            InlineKeyboardButton(_t("menu_btn_collect", lang),  callback_data="menu_collect"),
            InlineKeyboardButton(_t("menu_btn_history", lang),  callback_data="menu_history"),
        ],
        [
            InlineKeyboardButton(_t("menu_btn_settings", lang), callback_data="menu_settings"),
            InlineKeyboardButton(_t("menu_btn_help", lang),     callback_data="menu_help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ── Rasm harakatlar klaviaturasi ──────────────────────────────────────────────

def get_image_actions_keyboard(lang: str) -> InlineKeyboardMarkup:
    """
    Rasm qabul qilinganda ko'rsatiladigan amaliyotlar klaviaturasi.

    Args:
        lang: Foydalanuvchi tili

    Returns:
        InlineKeyboardMarkup
    """
    keyboard = [
        [
            InlineKeyboardButton(_t("btn_make_pdf", lang), callback_data="pdf_make"),
            InlineKeyboardButton(_t("btn_compress_pdf", lang), callback_data="pdf_compress"),
        ],
        [
            InlineKeyboardButton(_t("btn_ocr_pdf", lang), callback_data="pdf_ocr"),
            InlineKeyboardButton(_t("btn_edit", lang), callback_data="edit_menu"),
        ],
        [
            InlineKeyboardButton(_t("btn_cancel", lang), callback_data="pdf_cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ── Sifat klaviaturasi ────────────────────────────────────────────────────────

def get_quality_keyboard(lang: str, current: str = "high") -> InlineKeyboardMarkup:
    """
    PDF sifat tanlash klaviaturasi.

    Args:
        lang:    Foydalanuvchi tili
        current: Joriy sifat (belgilash uchun)
    """
    quality_map = {
        "low":   "btn_quality_low",
        "medium": "btn_quality_med",
        "high":  "btn_quality_hi",
        "ultra": "btn_quality_ultra",
    }

    keyboard = [
        [InlineKeyboardButton(
            f"✅ {_t(btn, lang)}" if q == current else _t(btn, lang),
            callback_data=f"q_{q[:3]}"
        )]
        for q, btn in quality_map.items()
    ]
    keyboard.append([
        InlineKeyboardButton(_t("btn_cancel_action", lang), callback_data="settings_close")
    ])
    return InlineKeyboardMarkup(keyboard)


# ── Sahifa o'lchami klaviaturasi ──────────────────────────────────────────────

def get_pagesize_keyboard(lang: str, current: str = "A4") -> InlineKeyboardMarkup:
    """Sahifa o'lchami tanlash klaviaturasi."""
    sizes = ["A3", "A4", "A5", "Letter", "Legal", "Original"]
    keyboard = []
    row = []
    for i, size in enumerate(sizes):
        label = f"✅ {size}" if size == current else size
        row.append(InlineKeyboardButton(label, callback_data=f"ps_{size[:3]}"))
        if len(row) == 3 or i == len(sizes) - 1:
            keyboard.append(row)
            row = []
    keyboard.append([
        InlineKeyboardButton(_t("btn_cancel_action", lang), callback_data="settings_close")
    ])
    return InlineKeyboardMarkup(keyboard)


# ── Yo'nalish klaviaturasi ────────────────────────────────────────────────────

def get_orientation_keyboard(lang: str, current: str = "portrait") -> InlineKeyboardMarkup:
    """Sahifa yo'nalishi tanlash klaviaturasi."""
    options = [
        ("portrait",  "btn_portrait",    "or_por"),
        ("landscape", "btn_landscape",   "or_lan"),
        ("auto",      "btn_auto_orient", "or_aut"),
    ]
    keyboard = [
        [InlineKeyboardButton(
            f"✅ {_t(btn, lang)}" if val == current else _t(btn, lang),
            callback_data=cb
        )]
        for val, btn, cb in options
    ]
    keyboard.append([
        InlineKeyboardButton(_t("btn_cancel_action", lang), callback_data="settings_close")
    ])
    return InlineKeyboardMarkup(keyboard)


# ── Chegara klaviaturasi ──────────────────────────────────────────────────────

def get_margin_keyboard(lang: str, current: str = "small") -> InlineKeyboardMarkup:
    """Chegara o'lchami tanlash klaviaturasi."""
    options = [
        ("none",   "btn_margin_none",   "mg_non"),
        ("small",  "btn_margin_small",  "mg_sml"),
        ("medium", "btn_margin_medium", "mg_med"),
        ("large",  "btn_margin_large",  "mg_lrg"),
    ]
    keyboard = [
        [InlineKeyboardButton(
            f"✅ {_t(btn, lang)}" if val == current else _t(btn, lang),
            callback_data=cb
        )]
        for val, btn, cb in options
    ]
    keyboard.append([
        InlineKeyboardButton(_t("btn_cancel_action", lang), callback_data="settings_close")
    ])
    return InlineKeyboardMarkup(keyboard)


# ── Til tanlash klaviaturasi ──────────────────────────────────────────────────

def get_language_keyboard() -> InlineKeyboardMarkup:
    """Til tanlash klaviaturasi (barcha tillarda bir xil)."""
    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# ── Tahrirlash menyusi klaviaturasi ──────────────────────────────────────────

def get_edit_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Rasm tahrirlash asosiy menyusi."""
    keyboard = [
        [
            InlineKeyboardButton(_t("btn_brightness", lang), callback_data="ed_bri_menu"),
            InlineKeyboardButton(_t("btn_contrast", lang),   callback_data="ed_con_menu"),
        ],
        [
            InlineKeyboardButton(_t("btn_grayscale", lang),  callback_data="ed_gray"),
            InlineKeyboardButton(_t("btn_sharpen", lang),    callback_data="ed_sharp"),
        ],
        [
            InlineKeyboardButton(_t("btn_rotate", lang),     callback_data="ed_rot_menu"),
            InlineKeyboardButton(_t("btn_a4_fit", lang),     callback_data="ed_a4"),
        ],
        [
            InlineKeyboardButton(_t("btn_reset_edit", lang), callback_data="ed_reset"),
        ],
        [
            InlineKeyboardButton(_t("btn_done_edit", lang),  callback_data="ed_done"),
            InlineKeyboardButton(_t("btn_cancel", lang),     callback_data="pdf_cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_brightness_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Yorqinlik darajasini tanlash klaviaturasi."""
    keyboard = [
        [
            InlineKeyboardButton(_t("btn_bright_m50",  lang), callback_data="ed_bri_m50"),
            InlineKeyboardButton(_t("btn_bright_m25",  lang), callback_data="ed_bri_m25"),
            InlineKeyboardButton(_t("btn_bright_norm", lang), callback_data="ed_bri_nor"),
        ],
        [
            InlineKeyboardButton(_t("btn_bright_p25",  lang), callback_data="ed_bri_p25"),
            InlineKeyboardButton(_t("btn_bright_p50",  lang), callback_data="ed_bri_p50"),
        ],
        [
            InlineKeyboardButton(_t("btn_back", lang), callback_data="edit_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_contrast_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Kontrast darajasini tanlash klaviaturasi."""
    keyboard = [
        [
            InlineKeyboardButton(_t("btn_contrast_low", lang), callback_data="ed_con_low"),
            InlineKeyboardButton(_t("btn_contrast_med", lang), callback_data="ed_con_med"),
        ],
        [
            InlineKeyboardButton(_t("btn_contrast_hi",  lang), callback_data="ed_con_hi"),
            InlineKeyboardButton(_t("btn_contrast_vhi", lang), callback_data="ed_con_vhi"),
        ],
        [
            InlineKeyboardButton(_t("btn_back", lang), callback_data="edit_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_rotation_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Aylantirish burchagini tanlash klaviaturasi."""
    keyboard = [
        [
            InlineKeyboardButton(_t("btn_rotate_90",  lang), callback_data="ed_rot_90"),
            InlineKeyboardButton(_t("btn_rotate_180", lang), callback_data="ed_rot_180"),
            InlineKeyboardButton(_t("btn_rotate_270", lang), callback_data="ed_rot_270"),
        ],
        [
            InlineKeyboardButton(_t("btn_back", lang), callback_data="edit_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ── Tarix klaviaturasi ────────────────────────────────────────────────────────

def get_history_keyboard(history_items: list[dict], lang: str) -> InlineKeyboardMarkup:
    """
    PDF tarix ro'yxati klaviaturasi.

    Args:
        history_items: Tarix elementlari ro'yxati [{id, file_name, ...}]
        lang:          Foydalanuvchi tili
    """
    keyboard = []
    for item in history_items:
        item_id = item["id"]
        name = item.get("file_name", "document.pdf")
        # Uzun nomlarni qisqartirish
        short_name = name[:20] + "..." if len(name) > 23 else name
        keyboard.append([
            InlineKeyboardButton(f"📄 {short_name}", callback_data=f"hi_info_{item_id}"),
        ])
        keyboard.append([
            InlineKeyboardButton(
                _t("btn_download", lang), callback_data=f"hi_dl_{item_id}"
            ),
            InlineKeyboardButton(
                _t("btn_delete", lang), callback_data=f"hi_rm_{item_id}"
            ),
        ])
    keyboard.append([
        InlineKeyboardButton(_t("btn_close", lang), callback_data="hist_close")
    ])
    return InlineKeyboardMarkup(keyboard)


# ── Reverse (PDF → Rasm) klaviaturasi ─────────────────────────────────────────

def get_reverse_format_keyboard(lang: str) -> InlineKeyboardMarkup:
    """PDF ni rasmlarga aylantirish uchun format tanlash klaviaturasi."""
    keyboard = [
        [
            InlineKeyboardButton(_t("btn_reverse_jpg", lang), callback_data="rev_jpg"),
            InlineKeyboardButton(_t("btn_reverse_png", lang), callback_data="rev_png"),
        ],
        [
            InlineKeyboardButton(_t("btn_reverse_zip", lang), callback_data="rev_zip"),
        ],
        [
            InlineKeyboardButton(_t("btn_cancel_action", lang), callback_data="rev_cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ── OCR til klaviaturasi ──────────────────────────────────────────────────────

def get_ocr_lang_keyboard(lang: str, current_ocr_lang: str = "en") -> InlineKeyboardMarkup:
    """OCR uchun til tanlash klaviaturasi."""
    from config import OCR_LANGUAGES
    keyboard = []
    row = []
    for code, info in OCR_LANGUAGES.items():
        display = info["display"]
        label = f"✅ {display}" if code == current_ocr_lang else display
        row.append(InlineKeyboardButton(label, callback_data=f"ocr_{code}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([
        InlineKeyboardButton(_t("btn_cancel_action", lang), callback_data="ocr_cancel")
    ])
    return InlineKeyboardMarkup(keyboard)


# ── OCR bilan PDF yuborish tugmasi ────────────────────────────────────────────

def get_after_edit_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Tahrirlashdan keyin ko'rsatiladigan klaviatura."""
    keyboard = [
        [
            InlineKeyboardButton(_t("btn_done_edit", lang), callback_data="ed_done"),
            InlineKeyboardButton(_t("btn_back", lang),      callback_data="edit_menu"),
        ],
        [
            InlineKeyboardButton(_t("btn_cancel", lang), callback_data="pdf_cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ── Admin panel klaviaturasi ──────────────────────────────────────────────────

def get_admin_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Admin panel tugmalari."""
    keyboard = [
        [
            InlineKeyboardButton("📊 Statistika", callback_data="adm_stats"),
            InlineKeyboardButton("🔄 Yangilash",  callback_data="adm_refresh"),
        ],
        [
            InlineKeyboardButton("🧹 Tozalash",   callback_data="adm_cleanup"),
            InlineKeyboardButton("📋 Loglar",     callback_data="adm_logs"),
        ],
        [
            InlineKeyboardButton("🚫 Yopish",     callback_data="adm_close"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ── Collect rejim tugmasi ─────────────────────────────────────────────────────

def get_collect_done_keyboard(lang: str, count: int) -> InlineKeyboardMarkup:
    """Collect rejimda ko'rsatiladigan tugmalar."""
    keyboard = [
        [
            InlineKeyboardButton(
                f"✅ PDF Qil ({count} ta rasm)", callback_data="collect_done"
            ),
        ],
        [
            InlineKeyboardButton(
                "🔢 Tartibni o'zgartirish", callback_data="collect_order"
            ),
            InlineKeyboardButton(
                "❌ Bekor", callback_data="collect_cancel"
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ── Tasdiqlash klaviaturasi ───────────────────────────────────────────────────

def get_confirm_keyboard(lang: str, confirm_data: str, cancel_data: str = "action_cancel") -> InlineKeyboardMarkup:
    """Umumiy tasdiqlash klaviaturasi."""
    keyboard = [
        [
            InlineKeyboardButton(_t("btn_confirm", lang), callback_data=confirm_data),
            InlineKeyboardButton(_t("btn_cancel_action", lang), callback_data=cancel_data),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# ── Yopish tugmasi ────────────────────────────────────────────────────────────

def get_close_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Faqat yopish tugmasi."""
    keyboard = [[
        InlineKeyboardButton(_t("btn_close", lang), callback_data="close_msg")
    ]]
    return InlineKeyboardMarkup(keyboard)
