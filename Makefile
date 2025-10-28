
run:
	python manage.py runserver

pages:  #
	python manage.py create_system_pages

migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

dev: pages run