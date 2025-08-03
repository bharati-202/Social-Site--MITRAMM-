from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Sum, F, Q
from django.db.models.functions import TruncDate
from posts.models import Post, Comment
from friends.models import Friendship
from private_messages.models import Message
from accounts.models import CustomUser

User = get_user_model()

class DailyMetrics(models.Model):
    date = models.DateField(unique=True)
    active_users = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    posts = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    friendships = models.IntegerField(default=0)
    messages = models.IntegerField(default=0)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Daily Metrics'
        verbose_name_plural = 'Daily Metrics'
        app_label = 'analytics'

    def __str__(self):
        return f"Metrics for {self.date}"

    @classmethod
    def update_daily_metrics(cls):
        today = timezone.now().date()
        metrics, created = cls.objects.get_or_create(date=today)
        
        # Update active users (users who performed any action today)
        active_users_query = CustomUser.objects.filter(
            Q(posts__created_at__date=today) |
            Q(comments__created_at__date=today) |
            Q(liked_posts__created_at__date=today) |
            Q(friendships1__created_at__date=today) |
            Q(friendships2__created_at__date=today) |
            Q(friend_messages_sent__created_at__date=today) |
            Q(friend_messages_received__created_at__date=today)
        ).distinct()
        metrics.active_users = active_users_query.count()
        
        # Update new users
        metrics.new_users = CustomUser.objects.filter(
            date_joined__date=today
        ).count()
        
        # Update posts
        metrics.posts = Post.objects.filter(
            created_at__date=today
        ).count()
        
        # Update comments
        metrics.comments = Comment.objects.filter(
            created_at__date=today
        ).count()
        
        # Update likes (count likes on posts created today)
        metrics.likes = Post.objects.filter(
            created_at__date=today
        ).aggregate(total_likes=Count('likes'))['total_likes'] or 0
        
        # Update friendships
        metrics.friendships = Friendship.objects.filter(
            created_at__date=today,
            status='accepted'
        ).count()
        
        # Update messages
        metrics.messages = Message.objects.filter(
            created_at__date=today
        ).count()
        
        metrics.save()
        return metrics

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    date = models.DateField()
    post_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    message_count = models.IntegerField(default=0)
    login_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']
        verbose_name_plural = 'User Activities'
        app_label = 'analytics'

    def __str__(self):
        return f"{self.user.username}'s activity on {self.date}"

    @classmethod
    def update_user_activity(cls, user):
        """Update or create user activity metrics for the current date"""
        today = timezone.now().date()
        
        # Get metrics from other models
        from posts.models import Post, Comment
        from private_messages.models import Message
        
        # Calculate user's activity for today
        post_count = Post.objects.filter(author=user, created_at__date=today).count()
        comment_count = Comment.objects.filter(author=user, created_at__date=today).count()
        like_count = Post.objects.filter(likes=user, created_at__date=today).count()
        message_count = Message.objects.filter(
            models.Q(sender=user) | models.Q(recipient=user),
            created_at__date=today
        ).count()
        
        # Update or create the user activity
        activity, created = cls.objects.update_or_create(
            user=user,
            date=today,
            defaults={
                'post_count': post_count,
                'comment_count': comment_count,
                'like_count': like_count,
                'message_count': message_count,
                'login_count': F('login_count') + 1
            }
        )
        
        return activity 