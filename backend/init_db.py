#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных.
"""

from setup_db import create_tables

def init_database():
    """
    Создание всех таблиц в базе данных.
    """
    create_tables()

if __name__ == "__main__":
    init_database() 