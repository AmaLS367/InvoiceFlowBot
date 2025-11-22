from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ForceReply
from typing import Dict, Any
from datetime import date

import re
import time
import uuid

from storage.db import init_db, _to_iso
from services.invoice_service import list_invoices, save_invoice as save_invoice_service
from domain.invoices import Invoice, InvoiceHeader, InvoiceItem, InvoiceComment
from decimal import Decimal
from ocr.engine.util import get_logger, set_request_id
from handlers.state import CURRENT_PARSE, PENDING_EDIT, PENDING_PERIOD
from handlers.utils import (
    format_money,
    format_invoice_header,
    format_invoice_items,
    format_invoice_full,
    fmt_header,  # For backwards compatibility with dict-based code
    fmt_items,  # For backwards compatibility with dict-based code
    main_kb, header_kb, items_index_kb, item_fields_kb
)

router = Router()
init_db()  # Initialize database on startup
logger = get_logger("ocr.engine")


def _parse_date_str(date_str: str) -> date | None:
    """
    Parse date string to date object.
    """
    if not date_str:
        return None
    try:
        return date.fromisoformat(date_str)
    except (ValueError, TypeError):
        # Try _to_iso first, then parse
        iso = _to_iso(date_str)
        if iso:
            try:
                return date.fromisoformat(iso)
            except (ValueError, TypeError):
                pass
    return None

# ---------- START / HELP ----------
@router.message(F.text == "/start")
async def cmd_start(message: Message):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_start")
    await message.answer(
        "Готов принять PDF/фото накладной и превратить в данные.\n"
        "Шаги: 1) пришлите файл, 2) проверьте/отредактируйте, "
        "3) сохраните в БД, 4) запрос по периоду.",
        reply_markup=main_kb()
    )
    logger.info(f"[TG] update done req={req} h=cmd_start")

@router.message(F.text == "/help")
async def cmd_help(message: Message):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_help")
    await message.answer(
        "Быстрые действия кнопками ниже.\n"
        "Команды для продвинутых: /show, /edit, /edititem, /comment, /save, /invoices.",
        reply_markup=main_kb()
    )
    logger.info(f"[TG] update done req={req} h=cmd_help")

# ---------- View draft ----------
@router.message(F.text == "/show")
async def cmd_show(message: Message):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_show")
    uid = message.from_user.id if message.from_user else 0
    if uid not in CURRENT_PARSE:
        await message.answer("Нет черновика. Пришлите документ.")
        return
    
    invoice = CURRENT_PARSE[uid].get("invoice")
    if invoice is None:
        # Fallback: try to get from parsed dict
        p = CURRENT_PARSE[uid].get("parsed")
        if p:
            head_text = fmt_header(p)
            items_text = fmt_items(p.get("items") or [])
            full = f"{head_text}\n\n" + "—"*30 + f"\n\n{items_text if items_text else 'Позиции не распознаны.'}"
            await message.answer(full if len(full) < 3900 else head_text)
        else:
            await message.answer("Нет черновика. Пришлите документ.")
    else:
        full_text = format_invoice_full(invoice)
        await message.answer(full_text if len(full_text) < 3900 else format_invoice_header(invoice))
    logger.info(f"[TG] update done req={req} h=cmd_show")

# ---------- Inline editing flow ----------
@router.callback_query(F.data == "act_edit")
async def cb_act_edit(call: CallbackQuery):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_act_edit")
    uid = call.from_user.id
    if uid not in CURRENT_PARSE:
        if call.message is not None:
            await call.message.answer("Нет черновика. Пришлите документ.")
            await call.answer()
        return
    
    invoice = CURRENT_PARSE[uid].get("invoice")
    if invoice is None:
        # Fallback: use parsed dict
        p = CURRENT_PARSE[uid].get("parsed")
        if p:
            head_text = fmt_header(p)
        else:
            head_text = "Нет черновика. Пришлите документ."
    else:
        head_text = format_invoice_header(invoice)
    
    if call.message is not None:
        await call.message.answer(head_text + "\nВыберите поле для редактирования:", reply_markup=header_kb())
        await call.answer()
    logger.info(f"[TG] update done req={req} h=cb_act_edit")

