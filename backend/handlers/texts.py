"""
Centralized user-facing strings for bot handlers, menus, and UI helpers.
"""

from __future__ import annotations

PLACEHOLDER = "—"
SECTION_DIVIDER = "—" * 34

# Telegram command menu descriptions
CMD_DESC_START = "Запустить бота"
CMD_DESC_HELP = "Помощь"
CMD_DESC_SHOW = "Показать текущий черновик"
CMD_DESC_SAVE = "Сохранить черновик в БД"
CMD_DESC_INVOICES = "Список сохранённых счетов"

# Common commands
START_TEXT = "Привет! Это бот для обработки инвойсов. Загрузите счет и бот распознает его."
HELP_TEXT = (
    "Быстрые действия кнопками ниже.\n"
    "Команды для продвинутых: /show, /edit, /edititem, /comment, /save, /invoices."
)

# File upload and OCR
UPLOAD_PROMPT = "Пришлите файл: PDF или фото накладной. Бот распознаёт и покажет черновик."
OCR_IN_PROGRESS = "📥 Получил файл. Распознаю…"
OCR_EMPTY_RESULT = "Распознавание завершилось без данных. Попробуйте другой файл или фото."
OCR_UNAVAILABLE = "Сервис распознавания сейчас недоступен. Попробуйте чуть позже."
FILE_PROCESSING_FAILED_WITH_FORMATS = (
    "Не удалось обработать файл. Попробуйте другой формат (PDF, JPG, PNG)."
)
FILE_PROCESSING_FAILED = "Не удалось обработать файл. Попробуйте другой формат."
FILE_FETCH_FAILED = "Не удалось получить файл."
PHOTO_FETCH_FAILED = "Не удалось получить фото."
FILE_SAVE_FAILED = "Ошибка при сохранении файла"
BOT_UNAVAILABLE = "Ошибка: бот недоступен"
DRAFT_SAVE_FAILED = "Не удалось сохранить черновик. Повторите попытку позже."
TABLE_TOO_LONG_SEND_CSV = "Таблица длинная, отправляю CSV."
OCR_REVIEW_TITLE = "⚠️ Проверьте распознавание:"
OCR_REVIEW_ITEM_REASONS = {
    "total_mismatch": "сумма не сходится с количеством × ценой с учётом скидки",
    "total_computed": "сумма не прочитана, рассчитана из количества и цены",
    "qty_computed": "количество не прочитано, рассчитано из суммы и цены",
    "price_computed": "цена не прочитана, рассчитана из суммы и количества",
    "qty_corrected": "в количестве восстановлен десятичный разделитель",
    "total_corrected": "в сумме восстановлен десятичный разделитель",
}
OCR_REVIEW_UNKNOWN_REASON = "значения требуют проверки"
OCR_REVIEW_ROWS_SKIPPED = "Не удалось разобрать {count} строк таблицы — их нет в черновике."
OCR_REVIEW_MORE_ITEMS = "…и ещё позиций: {count}"

# Drafts, editing, comments, saving
NO_DRAFT_UPLOAD_DOCUMENT = "Нет черновика. Загрузите документ."
NO_DRAFT_SEND_DOCUMENT = "Нет черновика. Пришлите документ."
NO_DRAFT_SHORT = "Нет черновика."

COMMENT_EMPTY_IGNORED = "Пустой комментарий игнорирован."
COMMENT_ADDED_SAVE_HINT = "Комментарий добавлен. /save чтобы сохранить в БД."
COMMENT_PROMPT = "Комментарий к счёту:"
COMMENT_USAGE = "Формат: /comment ваш текст"

EDIT_SELECT_HEADER_FIELD = "Выберите поле для редактирования:"
ITEMS_NOT_RECOGNIZED = "Позиции не распознаны."
FIELD_UPDATED = (
    'Поле обновлено. Нажмите кнопку "Сохранить" или введите команду /save чтобы сохранить в БД.'
)
TOTAL_UPDATED = (
    'Итого обновлено. Нажмите кнопку "Сохранить" или введите команду /save чтобы сохранить в БД.'
)
TOTAL_UPDATED_AS_TEXT = "Итого обновлено как текст (не число)."
ITEM_UPDATED = (
    'Обновлено. Нажмите кнопку "Сохранить" или введите команду /save чтобы сохранить в БД.'
)
HEADER_UPDATED = "Ок. Поля обновлены. /show для проверки или /save для сохранения."
LINE_UPDATED = "Позиция обновлена. /show для проверки, /save для сохранения."

INDEX_MISSING = "Индекс не указан."
INDEX_INVALID = "Неверный индекс."
INDEX_OUT_OF_RANGE = "Индекс вне диапазона."
NOT_A_NUMBER_RETRY = "Не число. Повторите."

SAVE_SUCCESS_PREFIX = "Сохранено в БД. ID счета:"

