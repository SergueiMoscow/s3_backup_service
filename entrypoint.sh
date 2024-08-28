#!/bin/bash

# Экспортируем переменные из .env файла
export $(grep -v '^#' .env | xargs)

# Выполняем миграции Alembic
alembic upgrade head

# Запускаем приложение
exec uvicorn api.app:app --host 0.0.0.0 --port ${PORT}