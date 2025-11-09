from django.urls import path

from . import views

app_name = "page"

urlpatterns = [
    # Список всех страниц
    path("admin-panel/pages/", views.admin_page_list_view, name="admin_page_list"),
    # Специальные страницы
    path("admin-panel/pages/main/", views.main_page_view, name="main_edit"),
    path("admin-panel/pages/contacts/", views.contacts_admin_edit_view, name="contacts"),
    # Системные и пользовательские страницы (редактируются по ID)
    path("admin-panel/pages/create/", views.page_create_view, name="page_create"),
    path("admin-panel/pages/<int:pk>/edit/", views.page_update_view, name="page_edit"),
    path("admin-panel/pages/<int:pk>/delete/", views.page_delete_view, name="page_delete"),
    # Админские списки новостей и акций
    path("admin-panel/news/", views.admin_news_list_view, name="admin_news_list"),
    path("admin-panel/sales/", views.admin_sales_list_view, name="admin_sales_list"),
    # Формы создания
    path("admin-panel/news/create/", views.news_view, name="news_create"),
    path("admin-panel/sales/create/", views.sales_view, name="sales_create"),
    # Редактирование и удаление
    path("admin-panel/news/<int:news_id>/edit/", views.news_update_view, name="news_edit"),
    path(
        "admin-panel/news/<int:news_id>/delete/",
        views.news_delete_view,
        name="news_delete",
    ),
    path(
        "admin-panel/sales/<int:sales_id>/edit/",
        views.sales_update_view,
        name="sales_edit",
    ),
    path(
        "admin-panel/sales/<int:sales_id>/delete/",
        views.sales_delete_view,
        name="sales_delete",
    ),
    # Публичные страницы
    path("", views.home_view, name="home"),
    path("afisha/", views.afisha_view, name="afisha"),
    path("soon/", views.soon_view, name="soon"),
    path("sales/", views.sale_news_list_view, name="sale_news_list"),
    path("sale/<int:item_id>/", views.sale_detail_view, name="sale_detail"),
    path("contacts/", views.contacts_view, name="contacts_public"),
    path("page/<slug:slug>/", views.page_detail_view, name="page_detail"),
]