EDIT_USAGE = "Формат: /edit supplier=... client=... date=YYYY-MM-DD doc=... total=123.45"
EDITITEM_USAGE = "Формат: /edititem <index> name=... qty=... price=... total=..."

# Invoice listing and period filter
INVOICES_USAGE = "Формат: /invoices YYYY-MM-DD YYYY-MM-DD [supplier=текст]"
INVOICES_NONE_FOUND = "Ничего не найдено."
INVOICES_TOTAL_LABEL = "Итого суммарно"
INVOICES_TOO_MANY_LINES = "Слишком много строк. Уточните фильтр."
PERIOD_FROM_PROMPT = "С даты (YYYY-MM-DD):"
PERIOD_TO_PROMPT = "По дату (YYYY-MM-DD):"
PERIOD_SUPPLIER_PROMPT = (
    "Фильтр по поставщику (опционально). Введите текст или «-» чтобы пропустить:"
)
PERIOD_DATES_MISSING = "Не указаны даты. Повторите ввод периода."

# Formatting labels
HEADER_DOCUMENT = "📑 Документ"
HEADER_DATE = "📅 Дата"
HEADER_SUPPLIER = "🏭 Поставщик"
HEADER_CLIENT = "👤 Клиент"
HEADER_TOTAL = "💰 Итого"

ITEM_NAME = "Название"
ITEM_CODE = "Код"
ITEM_QTY = "Кол-во"
ITEM_PRICE = "Цена"
ITEM_TOTAL = "Сумма"

SUMMARY_SUBTOTAL = "Подытог"
SUMMARY_TAX = "НДС"
SUMMARY_TOTAL = "Итого"
SUMMARY_CURRENCY = "Валюта"

COMMENTS_SECTION_TITLE = "💬 Комментарии:"

HEADER_FIELD_LABELS = {
    "supplier": "Поставщик",
    "client": "Клиент",
    "date": "Дата",
    "doc_number": "Номер",
    "total_sum": "Итого",
}

ITEM_FIELD_LABELS = {
    "name": "Название",
    "qty": "Кол-во",
    "price": "Цена",
    "total": "Сумма",
}

# Inline keyboard buttons
BUTTON_UPLOAD = "📄 Загрузить счёт"
BUTTON_EDIT = "✏️ Редактировать"
BUTTON_COMMENT = "💬 Комментарий"
BUTTON_SAVE = "💾 Сохранить"
BUTTON_PERIOD = "📊 Счета за период"
BUTTON_HELP = "ℹ️ Помощь"

BUTTON_SUPPLIER = "🏭 Поставщик"
BUTTON_CLIENT = "👤 Клиент"
BUTTON_DATE = "📅 Дата"
BUTTON_NUMBER = "📑 Номер"
BUTTON_TOTAL = "💰 Итого"
BUTTON_ITEMS = "📦 Позиции"

BUTTON_PREV_PAGE = "◀️"
BUTTON_NEXT_PAGE = "▶️"
BUTTON_BACK_TO_HEADER = "⬅️ К шапке"

BUTTON_ITEM_NAME = "✏️ Название"
BUTTON_ITEM_QTY = "🔢 Кол-во"
BUTTON_ITEM_PRICE = "💵 Цена"
BUTTON_ITEM_TOTAL = "🧮 Сумма"
BUTTON_BACK_TO_LIST = "⬅️ К списку"


def save_success(invoice_id: int) -> str:
    return f"{SAVE_SUCCESS_PREFIX} {invoice_id}"


def auto_sum_mismatch_comment(
    sum_items: float,
    header_sum: float,
    diff: float,
    doc_number: str,
    supplier: str,
) -> str:
    return (
        f"[auto] Несходство суммы: по позициям {sum_items:.2f}, "
        f"в шапке {header_sum:.2f}, разница {diff:+.2f}. "
        f"Документ: {doc_number}, Поставщик: {supplier}."
    )


def edit_enter_header_value(field_label: str) -> str:
    return f"Введите новое значение для «{field_label}»:"


def edit_enter_item_value(field_label: str, idx: int) -> str:
    return f"Введите новое значение для «{field_label}» у позиции #{idx}:"


def edit_select_item(total_count: int) -> str:
    return f"Выберите позицию для редактирования (всего: {total_count}):"


def format_item_edit_card(
    idx: int,
    name: str,
    code: str,
    qty: str,
    price: str,
    total: str,
) -> str:
    return (
        f"#{idx}\n"
        f"{ITEM_NAME}: {name}\n"
        f"{ITEM_CODE}: {code}\n"
        f"{ITEM_QTY}: {qty} | {ITEM_PRICE}: {price} | {ITEM_TOTAL}: {total}"
    )


def invoices_period_header(from_text: str, to_text: str, supplier: str | None) -> str:
    return f"Счета с {from_text} по {to_text}" + (
        f" | Поставщик содержит: {supplier}" if supplier else ""
    )


def invoices_items_count(count: int) -> str:
    return f"(items: {count})"
