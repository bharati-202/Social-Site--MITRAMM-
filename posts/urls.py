from django.urls import path
from . import views
from .post_management import post_list, edit_post, delete_post

app_name = 'posts'

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.post_create, name='create_post'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/edit/', views.post_edit, name='edit_post'),
    path('post/<int:pk>/delete/', views.post_delete, name='delete_post'),
    path('post/<int:pk>/like/', views.post_like, name='like_post'),
    path('post/<int:pk>/comment/', views.comment_create, name='add_comment'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    path('topic/<str:topic>/', views.topic_posts, name='topic_posts'),
    # Post management URLs
    path('management/', post_list, name='post_list'),
    path('management/post/<int:pk>/edit/', edit_post, name='edit_post_management'),
    path('management/post/<int:pk>/delete/', delete_post, name='delete_post_management'),
] 