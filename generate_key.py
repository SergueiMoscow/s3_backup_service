import os
from dotenv import load_dotenv, set_key
import secrets

# Загружаем переменные окружения из .env файла
env_path = '.env'
load_dotenv(env_path)

# Проверяем наличие ключа SECRET_KEY в переменных окружения
secret_key = os.getenv('SECRET_KEY')

if not secret_key:
    # Генерируем случайный ключ длиной 50 символов
    new_secret_key = secrets.token_urlsafe(50)
    print(f"Создан новый SECRET_KEY: {new_secret_key}")

    # Записываем новый ключ в .env файл
    set_key(env_path, 'SECRET_KEY', new_secret_key)
    print(f"SECRET_KEY добавлен в {env_path}.")
else:
    print("SECRET_KEY уже существует в .env файле.")
