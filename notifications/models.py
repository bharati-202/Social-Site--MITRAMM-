from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Notification(models.Model):
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        null=True,
        blank=True
    )
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    notification_type = models.CharField(max_length=50)
    link = models.URLField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        app_label = 'notifications'

    def __str__(self):
        return f'Notification for {self.recipient.username}' 