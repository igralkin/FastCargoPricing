# Сервис по расчёту стоимости страхования в зависимости от типа груза и объявленной стоимости

## Описание

FastCargoPricing — это REST API сервис для расчёта стоимости страхования груза на основе типа груза и его объявленной стоимости. Сервис поддерживает:
- CRUD операции с тарифами.
- Логирование изменений тарифов через Kafka.
- Хранение данных в PostgreSQL.
- Использование Docker для развёртывания всего стека.


## Технологии

- Python (FastAPI, SQLAlchemy 2)
- PostgreSQL
- Kafka
- Docker и Docker Compose


## Требования

1. **Docker** и **Docker Compose** должны быть установлены.
2. **Postman** (опционально, для тестирования API).


## Инструкция по развёртыванию

### 1. Клонирование репозитория

Склонируйте проект из Git:
```bash
git clone https://github.com/igralkin/FastCargoPricing
cd FastCargoPricing
```


### 2. Настройка `.env`

Создайте файл `.env` в корне проекта и заполните его следующим содержимым:

```env
# PostgreSQL
POSTGRES_USER=user_name
POSTGRES_PASSWORD=user_password
POSTGRES_DB=service_db
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:${POSTGRES_PORT}/${POSTGRES_DB}

# Kafka
KAFKA_SERVER=kafka:9092
KAFKA_TOPIC=rate_logs

# JWT
JWT_SECRET_KEY=your_secret_key
ALGORITHM=HS256
```


### 3. Запуск сервиса

Запустите проект с помощью Docker Compose:
```bash
docker-compose up --build
```

После успешного запуска сервис будет доступен на `http://localhost:8000`.


## API Документация

Для просмотра документации API перейдите по адресу:
```plaintext
http://localhost:8000/docs
```


## Тестирование через Postman

Коллекция **Postman** (`postman/FastCargoPricing API.postman_collection.json`) включает все основные эндпоинты:
1. Добавление тарифа.
2. Обновление тарифа.
3. Удаление тарифа.
4. Калькуляция стоимости страхования.

### Как использовать коллекцию
1. Импортируйте файл коллекции в Postman.
2. Запустите всю последовательность запросов, чтобы проверить функциональность сервиса.
3. Коллекция автоматически:
   - Добавит новый тариф.
   - Рассчитает стоимость страхования с новым тарифом.
   - Обновит тариф.
   - Рассчитает стоимость страхования с измененным тарифом.
   - Удалит тариф.


## Взаимодействие с Kafka и БД

### Чтение сообщений из Kafka:
1. Зайдите в контейнер Kafka:
   ```bash
   docker exec -it kafka /bin/bash
   ```
2. Подключитесь к топику `rate_logs`:
   ```bash
   kafka-console-consumer --bootstrap-server localhost:9092 --topic rate_logs --from-beginning
   ```

### Чтение тарифов из базы данных:
1. Зайдите в контейнер PostgreSQL:
   ```bash
   docker exec -it cargo_db bash
   ```
2. Запустите клиент psql:
   ```bash
   psql -U user_name -d cargodb
   ```
3. Выполните запросы для проверки таблиц:
   ```sql
   SELECT * FROM rates;
   SELECT * FROM rate_change_logs;
   ```


### Потенциальные ошибки
Если при запуске возникают ошибки:
1. Убедитесь, что порты `8000`, `5432`, и `9092` свободны.
2. Очистите тома Docker (если возникли проблемы с данными):
   ```bash
   docker-compose down -v
   ```
