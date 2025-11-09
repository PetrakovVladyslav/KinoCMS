from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/users/", views.admin_users_list, name="admin_users_list"),
    path(
        "admin-panel/users/<int:user_id>/edit/",
        views.admin_user_edit,
        name="admin_user_edit",
    ),
    path(
        "admin-panel/users/<int:user_id>/delete/",
        views.admin_user_delete,
        name="admin_user_delete",
    ),
    path("search/", views.search_movies, name="search_movies"),
    # Рассылки
    path("admin-panel/mailing/", views.admin_mailing, name="admin_mailing"),
    path("admin-panel/mailing/users/", views.admin_user_select, name="admin_user_select"),
    path("admin-panel/mailing/upload/", views.upload_mailing_file, name="upload_mailing_file"),
    path(
        "admin-panel/mailing/file/<int:file_id>/delete/",
        views.delete_mailing_file,
        name="delete_mailing_file",
    ),
    path("admin-panel/mailing/start/", views.start_mailing, name="start_mailing"),
    path(
        "admin-panel/mailing/status/<int:mailing_id>/",
        views.mailing_status,
        name="mailing_status",
    ),
]
