"""
English localization — all bot messages and buttons.
"""

EN_TEXTS: dict[str, str] = {

    # ── Main messages ─────────────────────────────────────────────────────────

    "welcome": (
        "👋 <b>Hello, {name}!</b>\n\n"
        "🤖 Welcome to <b>Image to PDF Pro Bot</b>!\n\n"
        "📌 <b>What can I do?</b>\n"
        "• 🖼️ Convert images to high-quality PDF\n"
        "• 📚 Merge multiple images into one PDF\n"
        "• 🔍 OCR — extract text from images\n"
        "• 📄 Split PDF into images\n"
        "• ✏️ Edit images (brightness, contrast, rotation)\n"
        "• 🗜️ Compress PDF files\n\n"
        "📎 <b>To start</b> just send an image!\n\n"
        "❓ Need help? Send /help"
    ),

    "help": (
        "📖 <b>User Guide</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🖼️ <b>Image → PDF</b>\n"
        "  Send an image and choose an action\n\n"
        "📚 <b>Multiple Images</b>\n"
        "  /collect → send images → /done\n\n"
        "🔍 <b>OCR (Text Recognition)</b>\n"
        "  Send image → tap «OCR PDF» button\n\n"
        "📄 <b>PDF → Images</b>\n"
        "  Send a PDF file or use /reverse\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "⚙️ <b>Commands</b>\n"
        "  /collect — multi-image collection mode\n"
        "  /done — finish collecting\n"
        "  /cancel — cancel operation\n"
        "  /quality — PDF quality settings\n"
        "  /pagesize — page size settings\n"
        "  /orientation — page orientation\n"
        "  /margin — margin size\n"
        "  /reverse — split PDF to images\n"
        "  /history — my PDF history\n"
        "  /lang — change language\n"
        "  /help — show help\n\n"
        "📦 <b>Supported formats:</b>\n"
        "  JPG, JPEG, PNG, WEBP, BMP, TIFF, HEIC"
    ),

    # ── Image received ────────────────────────────────────────────────────────

    "image_received": "📥 Image received! Choose an action:",
    "image_actions_caption": "🖼️ <b>File:</b> {filename}\n📦 <b>Size:</b> {size}",

    "btn_make_pdf":     "📄 Make PDF",
    "btn_compress_pdf": "🗜️ Compressed PDF",
    "btn_ocr_pdf":      "🔍 OCR PDF",
    "btn_edit":         "✏️ Edit",
    "btn_cancel":       "❌ Cancel",

    # ── Collect mode ──────────────────────────────────────────────────────────

    "collect_started": (
        "📚 <b>Collection mode enabled!</b>\n\n"
        "Send images one by one.\n"
        "Maximum: <b>{max_images}</b> images\n\n"
        "✅ Finish: /done\n"
        "❌ Cancel: /cancel"
    ),
    "collect_image_added":    "✅ Image {count} received. Total: {total}",
    "collect_max_reached":    "⚠️ Maximum images reached ({max}). Send /done.",
    "collect_no_images":      "❌ No images uploaded yet.",
    "collect_done_creating":  "⏳ Creating PDF... [{bar}] {percent}%",
    "collect_cancelled":      "❌ Collection cancelled. All files deleted.",
    "collect_not_active":     "❌ Collection mode is not active. Use /collect.",
    "collect_already_active": "ℹ️ Collection mode is already active. Keep sending images.",

    "order_help": (
        "🔢 <b>Reorder Images</b>\n\n"
        "Current images:\n{image_list}\n\n"
        "Enter the new order as numbers.\n"
        "Example: <code>3,1,2,4</code>"
    ),
    "order_applied":   "✅ Order changed!",
    "order_invalid":   "❌ Invalid order. All numbers must be specified.",
    "order_no_images": "❌ No images to reorder.",

    # ── PDF creation results ──────────────────────────────────────────────────

    "pdf_creating":    "⏳ Creating PDF...",
    "pdf_compressing": "⏳ Compressing PDF...",
    "pdf_ready": (
        "✅ <b>PDF is ready!</b>\n\n"
        "📦 Size: <b>{size}</b>\n"
        "📄 Pages: <b>{pages}</b>"
    ),
    "pdf_compressed_ready": (
        "✅ <b>PDF compressed and ready!</b>\n\n"
        "📦 Original size: <b>{original_size}</b>\n"
        "📦 Compressed: <b>{compressed_size}</b>\n"
        "💰 Saved: <b>{saved_percent}%</b>\n"
        "📄 Pages: <b>{pages}</b>"
    ),
    "pdf_error":     "❌ PDF creation failed. Try again: /start",
    "pdf_too_large": (
        "⚠️ <b>File is close to Telegram limit!</b>\n"
        "Size: {size} (Limit: 50MB)\n"
        "Reduce quality: /quality"
    ),
    "pdf_filename":  "document_{date}.pdf",

    # ── OCR ──────────────────────────────────────────────────────────────────

    "ocr_starting":    "🔍 Recognizing text...",
    "ocr_select_lang": "🌐 Select language for OCR:",
    "ocr_creating":    "⏳ Creating searchable PDF...",
    "ocr_success": (
        "✅ <b>OCR successful!</b>\n\n"
        "🔤 Characters recognized: <b>{chars}</b>\n"
        "📄 Searchable PDF created"
    ),
    "ocr_no_text":  "⚠️ No text found in image. Regular PDF created.",
    "ocr_error":    "❌ OCR error: {error}",
    "ocr_lang_set": "✅ OCR language set: {lang}",

    # ── Image editing ─────────────────────────────────────────────────────────

    "edit_menu":       "✏️ <b>Edit Menu</b>\nChoose an action:",
    "edit_brightness": "☀️ Choose brightness level:",
    "edit_contrast":   "🔲 Choose contrast level:",
    "edit_applying":   "⏳ Applying changes...",
    "edit_preview":    "👁️ Preview. Continue editing?",
    "edit_done":       "✅ Editing complete!",
    "edit_reset":      "🔄 Image reset to original",
    "edit_no_image":   "❌ No image to edit.",

    "btn_brightness":  "☀️ Brightness",
    "btn_contrast":    "🌑 Contrast",
    "btn_grayscale":   "⬛ Grayscale",
    "btn_rotate":      "🔄 Rotate",
    "btn_sharpen":     "🔆 Sharpen",
    "btn_a4_fit":      "📐 Fit to A4",
    "btn_reset_edit":  "↩️ Reset",
    "btn_done_edit":   "✅ Done, make PDF",
    "btn_back":        "◀️ Back",

    "btn_bright_m50":  "🌑 -50%",
    "btn_bright_m25":  "🌒 -25%",
    "btn_bright_norm": "⭕ Normal",
    "btn_bright_p25":  "🌔 +25%",
    "btn_bright_p50":  "☀️ +50%",

    "btn_contrast_low": "📉 Low",
    "btn_contrast_med": "➖ Medium",
    "btn_contrast_hi":  "➕ High",
    "btn_contrast_vhi": "📈 Very High",

    "btn_rotate_90":  "↻ 90°",
    "btn_rotate_180": "↻ 180°",
    "btn_rotate_270": "↻ 270°",

    # ── Quality settings ──────────────────────────────────────────────────────

    "quality_select":    "🎚️ <b>Select PDF quality:</b>",
    "quality_set":       "✅ Quality set to: {quality}",
    "btn_quality_low":   "🔴 Low (~100-300 KB)",
    "btn_quality_med":   "🟡 Medium (~500KB-1MB)",
    "btn_quality_hi":    "🟢 High (~2-5MB)",
    "btn_quality_ultra": "💎 Ultra (~5-15MB)",

    # ── Page settings ─────────────────────────────────────────────────────────

    "pagesize_select":    "📏 <b>Select page size:</b>",
    "pagesize_set":       "✅ Page size set to: {size}",

    "orientation_select": "🔄 <b>Select page orientation:</b>",
    "orientation_set":    "✅ Orientation set to: {orientation}",
    "btn_portrait":       "📱 Portrait",
    "btn_landscape":      "📺 Landscape",
    "btn_auto_orient":    "🤖 Auto",

    "margin_select":     "📐 <b>Select margin size:</b>",
    "margin_set":        "✅ Margin set to: {margin}",
    "btn_margin_none":   "⬛ None",
    "btn_margin_small":  "◻️ Small",
    "btn_margin_medium": "🔲 Medium",
    "btn_margin_large":  "⬜ Large",

    # ── Reverse: PDF → Images ─────────────────────────────────────────────────

    "reverse_prompt":     "📄 Send a PDF file or use /reverse command.",
    "reverse_select_fmt": (
        "🖼️ <b>PDF → Images</b>\n\n"
        "PDF: <b>{filename}</b>\n"
        "Pages: <b>{pages}</b>\n\n"
        "Select image format:"
    ),
    "reverse_page_range": (
        "📋 Enter page range (e.g.: <code>1-3, 5, 7-10</code>)\n"
        "Leave empty for all pages or send /all"
    ),
    "reverse_processing": "⏳ Splitting PDF into pages...",
    "reverse_page_done":  "✅ {pages} pages ready!",
    "reverse_zip_done":   "✅ ZIP archive ready! {pages} images",
    "reverse_no_pdf":     "❌ No PDF found. Send a PDF first.",
    "reverse_error":      "❌ PDF processing error: {error}",
    "reverse_invalid_range": "❌ Invalid page range. Example: 1-3, 5, 7",
    "btn_reverse_jpg":    "🖼️ JPG",
    "btn_reverse_png":    "📷 PNG",
    "btn_reverse_zip":    "🗜️ Compressed ZIP",

    # ── History ───────────────────────────────────────────────────────────────

    "history_title":   "📋 <b>Your PDF History:</b>",
    "history_empty":   "📭 Your history is empty. No PDFs created yet.",
    "history_item": (
        "📄 <b>{name}</b>\n"
        "   📦 {size} | 📅 {date} | 📃 {pages} pages"
    ),
    "history_deleted":   "🗑️ PDF deleted from history.",
    "history_not_found": "❌ PDF not found or already deleted.",
    "btn_download":      "⬇️ Download",
    "btn_delete":        "🗑️ Delete",

    # ── Language selection ────────────────────────────────────────────────────

    "lang_select": "🌐 <b>Tilni tanlang / Выберите язык / Choose language:</b>",
    "lang_set":    "✅ Language set to: English 🇬🇧",

    # ── Errors and warnings ───────────────────────────────────────────────────

    "error_invalid_format": (
        "❌ <b>Invalid format!</b>\n\n"
        "This format is not supported.\n"
        "Please send a file in one of these formats:\n"
        "📎 JPG, JPEG, PNG, WEBP, BMP, TIFF, HEIC"
    ),
    "error_file_too_large": (
        "❌ <b>File too large!</b>\n\n"
        "Maximum file size: <b>{max_size}</b>\n"
        "Your file: <b>{file_size}</b>\n\n"
        "Please send a smaller file."
    ),
    "error_banned":     "🚫 You cannot use this bot.",
    "error_rate_limit": "⏳ <b>Too many requests!</b>\n\nPlease wait {seconds} seconds.",
    "error_general":    "❌ An error occurred. Try again: /start",
    "error_pdf_send":   "❌ Error sending PDF.",
    "error_download":   "❌ Error downloading file.",
    "error_not_image":  "❌ This is not an image. Please send an image.",
    "error_not_pdf":    "❌ This is not a PDF. Please send a PDF file.",

    # ── Admin panel ───────────────────────────────────────────────────────────

    "admin_only": "🔐 This command is for administrators only.",
    "admin_panel": (
        "🔧 <b>Admin Panel</b>\n\n"
        "📊 <b>Statistics:</b>\n"
        "  👥 Total users: <b>{total_users}</b>\n"
        "  🟢 Active today: <b>{active_today}</b>\n"
        "  📄 Total PDFs: <b>{total_pdfs}</b>\n"
        "  📅 PDFs today: <b>{pdfs_today}</b>\n"
        "  🚫 Banned: <b>{banned_users}</b>\n\n"
        "📈 <b>Top features:</b>\n"
        "{top_actions}\n\n"
        "🔧 <b>Management commands:</b>\n"
        "/broadcast — Send to all users\n"
        "/ban [user_id] — Ban user\n"
        "/unban [user_id] — Unban user\n"
        "/stats [user_id] — User statistics\n"
        "/cleanup — Clean temp files\n"
        "/logs — Recent errors"
    ),
    "broadcast_usage":   "📢 Usage: /broadcast [message text]",
    "broadcast_started": "📤 Broadcasting started...",
    "broadcast_done": (
        "✅ <b>Broadcast complete!</b>\n\n"
        "✅ Sent: {sent}\n"
        "❌ Failed: {failed}"
    ),
    "ban_usage":     "Usage: /ban [user_id]",
    "ban_done":      "🚫 User {user_id} has been banned.",
    "ban_not_found": "❌ User not found.",
    "unban_done":    "✅ User {user_id} has been unbanned.",
    "stats_usage":   "Usage: /stats [user_id]",
    "stats_user": (
        "📊 <b>User Statistics</b>\n\n"
        "👤 ID: <code>{user_id}</code>\n"
        "📛 Name: {full_name}\n"
        "🔖 Username: @{username}\n"
        "🌐 Language: {lang}\n"
        "📅 Joined: {joined_at}\n"
        "🕐 Last active: {last_active}\n"
        "🚫 Banned: {is_banned}\n\n"
        "📄 PDFs created: {total_pdfs}\n"
        "🔍 OCR used: {ocr_count}\n"
        "🔄 Reverse used: {reverse_count}\n"
        "📋 PDFs in history: {history_count}"
    ),
    "cleanup_done": "🧹 Cleaned {count} temporary files.",
    "logs_title":   "📋 <b>Last {count} errors:</b>\n\n",
    "logs_empty":   "✅ Error log is empty.",

    # ── General buttons ───────────────────────────────────────────────────────

    "btn_cancel_action": "❌ Cancel",
    "btn_confirm":       "✅ Confirm",
    "btn_close":         "🚫 Close",
    "btn_refresh":       "🔄 Refresh",
    "btn_main_menu":     "🏠 Main Menu",

    "progress_uploading":  "📤 Uploading...",
    "progress_processing": "⚙️ Processing...",
    "progress_saving":     "💾 Saving...",
    "progress_sending":    "📨 Sending...",

    "welcome_back": "👋 Welcome back! Send an image or type /help.",

    "default_pdf_name":  "converted_{timestamp}.pdf",
    "ocr_pdf_name":      "ocr_{timestamp}.pdf",
    "multi_pdf_name":    "merged_{timestamp}.pdf",
    "reverse_zip_name":  "pages_{timestamp}.zip",
}
