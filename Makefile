
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

.PHONY: format lint check fix commit-fix push-all help

help:
	@echo "Available commands:"
	@echo "  make format      - Format code with ruff"
	@echo "  make lint        - Check code with ruff (no fixes)"
	@echo "  make check       - Run pre-commit checks (no fixes)"
	@echo "  make fix         - Auto-fix all issues"
	@echo "  make commit-fix  - Fix + auto-commit"
	@echo "  make push-all    - Fix + commit + push"

format:
	@echo "🎨 Formatting code..."
	@uv run ruff format .

lint:
	@echo "🔍 Linting code..."
	@uv run ruff check .

check:
	@echo "✅ Running pre-commit checks..."
	@uv run pre-commit run --all-files

fix:
	@echo "🔧 Auto-fixing issues..."
	@uv run ruff check --fix .
	@uv run ruff format .

commit-fix: fix
	@echo "📝 Checking for changes..."
	@git add -A
	@if git diff --cached --quiet; then \
		echo "✨ No changes to commit"; \
	else \
		echo "Files changed: $$(git diff --cached --name-only | wc -l)"; \
		git commit -m "style: apply ruff fixes" --quiet; \
		echo "✅ Changes committed"; \
	fi

push-all: commit-fix
	@echo "🚀 Pushing to remote..."
	@git push --quiet
	@echo "✅ Done!"