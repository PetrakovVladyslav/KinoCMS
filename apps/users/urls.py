from django.urls import path
from . import views


app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('edit-account-details/', views.update_account_details, name='update_account_details'),
    path('logout/', views.logout_view, name='logout')
]