FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

RUN apt-get update && apt-get install -y \
    postgresql-client \
    gettext \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Сначала только файлы зависимостей (для кэширования слоя)
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости
RUN uv sync --frozen --no-dev

COPY . .

RUN uv run python manage.py collectstatic --noinput


EXPOSE 8000