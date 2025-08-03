from django.urls import path
from . import views

app_name = 'friends'

urlpatterns = [
    path('', views.friend_list, name='friend_list'),
    path('send/<str:username>/', views.send_friend_request, name='send_request'),
    path('accept/<int:request_id>/', views.accept_request, name='accept_request'),
    path('reject/<int:request_id>/', views.reject_request, name='reject_request'),
    path('cancel/<int:request_id>/', views.cancel_request, name='cancel_request'),
    path('remove/<int:friendship_id>/', views.remove_friend, name='remove_friend'),
    path('message/<str:username>/', views.send_message, name='send_message'),
    path('messages/<str:username>/', views.view_messages, name='messages'),
] 