@router.callback_query(F.data.startswith("hed:"))
async def cb_hed_field(call: CallbackQuery):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_hed_field")
    uid = call.from_user.id
    if uid not in CURRENT_PARSE:
        await call.answer()
        return
    
    if call.data is not None:
        field = call.data.split(":",1)[1]
        nice = {"supplier":"Поставщик","client":"Клиент","date":"Дата","doc_number":"Номер","total_sum":"Итого"}[field]
    PENDING_EDIT[uid] = {"kind":"header","key":field}
    if call.message is not None:
        await call.message.answer(f"Введите новое значение для «{nice}»:", reply_markup=ForceReply(selective=True))
        await call.answer()
    logger.info(f"[TG] update done req={req} h=cb_hed_field")

@router.callback_query(F.data == "act_items")
async def cb_act_items(call: CallbackQuery):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_act_items")
    uid = call.from_user.id
    if uid not in CURRENT_PARSE:
        await call.answer()
        return
    
    invoice = CURRENT_PARSE[uid].get("invoice")
    if invoice:
        n = len(invoice.items)
    else:
        # Fallback: use parsed dict
        p = CURRENT_PARSE[uid].get("parsed")
        n = len(p.get("items") or []) if p else 0
    
    if n == 0:
        if call.message is not None:
            await call.message.answer("Позиции не распознаны.")
            await call.answer()
        return
    
    if call.message is not None:
        await call.message.answer(f"Выберите позицию для редактирования (всего: {n}):", reply_markup=items_index_kb(n, 1))
        await call.answer()
    logger.info(f"[TG] update done req={req} h=cb_act_items")        

@router.callback_query(F.data.startswith("items_page:"))
async def cb_items_page(call: CallbackQuery):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_items_page")
    uid = call.from_user.id
    if uid not in CURRENT_PARSE:
        await call.answer()
        return
        
    if call.data is not None:
        page = int(call.data.split(":")[1])
        invoice = CURRENT_PARSE[uid].get("invoice")
        if invoice:
            n = len(invoice.items)
        else:
            # Fallback: use parsed dict
            p = CURRENT_PARSE[uid].get("parsed")
            n = len(p.get("items") or []) if p else 0
        
        if call.message is not None:
            if isinstance(call.message, Message):
                await call.message.edit_reply_markup(reply_markup=items_index_kb(n, page))
                await call.answer()
    logger.info(f"[TG] update done req={req} h=cb_items_page")

@router.callback_query(F.data.startswith("item_pick:"))
async def cb_item_pick(call: CallbackQuery):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_item_pick")
    uid = call.from_user.id
    if uid not in CURRENT_PARSE:
        await call.answer()
        return
    
    if call.data is not None:
        idx = int(call.data.split(":")[1])
    
    invoice = CURRENT_PARSE[uid].get("invoice")
    if invoice:
        items = invoice.items
        if not (1 <= idx <= len(items)):
            await call.answer()
            return
        item = items[idx-1]
        text = (
            f"#{idx}\n"
            f"Название: {item.description or ''}\n"
            f"Код: {item.sku or ''}\n"
            f"Кол-во: {format_money(item.quantity)} | Цена: {format_money(item.unit_price)} | Сумма: {format_money(item.line_total)}"
        )
    else:
        # Fallback: use parsed dict
        p = CURRENT_PARSE[uid].get("parsed")
        items = p.get("items") or [] if p else []
        if not (1 <= idx <= len(items)):
            await call.answer()
            return
        it = items[idx-1]
        text = (
            f"#{idx}\n"
            f"Название: {it.get('name','')}\n"
            f"Код: {it.get('code','')}\n"
            f"Кол-во: {format_money(it.get('qty',0))} | Цена: {format_money(it.get('price',0))} | Сумма: {format_money(it.get('total',0))}"
        )
    
    if call.message is not None:
        await call.message.answer(text, reply_markup=item_fields_kb(idx))
        await call.answer()
    logger.info(f"[TG] update done req={req} h=cb_item_pick")

