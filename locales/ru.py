"""
Русская локализация — все сообщения и кнопки бота.
"""

RU_TEXTS: dict[str, str] = {

    # ── Основные сообщения ────────────────────────────────────────────────────

    "welcome": (
        "👋 <b>Привет, {name}!</b>\n\n"
        "🤖 Добро пожаловать в <b>Image to PDF Pro Bot</b>!\n\n"
        "📌 <b>Что я умею?</b>\n"
        "• 🖼️ Конвертировать изображения в высококачественный PDF\n"
        "• 📚 Объединять несколько изображений в один PDF\n"
        "• 🔍 OCR — распознавание текста на изображениях\n"
        "• 📄 Разбивать PDF на изображения\n"
        "• ✏️ Редактировать изображения (яркость, контраст, поворот)\n"
        "• 🗜️ Сжимать PDF файлы\n\n"
        "📎 <b>Для начала</b> просто отправьте изображение!\n\n"
        "❓ Нужна помощь? Отправьте /help"
    ),

    "help": (
        "📖 <b>Руководство пользователя</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🖼️ <b>Изображение → PDF</b>\n"
        "  Отправьте изображение и выберите действие\n\n"
        "📚 <b>Несколько изображений</b>\n"
        "  /collect → отправьте изображения → /done\n\n"
        "🔍 <b>OCR (Распознавание текста)</b>\n"
        "  Отправьте изображение → нажмите «OCR PDF»\n\n"
        "📄 <b>PDF → Изображения</b>\n"
        "  Отправьте PDF файл или используйте /reverse\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "⚙️ <b>Команды</b>\n"
        "  /collect — режим сбора изображений\n"
        "  /done — завершить сбор\n"
        "  /cancel — отмена\n"
        "  /quality — качество PDF\n"
        "  /pagesize — размер страницы\n"
        "  /orientation — ориентация страницы\n"
        "  /margin — размер полей\n"
        "  /reverse — PDF в изображения\n"
        "  /history — история PDF\n"
        "  /lang — выбор языка\n"
        "  /help — помощь\n\n"
        "📦 <b>Поддерживаемые форматы:</b>\n"
        "  JPG, JPEG, PNG, WEBP, BMP, TIFF, HEIC"
    ),

    # ── Получение изображений ─────────────────────────────────────────────────

    "image_received": "📥 Изображение получено! Выберите действие:",
    "image_actions_caption": "🖼️ <b>Файл:</b> {filename}\n📦 <b>Размер:</b> {size}",

    "btn_make_pdf":     "📄 Создать PDF",
    "btn_compress_pdf": "🗜️ Сжатый PDF",
    "btn_ocr_pdf":      "🔍 OCR + PDF",
    "btn_edit":         "✏️ Редактировать",
    "btn_cancel":       "❌ Отмена",

    # ── Режим сбора изображений ───────────────────────────────────────────────

    "collect_started": (
        "📚 <b>Режим сбора изображений включён!</b>\n\n"
        "Отправляйте изображения по одному.\n"
        "Максимум: <b>{max_images}</b> изображений\n\n"
        "✅ Завершить: /done\n"
        "❌ Отменить: /cancel"
    ),
    "collect_image_added":    "✅ Изображение {count} получено. Всего: {total}",
    "collect_max_reached":    "⚠️ Достигнут лимит ({max}). Отправьте /done.",
    "collect_no_images":      "❌ Изображения ещё не загружены.",
    "collect_done_creating":  "⏳ Создание PDF... [{bar}] {percent}%",
    "collect_cancelled":      "❌ Режим сбора отменён. Все файлы удалены.",
    "collect_not_active":     "❌ Режим сбора не активен. Используйте /collect.",
    "collect_already_active": "ℹ️ Режим сбора уже активен. Продолжайте отправку.",

    "order_help": (
        "🔢 <b>Изменить порядок</b>\n\n"
        "Текущие изображения:\n{image_list}\n\n"
        "Введите новый порядок числами.\n"
        "Например: <code>3,1,2,4</code>"
    ),
    "order_applied":   "✅ Порядок изменён!",
    "order_invalid":   "❌ Неверный порядок. Укажите все номера.",
    "order_no_images": "❌ Нет изображений для сортировки.",

    # ── Результаты создания PDF ───────────────────────────────────────────────

    "pdf_creating":    "⏳ Создание PDF...",
    "pdf_compressing": "⏳ Сжатие PDF...",
    "pdf_ready": (
        "✅ <b>PDF готов!</b>\n\n"
        "📦 Размер: <b>{size}</b>\n"
        "📄 Страниц: <b>{pages}</b>"
    ),
    "pdf_compressed_ready": (
        "✅ <b>PDF сжат и готов!</b>\n\n"
        "📦 Исходный размер: <b>{original_size}</b>\n"
        "📦 После сжатия: <b>{compressed_size}</b>\n"
        "💰 Экономия: <b>{saved_percent}%</b>\n"
        "📄 Страниц: <b>{pages}</b>"
    ),
    "pdf_error":      "❌ Ошибка создания PDF. Попробуйте снова: /start",
    "pdf_too_large": (
        "⚠️ <b>Файл близок к лимиту Telegram!</b>\n"
        "Размер: {size} (Лимит: 50MB)\n"
        "Уменьшите качество: /quality"
    ),
    "pdf_filename":   "document_{date}.pdf",

    # ── OCR ──────────────────────────────────────────────────────────────────

    "ocr_starting":    "🔍 Распознавание текста...",
    "ocr_select_lang": "🌐 Выберите язык для OCR:",
    "ocr_creating":    "⏳ Создание поискового PDF...",
    "ocr_success": (
        "✅ <b>OCR выполнен!</b>\n\n"
        "🔤 Распознано символов: <b>{chars}</b>\n"
        "📄 PDF с поиском готов"
    ),
    "ocr_no_text":  "⚠️ Текст на изображении не найден. Создан обычный PDF.",
    "ocr_error":    "❌ Ошибка OCR: {error}",
    "ocr_lang_set": "✅ Язык OCR установлен: {lang}",

    # ── Редактирование изображений ────────────────────────────────────────────

    "edit_menu":       "✏️ <b>Меню редактирования</b>\nВыберите действие:",
    "edit_brightness": "☀️ Выберите уровень яркости:",
    "edit_contrast":   "🔲 Выберите уровень контраста:",
    "edit_applying":   "⏳ Применение изменений...",
    "edit_preview":    "👁️ Предварительный просмотр. Продолжить?",
    "edit_done":       "✅ Редактирование завершено!",
    "edit_reset":      "🔄 Изображение сброшено",
    "edit_no_image":   "❌ Нет изображения для редактирования.",

    "btn_brightness":  "☀️ Яркость",
    "btn_contrast":    "🌑 Контраст",
    "btn_grayscale":   "⬛ Чёрно-белый",
    "btn_rotate":      "🔄 Повернуть",
    "btn_sharpen":     "🔆 Резкость",
    "btn_a4_fit":      "📐 Под A4",
    "btn_reset_edit":  "↩️ Сбросить",
    "btn_done_edit":   "✅ Готово, в PDF",
    "btn_back":        "◀️ Назад",

    "btn_bright_m50":  "🌑 -50%",
    "btn_bright_m25":  "🌒 -25%",
    "btn_bright_norm": "⭕ Норма",
    "btn_bright_p25":  "🌔 +25%",
    "btn_bright_p50":  "☀️ +50%",

    "btn_contrast_low": "📉 Низкий",
    "btn_contrast_med": "➖ Средний",
    "btn_contrast_hi":  "➕ Высокий",
    "btn_contrast_vhi": "📈 Макс.",

    "btn_rotate_90":  "↻ 90°",
    "btn_rotate_180": "↻ 180°",
    "btn_rotate_270": "↻ 270°",

    # ── Настройки качества ────────────────────────────────────────────────────

    "quality_select":    "🎚️ <b>Выберите качество PDF:</b>",
    "quality_set":       "✅ Качество установлено: {quality}",
    "btn_quality_low":   "🔴 Низкое (~100-300 KB)",
    "btn_quality_med":   "🟡 Среднее (~500KB-1MB)",
    "btn_quality_hi":    "🟢 Высокое (~2-5MB)",
    "btn_quality_ultra": "💎 Ультра (~5-15MB)",

    # ── Настройки страницы ────────────────────────────────────────────────────

    "pagesize_select":    "📏 <b>Выберите размер страницы:</b>",
    "pagesize_set":       "✅ Размер страницы: {size}",

    "orientation_select": "🔄 <b>Выберите ориентацию страницы:</b>",
    "orientation_set":    "✅ Ориентация установлена: {orientation}",
    "btn_portrait":       "📱 Портрет",
    "btn_landscape":      "📺 Альбом",
    "btn_auto_orient":    "🤖 Автоматически",

    "margin_select":      "📐 <b>Выберите размер полей:</b>",
    "margin_set":         "✅ Поля установлены: {margin}",
    "btn_margin_none":    "⬛ Без полей",
    "btn_margin_small":   "◻️ Маленькие",
    "btn_margin_medium":  "🔲 Средние",
    "btn_margin_large":   "⬜ Большие",

    # ── Reverse: PDF → Изображения ────────────────────────────────────────────

    "reverse_prompt":     "📄 Отправьте PDF файл или используйте /reverse.",
    "reverse_select_fmt": (
        "🖼️ <b>PDF → Изображения</b>\n\n"
        "PDF: <b>{filename}</b>\n"
        "Страниц: <b>{pages}</b>\n\n"
        "Выберите формат изображения:"
    ),
    "reverse_page_range": (
        "📋 Введите диапазон страниц (например: <code>1-3, 5, 7-10</code>)\n"
        "Для всех страниц оставьте пустым или отправьте /all"
    ),
    "reverse_processing": "⏳ Разбивка PDF на страницы...",
    "reverse_page_done":  "✅ {pages} страниц готово!",
    "reverse_zip_done":   "✅ ZIP архив готов! {pages} изображений",
    "reverse_no_pdf":     "❌ PDF не найден. Сначала отправьте PDF.",
    "reverse_error":      "❌ Ошибка обработки PDF: {error}",
    "reverse_invalid_range": "❌ Неверный диапазон страниц. Пример: 1-3, 5, 7",
    "btn_reverse_jpg":    "🖼️ JPG",
    "btn_reverse_png":    "📷 PNG",
    "btn_reverse_zip":    "🗜️ ZIP архив",

    # ── История ───────────────────────────────────────────────────────────────

    "history_title":   "📋 <b>Ваша история PDF:</b>",
    "history_empty":   "📭 История пуста. PDF ещё не создавались.",
    "history_item": (
        "📄 <b>{name}</b>\n"
        "   📦 {size} | 📅 {date} | 📃 {pages} стр."
    ),
    "history_deleted":   "🗑️ PDF удалён из истории.",
    "history_not_found": "❌ PDF не найден или уже удалён.",
    "btn_download":      "⬇️ Скачать",
    "btn_delete":        "🗑️ Удалить",

    # ── Выбор языка ───────────────────────────────────────────────────────────

    "lang_select": "🌐 <b>Tilni tanlang / Выберите язык / Choose language:</b>",
    "lang_set":    "✅ Язык установлен: Русский 🇷🇺",

    # ── Ошибки и предупреждения ───────────────────────────────────────────────

    "error_invalid_format": (
        "❌ <b>Неверный формат!</b>\n\n"
        "Этот формат не поддерживается.\n"
        "Пожалуйста, отправьте файл в одном из форматов:\n"
        "📎 JPG, JPEG, PNG, WEBP, BMP, TIFF, HEIC"
    ),
    "error_file_too_large": (
        "❌ <b>Файл слишком большой!</b>\n\n"
        "Максимальный размер: <b>{max_size}</b>\n"
        "Ваш файл: <b>{file_size}</b>\n\n"
        "Пожалуйста, отправьте файл меньшего размера."
    ),
    "error_banned":      "🚫 Вы не можете использовать этого бота.",
    "error_rate_limit":  "⏳ <b>Слишком много запросов!</b>\n\nПодождите {seconds} секунд.",
    "error_general":     "❌ Произошла ошибка. Попробуйте снова: /start",
    "error_pdf_send":    "❌ Ошибка отправки PDF.",
    "error_download":    "❌ Ошибка загрузки файла.",
    "error_not_image":   "❌ Это не изображение. Отправьте изображение.",
    "error_not_pdf":     "❌ Это не PDF. Отправьте PDF файл.",
    "error_unsupported_file": (
        "❌ <b>Этот формат файла не поддерживается.</b>\n\n"
        "📌 Бот принимает только:\n"
        "• 🖼️ Изображения: JPG, PNG, WEBP, BMP, TIFF, HEIC\n"
        "• 📄 PDF файлы (для команды /reverse)\n\n"
        "Для создания PDF отправьте изображение."
    ),

    # ── Админ панель ──────────────────────────────────────────────────────────

    "admin_only": "🔐 Эта команда только для администраторов.",
    "admin_panel": (
        "🔧 <b>Панель администратора</b>\n\n"
        "📊 <b>Статистика:</b>\n"
        "  👥 Всего пользователей: <b>{total_users}</b>\n"
        "  🟢 Активных сегодня: <b>{active_today}</b>\n"
        "  📄 Всего PDF: <b>{total_pdfs}</b>\n"
        "  📅 Сегодня PDF: <b>{pdfs_today}</b>\n"
        "  🚫 Заблокированных: <b>{banned_users}</b>\n\n"
        "📈 <b>Топ функции:</b>\n"
        "{top_actions}\n\n"
        "🔧 <b>Команды управления:</b>\n"
        "/broadcast — Рассылка всем\n"
        "/ban [user_id] — Заблокировать\n"
        "/unban [user_id] — Разблокировать\n"
        "/stats [user_id] — Статистика юзера\n"
        "/cleanup — Очистить temp файлы\n"
        "/logs — Последние ошибки"
    ),
    "broadcast_usage":   "📢 Использование: /broadcast [текст сообщения]",
    "broadcast_started": "📤 Рассылка начата...",
    "broadcast_done": (
        "✅ <b>Рассылка завершена!</b>\n\n"
        "✅ Отправлено: {sent}\n"
        "❌ Ошибок: {failed}"
    ),
    "ban_usage":     "Использование: /ban [user_id]",
    "ban_done":      "🚫 Пользователь {user_id} заблокирован.",
    "ban_not_found": "❌ Пользователь не найден.",
    "unban_done":    "✅ Пользователь {user_id} разблокирован.",
    "stats_usage":   "Использование: /stats [user_id]",
    "stats_user": (
        "📊 <b>Статистика пользователя</b>\n\n"
        "👤 ID: <code>{user_id}</code>\n"
        "📛 Имя: {full_name}\n"
        "🔖 Username: @{username}\n"
        "🌐 Язык: {lang}\n"
        "📅 Зарегистрирован: {joined_at}\n"
        "🕐 Последняя активность: {last_active}\n"
        "🚫 Заблокирован: {is_banned}\n\n"
        "📄 Создано PDF: {total_pdfs}\n"
        "🔍 Использовано OCR: {ocr_count}\n"
        "🔄 Использовано Reverse: {reverse_count}\n"
        "📋 PDF в истории: {history_count}"
    ),
    "cleanup_done": "🧹 Удалено {count} временных файлов.",
    "logs_title":   "📋 <b>Последние {count} ошибок:</b>\n\n",
    "logs_empty":   "✅ Журнал ошибок пуст.",

    # ── Общие кнопки ──────────────────────────────────────────────────────────

    "btn_cancel_action": "❌ Отмена",
    "btn_confirm":       "✅ Подтвердить",
    "btn_close":         "🚫 Закрыть",
    "btn_refresh":       "🔄 Обновить",
    "btn_main_menu":     "🏠 Главное меню",

    "progress_uploading":  "📤 Загрузка...",
    "progress_processing": "⚙️ Обработка...",
    "progress_saving":     "💾 Сохранение...",
    "progress_sending":    "📨 Отправка...",

    "welcome_back": "👋 С возвращением! Отправьте изображение или /help.",

    # ── Кнопки главного меню (ReplyKeyboard) ─────────────────────────────────

    "menu_btn_collect":   "📁 Собрать несколько фото",
    "menu_btn_history":   "📋 История",
    "menu_btn_settings":  "⚙️ Настройки",
    "menu_btn_help":      "❓ Помощь",

    "default_pdf_name":  "converted_{timestamp}.pdf",
    "ocr_pdf_name":      "ocr_{timestamp}.pdf",
    "multi_pdf_name":    "merged_{timestamp}.pdf",
    "reverse_zip_name":  "pages_{timestamp}.zip",
}
