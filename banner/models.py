from django.db import models
from django.utils import timezone


class Banner(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='banners/')
    url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    @property
    def is_valid(self):
        now = timezone.now()
        if self.end_date:
            return self.is_active and self.start_date <= now <= self.end_date
        return self.is_active and self.start_date <= now 