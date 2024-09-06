# Система резервного копирования на S3 сервер в объектное хранилище
## Условия для работы системы:
- Акканут на S3 сервере (проверено с Selectel (https://selectel.ru))
- Наличие контейнеров в объектном хранилище.
- Наличие сервисного пользователя.
- Прописанные переменные в .env файле
- Настроены конфигурации в config.json

.env:
- PORT - на каком порту работает сервер
- DB_DSN - Файл БД sqlite
- API_KEY - ключ для доступа к end-поинтам, который передаётся в header запроса, ключ api_key
- SECRET_KEY - ключ шифрования для зашифрованной записи в БД критичных данных (access_key, secret_key для доступа к хранилищу)

config.json:
- bucket-name - имя существующего на сервере bucket. Может быть как приватным, так и публичным, как стандартным, так и холодным.
- name - имя хранилища или имя контейнера (bucket) - для доступа. Все endpoints работают с этими именами.

## Установка:
`docker compose build`
`docker compose up -d`

После установки внести изменения в .env и config.json

### Конфигурация тестов и test-config.json:
access_key, secret_key, url не используется. Тест мокает обращение к серверу.
