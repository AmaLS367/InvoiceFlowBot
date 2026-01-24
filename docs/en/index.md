<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=150&section=header&text=Documentation&fontSize=50&animation=fadeIn&fontAlignY=38&desc=InvoiceFlowBot%20•%20Complete%20Guide&descAlignY=60&descSize=18"/>

<div align="center">

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=18&duration=3000&pause=1000&center=true&vCenter=true&width=500&lines=Automated+Invoice+Processing;Telegram+%2B+OCR+%2B+SQLite;Complete+Project+Documentation" alt="Typing SVG" />
</p>

</div>

## 📋 About

InvoiceFlowBot is a Telegram assistant that automates invoice capture for finance teams. Users forward PDFs or photos, the bot extracts a structured draft via Mindee, lets the operator review and edit details, and persists confirmed invoices to SQLite.

> [!NOTE]
> The workflow removes repetitive manual entry. Accountants receive a ready draft, adjust header fields or line items, add comments, and store the final version with a single command.

## 📚 Documentation Map

<div align="center">

### 🚀 Quick Start

<table>
<tr>
<td width="50%" align="center">
<img src="https://img.icons8.com/fluency/96/000000/laptop.png" width="64"/>
<br/>
<h4>💻 <a href="setup-local.md">Local Setup</a></h4>
<sub>Python environment and dependencies</sub>
</td>
<td width="50%" align="center">
<img src="https://img.icons8.com/fluency/96/000000/docker.png" width="64"/>
<br/>
<h4>🐳 <a href="setup-docker.md">Docker Setup</a></h4>
<sub>Containerization and deployment</sub>
</td>
</tr>
</table>

### 📖 Main Documentation

</div>

| Section | Description |
|---------|-------------|
| 📖 [System Overview](overview.md) | Architecture, components, data flow |
| 🏗️ [Architecture](architecture.md) | Diagrams and component interactions |
| ⚙️ [Configuration](config.md) | Environment variables and settings |
| 🗄️ [Database](database.md) | SQLite schema and migrations |
| 📝 [Logging](logging.md) | Log files and levels |
| 📖 [Usage](usage.md) | Commands and interactive buttons |
| 🧪 [Tests](tests.md) | Pytest and code coverage |
| 👨‍💻 [Development](development.md) | Developer guide |
| 📜 [Scripts](scripts.md) | Utility scripts and wrappers |
| 🔧 [Troubleshooting](troubleshooting.md) | Common issues and solutions |
| 📸 [Screenshots](screenshots.md) | Visual examples |

<details>
<summary><b>📋 Architecture Decision Records (ADR)</b></summary>

Documented decisions for key technologies:

- [ADR-0001: Mindee as primary OCR provider](../adr/0001-mindee-as-primary-ocr-provider.md)
- [ADR-0002: SQLite as primary storage](../adr/0002-sqlite-as-primary-storage.md)
- [ADR-0003: Aiogram 3 as Telegram framework](../adr/0003-aiogram3-as-telegram-framework.md)

</details>

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=100&section=footer"/>

</div>
