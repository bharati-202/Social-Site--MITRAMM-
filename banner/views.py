from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q
from .models import Banner


def get_active_banners():
    now = timezone.now()
    return Banner.objects.filter(
        is_active=True,
        start_date__lte=now
    ).filter(
        Q(end_date__isnull=True) | 
        Q(end_date__gte=now)
    ).order_by('order', '-created_at')


def banner_list(request):
    banners = get_active_banners()
    return render(request, 'banner/banner_list.html', {
        'banners': banners
    }) 