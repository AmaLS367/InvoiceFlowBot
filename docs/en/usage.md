<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=header&text=Usage+Guide&fontSize=40&animation=fadeIn"/>

<div align="center">

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=18&duration=3000&pause=1000&center=true&vCenter=true&width=500&lines=Bot+Commands;Interactive+Buttons;Complete+Workflow" alt="Typing SVG" />
</p>

[![Commands](https://img.shields.io/badge/Commands-8+-blue?style=for-the-badge)](#commands)
[![Buttons](https://img.shields.io/badge/Buttons-Interactive-green?style=for-the-badge)](#inline-buttons)
[![Workflow](https://img.shields.io/badge/Flow-Complete-orange?style=for-the-badge)](#draft-lifecycle)

</div>

## 📋 About Usage

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

`backend.handlers.utils` supplies inline keyboards for:
- Uploading another invoice.
- Editing header attributes directly.
- Adding comments or line items.
- Saving the draft.
- Launching period queries without typing the command.

Buttons mirror command capabilities and make the bot friendlier for non-technical users.

## Draft lifecycle

Per-user state keeps a draft until it is saved. You can upload multiple files, overwrite previous drafts, or add comments before persisting. After `/save` the state resets and the next `/show` refers to the following document.