@router.callback_query(F.data.startswith("itm_field:"))
async def cb_itm_field(call: CallbackQuery):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_itm_field")
    uid = call.from_user.id
    if call.data is None:
        await call.answer()
        return
    parts = call.data.split(":")
    idx = int(parts[1])
    key = parts[2]  # name/qty/price/total
    nice = {"name":"Название","qty":"Кол-во","price":"Цена","total":"Сумма"}[key]
    PENDING_EDIT[uid] = {"kind":"item","idx":idx,"key":key}
    if call.message is not None:
        await call.message.answer(f"Введите новое значение для «{nice}» у позиции #{idx}:", reply_markup=ForceReply(selective=True))
        await call.answer()
    logger.info(f"[TG] update done req={req} h=cb_itm_field")

# ---------- Handle ForceReply input ----------
@router.message(F.reply_to_message)
async def on_force_reply(message: Message):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=on_force_reply")
    uid = message.from_user.id if message.from_user else 0
    
    # Comment from inline button
    if uid in PENDING_EDIT and PENDING_EDIT.get(uid, {}).get("kind") == "comment":
        if uid not in CURRENT_PARSE:
            await message.answer("Нет черновика. Загрузите документ.")
            PENDING_EDIT.pop(uid, None)
            return
        text = (message.text or "").strip()
        if not text:
            await message.answer("Пустой комментарий игнорирован.")
        else:
            CURRENT_PARSE[uid].setdefault("comments", []).append(text)
            await message.answer("Комментарий добавлен.")
        PENDING_EDIT.pop(uid, None)
        logger.info(f"[TG] update done req={req} h=on_force_reply_comment")
        return
    
    # Period: step-by-step input
    if uid in PENDING_PERIOD:
        st = PENDING_PERIOD[uid]
        if message.text is not None:
            val = message.text.strip()

        if st["step"] == "from":
            iso = _to_iso(val) or val  # Accept as-is if parsing fails, DB will handle it
            st["from"] = iso
            st["step"] = "to"
            await message.answer("По дату (YYYY-MM-DD):", reply_markup=ForceReply(selective=True))
            return

        if st["step"] == "to":
            iso = _to_iso(val) or val
            st["to"] = iso
            st["step"] = "supplier"
            await message.answer("Фильтр по поставщику (опционально). Введите текст или «-» чтобы пропустить:",
                                 reply_markup=ForceReply(selective=True))
            return

        if st["step"] == "supplier":
            supplier = None if val in ("", "-") else val
            f_str, t_str = st.get("from"), st.get("to")
            del PENDING_PERIOD[uid]

            if not f_str or not t_str:
                await message.answer("Не указаны даты. Повторите ввод периода.")
                return
            
            # Convert string dates to date objects
            from_date = _parse_date_str(f_str)
            to_date = _parse_date_str(t_str)
            
            invoices = list_invoices(from_date=from_date, to_date=to_date, supplier=supplier)
            if not invoices:
                await message.answer("Ничего не найдено.")
                return

            lines = []
            total = 0.0
            for invoice in invoices:
                # Get invoice ID from storage (we need to query it separately for now)
                # For now, we'll use a placeholder or skip ID display
                invoice_date_str = invoice.header.invoice_date.isoformat() if invoice.header.invoice_date else "—"
                invoice_total = float(invoice.header.total_amount) if invoice.header.total_amount is not None else 0.0
                total += invoice_total
                items_count_val = len(invoice.items)
                lines.append(
                    f"  {invoice_date_str}  {invoice.header.invoice_number or '—'}  "
                    f"{invoice.header.supplier_name or '—'}  = {format_money(invoice_total)}  "
                    f"(items: {items_count_val})"
                )
            head = f"Счета с {f_str} по {t_str}" + (f" | Поставщик содержит: {supplier}" if supplier else "")
            text = head + "\n" + "\n".join(lines[:150]) + f"\n—\nИтого суммарно: {format_money(total)}"
            await message.answer(text if len(text) < 3900 else (head + "\nСлишком много строк. Уточните фильтр."))
            return

    if uid not in PENDING_EDIT or uid not in CURRENT_PARSE:
        return
    cfg = PENDING_EDIT.pop(uid)
    
    invoice = CURRENT_PARSE[uid].get("invoice")
    if invoice is None:
        # Fallback: work with parsed dict
        parsed = CURRENT_PARSE[uid].get("parsed")
        if not parsed:
            await message.answer("Нет черновика. Загрузите документ.")
            return
        
        if message.text is not None:
            val = message.text.strip()

        if cfg["kind"] == "header":
            k = cfg["key"]
            if k == "total_sum":
                try:
                    parsed[k] = float(val.replace(",", "."))
                    ok = True
                except:
                    parsed[k] = val
                    ok = False
                await message.answer('Итого обновлено. Нажмите кнопку "Сохранить" или введите команду /save чтобы сохранить в БД.' if ok else "Итого обновлено как текст (не число).")
            else:
                parsed[k] = val
                await message.answer('Поле обновлено. Нажмите кнопку "Сохранить" или введите команду /save чтобы сохранить в БД.')
        else:
            idx = cfg["idx"]
            items = parsed.get("items") or []
            if not (1 <= idx <= len(items)):
                await message.answer("Индекс вне диапазона.")
                return
            key = cfg["key"]
            if key == "name" or key == "code":
                items[idx-1][key] = val
                await message.answer('Обновлено. Нажмите кнопку "Сохранить" или введите команду /save чтобы сохранить в БД.')
            else:
                try:
                    items[idx-1][key] = float(val.replace(",", "."))
                    await message.answer('Обновлено. Нажмите кнопку "Сохранить" или введите команду /save чтобы сохранить в БД.')
                except:
                    await message.answer("Не число. Повторите.")
    else:
        # Work with Invoice domain model
        if message.text is not None:
            val = message.text.strip()

        if cfg["kind"] == "header":
            k = cfg["key"]
            header = invoice.header
            if k == "supplier":
                header.supplier_name = val
            elif k == "client":
                header.customer_name = val
            elif k == "date":
                # Try to parse date
                parsed_date = _parse_date_str(val)
                header.invoice_date = parsed_date
            elif k == "doc_number":
                header.invoice_number = val
            elif k == "total_sum":
                try:
                    header.total_amount = Decimal(str(val.replace(",", ".")))
                    ok = True
                except:
                    ok = False
                await message.answer('Итого обновлено. Нажмите кнопку "Сохранить" или введите команду /save чтобы сохранить в БД.' if ok else "Итого обновлено как текст (не число).")
                return
            await message.answer('Поле обновлено. Нажмите кнопку "Сохранить" или введите команду /save чтобы сохранить в БД.')
        else:
            idx = cfg["idx"]
            items = invoice.items
            if not (1 <= idx <= len(items)):
                await message.answer("Индекс вне диапазона.")
                return
            key = cfg["key"]
            item = items[idx-1]
            if key == "name":
                item.description = val
            elif key == "code":
                item.sku = val
            elif key == "qty":
                try:
                    item.quantity = Decimal(str(val.replace(",", ".")))
                except:
                    await message.answer("Не число. Повторите.")
                    return
            elif key == "price":
                try:
                    item.unit_price = Decimal(str(val.replace(",", ".")))
                except:
                    await message.answer("Не число. Повторите.")
                    return
            elif key == "total":
                try:
                    item.line_total = Decimal(str(val.replace(",", ".")))
                except:
                    await message.answer("Не число. Повторите.")
                    return
            await message.answer('Обновлено. Нажмите кнопку "Сохранить" или введите команду /save чтобы сохранить в БД.')
    logger.info(f"[TG] update done req={req} h=on_force_reply")

