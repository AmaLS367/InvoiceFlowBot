<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=header&text=Docker+Setup&fontSize=40&animation=fadeIn"/>

<div align="center">

[![Docker](https://img.shields.io/badge/Docker-Compose-blue?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Container](https://img.shields.io/badge/Container-Ready-green?style=for-the-badge)](https://hub.docker.com/)
[![Quick Start](https://img.shields.io/badge/Setup-5%20Minutes-orange?style=for-the-badge)](#запуск-контейнера)

</div>

## 📋 О Docker

Docker позволяет развернуть InvoiceFlowBot без локальной установки Python и зависимостей. Контейнер содержит все нужные пакеты, а на хост монтируются только база и логи.

> [!TIP]
> Docker - самый быстрый способ запуска! Все зависимости уже включены в образ.

## ⚙️ Подготовка

1. Скопируйте настройки:
```powershell
Copy-Item .env.example .env
notepad .env
```

2. Убедитесь, что файл `data.sqlite` существует и именно файл, а не директория. На Windows при отсутствии файла Docker может создать папку с таким именем. Если это произошло, удалите папку и пересоздайте пустой файл:
```powershell
Remove-Item .\data.sqlite -Recurse -Force
New-Item .\data.sqlite -ItemType File | Out-Null
```

## 🚀 Запуск контейнера

```powershell
docker-compose up --build -d
```

> [!NOTE]
> - `--build` пересобирает образ при обновлениях
> - `-d` запускает стек в фоновом режиме

## 🔄 Остановка и обновление

Остановить сервис:
```powershell
docker-compose down
```

Получить свежую версию и пересобрать:
```powershell
git pull
docker-compose up --build -d
```

## Томы и данные

Файл `docker-compose.yml` монтирует ресурсы:
- `./data.sqlite:/app/data.sqlite` — база счетов. Держите ее в бэкапах.
- `./logs:/app/logs` — логи OCR и ошибок доступны на хосте.

Логи и база сохраняются между рестартами контейнера, поэтому перед обновлениями достаточно сделать резервную копию этих путей.
