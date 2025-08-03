from django.urls import path
from . import views

app_name = 'messages'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('send/<str:username>/', views.send_message, name='send_message'),
    path('conversation/<str:username>/', views.conversation, name='conversation'),
] 