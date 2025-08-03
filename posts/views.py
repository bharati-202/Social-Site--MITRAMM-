from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Post, Comment, Topic
from .forms import PostForm, CommentForm
from django.contrib.auth import logout
from django.db.models import Q, Count
from accounts.models import CustomUser
from friends.models import Friendship


def home(request):
    if request.user.is_authenticated:
        # Get posts from users the current user is following
        following = Friendship.objects.filter(
            user1=request.user,
            status='accepted'
        ).values_list('user2_id', flat=True)
        
        posts = Post.objects.filter(
            author_id__in=following
        ).select_related('author').prefetch_related(
            'likes', 'comments'
        ).order_by('-created_at')
        
        # Get suggested users (users not being followed)
        suggested_users = CustomUser.objects.exclude(
            id__in=following
        ).exclude(id=request.user.id).order_by('?')[:5]
    else:
        posts = Post.objects.all().select_related(
            'author'
        ).prefetch_related('likes', 'comments').order_by('-created_at')
        suggested_users = None
    
    # Get trending topics
    trending_topics = Topic.objects.annotate(
        post_count=Count('posts')
    ).order_by('-post_count')[:10]
    
    context = {
        'posts': posts,
        'suggested_users': suggested_users,
        'trending_topics': trending_topics,
    }
    return render(request, 'posts/home.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Your post has been created!')
            return redirect('accounts:home')
    else:
        form = PostForm()
    return render(request, 'accounts/post_form.html', {'form': form})


@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related('author').prefetch_related('likes', 'comments'), pk=pk)
    comments = post.comments.all().select_related('author')
    comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your post has been updated!')
            return redirect('accounts:home')
    else:
        form = PostForm(instance=post)
    return render(request, 'accounts/post_form.html', {'form': form, 'post': post})


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Your post has been deleted!')
        return redirect('accounts:home')
    return render(request, 'accounts/post_confirm_delete.html', {'post': post})


@login_required
@require_POST
def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes.count()
    })


@login_required
@require_POST
def comment_create(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        messages.success(request, 'Your comment has been added!')
    return redirect('posts:post_detail', pk=post.pk)


@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    post_pk = comment.post.pk
    comment.delete()
    messages.success(request, 'Your comment has been deleted!')
    return redirect('posts:post_detail', pk=post_pk)


def logout_view(request):
    logout(request)
    return redirect('accounts:home')


@login_required
def topic_posts(request, topic):
    """View to display posts with a specific hashtag."""
    posts = Post.objects.filter(
        content__icontains=f'#{topic}'
    ).select_related('author').prefetch_related('likes', 'comments').order_by('-created_at')
    
    context = {
        'posts': posts,
        'topic': topic,
    }
    return render(request, 'posts/topic_posts.html', context)