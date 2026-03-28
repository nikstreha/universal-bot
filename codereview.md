# Code Review — universal_bot

> Дата: 2026-03-28
> Ветка: `feature/ddd-migrate`
> Автор ревью: Claude Sonnet 4.6

---

## Оглавление

1. [Общая оценка](#1-общая-оценка)
2. [Критические баги](#2-критические-баги)
3. [Архитектурные проблемы](#3-архитектурные-проблемы)
4. [Нарушения DDD / Clean Architecture](#4-нарушения-ddd--clean-architecture)
5. [Проблемы типизации](#5-проблемы-типизации)
6. [Качество кода](#6-качество-кода)
7. [Конфигурация и инфраструктура](#7-конфигурация-и-инфраструктура)
8. [Тесты](#8-тесты)
9. [Положительные моменты](#9-положительные-моменты)
10. [Приоритизированный план исправлений](#10-приоритизированный-план-исправлений)

---

## 1. Общая оценка

Проект строится на хорошей основе — DDD + Hexagonal Architecture, async I/O, Dishka DI, Pydantic. Архитектурный скелет продуман. Однако проект находится в незавершённом состоянии: есть критические баги в инфраструктурном слое, presentation-слой почти полностью заглушен, отсутствует слой use-case, а тесты не написаны совсем.

| Категория | Оценка |
|-----------|--------|
| Архитектура | 7/10 |
| Корректность кода | 4/10 |
| Типизация | 6/10 |
| Тестируемость | 3/10 |
| Завершённость | 3/10 |

---

## 2. Критические баги

### 2.1 Бесконечная рекурсия в `RedisProvider`

**Файл:** `src/universal_bot/infrastructure/redis/redis_provider.py`

```python
# ТЕКУЩИЙ КОД — СЛОМАН
@property
def redis(self) -> Redis:
    if self.redis is None:       # вызывает себя → RecursionError
        raise RuntimeError(...)
    return self.redis            # вызывает себя → RecursionError
```

**Исправление:**

```python
@property
def redis(self) -> Redis:
    if self._redis is None:
        raise RuntimeError("Redis client is not initialized")
    return self._redis
```

При любом обращении к `redis` — в `get()`, `set()` — происходит `RecursionError`. Redis полностью нерабочий.

---

### 2.2 Отсутствие вызова `.model_dump()` в `MyChatWriter`

**Файл:** `src/universal_bot/infrastructure/mongodb/repositories/chat/writer.py`, строка ~30

```python
# ТЕКУЩИЙ КОД — СЛОМАН
message_doc = MessageMapper.to_document(message).model_dump  # ← это атрибут, не вызов!
await self.collection.update_one(
    {"user_id": user_id},
    {"$push": {"messages": message_doc}}
)
```

**Исправление:**

```python
message_doc = MessageMapper.to_document(message).model_dump()
```

`MongoDB` получит bound method вместо словаря, операция `$push` упадёт с ошибкой. Добавление сообщений не работает.

---

### 2.3 Несоответствие имени поля в `MyChatReader`

**Файл:** `src/universal_bot/infrastructure/mongodb/repositories/chat/reader.py`

```python
# ТЕКУЩИЙ КОД — СЛОМАН
doc = await self.collection.find_one({"user.user_id": user_id})
```

**Ожидаемое:** документ хранится с полем `user_id` на верхнем уровне (так сохраняет `MyChatWriter`):

```python
# В ChatDocument
_id: int
user_id: int   # ← верхнеуровневый ключ
```

**Исправление:**

```python
doc = await self.collection.find_one({"user_id": user_id})
```

`get_by_user_id()` всегда возвращает `None`, весь chat-функционал нерабочий.

---

### 2.4 Использование несуществующей модели

**Файл:** `src/universal_bot/composition/configuration/config.py`

```python
CHAT_MODEL: str = "gpt-5-mini"
```

Модели `gpt-5-mini` не существует в OpenAI API (вероятно, имелось в виду `gpt-4o-mini`). При попытке сгенерировать ответ — ошибка API.

---

### 2.5 Захардкоженный ID администратора

**Файл:** `src/universal_bot/presentation/telegram/router/admin_handlers.py`

```python
ADMIN_ID = 775965340  # HARDCODED
```

Это не должно быть в коде. Даже для личного бота ID должен приходить из конфигурации — иначе при смене аккаунта придётся менять код.

---

## 3. Архитектурные проблемы

### 3.1 Отсутствует слой Use Cases / Application Services

Вся архитектура предполагает Application Layer с Use Cases, но он отсутствует. Есть только порты и DTO, но нет самих сценариев. Handlers должны вызывать Use Cases, а не напрямую репозитории.

**Текущий поток:**
```
Handler → (ничего) → Repository
```

**Ожидаемый поток:**
```
Handler → UseCase → Repository/Provider
```

Это нарушает принцип единственной ответственности и делает presentation-слой зависимым от инфраструктуры.

---

### 3.2 `IUserReader` возвращает `UserDocument`, а не Domain Entity

**Файл:** `src/universal_bot/application/port/db/repositories/user/reader.py`

```python
class IUserReader(ABC):
    async def get_by_id(self, user_id: UserId) -> UserDocument | None:
```

Порт приложения не должен знать про `UserDocument` — это деталь инфраструктуры. Интерфейс должен возвращать `User` (domain entity).

**Правило:** слой `application/port` должен оперировать только domain-объектами и DTO, но не document-моделями.

**Исправление:**

```python
class IUserReader(ABC):
    async def get_by_id(self, user_id: UserId) -> User | None:
    async def is_user_permitted(self, user_id: UserId) -> bool:
    async def is_user_admin(self, user_id: UserId) -> bool:
```

Аналогичная проблема в `IMyChatReader` — возвращает `ChatDocument` и `list[MessageDocument]`.

---

### 3.3 Дублирование метода `get_by_id` в `IUserWriter`

**Файл:** `src/universal_bot/application/port/db/repositories/user/writer.py`

```python
class IUserWriter(ABC):
    async def get_by_id(self, user_id: UserId) -> User | None:  # ← зачем read в write-порту?
    async def create(self, user: User) -> None:
    async def replace(self, user: User) -> None:
```

`get_by_id` — операция чтения и не должна быть в `IUserWriter`. Это нарушает Command-Query Separation. Если write-операция требует чтения — пусть она принимает готовый объект.

---

### 3.4 `ChatMapper.to_entity()` не реализован

**Файл:** `src/universal_bot/infrastructure/mongodb/mapper/chat/chat_mapper.py`

```python
class ChatMapper:
    @staticmethod
    def to_document(entity: MyChat) -> ChatDocument: ...

    @staticmethod
    def to_entity(document: ChatDocument) -> MyChat: ...  # NotImplemented или отсутствует
```

Без `to_entity` чтение из MongoDB не может вернуть domain entity — только raw документ. Весь цикл "load entity → modify → persist" не работает.

---

### 3.5 `system_commands` router не подключён

**Файл:** `src/universal_bot/composition/api_app.py`

```python
dp.include_router(bot_router)
# system_commands.router не включён!
```

Команды `/start` и `/help` никогда не обработаются.

---

### 3.6 Handlers не используют DI

**Файл:** `src/universal_bot/presentation/telegram/router/admin_handlers.py`

```python
@router.message(F.text == AdminButtons.ADD_USER)
async def add_user_handler(message: types.Message) -> None:
    await message.answer("add user")  # заглушка без инъекции зависимостей
```

Dishka настроен, но handlers не принимают никаких зависимостей через него. Весь IoC-контейнер бесполезен на уровне presentation.

---

## 4. Нарушения DDD / Clean Architecture

### 4.1 Domain entity импортирует инфраструктурные типы

Если в маппере или репозитории происходит `from universal_bot.domain.entity.user import User` — это нормально. Но если в entity появляются импорты из `infrastructure` или `application.port` — это нарушение. Проверить при расширении кода.

---

### 4.2 `UserDocument` используется как domain object в портах

Как описано в п. 3.2 — document-модели MongoDB протекают через границу Application Layer в порты. Domain Layer становится зависимым от деталей персистентности.

---

### 4.3 `Entity` базовый класс — лишний generic

**Файл:** `src/universal_bot/domain/entity/common.py`

```python
class Entity(Generic[IdType]):
    id_: IdType
```

Generic-параметр здесь не добавляет пользы — Python не проверяет дженерики в рантайме, а статическая польза минимальна. Если хотите статических гарантий, потребуется `Protocol` или `TypeVar` с bound. Иначе — усложнение без выгоды.

---

### 4.4 Value Objects без валидации

**Файл:** `src/universal_bot/domain/value_object/user/user_name.py`, и другие

```python
@dataclass(frozen=True)
class UserName:
    value: str
```

Value Object должен гарантировать инварианты при создании. Нет проверки на пустую строку, длину, допустимые символы. Если `UserName("")` — это невалидное состояние домена, оно должно быть невозможно создать.

**Пример исправления:**

```python
@dataclass(frozen=True)
class UserName:
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("UserName cannot be empty")
        if len(self.value) > 64:
            raise ValueError("UserName too long")
```

---

### 4.5 `MyChat.messages` nullable без обоснования

**Файл:** `src/universal_bot/domain/entity/chat.py`

```python
messages: list[Message] | None
```

Агрегат без сообщений — это агрегат с пустым списком, а не `None`. `None` создаёт необходимость проверок везде. Инициализировать как `field(default_factory=list)`.

---

## 5. Проблемы типизации

### 5.1 Смешанные стили импортов

В части файлов:
```python
from src.universal_bot.domain.entity.user import User
```

В других:
```python
from universal_bot.domain.entity.user import User
```

Нужно выбрать один стиль (предпочтительно без `src.` префикса) и применить везде.

---

### 5.2 `# type: ignore` и `# pyright: ignore` без объяснений

Если приходится игнорировать type checker — нужен комментарий почему:

```python
some_value  # type: ignore[assignment]  # aiogram returns Any here, see issue #123
```

---

### 5.3 Неиспользуемые импорты в handlers

`admin_handlers.py` импортирует `IUserReader`, `IUserWriter` и другие зависимости, но не использует их в handler-функциях. Это создаёт путаницу и нарушает правила линтера.

---

### 5.4 `TokenUsed` как `int`, завёрнутый в dataclass

```python
@dataclass(frozen=True)
class TokenUsed:
    value: int
```

Это добавляет обёртку без инвариантов. Либо добавить валидацию (`value >= 0`), либо использовать `NewType`:

```python
TokenUsed = NewType("TokenUsed", int)
```

Аналогично для других thin value objects.

---

## 6. Качество кода

### 6.1 `BotApplication` — метод `up()` слишком много делает

**Файл:** `src/universal_bot/composition/api_app.py`

Метод `up()` создаёт `Bot`, `Dispatcher`, подключает роутеры, настраивает Dishka и запускает polling — это 5 разных ответственностей. Нужно декомпозировать:

```python
async def up(self) -> None:
    bot = self._create_bot()
    dp = self._create_dispatcher()
    self._setup_routers(dp)
    self._setup_di(dp)
    await dp.start_polling(bot)
```

---

### 6.2 `build_app()` читает конфигурацию дважды

Если `Settings()` вызывается как внутри `build_app()`, так и внутри `ConfigurationProvider` в IoC — конфигурация загружается дважды. Нужно создавать `Settings` один раз и передавать в контейнер.

---

### 6.3 Отсутствует обработка ошибок в Telegram handlers

```python
async def start_handler(message: types.Message) -> None:
    await message.answer("Hello!")
```

Нет try/except, нет логирования ошибок. При любом сбое (например, MongoDB недоступен) бот просто упадёт без информативного сообщения пользователю.

**Минимум:**

```python
async def start_handler(message: types.Message) -> None:
    try:
        await message.answer("Hello!")
    except Exception:
        logger.exception("Error in start_handler")
        await message.answer("Произошла ошибка. Попробуйте позже.")
```

---

### 6.4 `MongoConnector` — контекстный менеджер или инъекция?

Если `MongoConnector` — это контекстный менеджер, то кто управляет его жизненным циклом? Репозитории принимают `MongoConnector` через DI, но непонятно, как и когда вызываются `__aenter__` / `__aexit__`. Это нужно явно документировать или решить через Dishka lifecycle.

---

### 6.5 Нет логирования на уровне application/domain

Логирование есть в инфраструктурном слое (`logger.info("Uploading...")` в MinIO), но нет в application и domain. Для диагностики полезно логировать ключевые события:

```python
logger.info("Creating user", extra={"user_id": user_id, "role": role})
```

---

### 6.6 `UserRole.weight` — магические числа

```python
class UserRole(IntEnum):
    SUPERADMIN = 30
    ADMIN = 20
    TEMP_ADMIN = 15
    USER = 10
    TEMP_USER = 5
    OTHER = 0
    BANNED = -10
```

Числа сами по себе нормальны для весов, но методы `is_permitted()` и `is_admin()` в репозитории сравнивают `role.weight >= TEMP_USER.weight`. Лучше вынести эту логику в сам `UserRole`:

```python
class UserRole(IntEnum):
    ...

    @property
    def is_permitted(self) -> bool:
        return self >= UserRole.TEMP_USER

    @property
    def is_admin(self) -> bool:
        return self >= UserRole.TEMP_ADMIN
```

Тогда репозиторий не будет знать про пороговые значения.

---

### 6.7 Dockerfile запускает `uvicorn`, а не бота

**Файл:** `Dockerfile`

```dockerfile
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7000"]
```

Но точка входа бота — `python -m src.cli api` (polling, не HTTP-сервер). `uvicorn` и `src.main:app` не существуют. Dockerfile нерабочий.

**Исправление:**

```dockerfile
CMD ["python", "-m", "src.cli", "api"]
```

---

## 7. Конфигурация и инфраструктура

### 7.1 `docker-compose.yml` — версия устарела

```yaml
version: "3.8"
```

Поле `version` в Docker Compose V2 устарело (deprecated) и игнорируется. Можно убрать.

---

### 7.2 Нет сервиса бота в `docker-compose.yml`

`docker-compose.yml` поднимает Redis, MongoDB, MinIO, Mongo Express — но не сам бот. Для полноценного dev/prod окружения нужен сервис `bot`:

```yaml
bot:
  build: .
  depends_on:
    mongodb:
      condition: service_healthy
    redis:
      condition: service_healthy
  env_file: .env
  restart: unless-stopped
```

---

### 7.3 MongoDB без аутентификации в compose

```yaml
mongodb:
  image: mongo:8
  # нет MONGO_INITDB_ROOT_USERNAME / MONGO_INITDB_ROOT_PASSWORD
```

Для dev-окружения приемлемо, но `config.py` строит `mongo_url` с credentials. Нужно либо убрать credentials из URL для dev, либо добавить их в compose.

---

### 7.4 MinIO credentials в открытом виде

```yaml
environment:
  MINIO_ROOT_USER: minioadmin
  MINIO_ROOT_PASSWORD: minioadmin
```

Для dev приемлемо, но должно быть задокументировано что это dev-only значения, не production.

---

### 7.5 Нет `.env.example` в репозитории (или он неполный)

Все необходимые переменные окружения должны быть документированы в `.env.example`. Судя по `config.py`, требуется: `BOT_TOKEN`, `MODEL_TOKEN`, `PROXYAPI_BASE_URL`, `MINIO_*`, `REDIS_*`, `MONGO_*`.

---

### 7.6 `pyproject.toml` — `requires-python = ">=3.14"`

Python 3.14 — pre-release на момент написания. Если используются специфичные фичи 3.14 — нужно явно указать что и почему. Если нет — лучше снизить до `>=3.12` для совместимости с Docker-образами.

---

## 8. Тесты

Директория `tests/` существует, но полностью пуста.

**Минимально необходимое покрытие:**

| Компонент | Тип теста | Приоритет |
|-----------|-----------|-----------|
| Domain entities (User, MyChat) | Unit | Высокий |
| Value Objects (валидация) | Unit | Высокий |
| UserRole permission logic | Unit | Высокий |
| Mappers (to_document / to_entity) | Unit | Высокий |
| Repository implementations | Integration | Средний |
| Use Cases (после реализации) | Unit с mock | Средний |
| Telegram handlers | Integration | Низкий |

**Инфраструктура для тестов уже есть:** `pytest-asyncio` и `pytest` в dev-зависимостях. Нужно только написать тесты.

Пример структуры:

```
tests/
├── unit/
│   ├── domain/
│   │   ├── test_user.py
│   │   ├── test_chat.py
│   │   └── test_value_objects.py
│   └── infrastructure/
│       └── mapper/
│           ├── test_user_mapper.py
│           └── test_chat_mapper.py
└── integration/
    └── mongodb/
        └── test_user_repository.py
```

---

## 9. Положительные моменты

- **Чистая архитектура**: Разделение на domain / application / infrastructure / presentation / composition соблюдено строго. Добавить новый AI-провайдер или заменить MongoDB на PostgreSQL можно без изменения доменного кода.
- **Async-first**: Все операции I/O асинхронны. `asyncio`, `aiogram`, `motor`/`pymongo` async, async Redis — всё согласовано.
- **Interface Segregation**: Отдельные `IUserReader` / `IUserWriter` — правильное применение ISP. Read-модели могут использовать денормализацию независимо от write-моделей.
- **Dishka DI**: Хороший выбор для async Python. Scoped lifecycle (APP/REQUEST) правильно настроен.
- **Pydantic Settings**: Конфигурация через `pydantic-settings` с явными типами — лучше чем `os.getenv()`.
- **Pre-commit hooks**: Ruff + Pyright в pre-commit — хорошая практика. Не даёт закоммитить некорректный код.
- **Frozen dataclasses**: Value Objects реализованы как `@dataclass(frozen=True)` — иммутабельность гарантирована на уровне Python.
- **UserRole с весами**: Гибкая система ролей с числовыми весами позволяет легко добавлять новые роли без изменения логики сравнения.

---

## 10. Приоритизированный план исправлений

### P0 — Немедленно (проект не работает без этих фиксов)

1. Исправить бесконечную рекурсию в `RedisProvider` (`self._redis`)
2. Добавить `()` в `model_dump` в `MyChatWriter`
3. Исправить поле запроса в `MyChatReader` (`user_id` вместо `user.user_id`)
4. Исправить `CMD` в `Dockerfile`
5. Подключить `system_commands.router` в `api_app.py`
6. Убрать `gpt-5-mini` → `gpt-4o-mini`

### P1 — Высокий приоритет (архитектура)

7. Реализовать `ChatMapper.to_entity()`
8. Убрать `UserDocument`/`ChatDocument` из портов приложения, заменить на domain entities
9. Убрать `get_by_id` из `IUserWriter`
10. Вынести `ADMIN_ID` в конфигурацию

### P2 — Средний приоритет (качество)

11. Добавить Use Cases / Application Services
12. Добавить DI в Telegram handlers
13. Добавить валидацию в Value Objects
14. Исправить `messages: list[Message] | None` → `list[Message]` с дефолтом
15. Написать unit-тесты для domain и mapper слоёв

### P3 — Низкий приоритет (улучшения)

16. Добавить сервис `bot` в `docker-compose.yml`
17. Добавить обработку ошибок в handlers
18. Унифицировать стиль импортов
19. Перенести логику `is_permitted`/`is_admin` в `UserRole`
20. Убрать `version: "3.8"` из `docker-compose.yml`
