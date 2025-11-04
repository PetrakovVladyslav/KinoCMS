
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
