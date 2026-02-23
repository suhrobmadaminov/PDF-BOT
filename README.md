# 🤖 Image to PDF Pro Bot

Rasmlarni professional PDF ga aylantiruvchi Telegram bot.

---

## 📋 Talablar

- Python 3.11 yoki undan yuqori
- Tesseract OCR (OCR funksiyasi uchun)
- Windows/Linux/macOS

---

## 🚀 O'rnatish bosqichlari

### 1. Repozitoriyni yuklab olish

```bash
git clone <repo_url>
cd "Pdf bot"
```

### 2. Virtual muhit yaratish

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

> **Eslatma:** `easyocr` va `torch` yuklab olish vaqti biroz ko'p ketishi mumkin (500MB+).
> Agar OCR kerak bo'lmasa, `easyocr`, `torch` va `torchvision` ni requirements.txt dan olib tashlang.

---

## ⚙️ .env Sozlash

`.env` faylini oching va quyidagilarni to'ldiring:

```env
# Telegram Bot Token — @BotFather dan oling
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxyz

# Admin foydalanuvchilarning Telegram ID lari (vergul bilan)
ADMIN_IDS=123456789,987654321

# Maksimal rasm hajmi (bayt) — 20MB
MAX_FILE_SIZE=20971520

# Bir sessiyada maksimal rasmlar soni
MAX_IMAGES_PER_SESSION=50

# Tarix necha kun saqlansin
HISTORY_DAYS=7

# Vaqtinchalik fayllar papkasi
TEMP_DIR=./temp

# Tarix fayllar papkasi
HISTORY_DIR=./history

# Log darajasi
LOG_LEVEL=INFO
```

**Telegram ID ni qanday bilish:**
1. [@userinfobot](https://t.me/userinfobot) ga `/start` yuboring
2. Bot sizning ID ingizni ko'rsatadi

---

## 🔤 Tesseract O'rnatish (OCR uchun)

### Windows

1. [Tesseract yuklab olish](https://github.com/UB-Mannheim/tesseract/wiki)
2. `tesseract-ocr-w64-setup-v5.x.x.exe` ni ishga tushiring
3. O'rnatishda **qo'shimcha tillar** ni tanlang:
   - Uzbek (uzb)
   - Russian (rus)
   - Arabic (ara)
4. O'rnatish yo'lini PATH ga qo'shing: `C:\Program Files\Tesseract-OCR`
5. Sinash:
   ```cmd
   tesseract --version
   ```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-uzb   # O'zbek tili
sudo apt install tesseract-ocr-rus   # Rus tili
sudo apt install tesseract-ocr-ara   # Arab tili
```

### macOS

```bash
brew install tesseract
brew install tesseract-lang
```

---

## ▶️ Botni Ishga Tushirish

```bash
python main.py
```

Muvaffaqiyatli ishga tushganda konsolda quyidagi ko'rinadi:
```
==================================================
  IMAGE TO PDF PRO BOT ishga tushmoqda...
==================================================
INFO | Ma'lumotlar bazasi ulandi
INFO | Barcha handlerlar ro'yxatga olindi
INFO | Bot polling boshlandi (Ctrl+C bilan to'xtatish)
```

---

## 🔧 Bot Buyruqlari

| Buyruq | Tavsif |
|--------|--------|
| `/start` | Botni boshlash |
| `/help` | Yordam |
| `/collect` | Ko'p rasm yig'ish rejimi |
| `/done` | Yig'ishni tugatish va PDF qilish |
| `/cancel` | Rejimni bekor qilish |
| `/order` | Rasm tartibini o'zgartirish |
| `/quality` | PDF sifat darajasi |
| `/pagesize` | Sahifa o'lchami |
| `/orientation` | Sahifa yo'nalishi |
| `/margin` | Sahifa chegarasi |
| `/reverse` | PDF → Rasmlar |
| `/history` | PDF tarixim |
| `/lang` | Tilni o'zgartirish |
| `/admin` | Admin panel (faqat adminlar) |

---

## 📁 Fayl Strukturasi

```
Pdf bot/
├── main.py              — Asosiy ishga tushirish fayli
├── config.py            — Konfiguratsiya
├── database.py          — Ma'lumotlar bazasi
├── handlers/
│   ├── start_handler.py    — /start, /help
│   ├── image_handler.py    — Rasm qayta ishlash
│   ├── pdf_handler.py      — Ko'p rasm va tarix
│   ├── settings_handler.py — Sozlamalar
│   ├── admin_handler.py    — Admin panel
│   └── reverse_handler.py  — PDF → Rasm
├── services/
│   ├── pdf_converter.py    — PDF yaratish
│   ├── ocr_service.py      — Matn aniqlash
│   ├── image_editor.py     — Rasm tahrirlash
│   └── file_optimizer.py   — Optimallashtirish
├── locales/
│   ├── uz.py               — O'zbek tili
│   ├── ru.py               — Rus tili
│   └── en.py               — Ingliz tili
├── utils/
│   ├── keyboards.py        — Inline klaviaturalar
│   └── helpers.py          — Yordamchi funksiyalar
├── temp/                — Vaqtinchalik fayllar
├── history/             — PDF tarix fayllar
├── logs/                — Log fayllar
├── .env                 — Muhit o'zgaruvchilari
└── requirements.txt     — Python kutubxonalari
```

---

## ❗ Xatoliklarni Hal Qilish

### "BOT_TOKEN topilmadi"
- `.env` faylida `BOT_TOKEN` to'g'ri yozilganligini tekshiring
- Token to'g'ri ekanligini `@BotFather` orqali tekshiring

### "pytesseract: tesseract is not installed"
- Tesseract o'rnatilganligini tekshiring: `tesseract --version`
- Windows da PATH ga qo'shilganligini tekshiring
- Python skriptini qayta ishga tushiring

### "easyocr model yuklanmoqda..."
- Birinchi ishga tushirishda easyocr modellari yuklab olinadi (~500MB)
- Internet aloqasini tekshiring
- Sabr qiling (:

### "ModuleNotFoundError"
- Virtual muhit faolligini tekshiring
- `pip install -r requirements.txt` ni qayta ishga tushiring

### "Permission denied" (Windows)
- CMD yoki PowerShell ni Administrator sifatida oching

### "Port yoki fayl band"
- Boshqa bot instance ishlamasligini tekshiring
- `temp/` papkasida eski fayllar borligini tekshiring

---

## 📊 Ma'lumotlar Bazasi

Bot SQLite ma'lumotlar bazasidan foydalanadi (`pdf_bot.db`).

**Jadvallar:**
- `users` — foydalanuvchilar
- `sessions` — aktiv sessiyalar
- `pdf_history` — PDF tarix
- `statistics` — foydalanuvchi statistikasi
- `settings` — foydalanuvchi sozlamalari

---

## 🔒 Xavfsizlik

- Har foydalanuvchi uchun **rate limiting** (1 daqiqada 10 so'rov)
- Maksimal fayl hajmi: **20MB**
- Bir sessiyada maksimal rasmlar: **50 ta**
- Admin buyruqlari faqat `ADMIN_IDS` da ro'yxatga olingan IDlar uchun
- Bloklangan foydalanuvchilar bot bilan muloqot qila olmaydi

---

## 📄 Litsenziya

MIT License — bepul foydalanish va tarqatish mumkin.

---

*Muammo yoki takliflar uchun GitHub Issues dan foydalaning.*
