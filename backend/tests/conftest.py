import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db
from config import settings
# Импортируем модели для правильной инициализации
from models_init import User, Novel, Chapter, AISuggestion

# Создание тестовой базы данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """
    Переопределение зависимости для получения тестовой БД.
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture
def db_session():
    """
    Фикстура для создания тестовой сессии БД.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """
    Фикстура для создания тестового клиента.
    """
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user_data():
    """
    Фикстура с тестовыми данными пользователя.
    """
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }

@pytest.fixture
def test_novel_data():
    """
    Фикстура с тестовыми данными новеллы.
    """
    return {
        "title": "Test Novel",
        "description": "A test novel description",
        "genre": "fantasy",
        "is_public": False
    } 