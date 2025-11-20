MANAGE=python manage.py
CELERY=celery -A config

run-dev:
	$(MANAGE) migrate --noinput
	$(MANAGE) collectstatic --noinput
	$(MANAGE) init_project --days 7
	gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3

run-celery:
	$(CELERY) worker -l info






run:
	python manage.py runserver

pages:  #
	python manage.py create_system_pages

sessions:
	python manage.py generate_sessions

migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

dev: pages sessions run

.PHONY: fix check ship quick help

help:
	@echo "Available commands:"
	@echo "  make fix    - Just fix and format (no commit)"
	@echo "  make check  - Check code without changes"
	@echo "  make ship   - Full workflow: fix → commit (prompt) → push"
	@echo "  make quick  - Quick: fix → commit 'style: fixes' → push"

# Быстрая проверка кода
check:
	@echo "🔍 Checking code..."
	@uv run ruff check .

# Только фиксы без коммита
fix:
	@echo "🔧 Fixing and formatting..."
	@uv run ruff check --fix .
	@uv run ruff format .
	@echo "✅ Done"

# Полный workflow с запросом сообщения и подтверждением push
ship:
	@echo "🔍 Checking code..."
	@uv run ruff check . || true
	@echo ""
	@echo "🔧 Fixing issues..."
	@uv run ruff check --fix .
	@echo ""
	@echo "🎨 Formatting code..."
	@uv run ruff format .
	@echo ""
	@git add -A
	@if git diff --cached --quiet; then \
		echo "✨ No changes to commit"; \
	else \
		echo "📊 Changed files:"; \
		git diff --cached --name-only | sed 's/^/  • /'; \
		echo ""; \
		read -p "💬 Commit message: " msg; \
		while [ -z "$$msg" ]; do \
			echo "❌ Cannot be empty!"; \
			read -p "💬 Commit message: " msg; \
		done; \
		git commit -m "$$msg" --quiet; \
		echo "✅ Committed: $$msg"; \
		echo ""; \
		read -p "🚀 Push to remote? [Y/n] " yn; \
		case "$$yn" in \
			[Nn]* ) echo "⏸️  Push skipped";; \
			* ) git push && echo "✅ Pushed!" || echo "❌ Push failed!";; \
		esac; \
	fi

# Быстрый автоматический workflow без запросов
quick:
	@echo "🔧 Applying fixes..."
	@uv run ruff check --fix . > /dev/null 2>&1 || true
	@uv run ruff format . > /dev/null 2>&1
	@git add -A
	@if git diff --cached --quiet; then \
		echo "✨ No changes to commit"; \
	else \
		echo "📊 Committing changes:"; \
		git diff --cached --name-only | sed 's/^/  • /'; \
		git commit -m "style: apply ruff fixes" --quiet; \
		echo "🚀 Pushing to remote..."; \
		git push && echo "✅ Done!" || echo "❌ Push failed!"; \
	fi



