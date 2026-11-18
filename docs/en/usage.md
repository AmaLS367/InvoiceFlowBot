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
> Run `/start` to get started.

## Typical flow

1. Run `/start` to open the menu and choose from Russian, English, German, Spanish, French, Italian, and Portuguese. The bot uses your saved preference, then your Telegram language if supported, then Russian.
2. Upload an invoice as a PDF, JPEG, PNG, WebP, or a Telegram photo. Convert HEIC/HEIF to JPEG or PNG first.
3. The bot displays the draft automatically after OCR and can attach a CSV for a long item table. Use `/show` to see the draft again.
4. Review any flagged values and edit the header or existing items. Add a comment if needed.
5. Save the invoice with `/save` or the Save button. The bot records a comment if the sum of the items differs from the invoice total.
6. Request saved invoices using `/invoices` or the period button.

## Commands

- `/start` — open the language picker and the main menu.
- `/help` — see the available actions.
- `/language` — open the language picker, also available as **🌐 Language**. A selection updates the command menu in a private chat.
- `/show` — display the active draft.
- `/save` — save the invoice to SQLite and remove the draft.
- `/edit supplier=ACME; client=Corp; date=2025-01-15; doc=123; total=123.45` — edit several header fields. Separate assignments with semicolons.
- `/edititem 1 name=Widget; qty=5; price=10.50; total=52.50` — edit a line item. The first item is numbered 1. You can also set `code`.
- `/comment <text>` — add a comment to the active draft.
- `/invoices YYYY-MM-DD YYYY-MM-DD [supplier=text]` — query saved invoices by date and optionally by supplier.

## Inline buttons

The menu can prompt for an upload, edit header fields or existing items, add comments, save a draft, open help or language settings, and query by period. Use the period button to enter a supplier name containing spaces.

## Draft lifecycle

SQLite stores one active draft per Telegram user. A new successful upload replaces that draft. After saving, upload another invoice to start a new draft.

The language preference and draft are per user. The period query searches the saved invoices for the entire bot instance, filtered by date and supplier.
