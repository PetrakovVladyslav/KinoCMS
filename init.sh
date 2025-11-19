echo "Ожидание базы данных..."
sleep 10

echo "Применение миграций..."
python manage.py migrate

echo "Создание суперпользователя..."
python manage.py create_superuser

echo "Создание сессий и расписаний..."
python manage.py generate_sessions
python manage.py create_system_pages

echo "Инициализация завершена!"