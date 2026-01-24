<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=150&section=header&text=Contributing%20Guide&fontSize=50&animation=fadeIn&fontAlignY=38&desc=Help%20us%20make%20InvoiceFlowBot%20better!&descAlignY=60&descSize=18"/>

<div align="center">

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=20&duration=3000&pause=1000&center=true&vCenter=true&width=500&lines=Welcome+Contributors!;Build+%7C+Test+%7C+Document;Quality+First+Development" alt="Typing SVG" />
</p>

[![Code Quality](https://img.shields.io/badge/code%20quality-high-brightgreen?style=for-the-badge)](https://github.com/astral-sh/ruff)
[![Tests](https://img.shields.io/badge/tests-passing-success?style=for-the-badge&logo=pytest)](https://docs.pytest.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge)](http://makeapullrequest.com)

</div>

---

## 📖 Overview

This document describes how to work with the codebase as a developer.

## 💻 Development Environment

> [!TIP]
> Follow these steps to set up your local development environment

<details>
<summary><b>🚀 Quick Setup Guide</b></summary>

### 1️⃣ Clone the repository

```powershell
git clone https://github.com/AmaLS367/InvoiceFlowBot.git
cd InvoiceFlowBot
```

### 2️⃣ Create and activate virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3️⃣ Install dependencies in editable mode with dev extras

```powershell
python -m pip install -e .[dev]
```

> [!NOTE]
> This installs all development tools: pytest, ruff, mypy, pre-commit, bandit

</details>

## 🧪 Running Tests and Checks

> [!IMPORTANT]
> Always run these checks before committing code!

<div align="center">

```mermaid
graph LR
    A[💻 Code Changes] -->|Run| B[🔍 Ruff Lint]
    B -->|Pass| C[🏷️ MyPy Types]
    C -->|Pass| D[🧪 Pytest]
    D -->|Pass| E[✅ Commit]

    style A fill:#4A90E2,stroke:#2c3e50,stroke-width:2px,color:#fff
    style B fill:#FFD93D,stroke:#2c3e50,stroke-width:2px,color:#333
    style C fill:#FF6B6B,stroke:#2c3e50,stroke-width:2px,color:#fff
    style D fill:#50C878,stroke:#2c3e50,stroke-width:2px,color:#fff
    style E fill:#B19CD9,stroke:#2c3e50,stroke-width:2px,color:#fff
```

</div>

### ⚡ Quick Check Commands

```powershell
# 🔍 Lint check
python -m ruff check .

# 🏷️ Type check
python -m mypy backend/

# 🧪 Run tests
python -m pytest
```

| Tool | Purpose | Config |
|------|---------|--------|
| 🔍 **ruff** | Linting & formatting | `pyproject.toml` |
| 🏷️ **mypy** | Type checking | `pyproject.toml` |
| 🧪 **pytest** | Unit & integration tests | `pyproject.toml` |
| 📊 **coverage** | Code coverage | `pyproject.toml` |

> [!NOTE]
> Unit tests and integration tests live under the `tests/` package.

## 🎣 Pre-commit Hooks

<div align="center">

![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=for-the-badge&logo=pre-commit&logoColor=white)

</div>

This project uses `pre-commit` for automated local checks:

<table align="center">
<tr>
<td align="center">
<img src="https://img.icons8.com/fluency/48/000000/code.png" width="32"/>
<br/>
<b>🔍 Ruff</b>
<br/>
<sub>Lint & Format</sub>
</td>
<td align="center">
<img src="https://img.icons8.com/fluency/48/000000/python.png" width="32"/>
<br/>
<b>🏷️ MyPy</b>
<br/>
<sub>Type Checking</sub>
</td>
<td align="center">
<img src="https://img.icons8.com/fluency/48/000000/security-checked.png" width="32"/>
<br/>
<b>🔒 Bandit</b>
<br/>
<sub>Security Checks</sub>
</td>
</tr>
</table>

### 🔧 Install and run hooks

```powershell
# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

> [!NOTE]
> CI will automatically run `pre-commit` on every push and pull request.

## 📜 Coding Guidelines

> [!IMPORTANT]
> Follow these principles to maintain code quality

### 🏗️ Architecture Principles

```mermaid
graph TD
    A[handlers] -->|uses| B[services]
    B -->|uses| C[domain]
    B -->|uses| D[ocr]
    B -->|uses| E[storage]
    F[core] -->|configures| A
    F -->|configures| B

    style A fill:#4A90E2,stroke:#2c3e50,stroke-width:2px,color:#fff
    style B fill:#50C878,stroke:#2c3e50,stroke-width:2px,color:#fff
    style C fill:#FFD93D,stroke:#2c3e50,stroke-width:2px,color:#333
    style D fill:#FF6B6B,stroke:#2c3e50,stroke-width:2px,color:#fff
    style E fill:#B19CD9,stroke:#2c3e50,stroke-width:2px,color:#fff
    style F fill:#A8E6CF,stroke:#2c3e50,stroke-width:2px,color:#333
```

### ✅ Best Practices

| Rule | Description | Why |
|------|-------------|-----|
| 🐍 **Python 3.11+** | Target modern Python | New features & performance |
| 🏛️ **Layer Separation** | `domain` → `services` → `handlers` | Clean architecture |
| 🧠 **Business Logic** | Keep in `services` & `domain` | Not in handlers |
| ⚡ **Async I/O** | For network & database | Better performance |
| 🧪 **Test Coverage** | For non-trivial changes | Prevent regressions |

<details>
<summary><b>📁 Project Structure</b></summary>

```
InvoiceFlowBot/
├── backend/
│   ├── 🎯 domain/      # Business entities
│   ├── ⚙️ services/    # Business logic
│   ├── 🔍 ocr/         # OCR providers
│   ├── 💾 storage/     # Database layer
│   ├── 🤖 handlers/    # Telegram handlers
│   └── 🔧 core/        # Configuration & DI
```

</details>

## 📚 Documentation

> [!TIP]
> Keep documentation up-to-date with your changes!

### 🏗️ Architecture & Design

<table>
<tr>
<td width="50%">

**📊 Architecture Docs**
- `docs/en/architecture.md`
- `docs/ru/architecture.md`

High-level system diagrams and component interactions

</td>
<td width="50%">

**📋 ADR (Architecture Decision Records)**
- `docs/adr/`

Documented decisions for key technology choices

</td>
</tr>
</table>

### ✍️ When to Update Docs

| Change Type | Update |
|-------------|--------|
| 🔧 Configuration | `docs/*/config.md` |
| 🐳 Deployment | `docs/*/setup-*.md` |
| 🏗️ Architecture | `docs/*/architecture.md` |
| ⚙️ Features | `docs/*/usage.md` |

---

<div align="center">

## 🤝 Thank You for Contributing!

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=18&duration=3000&pause=1000&center=true&vCenter=true&width=500&lines=Every+contribution+matters;Let's+build+something+amazing!;Happy+coding!" alt="Typing SVG" />
</p>

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=100&section=footer"/>

**Questions? Open an issue or discussion!** 💬

</div>
