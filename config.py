"""
Konfiguratsiya moduli — barcha sozlamalar markaziy boshqaruv.
.env faylidan o'zgaruvchilar yuklanadi va butun bot uchun konstanta sifatida taqdim etiladi.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

# ── Bot asosiy sozlamalari ────────────────────────────────────────────────────

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN .env faylida topilmadi!\n"
        "Iltimos .env faylini to'g'ri sozlang va BOT_TOKEN ni kiriting."
    )

# Admin IDlari — .env dan o'qiladi
_admin_ids_str: str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: list[int] = [
    int(x.strip())
    for x in _admin_ids_str.split(",")
    if x.strip().lstrip("-").isdigit()
]

# ── Fayl cheklovlari ──────────────────────────────────────────────────────────

# Maksimal fayl hajmi (bayt) — default 20MB
MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(20 * 1024 * 1024)))

# Bir sessiyada maksimal rasmlar soni
MAX_IMAGES_PER_SESSION: int = int(os.getenv("MAX_IMAGES_PER_SESSION", "50"))

# Tarix necha kun saqlansin
HISTORY_DAYS: int = int(os.getenv("HISTORY_DAYS", "7"))

# Telegram fayl yuklash limiti (50MB)
TELEGRAM_MAX_FILE_SIZE: int = 50 * 1024 * 1024

# ── Papka yo'llari ────────────────────────────────────────────────────────────

# Bot joylashgan asosiy papka
BASE_DIR: Path = Path(__file__).parent.resolve()

# Railway Volume yoki lokal papka:
# Railway da DATA_DIR=/data deb environment variable qo'ying
# Lokal da esa avtomatik BASE_DIR ichidagi papkalar ishlatiladi
DATA_DIR: Path = Path(os.getenv("DATA_DIR", str(BASE_DIR)))

# Vaqtinchalik fayllar papkasi (/tmp — Railway va Linux da doim mavjud)
TEMP_DIR: Path = Path(os.getenv("TEMP_DIR", "/tmp/pdf_bot_temp"))

# PDF tarix fayllar papkasi (DATA_DIR ichida — persistent storage)
HISTORY_DIR: Path = Path(os.getenv("HISTORY_DIR", str(DATA_DIR / "history")))

# Log fayllar papkasi
LOG_DIR: Path = DATA_DIR / "logs"

# Barcha papkalarni yaratish (mavjud bo'lmasa)
for _dir in [TEMP_DIR, HISTORY_DIR, LOG_DIR]:
    _dir.mkdir(parents=True, exist_ok=True)

# ── Logging sozlamalari ───────────────────────────────────────────────────────

LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE: Path = LOG_DIR / "bot.log"
LOG_ERROR_FILE: Path = LOG_DIR / "errors.log"

# ── Ma'lumotlar bazasi ────────────────────────────────────────────────────────

# Railway da DATA_DIR=/data bo'lsa, database u yerda saqlanadi (persistent)
DATABASE_PATH: Path = DATA_DIR / "pdf_bot.db"

# ── Rasm formatlari ───────────────────────────────────────────────────────────

# Ruxsat etilgan MIME turlar
ALLOWED_MIME_TYPES: frozenset[str] = frozenset({
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/bmp",
    "image/tiff",
    "image/heic",
    "image/heif",
})

# Ruxsat etilgan fayl kengaytmalari
ALLOWED_EXTENSIONS: frozenset[str] = frozenset({
    ".jpg", ".jpeg", ".png", ".webp",
    ".bmp", ".tiff", ".tif", ".heic", ".heif",
})

# ── Sahifa o'lchamlari (mm da) ────────────────────────────────────────────────

PAGE_SIZES: dict[str, tuple[float, float] | None] = {
    "A3":       (297.0, 420.0),
    "A4":       (210.0, 297.0),
    "A5":       (148.0, 210.0),
    "Letter":   (215.9, 279.4),
    "Legal":    (215.9, 355.6),
    "Original": None,   # Rasmning o'z o'lchami saqlanadi
}

# ── Sifat darajalari ──────────────────────────────────────────────────────────

QUALITY_SETTINGS: dict[str, dict] = {
    "low": {
        "dpi": 72,
        "quality": 40,
        "optimize": True,
        "max_size": (800, 800),
        "label": "🔴 Past",
        "desc": "~100-300 KB",
    },
    "medium": {
        "dpi": 150,
        "quality": 70,
        "optimize": True,
        "max_size": (1920, 1920),
        "label": "🟡 O'rta",
        "desc": "~500KB-1MB",
    },
    "high": {
        "dpi": 200,
        "quality": 85,
        "optimize": False,
        "max_size": (2560, 2560),
        "label": "🟢 Yuqori",
        "desc": "~2-5MB",
    },
    "ultra": {
        "dpi": 300,
        "quality": 95,
        "optimize": False,
        "max_size": (4096, 4096),
        "label": "💎 Ultra",
        "desc": "~5-15MB",
    },
}

# ── OCR tillari ───────────────────────────────────────────────────────────────

OCR_LANGUAGES: dict[str, dict] = {
    "uz": {
        "tesseract": "uzb",
        "easyocr": ["uz"],
        "display": "🇺🇿 O'zbek",
    },
    "ru": {
        "tesseract": "rus",
        "easyocr": ["ru"],
        "display": "🇷🇺 Русский",
    },
    "en": {
        "tesseract": "eng",
        "easyocr": ["en"],
        "display": "🇬🇧 English",
    },
    "ar": {
        "tesseract": "ara",
        "easyocr": ["ar"],
        "display": "🇸🇦 العربية",
    },
}

# ── Rate Limiting ─────────────────────────────────────────────────────────────

# 1 daqiqada maksimal so'rovlar soni
RATE_LIMIT_REQUESTS: int = 10

# Vaqt oynasi (sekund)
RATE_LIMIT_WINDOW: int = 60

# ── Tarix ─────────────────────────────────────────────────────────────────────

# Har foydalanuvchi uchun saqlaniladigan maksimal PDF soni
MAX_HISTORY_COUNT: int = 5

# ── Margin o'lchamlari (piksel, 72 DPI uchun) ─────────────────────────────────

MARGIN_SIZES: dict[str, int] = {
    "none":   0,
    "small":  10,
    "medium": 30,
    "large":  50,
}

# ── Default foydalanuvchi sozlamalari ─────────────────────────────────────────

DEFAULT_SETTINGS: dict = {
    "quality":     "high",
    "pagesize":    "A4",
    "orientation": "portrait",
    "margin":      "small",
    "ocr_lang":    "en",
}

# ── Interfeys tillari ─────────────────────────────────────────────────────────

SUPPORTED_LANGS: list[str] = ["uz", "ru", "en"]
DEFAULT_LANG: str = "uz"

# ── APScheduler sozlamalari ───────────────────────────────────────────────────

# Eski fayllarni tozalash vaqti (har kecha 03:00 da)
CLEANUP_HOUR: int = 3
CLEANUP_MINUTE: int = 0
