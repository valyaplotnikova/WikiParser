# 🌐 WikiParser — Парсер статей с Wikipedia

> **Проект для рекурсивного парсинга статей с Wikipedia, сохранения их в БД и генерации краткого описания (summary) с помощью нейросети.**

---

## 📌 Описание

**WikiParser** — это асинхронное приложение на FastAPI, которое:

1. Парсит статьи с Wikipedia рекурсивно (до 5 уровня вложенности).
2. Сохраняет статьи в PostgreSQL.
3. Генерирует краткие описания (summary) для корневых статей через API нейросетей (например, OpenAI или DeepSeek).
4. Предоставляет эндпоинты:
   - Запуск парсинга по URL
   - Получение summary по URL статьи

---

## 🧩 Технологии

- 🚀 **FastAPI** — для создания REST API
- 🗄️ **PostgreSQL** + SQLAlchemy (асинхронный доступ через `asyncpg`)
- 🕸️ **HTTPX / aiohttp** — для асинхронных HTTP-запросов
- 🧠 **OpenAI / DeepSeek API** — для генерации summary
- 🐍 **Python 3.11+**
- 🐳 **Docker / Docker Compose** — для запуска всех сервисов локально

---

## 🛠 Установка и запуск

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/valyaplotnikova/WikiParser.git
cd WikiParser
```

### 2. Настройте переменные окружения

Создайте файл `.env` на базе файла .env.example:

### 3. Запустите проект через Docker

```bash
docker-compose up --build
```

API будет доступен по адресу: `http://localhost:8000`

---

## 🌐 Доступные эндпоинты

| Метод | Путь           | Описание |
|-------|----------------|----------|
| POST  | `/parse`       | Запускает парсинг статьи и всех связанных статей (до 5 уровней) |
| GET   | `/summary`     | Возвращает краткое описание (summary) для указанной статьи |

Пример запроса:

```json
POST /parse
{
  "url": "https://en.wikipedia.org/wiki/Python_(programming_language)"
}
```

---

