FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

RUN apt-get update && apt-get install -y \
    postgresql-client \
    gettext \
    && rm -rf /var/lib/apt/lists/*



WORKDIR /app

# Включаем кэширование uv
ENV UV_CACHE_DIR=/root/.cache/uv

# Сначала только файлы зависимостей (для кэширования слоя)
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Устанавливаем зависимости через uv
RUN uv pip install
# Копируем весь проект
COPY . .

RUN uv run python manage.py collectstatic --noinput


EXPOSE 8000