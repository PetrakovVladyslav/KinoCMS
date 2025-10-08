from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Создает тестовых пользователей для админ-панели'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Количество пользователей для создания (по умолчанию: 20)'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        
        # Данные для генерации тестовых пользователей
        first_names = [
            'Александр', 'Дмитрий', 'Максим', 'Сергей', 'Андрей', 
            'Алексей', 'Артем', 'Илья', 'Кирилл', 'Михаил',
            'Анна', 'Елена', 'Ольга', 'Татьяна', 'Ирина',
            'Мария', 'Наталья', 'Юлия', 'Светлана', 'Екатерина'
        ]
        
        last_names = [
            'Иванов', 'Петров', 'Сидоров', 'Смирнов', 'Кузнецов',
            'Попов', 'Васильев', 'Соколов', 'Михайлов', 'Новиков',
            'Федоров', 'Морозов', 'Волков', 'Алексеев', 'Лебедев',
            'Семенов', 'Егоров', 'Павлов', 'Козлов', 'Степанов'
        ]
        
        cities = ['kyiv', 'dnipro', 'lviv', 'odessa', 'kharkiv']
        genders = ['male', 'female']
        languages = ['ru', 'uk']
        
        created_users = 0
        
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            # Генерация email
            email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@test.com"
            
            # Проверяем, что email уникальный
            if User.objects.filter(email=email).exists():
                email = f"user{random.randint(1000, 9999)}@test.com"
            
            # Генерация телефона
            phone = f"0{random.randint(90, 99)}{random.randint(1000000, 9999999)}"
            
            # Генерация даты рождения
            start_date = datetime(1970, 1, 1)
            end_date = datetime(2005, 12, 31)
            random_date = start_date + timedelta(
                seconds=random.randint(0, int((end_date - start_date).total_seconds()))
            )
            
            # Генерация адреса
            streets = ['ул. Крещатик', 'ул. Грушевского', 'пр. Независимости', 'ул. Саксаганского', 'пер. Шевченко']
            address = f"{random.choice(streets)}, {random.randint(1, 200)}"
            
            # Генерация номера карты
            card_number = f"{random.randint(1000, 9999)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}"
            
            try:
                user = User.objects.create_user(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password='testpass123',
                    phone_number=phone,
                    date_of_birth=random_date.date(),
                    city=random.choice(cities),
                    gender=random.choice(genders),
                    language=random.choice(languages),
                    address=address,
                    card_number=card_number,
                )
                
                # Случайно устанавливаем дату регистрации в прошлом
                days_ago = random.randint(1, 365)
                user.date_joined = timezone.now() - timedelta(days=days_ago)
                user.save()
                
                created_users += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f'Создан пользователь: {user.get_full_name()} ({user.email})')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка при создании пользователя {email}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Успешно создано {created_users} из {count} пользователей')
        )