# storage

Личное файловое хранилище с Android-клиентом и Telegram-ботом для транскрибации.
Доступ выдаёт один администратор по whitelist. Бот получает обновления через polling или webhook,
администрирование — обычными кнопками. Вход в приложение подтверждается в Telegram;
на сервере используются обычные сессии, без JWT.

Бэкенд: Python 3.14, FastAPI, Dishka, SQLAlchemy asyncio, SQLite, Alembic и MinIO.
Транскрибация: faster-whisper; файлы до 20 МБ. Точные версии зависимостей — в `uv.lock`.
Аудио декодируется установленным в образах FFmpeg в mono PCM 16 kHz перед передачей
модели. Декодирование ограничено по времени и длительности аудио; сетевые протоколы
и плейлисты отключены. Это также устраняет несовместимость декодера faster-whisper
1.2.1 с PyAV 19 (`metadata_errors`). Модель хранится в постоянном кеш-каталоге worker.
На каждое новое аудио бот создаёт один ответ: очередь, расшифровка и итог меняют
текст этого сообщения. Идентификатор ответа сохраняется в SQLite. Длинный результат
заменяет это же сообщение файлом `transcription.txt`; отдельного ответа с файлом нет.

## Запуск

Единственный файл настроек — `.env`, пример — `.env.example`.
Скопировать пример, если файла ещё нет, заполнить настройки и установить `chmod 600 .env`.
Существующий `.env` автоматически не перезаписывается. Его читают приложение,
MinIO и Compose; отдельных файлов по сервисам и окружениям нет.

Логи и алерты обслуживает отдельный `monitoring/compose.yml` (Alloy, Loki, Grafana).
Каталог `monitoring/` приватный, исключён из Git и переносится на сервер отдельно;
инструкция находится в `monitoring/README.md`. Мониторинг запускается до приложения.

Production:

```bash
docker compose -f compose.production.yml config --quiet
docker compose -f monitoring/compose.yml up -d --wait
docker compose -f compose.production.yml up -d --build
```

Для CPU-разработки в том же `.env` установить `APP__SERVER__ENV=dev`,
`APP__ASR__DEVICE=cpu`, `APP__ASR__COMPUTE_TYPE=int8`, указать свои DEV_UID/DEV_GID.
MODEL_CACHE_DIR должен указывать на доступный каталог хоста.

```bash
mkdir -p var/cache
docker compose -f monitoring/compose.yml up -d --wait
docker compose up --build api worker
docker compose --profile telegram up bot
```

API публикуется на `127.0.0.1:7000`. MinIO dev доступен на `127.0.0.1:9000`,
production MinIO не публикует порты. Миграции выполняет Compose перед запуском.
Режим задаётся в `.env`: `APP__TELEGRAM__MODE=polling` или `webhook`.
Polling не требует публичного HTTPS; webhook требует HTTPS-адрес и секрет,
регистрируется при запуске бота. После смены режима пересоздать API и бот.
Администрирование пользователей выполняется только кнопками Telegram-бота.

Подготовка каталогов и постоянного HDD описана в [инструкции деплоя](docs/deployment.md).

## Документация

- [Деплой в Docker](docs/deployment.md)
- [CLI](docs/cli.md)
- [Архитектура](docs/architecture.md)
- [Логика и ограничения](docs/operations.md)
- [API](docs/api.md)
- [Аудит безопасности](docs/security-audit.md)
- [Ручная проверка](docs/manual-testing.md)
- [Дизайн](docs/design.md)

Проверки без добавления тестов:

```bash
uv run --frozen ruff check src
uv run --frozen ruff format --check src/universal_bot
uv run --frozen alembic check
```

GPU-транскрибацию необходимо отдельно проверить на сервере с RTX 2060 и подходящими
CUDA/cuDNN. Ручной прогон файлового API не подтверждает работу GPU или Android-сборки.
