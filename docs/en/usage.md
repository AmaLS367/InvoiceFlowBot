# 📖 Usage

> [!TIP]
> Start with `/start` command to see the interactive menu!

## 🎯 Typical flow:

1. Start a chat with the bot and run `/start` to display the menu.
2. Upload an invoice as a PDF or image. The bot acknowledges receipt and forwards the file to OCR.
3. Mindee extraction completes and the bot shares a draft via `/show`.
4. Adjust header fields or line items using commands or inline buttons.
5. Confirm the draft with `/save`, which writes it to SQLite.
6. Request historical data with `/invoices <from> <to> [supplier=...]`.

## Commands

- `/start` — initialize the session and show the keyboard.
- `/help` — short reminder of available actions.
- `/show` — display the current draft.
- `/save` — persist the draft and clear the state.
- `/edit supplier=... client=... date=YYYY-MM-DD doc=... total=123.45` — batch-edit header fields.
- `/edititem <index> name=... qty=... price=... total=...` — tweak a specific line item.
- `/comment <text>` — append a comment to the active invoice.
- `/invoices YYYY-MM-DD YYYY-MM-DD [supplier=text]` — list stored invoices for a given period with optional supplier filtering.

## Inline buttons

`handlers/utils.py` supplies inline keyboards for:
- Uploading another invoice.
- Editing header attributes directly.
- Adding comments or line items.
- Saving the draft.
- Launching period queries without typing the command.

Buttons mirror command capabilities and make the bot friendlier for non-technical users.

## Draft lifecycle

Per-user state keeps a draft until it is saved. You can upload multiple files, overwrite previous drafts, or add comments before persisting. After `/save` the state resets and the next `/show` refers to the following document.