# ---------- Comments / Save / Query ----------
@router.message(F.text.regexp(r"^/comment(\s|$)"))
async def cmd_comment(message: Message):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_comment")
    uid = message.from_user.id if message.from_user else 0
    if uid not in CURRENT_PARSE:
        await message.answer("Нет черновика. Загрузите документ.")
        return
    if message.text is not None and " " in message.text:
        text = message.text.split(" ", 1)[1].strip() if " " in message.text else ""
        if not text:
            await message.answer("Формат: /comment ваш текст")
            return
    CURRENT_PARSE[uid].setdefault("comments", []).append(text)
    await message.answer("Комментарий добавлен. /save чтобы сохранить в БД.")
    logger.info(f"[TG] update done req={req} h=cmd_comment")

@router.message(F.text == "/save")
async def cmd_save(message: Message):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_save")
    uid = message.from_user.id if message.from_user else 0
    if uid not in CURRENT_PARSE:
        await message.answer("Нет черновика.")
        return
    draft = CURRENT_PARSE.pop(uid)
    invoice = draft.get("invoice")
    
    # If invoice is not in state, reconstruct from parsed dict
    if invoice is None:
        parsed = draft["parsed"]
        header = InvoiceHeader(
            supplier_name=parsed.get("supplier"),
            customer_name=parsed.get("client"),
            invoice_number=parsed.get("doc_number"),
            invoice_date=_parse_date_str(parsed.get("date")) if parsed.get("date") else None,
            total_amount=Decimal(str(parsed.get("total_sum", 0))) if parsed.get("total_sum") else None,
        )
        items = []
        for it in parsed.get("items", []):
            items.append(InvoiceItem(
                description=it.get("name", ""),
                sku=it.get("code"),
                quantity=Decimal(str(it.get("qty", 0))),
                unit_price=Decimal(str(it.get("price", 0))),
                line_total=Decimal(str(it.get("total", 0))),
            ))
        invoice = Invoice(header=header, items=items)
    
    comments = draft.get("comments", [])
    
    # Auto-comment for sum mismatch
    header_sum = float(invoice.header.total_amount) if invoice.header.total_amount is not None else 0.0
    sum_items = sum(float(item.line_total) for item in invoice.items)
    diff = round(sum_items - header_sum, 2)
    
    if abs(diff) >= 0.01:
        doc_number = invoice.header.invoice_number or "—"
        supplier = invoice.header.supplier_name or "—"
        auto_text = (
            f"[auto] Несходство суммы: по позициям {sum_items:.2f}, "
            f"в шапке {header_sum:.2f}, разница {diff:+.2f}. "
            f"Документ: {doc_number}, Поставщик: {supplier}."
        )
        # Check if comment already exists
        existing_messages = [c.message for c in invoice.comments]
        if auto_text not in existing_messages:
            invoice.comments.append(InvoiceComment(message=auto_text))
    
    # Add text comments
    for comment_text in comments:
        if isinstance(comment_text, str):
            invoice.comments.append(InvoiceComment(message=comment_text))
    
    inv_id = save_invoice_service(invoice, user_id=uid)
    await message.answer(f"Сохранено в БД. ID счета: {inv_id}")
    logger.info(f"[TG] update done req={req} h=cmd_save")

