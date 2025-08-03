from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('settings/', views.account_settings, name='account_settings'),
    path('search/', views.search_users, name='search_users'),
    path('login/', auth_views.LoginView.as_view(template_name='account/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Using allauth's logout view instead
    # path('logout/', auth_views.LogoutView.as_view(template_name='account/logout.html'), name='logout'),
] 