# Recipe Generation API

## Генерация рецептов через LLM

### Описание

Система поддерживает асинхронную генерацию рецептов с использованием LLM (Large Language Model) через OpenRouter. Процесс включает:

1. Пользователь отправляет запрос на генерацию рецепта
2. Система ставит задачу в очередь (taskiq)
3. Воркер вызывает LLM через OpenRouter API
4. Результат валидируется и сохраняется в БД

### Зависимости

Следующие пакеты должны быть установлены (уже добавлены в `pyproject.toml`):

- `taskiq` - система очередей задач
- `taskiq-aio-pika` - брокер для taskiq (опционально, сейчас используется InMemoryBroker)
- `taskiq-fastapi` - интеграция с FastAPI
- `openai` - клиент для OpenRouter API

### Конфигурация

#### 1. OpenRouter API ключ

Получите API ключ:
1. Зарегистрируйтесь на https://openrouter.ai/
2. Получите ключ на https://openrouter.ai/workspaces/default/keys
3. Добавьте в файл `.env`:

```
APP_CONFIG__API__ROUTER_KEY=your_key_here
```

#### 2. Структура проекта

```
app/
  task_queue/          # Конфигурация брокера очереди
    __init__.py
    broker.py
  tasks/              # Задачи для асинхронного выполнения
    __init__.py
    recipe_generation.py
  models/
    recipe_generation.py  # Pydantic схемы для генерации
```

### Использование API

#### Endpoint: POST /api/recipes/generate

Отправить запрос на генерацию рецепта:

```bash
curl -X POST http://localhost:8000/api/recipes/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "prompt": "Хочу рецепт пасты с курицей и сливочным соусом"
  }'
```

**Ответ:**

```json
{
  "status": "Генерация началась"
}
```

### Запуск

#### 1. Запуск API сервера

```bash
cd app
python main.py
```

или

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Запуск воркера (в отдельном терминале)

```bash
cd app
taskiq worker task_queue:broker --fs-discover --tasks-pattern "**/tasks"
```

или используйте скрипт:

```bash
chmod +x run_worker.sh
./run_worker.sh
```

### Структура генерируемого рецепта

LLM возвращает структурированный JSON с следующими полями:

```json
{
  "title": "Паста с курицей и сливочным соусом",
  "description": "Подробное описание и инструкции готовки...",
  "cooking_time": 30,
  "difficulty": 2,
  "cuisine_name": "итальянская",
  "ingredients": [
    {
      "name": "паста",
      "quantity": 400,
      "measurement": "GRAMS"
    },
    {
      "name": "куриное филе",
      "quantity": 300,
      "measurement": "GRAMS"
    },
    {
      "name": "сливки",
      "quantity": 200,
      "measurement": "MILLILITERS"
    }
  ],
  "allergens": ["молочные продукты", "глютен"]
}
```

### Валидация и сохранение

После получения ответа от LLM система:

1. **Валидирует данные** через Pydantic схему `GeneratedRecipeSchema`
2. **Создает или получает** существующие записи:
   - `Cuisine` (кухня)
   - `Ingredient` (ингредиенты)
   - `Allergen` (аллергены)
3. **Сохраняет рецепт** в БД с автором = текущий пользователь
4. **Избегает дубликатов** - проверяет существование перед созданием

### Механизм повторных попыток (Retry)

Task имеет встроенный механизм повторных попыток в случае ошибок.
Если генерация не удалась, система попытается выполнить задачу снова.

### Модели данных

#### Measurement Enum

Единицы измерения ингредиентов:
- `GRAMS` (1) - граммы
- `PIECES` (2) - штуки
- `MILLILITERS` (3) - миллилитры

#### Difficulty Levels

Сложность рецепта от 1 до 5:
- 1 - очень просто
- 2 - просто
- 3 - средне
- 4 - сложно
- 5 - очень сложно

### Примеры

#### Пример 1: Простой рецепт

```bash
curl -X POST http://localhost:8000/api/recipes/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token" \
  -d '{"prompt": "Простой рецепт яичницы"}'
```

#### Пример 2: Сложный рецепт с ограничениями

```bash
curl -X POST http://localhost:8000/api/recipes/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token" \
  -d '{"prompt": "Рецепт без глютена и молочных продуктов"}'
```

### Troubleshooting

#### Ошибка: "API ключ не найден"

Убедитесь, что в `.env` файле правильно установлен `APP_CONFIG__API__ROUTER_KEY`.

#### Ошибка: "Воркер не подхватывает задачи"

1. Убедитесь, что воркер запущен в отдельном терминале
2. Проверьте правильность команды запуска воркера
3. Проверьте логи воркера на ошибки

#### Task зависает

Если task зависает, это может быть:
- Ошибка в LLM API
- Проблемы с подключением к БД
- Timeout при вызове LLM

Проверьте логи и убедитесь, что все зависимости установлены.

### Логирование

Приложение логирует:
- Начало генерации рецепта
- Успешное создание новых записей (кухня, ингредиенты, аллергены)
- Ошибки при генерации и сохранении
- Успешное сохранение рецепта в БД

Проверьте логи воркера и приложения для отладки проблем.

### Планы развития

- [ ] Замена InMemoryBroker на RabbitMQ (taskiq-aio-pika)
- [ ] WebSocket для real-time уведомлений о статусе генерации
- [ ] Кеширование часто используемых ингредиентов и аллергенов
- [ ] Улучшение промптов для более точной генерации
- [ ] Добавление рейтинга и отзывов к генерируемым рецептам