@router.message(F.text.regexp(r"^/invoices\s"))
async def cmd_invoices(message: Message):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_invoices")
    if message.text is None:
        await message.answer("Формат: /invoices YYYY-MM-DD YYYY-MM-DD [supplier=текст]")
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("Формат: /invoices YYYY-MM-DD YYYY-MM-DD [supplier=текст]")
        return
    f_str, t_str = parts[1], parts[2]
    supplier = None
    if len(parts) >= 4 and parts[3].lower().startswith("supplier="):
        supplier = parts[3].split("=",1)[1]
    
    # Convert string dates to date objects
    from_date = _parse_date_str(f_str)
    to_date = _parse_date_str(t_str)
    
    invoices = list_invoices(from_date=from_date, to_date=to_date, supplier=supplier)
    if not invoices:
        await message.answer("Ничего не найдено.")
        return
    
    lines = []
    total = 0.0
    for invoice in invoices:
        invoice_date_str = invoice.header.invoice_date.isoformat() if invoice.header.invoice_date else "—"
        invoice_total = float(invoice.header.total_amount) if invoice.header.total_amount is not None else 0.0
        total += invoice_total
        items_count_val = len(invoice.items)
        lines.append(
            f"  {invoice_date_str}  {invoice.header.invoice_number or '—'}  "
            f"{invoice.header.supplier_name or '—'}  = {format_money(invoice_total)}  "
            f"(items: {items_count_val})"
        )
    head = f"Счета с {f_str} по {t_str}" + (f" | Поставщик содержит: {supplier}" if supplier else "")
    text = head + "\n" + "\n".join(lines[:150]) + f"\n—\nИтого суммарно: {format_money(total)}"
    await message.answer(text if len(text) < 3900 else (head + "\nСлишком много строк. Уточните фильтр."))
    logger.info(f"[TG] update done req={req} h=cmd_invoices")

