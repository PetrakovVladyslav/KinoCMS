from django.urls import path
from . import views

app_name = 'page'

urlpatterns = [
    # Список всех страниц
    path('admin-panel/pages/', views.admin_list_view, name='admin_list'),
    
    # Системные страницы
    path('admin-panel/pages/main/', views.main_page_view, name='main_edit'),
    path('admin-panel/pages/about-cinema/', views.about_cinema_view, name='about_cinema'),
    path('admin-panel/pages/coffee-bar/', views.coffee_bar_view, name='coffee_bar'),
    path('admin-panel/pages/vip-hall/', views.vip_hall_view, name='vip_hall'),
    path('admin-panel/pages/advertising/', views.advertising_view, name='advertising'),
    path('admin-panel/pages/children-room/', views.children_room_view, name='children_room'),
    path('admin-panel/pages/contacts/', views.contacts_view, name='contacts'),
    
    # Пользовательские страницы
    path('admin-panel/pages/create/', views.page_create_view, name='page_create'),
    path('admin-panel/pages/<int:pk>/edit/', views.page_update_view, name='page_edit'),
    path('admin-panel/pages/<int:pk>/delete/', views.page_delete_view, name='page_delete'),

    path('', views.home_view, name='home'),
    path('afisha/', views.afisha_view, name='afisha'),
    path('soon/', views.soon_view, name='soon'),
]
