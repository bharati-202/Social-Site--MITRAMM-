from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from .models import Post
from .forms import PostForm

def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def post_list(request):
    search_query = request.GET.get('search', '')
    author_filter = request.GET.get('author', '')
    
    posts = Post.objects.all().order_by('-created_at')
    
    if search_query:
        posts = posts.filter(content__icontains=search_query)
    
    if author_filter:
        posts = posts.filter(author__username__icontains=author_filter)
    
    context = {
        'posts': posts,
        'search_query': search_query,
        'author_filter': author_filter
    }
    return render(request, 'posts/post_management.html', context)

@login_required
@user_passes_test(is_staff)
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully.')
            return redirect('posts:post_list')
    else:
        form = PostForm(instance=post)
    
    context = {
        'form': form,
        'post': post
    }
    return render(request, 'posts/post_form.html', context)

@login_required
@user_passes_test(is_staff)
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully.')
        return redirect('posts:post_list')
    
    context = {
        'post': post
    }
    return render(request, 'posts/post_confirm_delete.html', context) 