from models_init import User, Novel, Chapter, AISuggestion, Base
from database import engine

def create_tables():
    """
    Создает все таблицы в базе данных.
    """
    print("Создание таблиц в базе данных...")
    Base.metadata.create_all(bind=engine)
    print("Таблицы успешно созданы!")

def drop_tables():
    """
    Удаляет все таблицы из базы данных.
    """
    print("Удаление всех таблиц из базы данных...")
    Base.metadata.drop_all(bind=engine)
    print("Таблицы успешно удалены!")

def recreate_tables():
    """
    Пересоздает все таблицы в базе данных.
    """
    drop_tables()
    create_tables()

if __name__ == "__main__":
    recreate_tables()
