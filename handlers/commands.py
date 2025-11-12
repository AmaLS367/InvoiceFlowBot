from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ForceReply
from typing import Dict, Any

import re
import time
import uuid

from storage.db import init_db, save_invoice, query_invoices, items_count, _to_iso
from ocr.engine.util import get_logger, set_request_id
from handlers.state import CURRENT_PARSE, PENDING_EDIT, PENDING_PERIOD
from handlers.utils import (
    format_money, fmt_header, fmt_items,
    main_kb, header_kb, items_index_kb, item_fields_kb
)

router = Router()
init_db()  # Initialize database on startup
logger = get_logger("ocr.engine")

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
    p = CURRENT_PARSE[uid]["parsed"]
    head_text = fmt_header(p)
    items_text = fmt_items(p.get("items") or [])
    full = f"{head_text}\n\n" + "—"*30 + f"\n\n{items_text if items_text else 'Позиции не распознаны.'}"
    await message.answer(full if len(full) < 3900 else head_text)
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
            await call.answer(); return
    head_text = fmt_header(CURRENT_PARSE[uid]["parsed"])
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
        await call.answer(); return
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
        await call.answer(); return
    n = len(CURRENT_PARSE[uid]["parsed"].get("items") or [])
    if n == 0:
        if call.message is not None:
            await call.message.answer("Позиции не распознаны.")
            await call.answer(); return
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
        await call.answer(); return
        
    if call.data is not None:
        page = int(call.data.split(":")[1])
        n = len(CURRENT_PARSE[uid]["parsed"].get("items") or [])
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
        await call.answer(); return
    if call.data is not None:
        idx = int(call.data.split(":")[1])
    items = CURRENT_PARSE[uid]["parsed"].get("items") or []
    if not (1 <= idx <= len(items)):
        await call.answer(); return
    it = items[idx-1]
    text = (f"#{idx}\n"
            f"Название: {it.get('name','')}\n"
            f"Код: {it.get('code','')}\n"
            f"Кол-во: {format_money(it.get('qty',0))} | Цена: {format_money(it.get('price',0))} | Сумма: {format_money(it.get('total',0))}")
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
    if call.data is not None:
        parts = call.data.split(":")
    idx = int(parts[1]); key = parts[2]  # name/qty/price/total
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
            f, t = st.get("from"), st.get("to")
            del PENDING_PERIOD[uid]

            if not f or not t:
                await message.answer("Не указаны даты. Повторите ввод периода.")
                return
            rows = query_invoices(uid, f, t, supplier)
            if not rows:
                await message.answer("Ничего не найдено.")
                return

            lines = []
            total = 0.0
            for r in rows:
                date = r["date_iso"] or r["date"] or "—"
                total += float(r["total_sum"] or 0)
                lines.append(f"#{r['id']}  {date}  {r['doc_number'] or '—'}  {r['supplier'] or '—'}  = {format_money(r['total_sum'] or 0)}  (items: {items_count(r['id'])})")
            head = f"Счета с {f} по {t}" + (f" | Поставщик содержит: {supplier}" if supplier else "")
            text = head + "\n" + "\n".join(lines[:150]) + f"\n—\nИтого суммарно: {format_money(total)}"
            await message.answer(text if len(text) < 3900 else (head + "\nСлишком много строк. Уточните фильтр."))
            return

    if uid not in PENDING_EDIT or uid not in CURRENT_PARSE:
        return
    cfg = PENDING_EDIT.pop(uid)
    parsed = CURRENT_PARSE[uid]["parsed"]
    if message.text is not None:
        val = message.text.strip()

    if cfg["kind"] == "header":
        k = cfg["key"]
        if k == "total_sum":
            try: parsed[k] = float(val.replace(",", ".")); ok = True
            except: parsed[k] = val; ok = False
            await message.answer('Итого обновлено. Нажмите кнопку "Сохранить" или введите команду /save чтобы сохранить в БД.' if ok else "Итого обновлено как текст (не число).")
        else:
            parsed[k] = val
            await message.answer('Поле обновлено. Нажмите кнопку "Сохранить" или введите команду /save чтобы сохранить в БД.')
    else:
        idx = cfg["idx"]
        items = parsed.get("items") or []
        if not (1 <= idx <= len(items)):
            await message.answer("Индекс вне диапазона."); return
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
    parsed = draft["parsed"]
    source_path = draft.get("path","")
    raw_text = draft.get("raw_text","")
    comments = draft.get("comments", [])
    # Auto-comment for sum mismatch
    try:
        header_sum_raw = parsed.get("total_sum") or 0
        header_sum = float(header_sum_raw.replace(",", ".")) if isinstance(header_sum_raw, str) else float(header_sum_raw)
    except Exception:
        header_sum = 0.0

    # Calculate sum from items
    items = parsed.get("items") or []
    sum_items = 0.0
    for it in items:
        t = it.get("total")
        if t in (None, ""):
            q = it.get("qty") or 0
            p = it.get("price") or 0
            try:
                t_val = float(q) * float(p)
            except Exception:
                # Support strings with commas
                try:
                    t_val = float(str(q).replace(",", ".")) * float(str(p).replace(",", "."))
                except Exception:
                    t_val = 0.0
        else:
            try:
                t_val = float(t)
            except Exception:
                try:
                    t_val = float(str(t).replace(",", "."))
                except Exception:
                    t_val = 0.0
        sum_items += t_val

    diff = round(sum_items - header_sum, 2)
    if abs(diff) >= 0.01:
        doc_number = parsed.get("doc_number") or "—"
        supplier = parsed.get("supplier") or "—"
        auto_text = (
            f"[auto] Несходство суммы: по позициям {sum_items:.2f}, "
            f"в шапке {header_sum:.2f}, разница {diff:+.2f}. "
            f"Документ: {doc_number}, Поставщик: {supplier}."
        )
        if not isinstance(comments, list):
            comments = []
        if auto_text not in comments:
            comments.append(auto_text)
    inv_id = save_invoice(uid, parsed, source_path, raw_text, comments)
    await message.answer(f"Сохранено в БД. ID счета: {inv_id}")
    logger.info(f"[TG] update done req={req} h=cmd_save")

@router.message(F.text.regexp(r"^/invoices\s"))
async def cmd_invoices(message: Message):
    req = f"tg-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    set_request_id(req)
    logger.info(f"[TG] update start req={req} h=cmd_invoices")
    if message.text is not None:
        parts = message.text.split()
    if len(parts) < 3:
        await message.answer("Формат: /invoices YYYY-MM-DD YYYY-MM-DD [supplier=текст]")
        return
    f, t = parts[1], parts[2]
    supplier = None
    if len(parts) >= 4 and parts[3].lower().startswith("supplier="):
        supplier = parts[3].split("=",1)[1]
    rows = query_invoices(message.from_user.id if message.from_user else 0, f, t, supplier)
    if not rows:
        await message.answer("Ничего не найдено."); return
    lines = []; total = 0.0
    for r in rows:
        date = r["date_iso"] or r["date"] or "—"
        total += float(r["total_sum"] or 0)
        lines.append(f"#{r['id']}  {date}  {r['doc_number'] or '—'}  {r['supplier'] or '—'}  = {format_money(r['total_sum'] or 0)}  (items: {items_count(r['id'])})")
    head = f"Счета с {f} по {t}" + (f" | Поставщик содержит: {supplier}" if supplier else "")
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
        await message.answer("Нет черновика. Загрузите документ."); return
    if message.text is not None:
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
        await message.answer("Нет черновика. Загрузите документ."); return
     
     if message.text is not None:
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

