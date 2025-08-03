from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import DailyMetrics, UserActivity
from posts.models import Post, Comment
from friends.models import Friendship
from private_messages.models import Message
import re

User = get_user_model()

def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(lambda u: u.is_staff)
def analytics_dashboard(request):
    """View for the analytics dashboard."""
    # Get date range (last 30 days)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Get daily metrics for the date range
    daily_metrics = DailyMetrics.objects.filter(
        date__range=[start_date, end_date]
    ).order_by('date')
    
    # Calculate total counts
    total_posts = Post.objects.count()
    total_comments = Comment.objects.count()
    total_friendships = Friendship.objects.filter(status='accepted').count()
    total_messages = Message.objects.count()
    total_users = User.objects.count()
    
    # Calculate daily averages
    avg_active_users = daily_metrics.aggregate(avg=Avg('active_users'))['avg'] or 0
    avg_new_users = daily_metrics.aggregate(avg=Avg('new_users'))['avg'] or 0
    avg_posts = daily_metrics.aggregate(avg=Avg('posts'))['avg'] or 0
    avg_comments = daily_metrics.aggregate(avg=Avg('comments'))['avg'] or 0
    avg_likes = daily_metrics.aggregate(avg=Avg('likes'))['avg'] or 0
    avg_friendships = daily_metrics.aggregate(avg=Avg('friendships'))['avg'] or 0
    avg_messages = daily_metrics.aggregate(avg=Avg('messages'))['avg'] or 0
    
    # Get top active users
    top_users = User.objects.annotate(
        activity_count=Count('posts') + Count('comments') + Count('liked_posts')
    ).order_by('-activity_count')[:5]
    
    # Prepare data for charts
    dates = [metric.date.strftime('%Y-%m-%d') for metric in daily_metrics]
    active_users = [metric.active_users for metric in daily_metrics]
    new_users = [metric.new_users for metric in daily_metrics]
    posts = [metric.posts for metric in daily_metrics]
    comments = [metric.comments for metric in daily_metrics]
    likes = [metric.likes for metric in daily_metrics]
    friendships = [metric.friendships for metric in daily_metrics]
    messages = [metric.messages for metric in daily_metrics]
    
    context = {
        'daily_metrics': daily_metrics,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_friendships': total_friendships,
        'total_messages': total_messages,
        'total_users': total_users,
        'avg_active_users': round(avg_active_users, 1),
        'avg_new_users': round(avg_new_users, 1),
        'avg_posts': round(avg_posts, 1),
        'avg_comments': round(avg_comments, 1),
        'avg_likes': round(avg_likes, 1),
        'avg_friendships': round(avg_friendships, 1),
        'avg_messages': round(avg_messages, 1),
        'top_users': top_users,
        'date_range': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
        'chart_data': {
            'dates': dates,
            'active_users': active_users,
            'new_users': new_users,
            'posts': posts,
            'comments': comments,
            'likes': likes,
            'friendships': friendships,
            'messages': messages,
        }
    }
    return render(request, 'analytics/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def user_activity_report(request, username):
    # Get date range for the last 30 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Get user activity for the last 30 days
    user_activity = UserActivity.objects.filter(
        user__username=username,
        date__range=(start_date, end_date)
    ).order_by('date')
    
    # Calculate totals
    total_activity = {
        'posts': user_activity.aggregate(total=Sum('post_count'))['total'] or 0,
        'comments': user_activity.aggregate(total=Sum('comment_count'))['total'] or 0,
        'likes': user_activity.aggregate(total=Sum('like_count'))['total'] or 0,
        'messages': user_activity.aggregate(total=Sum('message_count'))['total'] or 0,
        'logins': user_activity.aggregate(total=Sum('login_count'))['total'] or 0,
    }
    
    context = {
        'user_activity': user_activity,
        'total_activity': total_activity,
        'username': username,
        'date_range': {
            'start': start_date,
            'end': end_date
        }
    }
    
    return render(request, 'analytics/user_activity.html', context)

@login_required
@user_passes_test(is_admin)
def post_management(request):
    # Get all posts ordered by creation date (newest first)
    posts = Post.objects.select_related('author').order_by('-created_at')
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    author_filter = request.GET.get('author', '')
    
    # Apply filters if provided
    if search_query:
        posts = posts.filter(content__icontains=search_query)
    if author_filter:
        posts = posts.filter(author__username__icontains=author_filter)
    
    context = {
        'posts': posts,
        'search_query': search_query,
        'author_filter': author_filter,
    }
    
    return render(request, 'analytics/post_management.html', context)

@login_required
@user_passes_test(is_admin)
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            post.content = content
            post.save()
            messages.success(request, 'Post updated successfully.')
            return redirect('analytics:post_management')
    
    context = {
        'post': post,
    }
    
    return render(request, 'analytics/edit_post.html', context)

@login_required
@user_passes_test(is_admin)
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully.')
        return redirect('analytics:post_management')
    
    context = {
        'post': post,
    }
    
    return render(request, 'analytics/delete_post.html', context)

def get_trending_topics():
    # Get posts from the last 7 days
    start_date = timezone.now() - timedelta(days=7)
    recent_posts = Post.objects.filter(created_at__gte=start_date)
    
    # Extract hashtags and count their occurrences
    hashtag_counts = {}
    for post in recent_posts:
        hashtags = re.findall(r'#(\w+)', post.content.lower())
        for tag in hashtags:
            hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
    
    # Sort hashtags by count and get top 10
    trending_topics = sorted(
        hashtag_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    return trending_topics 