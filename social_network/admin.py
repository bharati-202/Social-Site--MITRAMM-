from django.contrib import admin
from django.contrib.admin import AdminSite
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from accounts.models import CustomUser
from posts.models import Post, Comment
from friends.models import Friendship, FriendRequest

class SocialNetworkAdminSite(AdminSite):
    site_header = 'Social Network Administration'
    site_title = 'Social Network Admin'
    index_title = 'Social Network Dashboard'

admin_site = SocialNetworkAdminSite(name='admin')

class DashboardAdmin(admin.ModelAdmin):
    change_list_template = 'admin/dashboard.html'
    
    def changelist_view(self, request, extra_context=None):
        # Get date ranges
        today = timezone.now().date()
        last_week = today - timedelta(days=7)
        last_month = today - timedelta(days=30)
        
        # User statistics
        total_users = CustomUser.objects.count()
        new_users_today = CustomUser.objects.filter(date_joined__date=today).count()
        new_users_week = CustomUser.objects.filter(date_joined__date__gte=last_week).count()
        new_users_month = CustomUser.objects.filter(date_joined__date__gte=last_month).count()
        
        # Post statistics
        total_posts = Post.objects.count()
        new_posts_today = Post.objects.filter(created_at__date=today).count()
        new_posts_week = Post.objects.filter(created_at__date__gte=last_week).count()
        new_posts_month = Post.objects.filter(created_at__date__gte=last_month).count()
        
        # Comment statistics
        total_comments = Comment.objects.count()
        new_comments_today = Comment.objects.filter(created_at__date=today).count()
        new_comments_week = Comment.objects.filter(created_at__date__gte=last_week).count()
        new_comments_month = Comment.objects.filter(created_at__date__gte=last_month).count()
        
        # Friendship statistics
        total_friendships = Friendship.objects.count()
        new_friendships_today = Friendship.objects.filter(created_at__date=today).count()
        new_friendships_week = Friendship.objects.filter(created_at__date__gte=last_week).count()
        new_friendships_month = Friendship.objects.filter(created_at__date__gte=last_month).count()
        
        # Friend request statistics
        total_requests = FriendRequest.objects.count()
        pending_requests = FriendRequest.objects.filter(status='pending').count()
        accepted_requests = FriendRequest.objects.filter(status='accepted').count()
        rejected_requests = FriendRequest.objects.filter(status='rejected').count()
        
        # Most active users
        most_active_users = CustomUser.objects.annotate(
            post_count=Count('posts'),
            comment_count=Count('comments'),
            like_count=Count('likes')
        ).order_by('-post_count', '-comment_count', '-like_count')[:5]
        
        # Most liked posts
        most_liked_posts = Post.objects.annotate(
            like_count=Count('likes')
        ).order_by('-like_count')[:5]
        
        # Extra context for the template
        extra_context = extra_context or {}
        extra_context.update({
            'total_users': total_users,
            'new_users_today': new_users_today,
            'new_users_week': new_users_week,
            'new_users_month': new_users_month,
            'total_posts': total_posts,
            'new_posts_today': new_posts_today,
            'new_posts_week': new_posts_week,
            'new_posts_month': new_posts_month,
            'total_comments': total_comments,
            'new_comments_today': new_comments_today,
            'new_comments_week': new_comments_week,
            'new_comments_month': new_comments_month,
            'total_friendships': total_friendships,
            'new_friendships_today': new_friendships_today,
            'new_friendships_week': new_friendships_week,
            'new_friendships_month': new_friendships_month,
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'accepted_requests': accepted_requests,
            'rejected_requests': rejected_requests,
            'most_active_users': most_active_users,
            'most_liked_posts': most_liked_posts,
        })
        
        return super().changelist_view(request, extra_context=extra_context)

# Register the dashboard
admin_site.register(CustomUser, DashboardAdmin) 