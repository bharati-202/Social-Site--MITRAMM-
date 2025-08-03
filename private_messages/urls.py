from django.urls import path
from . import views

app_name = 'private_messages'

urlpatterns = [
    path('', views.messages, name='messages'),
    path('<str:username>/', views.messages, name='messages'),
] 