from django.urls import path
from . import views

app_name = 'page'

urlpatterns = [
    # Список всех страниц
    path('admin-panel/pages/', views.PageListView.as_view(), name='admin_list'),
    
    # Создание страниц (только PageElse)
    path('admin-panel/pages/else/add/', views.PageElseCreateView.as_view(), name='else_create'),
    
    # Редактирование страниц
    path('admin-panel/pages/main/<int:pk>/edit/', views.PageMainUpdateView.as_view(), name='main_edit'),
    path('admin-panel/pages/else/<int:pk>/edit/', views.PageElseUpdateView.as_view(), name='else_edit'),
    path('admin-panel/pages/contacts/<int:pk>/edit/', views.PageContactsUpdateView.as_view(), name='contacts_edit'),
    
    # Удаление страниц (только PageElse)
    path('admin-panel/pages/else/<int:pk>/delete/', views.PageElseDeleteView.as_view(), name='else_delete'),
]
