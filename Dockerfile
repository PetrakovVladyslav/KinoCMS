# Используем официальный образ с Python 3.13 и uv
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей сначала (для кэширования слоя)
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости проекта
RUN uv sync --frozen --no-dev

# Копируем весь проект в контейнер
COPY . .

# Копируем .env для django-environ
COPY .env ./

# Задаём минимальные переменные окружения, чтобы Django мог собрать статику
ENV DJANGO_SETTINGS_MODULE=config.settings

# Собираем статические файлы Django
RUN uv run python manage.py collectstatic --noinput

# Открываем порт приложения
EXPOSE 8000

# Команда по умолчанию при запуске контейнера
CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
