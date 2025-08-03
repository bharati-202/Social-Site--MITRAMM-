from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .models import Post, Comment, Topic
from accounts.models import CustomUser
from friends.models import Friendship
from datetime import datetime, timedelta
import re

def home(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    # Get posts from users the current user is following
    following = Friendship.objects.filter(
        user1=request.user,
        status='accepted'
    ).values_list('user2_id', flat=True)
    
    # Get posts from followed users and the current user
    posts = Post.objects.filter(
        Q(author_id__in=following) | Q(author=request.user)
    ).select_related('author').order_by('-created_at')
    
    # Filter out posts with invalid authors
    posts = [post for post in posts if post.author and post.author.username]
    
    # Get trending topics (topics with most posts in the last 7 days)
    trending_topics = Topic.objects.filter(
        post__created_at__gte=datetime.now() - timedelta(days=7)
    ).annotate(
        post_count=Count('post')
    ).order_by('-post_count')[:5]
    
    # Get suggested users (users not being followed)
    following_ids = list(following) + [request.user.id]
    suggested_users = CustomUser.objects.exclude(
        id__in=following_ids
    ).exclude(
        id=request.user.id
    ).order_by('?')[:5]
    
    context = {
        'posts': posts,
        'trending_topics': trending_topics,
        'suggested_users': suggested_users,
    }
    
    return render(request, 'core/home.html', context)

@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        video = request.FILES.get('video')
        
        if content or image or video:
            post = Post.objects.create(
                author=request.user,
                content=content,
                image=image,
                video=video
            )
            
            # Extract and create topics from content
            if content:
                words = content.split()
                for word in words:
                    if word.startswith('#'):
                        topic_name = word[1:].lower()
                        topic, created = Topic.objects.get_or_create(name=topic_name)
                        post.topics.add(topic)
            
            messages.success(request, 'Post created successfully!')
            return redirect('core:home')
        else:
            messages.error(request, 'Post cannot be empty!')
    
    return redirect('core:home')

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        video = request.FILES.get('video')
        
        if content or image or video:
            post.content = content
            if image:
                post.image = image
            if video:
                post.video = video
            post.save()
            
            # Update topics
            post.topics.clear()
            if content:
                words = content.split()
                for word in words:
                    if word.startswith('#'):
                        topic_name = word[1:].lower()
                        topic, created = Topic.objects.get_or_create(name=topic_name)
                        post.topics.add(topic)
            
            messages.success(request, 'Post updated successfully!')
            return redirect('core:post_detail', post_id=post.id)
        else:
            messages.error(request, 'Post cannot be empty!')
    
    return render(request, 'core/edit_post.html', {'post': post})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.delete()
    messages.success(request, 'Post deleted successfully!')
    return redirect('core:home')

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('core:home')

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).order_by('-created_at')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
            return redirect('core:post_detail', post_id=post.id)
    
    return render(request, 'core/post_detail.html', {
        'post': post,
        'comments': comments
    })

@login_required
def topic_posts(request, topic_name):
    topic = get_object_or_404(Topic, name=topic_name)
    posts = Post.objects.filter(topics=topic).order_by('-created_at')
    return render(request, 'core/topic_posts.html', {
        'topic': topic,
        'posts': posts
    })

@login_required
def search(request):
    query = request.GET.get('q', '')
    if query:
        # Search in posts
        posts = Post.objects.filter(
            Q(content__icontains=query) |
            Q(author__username__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query)
        ).distinct()
        
        # Search in users
        users = CustomUser.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id)
        
        # Search in topics
        topics = Topic.objects.filter(name__icontains=query)
        
        return render(request, 'core/search_results.html', {
            'query': query,
            'posts': posts,
            'users': users,
            'topics': topics
        })
    
    return render(request, 'core/search.html') 