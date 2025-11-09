FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Устанавливаем uv
RUN uv pip install --upgrade pip && pip install uv

# Копируем pyproject.toml (и poetry.lock, если есть)
COPY pyproject.toml /app/
COPY uv.lock* /app/  # если есть lock-файл
COPY . /app/

# Устанавливаем зависимости через uv
RUN uv pip install
# Копируем весь проект
COPY . /app/

# Команда по умолчанию для запуска Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]