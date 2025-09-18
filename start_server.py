
import sys
import os
import subprocess

# Переходим в директорию backend и запускаем сервер
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
os.chdir(backend_dir)

print("🚀 Запускаем сервер Novelsia...")
print(f"📁 Рабочая директория: {os.getcwd()}")
print("🌐 Сервер будет доступен по адресу: http://localhost:8000")
print("📚 API документация: http://localhost:8000/docs")
print("=" * 50)

try:
    subprocess.run([sys.executable, "run.py"], check=True)
except KeyboardInterrupt:
    print("\n🛑 Сервер остановлен пользователем")
except Exception as e:
    print(f"❌ Ошибка запуска сервера: {e}")
