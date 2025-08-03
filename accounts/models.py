from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^[6-9]\d{9}$',
        message="Mobile number must be 10 digits long and start with 6-9"
    )
    mobile_number = models.CharField(
        max_length=10,
        validators=[phone_regex],
        help_text="Enter a valid 10-digit mobile number starting with 6-9"
    )
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(max_length=200, blank=True)
    following = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True
    )
    
    def __str__(self):
        return self.username 