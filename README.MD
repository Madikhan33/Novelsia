# Project Name

Описание вашего проекта.

## Требования

- Python 3.7+
- Node.js 14+
- npm или yarn

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone <url-репозитория>
cd <название-проекта>
```

### 2. Установка зависимостей Python

```bash
pip install -r requirements.txt
```

### 3. Запуск бэкенда

```bash
cd backend
python main.py
```

Бэкенд будет доступен по адресу: `http://localhost:8000` (или другому порту, указанному в настройках)

### 4. Запуск фронтенда

В новом терминале:

```bash
npm run dev
```

Фронтенд будет доступен по адресу: `http://localhost:3000` (или другому порту, указанному в настройках)

## Структура проекта

```
project/
├── backend/
│   ├── main.py
│   └── ...
├── src/
│   └── ...
├── requirements.txt
├── package.json
└── README.md
```

## Переменные окружения

Создайте файл `.env` в корне проекта и добавьте необходимые переменные:

```
# Пример переменных
DATABASE_URL=sqlite:///./novelsia.db

SECRET_KEY=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

OPENAI_API_KEY=
ENVIRONMENT=development
DEBUG=True

# Google OAuth2 Configuration
GOOGLE_CLIENT_ID=611748627811-chokt7jor54104eo6kca8uf8bvh8bk2l.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# Frontend URL for OAuth redirects
FRONTEND_URL=http://localhost:3000
```

## API Documentation

После запуска бэкенда документация API будет доступна по адресу:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Разработка

### Полезные команды

```bash
# Установка новых Python зависимостей
pip install <package_name>
pip freeze > requirements.txt

# Установка новых npm зависимостей
npm install <package_name>

# Проверка кода
flake8 backend/
eslint src/
```


## Авторы

- Ваше имя - [Madikhan](madizhysip@gmail.com)