# ---------- Legacy text commands (kept for convenience) ----------
def _apply_field(parsed: Dict[str, Any], k: str, v: str):
    keymap = {
        "supplier":"supplier","поставщик":"supplier",
        "client":"client","клиент":"client",
        "date":"date","дата":"date",
        "doc":"doc_number","number":"doc_number","номер":"doc_number","doc_number":"doc_number",
        "total":"total_sum","итого":"total_sum","sum":"total_sum",
    }
    k = k.strip().lower()
    if k in keymap:
        dst = keymap[k]
        if dst == "total_sum":
            try: parsed[dst] = float(v.replace(",", "."))
            except: parsed[dst] = v
        else:
            parsed[dst] = v.strip()

@router.message(F.text.regexp(r"^/edit(\s|$)"))
async def cmd_edit_legacy(message: Message):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_edit_legacy")

    uid = message.from_user.id if message.from_user else 0
    if uid not in CURRENT_PARSE:
        await message.answer("Нет черновика. Загрузите документ.")
        return
    if message.text is None:
        await message.answer("Формат: /edit supplier=... client=... date=YYYY-MM-DD doc=... total=123.45")
        return
    args = message.text.split(" ", 1)
    if len(args) < 2:
        await message.answer("Формат: /edit supplier=... client=... date=YYYY-MM-DD doc=... total=123.45"); return
    parsed = CURRENT_PARSE[uid]["parsed"]
    for part in re.split(r"[;,]\s*|\s{2,}", args[1].strip()):
        if "=" in part:
            k, v = part.split("=", 1)
            _apply_field(parsed, k, v)
    await message.answer("Ок. Поля обновлены. /show для проверки или /save для сохранения.")
    logger.info(f"[TG] update done req={req} h=cmd_edit_legacy")

@router.message(F.text.regexp(r"^/edititem(\s|$)"))
async def cmd_edititem_legacy(message: Message):
     req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
     set_request_id(req)
     logger.info(f"[TG] update start req={req} h=cmd_edititem_legacy")

     uid = message.from_user.id if message.from_user else 0

     if uid not in CURRENT_PARSE:
        await message.answer("Нет черновика. Загрузите документ.")
        return
     
     if message.text is None:
        await message.answer("Формат: /edititem <index> name=... qty=... price=... total=...")
        return
     args = message.text.split(" ", 2)

     if len(args) < 3:
        await message.answer("Формат: /edititem <index> name=... qty=... price=... total=..."); return
     
     try: 
         idx = int(args[1])
     except: 
        await message.answer("Неверный индекс."); return
     
     parsed = CURRENT_PARSE[uid]["parsed"]; items = parsed.get("items") or []
     if idx < 1 or idx > len(items):
        await message.answer("Индекс вне диапазона."); return
     
     updates = args[2]
     for part in re.split(r"[;,]\s*|\s{2,}", updates.strip()):
        if "=" in part:
            k, v = part.split("=", 1); k = k.strip().lower()
            if k == "name": items[idx-1]["name"] = v.strip()
            elif k == "code": items[idx-1]["code"] = v.strip()
            elif k == "qty":
                try: items[idx-1]["qty"] = float(v.replace(",", ".")); 
                except: pass
            elif k == "price":
                try: items[idx-1]["price"] = float(v.replace(",", ".")); 
                except: pass
            elif k == "total":
                try: items[idx-1]["total"] = float(v.replace(",", ".")); 
                except: pass
     await message.answer("Позиция обновлена. /show для проверки, /save для сохранения.")
     logger.info(f"[TG] update done req={req} h=cmd_edititem_legacy")

@router.callback_query(F.data == "act_period")
async def cb_act_period(call: CallbackQuery):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cb_act_period")

    uid = call.from_user.id
    PENDING_PERIOD[uid] = {"step": "from"}
    if call.message is not None:
        await call.message.answer("С даты (YYYY-MM-DD):", reply_markup=ForceReply(selective=True))
        await call.answer()
    logger.info(f"[TG] update done req={req} h=cb_act_period")

