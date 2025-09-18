from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Импорты для роутов
from routes.auth import router as auth_router
from routes.novels import router as novels_router
from routes.chapters import router as chapters_router
from routes.ai_suggestions import router as ai_suggestions_router
from routes.context import router as context_router
from routes.users import router as users_router

# Настройка логирования
from logging_config import setup_logging

# Импорт всех моделей для правильной инициализации SQLAlchemy mappers
from models_init import User, Novel, Chapter, AISuggestion, Base

# Импорт для инициализации базы данных
from database import engine

# Настройка логирования
setup_logging()

# Создание таблиц базы данных при запуске
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Novelsia API",
    description="API для создания и управления новеллами с AI-помощником",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все домены для разработки
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутов
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(novels_router, prefix="/api/novels", tags=["Novels"])
app.include_router(chapters_router, prefix="/api/chapters", tags=["Chapters"])
app.include_router(ai_suggestions_router, prefix="/api/ai", tags=["AI Suggestions"])
app.include_router(context_router, prefix="/api/context", tags=["Context"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])

@app.get("/")
async def root():
    return {"message": "Welcome to Novelsia API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


