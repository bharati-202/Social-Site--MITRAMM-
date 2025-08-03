from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from .forms import UserProfileForm
from posts.models import Post
from friends.models import Friendship
from django.contrib.auth import logout
from django.core.files import File
import os
from django.conf import settings


User = get_user_model()


@login_required
def home(request):
    """Home page view that shows recent posts from friends."""
    # Get all posts
    posts = Post.objects.select_related('author').prefetch_related('likes', 'comments').all()
    
    # Create or get sample suggested users
    sample_users_data = [
        {
            'username': 'tech_enthusiast',
            'first_name': 'Alex',
            'last_name': 'Johnson',
            'email': 'alex@example.com',
            'bio': 'Tech lover | Developer | Coffee addict'
        },
        {
            'username': 'travel_lover',
            'first_name': 'Sarah',
            'last_name': 'Williams',
            'email': 'sarah@example.com',
            'bio': 'Wanderlust | Photographer | Adventure seeker'
        },
        {
            'username': 'foodie_chef',
            'first_name': 'Michael',
            'last_name': 'Chen',
            'email': 'michael@example.com',
            'bio': 'Professional Chef | Food Blogger | Recipe Creator'
        },
        {
            'username': 'fitness_guru',
            'first_name': 'Emma',
            'last_name': 'Davis',
            'email': 'emma@example.com',
            'bio': 'Fitness Trainer | Nutritionist | Wellness Coach'
        },
        {
            'username': 'art_creator',
            'first_name': 'David',
            'last_name': 'Park',
            'email': 'david@example.com',
            'bio': 'Digital Artist | Illustrator | Creative Director'
        }
    ]
    
    # Create or get users
    suggested_users = []
    for user_data in sample_users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'email': user_data['email'],
                'bio': user_data['bio'],
                'is_active': True
            }
        )
        if created:
            # Set a default password for new users
            user.set_password('samplepassword123')
            user.save()
        suggested_users.append(user)
    
    context = {
        'posts': posts,
        'suggested_users': suggested_users
    }
    return render(request, 'accounts/home.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).select_related('author').prefetch_related('likes', 'comments')
    
    # Check if the current user is friends with the profile user
    is_friend = False
    if request.user.is_authenticated:
        is_friend = Friendship.objects.filter(
            Q(user1=request.user, user2=user) |
            Q(user1=user, user2=request.user)
        ).exists()
    
    context = {
        'profile_user': user,
        'posts': posts,
        'is_friend': is_friend,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def account_settings(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/settings.html', {'form': form})


@login_required
def search_users(request):
    query = request.GET.get('q', '')
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id)
    else:
        users = []
    
    return render(request, 'accounts/search.html', {
        'users': users,
        'query': query
    }) 
    
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out!')
    return redirect('accounts:home')