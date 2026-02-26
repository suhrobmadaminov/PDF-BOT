"""
O'zbek tili lokalizatsiyasi — barcha bot xabarlari va tugmalar.
"""

UZ_TEXTS: dict[str, str] = {

    # ── Asosiy xabarlar ──────────────────────────────────────────────────────

    "welcome": (
        "👋 <b>Assalomu alaykum, {name}!</b>\n\n"
        "🤖 <b>Image to PDF Pro Bot</b> ga xush kelibsiz!\n\n"
        "📌 <b>Men nima qila olaman?</b>\n"
        "• 🖼️ Rasmlarni yuqori sifatli PDF ga aylantirish\n"
        "• 📚 Bir nechta rasmlarni bitta PDF ga birlashtirish\n"
        "• 🔍 OCR — rasm ichidagi matnni aniqlash\n"
        "• 📄 PDF ni rasmlarga ajratish\n"
        "• ✏️ Rasmlarni tahrirlash (yorqinlik, kontrast, aylantirish)\n"
        "• 🗜️ PDF fayllarni siqish\n\n"
        "📎 <b>Boshlash uchun</b> shunchaki rasm yuboring!\n\n"
        "❓ Yordam kerakmi? /help buyrug'ini yuboring."
    ),

    "help": (
        "📖 <b>Foydalanish qo'llanmasi</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🖼️ <b>Rasm → PDF</b>\n"
        "  Rasm yuboring va tugmalardan tanlang\n\n"
        "📚 <b>Ko'p rasmli PDF</b>\n"
        "  /collect → rasmlarni yuboring → /done\n\n"
        "🔍 <b>OCR (Matn aniqlash)</b>\n"
        "  Rasm yuboring → «OCR bilan PDF» tugmasini bosing\n\n"
        "📄 <b>PDF → Rasmlar</b>\n"
        "  PDF faylni yuboring yoki /reverse buyrug'i\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "⚙️ <b>Buyruqlar</b>\n"
        "  /collect — ko'p rasm yig'ish rejimi\n"
        "  /done — yig'ishni tugatish\n"
        "  /cancel — bekor qilish\n"
        "  /quality — PDF sifatini tanlash\n"
        "  /pagesize — sahifa o'lchamini tanlash\n"
        "  /orientation — sahifa yo'nalishi\n"
        "  /margin — chegara o'lchami\n"
        "  /reverse — PDF ni rasmlarga ajratish\n"
        "  /history — PDF tarixim\n"
        "  /lang — til tanlash\n"
        "  /help — yordam\n\n"
        "📦 <b>Qo'llab-quvvatlanadigan formatlar:</b>\n"
        "  JPG, JPEG, PNG, WEBP, BMP, TIFF, HEIC"
    ),

    # ── Rasm qabul qilish ────────────────────────────────────────────────────

    "image_received": "📥 Rasm qabul olindi! Nima qilishni tanlang:",
    "image_actions_caption": "🖼️ <b>Rasm:</b> {filename}\n📦 <b>Hajmi:</b> {size}",

    # Rasm harakatlar klaviaturasi
    "btn_make_pdf":     "📄 PDF Qil",
    "btn_compress_pdf": "🗜️ Siqib PDF Qil",
    "btn_ocr_pdf":      "🔍 OCR bilan PDF",
    "btn_edit":         "✏️ Tahrirlash",
    "btn_cancel":       "❌ Bekor",

    # ── Ko'p rasmli rejim ────────────────────────────────────────────────────

    "collect_started": (
        "📚 <b>Ko'p rasm yig'ish rejimi yoqildi!</b>\n\n"
        "Endi rasmlarni birin-ketin yuboring.\n"
        "Maksimum: <b>{max_images} ta</b> rasm\n\n"
        "✅ Tugatish: /done\n"
        "❌ Bekor qilish: /cancel"
    ),
    "collect_image_added":   "✅ {count}-rasm qabul olindi. Jami: {total} ta",
    "collect_max_reached":   "⚠️ Maksimal rasm soni ({max}) ga yetdingiz. /done yuboring.",
    "collect_no_images":     "❌ Hali rasm yuklanmagan. Avval rasm yuboring.",
    "collect_done_creating": "⏳ PDF yaratilmoqda... [{bar}] {percent}%",
    "collect_cancelled":     "❌ Yig'ish rejimi bekor qilindi. Barcha rasmlar o'chirildi.",
    "collect_not_active":    "❌ Hozir yig'ish rejimi faol emas. /collect buyrug'ini yuboring.",
    "collect_already_active": "ℹ️ Yig'ish rejimi allaqachon faol. Rasmlarni yuborishda davom eting.",

    "order_help": (
        "🔢 <b>Tartibni o'zgartirish</b>\n\n"
        "Hozirgi rasmlar:\n{image_list}\n\n"
        "Yangi tartibni raqamlar bilan yozing.\n"
        "Masalan: <code>3,1,2,4</code>\n"
        "(3-rasm birinchi, 1-rasm ikkinchi bo'ladi)"
    ),
    "order_applied":  "✅ Tartib o'zgartirildi!",
    "order_invalid":  "❌ Noto'g'ri tartib. Barcha raqamlar ko'rsatilishi kerak.",
    "order_no_images": "❌ Tartiblash uchun rasmlar yo'q.",

    # ── PDF yaratish natijalari ───────────────────────────────────────────────

    "pdf_creating":        "⏳ PDF yaratilmoqda...",
    "pdf_compressing":     "⏳ PDF siqilmoqda...",
    "pdf_ready": (
        "✅ <b>PDF tayyor!</b>\n\n"
        "📦 Hajmi: <b>{size}</b>\n"
        "📄 Sahifalar: <b>{pages}</b>"
    ),
    "pdf_compressed_ready": (
        "✅ <b>PDF siqildi va tayyor!</b>\n\n"
        "📦 Asl hajm: <b>{original_size}</b>\n"
        "📦 Siqilgan: <b>{compressed_size}</b>\n"
        "💰 Tejaldi: <b>{saved_percent}%</b>\n"
        "📄 Sahifalar: <b>{pages}</b>"
    ),
    "pdf_error": "❌ PDF yaratishda xatolik yuz berdi. Qayta urinib ko'ring: /start",
    "pdf_too_large": (
        "⚠️ <b>Fayl Telegram limitiga yaqin!</b>\n"
        "Hajmi: {size} (Limit: 50MB)\n"
        "Sifatni pastroq tanlashingiz mumkin: /quality"
    ),
    "pdf_filename":        "document_{date}.pdf",

    # ── OCR ─────────────────────────────────────────────────────────────────

    "ocr_starting":        "🔍 Matn aniqlanmoqda...",
    "ocr_select_lang":     "🌐 OCR uchun tilni tanlang:",
    "ocr_creating":        "⏳ Qidiriluvchi PDF yaratilmoqda...",
    "ocr_success": (
        "✅ <b>OCR muvaffaqiyatli!</b>\n\n"
        "🔤 Aniqlangan belgilar: <b>{chars}</b>\n"
        "📄 PDF qidiriladigan"
    ),
    "ocr_no_text":         "⚠️ Rasmda matn topilmadi. Oddiy PDF yaratildi.",
    "ocr_error":           "❌ OCR xatolik: {error}",
    "ocr_lang_set":        "✅ OCR tili o'rnatildi: {lang}",

    # ── Rasm tahrirlash ──────────────────────────────────────────────────────

    "edit_menu":           "✏️ <b>Tahrirlash menyusi</b>\nQaysi amaliyotni bajarishni tanlang:",
    "edit_brightness":     "☀️ Yorqinlik darajasini tanlang:",
    "edit_contrast":       "🔲 Kontrast darajasini tanlang:",
    "edit_applying":       "⏳ Tahrirlash qo'llanmoqda...",
    "edit_preview":        "👁️ Ko'rinish. Davom etasizmi?",
    "edit_done":           "✅ Tahrirlash tugadi!",
    "edit_reset":          "🔄 Rasm asl holatiga qaytarildi",
    "edit_no_image":       "❌ Tahrirlash uchun rasm yo'q.",

    "btn_brightness":   "☀️ Yorqinlik",
    "btn_contrast":     "🌑 Kontrast",
    "btn_grayscale":    "⬛ Qora-oq",
    "btn_rotate":       "🔄 Aylantirish",
    "btn_sharpen":      "🔆 Keskinlashtirish",
    "btn_a4_fit":       "📐 A4 ga moslashtirish",
    "btn_reset_edit":   "↩️ Qaytarish",
    "btn_done_edit":    "✅ Tayyor, PDF qil",
    "btn_back":         "◀️ Orqaga",

    "btn_bright_m50":   "🌑 -50%",
    "btn_bright_m25":   "🌒 -25%",
    "btn_bright_norm":  "⭕ Normal",
    "btn_bright_p25":   "🌔 +25%",
    "btn_bright_p50":   "☀️ +50%",

    "btn_contrast_low":  "📉 Past",
    "btn_contrast_med":  "➖ O'rta",
    "btn_contrast_hi":   "➕ Yuqori",
    "btn_contrast_vhi":  "📈 Juda yuqori",

    "btn_rotate_90":   "↻ 90°",
    "btn_rotate_180":  "↻ 180°",
    "btn_rotate_270":  "↻ 270°",

    # ── Sifat sozlamalari ────────────────────────────────────────────────────

    "quality_select":     "🎚️ <b>PDF sifatini tanlang:</b>",
    "quality_set":        "✅ Sifat o'rnatildi: {quality}",
    "btn_quality_low":    "🔴 Past (~100-300 KB)",
    "btn_quality_med":    "🟡 O'rta (~500KB-1MB)",
    "btn_quality_hi":     "🟢 Yuqori (~2-5MB)",
    "btn_quality_ultra":  "💎 Ultra (~5-15MB)",

    # ── Sahifa sozlamalari ───────────────────────────────────────────────────

    "pagesize_select":    "📏 <b>Sahifa o'lchamini tanlang:</b>",
    "pagesize_set":       "✅ Sahifa o'lchami: {size}",

    "orientation_select": "🔄 <b>Sahifa yo'nalishini tanlang:</b>",
    "orientation_set":    "✅ Yo'nalish o'rnatildi: {orientation}",
    "btn_portrait":       "📱 Vertikal (Portrait)",
    "btn_landscape":      "📺 Gorizontal (Landscape)",
    "btn_auto_orient":    "🤖 Avtomatik",

    "margin_select":      "📐 <b>Chegara o'lchamini tanlang:</b>",
    "margin_set":         "✅ Chegara o'rnatildi: {margin}",
    "btn_margin_none":    "⬛ Yo'q",
    "btn_margin_small":   "◻️ Kichik",
    "btn_margin_medium":  "🔲 O'rta",
    "btn_margin_large":   "⬜ Katta",

    # ── Reverse: PDF → Rasmlar ───────────────────────────────────────────────

    "reverse_prompt":     "📄 PDF faylni yuboring yoki /reverse buyrug'ini kiriting.",
    "reverse_select_fmt": (
        "🖼️ <b>PDF → Rasm</b>\n\n"
        "PDF: <b>{filename}</b>\n"
        "Sahifalar: <b>{pages}</b>\n\n"
        "Rasm formatini tanlang:"
    ),
    "reverse_page_range": (
        "📋 Sahifa oralig'ini kiriting (masalan: <code>1-3, 5, 7-10</code>)\n"
        "Barcha sahifalar uchun bo'sh qoldiring yoki /all yuboring."
    ),
    "reverse_processing": "⏳ PDF sahifalarga ajratilmoqda...",
    "reverse_page_done":  "✅ {pages} ta sahifa tayyor!",
    "reverse_zip_done":   "✅ ZIP arxiv tayyor! {pages} ta rasm",
    "reverse_no_pdf":     "❌ PDF topilmadi. Avval PDF yuboring.",
    "reverse_error":      "❌ PDF qayta ishlashda xato: {error}",
    "reverse_invalid_range": "❌ Noto'g'ri sahifa oralig'i. Masalan: 1-3, 5, 7",
    "btn_reverse_jpg":    "🖼️ JPG",
    "btn_reverse_png":    "📷 PNG",
    "btn_reverse_zip":    "🗜️ Siqilgan ZIP",

    # ── Tarix ───────────────────────────────────────────────────────────────

    "history_title":      "📋 <b>PDF tarixingiz:</b>",
    "history_empty":      "📭 PDF tarixingiz bo'sh. Hali PDF yaratilmagan.",
    "history_item": (
        "📄 <b>{name}</b>\n"
        "   📦 {size} | 📅 {date} | 📃 {pages} sahifa"
    ),
    "history_deleted":    "🗑️ PDF tarixdan o'chirildi.",
    "history_not_found":  "❌ Bu PDF topilmadi yoki allaqachon o'chirilgan.",
    "btn_download":       "⬇️ Yuklab olish",
    "btn_delete":         "🗑️ O'chirish",

    # ── Til tanlash ──────────────────────────────────────────────────────────

    "lang_select":        "🌐 <b>Tilni tanlang / Выберите язык / Choose language:</b>",
    "lang_set":           "✅ Til o'rnatildi: O'zbek 🇺🇿",

    # ── Xatolar va ogohlantirishlar ───────────────────────────────────────────

    "error_invalid_format": (
        "❌ <b>Noto'g'ri format!</b>\n\n"
        "Bu format qo'llab-quvvatlanmaydi.\n"
        "Iltimos quyidagi formatlardan birini yuboring:\n"
        "📎 JPG, JPEG, PNG, WEBP, BMP, TIFF, HEIC"
    ),
    "error_file_too_large": (
        "❌ <b>Fayl juda katta!</b>\n\n"
        "Maksimal fayl hajmi: <b>{max_size}</b>\n"
        "Sizning faylingiz: <b>{file_size}</b>\n\n"
        "Iltimos, kichikroq fayl yuboring."
    ),
    "error_banned": "🚫 Siz ushbu botdan foydalana olmaysiz.",
    "error_rate_limit": (
        "⏳ <b>Juda ko'p so'rov!</b>\n\n"
        "Iltimos {seconds} soniya kuting."
    ),
    "error_general": "❌ Xatolik yuz berdi. Qayta urinib ko'ring: /start",
    "error_pdf_send": "❌ PDF yuborishda xatolik yuz berdi.",
    "error_download": "❌ Faylni yuklab olishda xatolik.",
    "error_not_image": "❌ Bu rasm emas. Iltimos rasm yuboring.",
    "error_not_pdf":   "❌ Bu PDF emas. Iltimos PDF fayl yuboring.",
    "error_unsupported_file": (
        "❌ <b>Bu fayl formati qo'llab-quvvatlanmaydi.</b>\n\n"
        "📌 Bot faqat quyidagilarni qabul qiladi:\n"
        "• 🖼️ Rasmlar: JPG, PNG, WEBP, BMP, TIFF, HEIC\n"
        "• 📄 PDF fayllar (/reverse buyrug'i uchun)\n\n"
        "PDF yaratish uchun rasm yuboring."
    ),

    # ── Admin panel ──────────────────────────────────────────────────────────

    "admin_only":         "🔐 Bu buyruq faqat adminlar uchun.",
    "admin_panel": (
        "🔧 <b>Admin Panel</b>\n\n"
        "📊 <b>Statistika:</b>\n"
        "  👥 Jami foydalanuvchilar: <b>{total_users}</b>\n"
        "  🟢 Bugungi aktiv: <b>{active_today}</b>\n"
        "  📄 Jami PDF lar: <b>{total_pdfs}</b>\n"
        "  📅 Bugungi PDF lar: <b>{pdfs_today}</b>\n"
        "  🚫 Bloklangan: <b>{banned_users}</b>\n\n"
        "📈 <b>Top funksiyalar:</b>\n"
        "{top_actions}\n\n"
        "🔧 <b>Boshqaruv buyruqlari:</b>\n"
        "/broadcast — Barcha foydalanuvchilarga xabar\n"
        "/ban [user_id] — Bloklash\n"
        "/unban [user_id] — Blokdan chiqarish\n"
        "/stats [user_id] — Foydalanuvchi statistikasi\n"
        "/cleanup — Temp fayllarni tozalash\n"
        "/logs — Oxirgi xatolar"
    ),
    "broadcast_usage":    "📢 Foydalanish: /broadcast [xabar matni]",
    "broadcast_started":  "📤 Xabar yuborish boshlandi...",
    "broadcast_done": (
        "✅ <b>Broadcast tugadi!</b>\n\n"
        "✅ Yuborildi: {sent}\n"
        "❌ Xato: {failed}"
    ),
    "ban_usage":          "Foydalanish: /ban [user_id]",
    "ban_done":           "🚫 Foydalanuvchi {user_id} bloklandi.",
    "ban_not_found":      "❌ Foydalanuvchi topilmadi.",
    "unban_done":         "✅ Foydalanuvchi {user_id} blokdan chiqarildi.",
    "stats_usage":        "Foydalanish: /stats [user_id]",
    "stats_user": (
        "📊 <b>Foydalanuvchi statistikasi</b>\n\n"
        "👤 ID: <code>{user_id}</code>\n"
        "📛 Ism: {full_name}\n"
        "🔖 Username: @{username}\n"
        "🌐 Til: {lang}\n"
        "📅 Qo'shilgan: {joined_at}\n"
        "🕐 Oxirgi faollik: {last_active}\n"
        "🚫 Bloklangan: {is_banned}\n\n"
        "📄 Yaratilgan PDF: {total_pdfs}\n"
        "🔍 OCR ishlatilgan: {ocr_count}\n"
        "🔄 Reverse ishlatilgan: {reverse_count}\n"
        "📋 Tarixdagi PDF: {history_count}"
    ),
    "cleanup_done":       "🧹 {count} ta vaqtinchalik fayl o'chirildi.",
    "logs_title":         "📋 <b>Oxirgi {count} ta xato:</b>\n\n",
    "logs_empty":         "✅ Xatolar jurnali bo'sh.",

    # ── Umumiy tugmalar ──────────────────────────────────────────────────────

    "btn_cancel_action":  "❌ Bekor qilish",
    "btn_confirm":        "✅ Tasdiqlash",
    "btn_close":          "🚫 Yopish",
    "btn_refresh":        "🔄 Yangilash",
    "btn_main_menu":      "🏠 Bosh menyu",

    # ── Progress bar ─────────────────────────────────────────────────────────

    "progress_uploading":  "📤 Yuklanmoqda...",
    "progress_processing": "⚙️ Qayta ishlanmoqda...",
    "progress_saving":     "💾 Saqlanmoqda...",
    "progress_sending":    "📨 Yuborilmoqda...",

    # ── Xush kelibsiz xabar foydalanuvchi qaytganda ───────────────────────────

    "welcome_back": "👋 Qaytganingiz bilan! Rasm yuboring yoki /help buyrug'ini kiriting.",

    # ── Asosiy menyu tugmalari (ReplyKeyboard) ────────────────────────────────

    "menu_btn_collect":    "📁 Ko'p rasm yig'ish",
    "menu_btn_history":    "📋 Tarix",
    "menu_btn_settings":   "⚙️ Sozlamalar",
    "menu_btn_help":       "❓ Yordam",

    # ── Fayl nomi ────────────────────────────────────────────────────────────

    "default_pdf_name":    "converted_{timestamp}.pdf",
    "ocr_pdf_name":        "ocr_{timestamp}.pdf",
    "multi_pdf_name":      "merged_{timestamp}.pdf",
    "reverse_zip_name":    "pages_{timestamp}.zip",
}
