from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import PageMain, PageElse, PageContacts

User = get_user_model()

class PageViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Create staff user for testing
        self.staff_user = User.objects.create_user(
            username='staff_test',
            email='staff@test.com',
            password='testpass123',
            is_staff=True
        )
        
    def test_admin_list_view_requires_staff(self):
        """Test that admin_list_view requires staff permission"""
        response = self.client.get(reverse('page:admin_list'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        
    def test_admin_list_view_with_staff(self):
        """Test that admin_list_view works for staff users"""
        self.client.login(username='staff_test', password='testpass123')
        response = self.client.get(reverse('page:admin_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Управление страницами')
        
    def test_main_page_view_get(self):
        """Test main page view GET request"""
        self.client.login(username='staff_test', password='testpass123')
        response = self.client.get(reverse('page:main_edit'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Редактировать главную страницу')
        
    def test_main_page_view_post(self):
        """Test main page view POST request"""
        self.client.login(username='staff_test', password='testpass123')
        data = {
            'phone_number1': '+38 (099) 123-45-67',
            'phone_number2': '+38 (099) 765-43-21',
            'seo_text': 'Test SEO text',
            'seo_text_ru': 'Тест SEO текст',
            'seo_text_uk': 'Тест SEO текст',
            'status': True,
        }
        response = self.client.post(reverse('page:main_edit'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Check if data was saved
        main_page = PageMain.objects.first()
        self.assertIsNotNone(main_page)
        self.assertEqual(main_page.phone_number1, '+38 (099) 123-45-67')
        
    def test_coffee_bar_view(self):
        """Test coffee bar view"""
        self.client.login(username='staff_test', password='testpass123')
        response = self.client.get(reverse('page:coffee_bar'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Кофе-бар')
        
    def test_page_create_view(self):
        """Test page creation"""
        self.client.login(username='staff_test', password='testpass123')
        response = self.client.get(reverse('page:page_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Создать новую страницу')
        
        # Test POST
        data = {
            'name': 'Тестовая страница',
            'name_ru': 'Тестовая страница',
            'name_uk': 'Тестова сторінка',
            'description': 'Описание тестовой страницы',
            'description_ru': 'Описание тестовой страницы',
            'description_uk': 'Опис тестової сторінки',
            'status': True,
        }
        response = self.client.post(reverse('page:page_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Check if page was created
        page = PageElse.objects.filter(name='Тестовая страница').first()
        self.assertIsNotNone(page)
        self.assertTrue(page.can_delete)  # New pages should be deleteable
        
    def test_contacts_view(self):
        """Test contacts view"""
        self.client.login(username='staff_test', password='testpass123')
        response = self.client.get(reverse('page:contacts'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Редактировать контакты')
