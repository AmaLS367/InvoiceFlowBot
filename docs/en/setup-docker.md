<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=header&text=Docker+Setup&fontSize=40&animation=fadeIn"/>

<div align="center">

[![Docker](https://img.shields.io/badge/Docker-Compose-blue?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Container](https://img.shields.io/badge/Container-Ready-green?style=for-the-badge)](https://hub.docker.com/)
[![Quick Start](https://img.shields.io/badge/Setup-5%20Minutes-orange?style=for-the-badge)](#start-the-stack)

</div>

## 📋 About Docker

Docker provides a self-contained runtime for InvoiceFlowBot: Python, dependencies, and the bot code run inside the container, while the host only keeps the database and logs.

> [!TIP]
> Docker is the fastest way to get started! All dependencies included.

## ⚙️ Preparation

1. Copy environment settings:
```powershell
Copy-Item .env.example .env
notepad .env
```

2. Ensure `data.sqlite` exists as a file, not a directory. On Windows Docker can accidentally create a folder when the path is missing. If that happens, remove it and create an empty file:
```powershell
Remove-Item .\data.sqlite -Recurse -Force
New-Item .\data.sqlite -ItemType File | Out-Null
```

## 🚀 Start the stack

```powershell
docker-compose up --build -d
```

> [!NOTE]
> - `--build` rebuilds the image after updates
> - `-d` runs the service in background mode

## 🔄 Stop and upgrade

Stop the bot:
```powershell
docker-compose down
```

Pull the latest code and rebuild:
```powershell
git pull
docker-compose up --build -d
```

## Volumes

`docker-compose.yml` mounts:
- `./data.sqlite:/app/data.sqlite` — SQLite database persisted on the host.
- `./logs:/app/logs` — OCR and error logs accessible outside the container.

Keep backups of both paths before upgrades to avoid data loss.
