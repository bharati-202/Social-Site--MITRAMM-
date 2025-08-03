from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Message

User = get_user_model()

@login_required
def inbox(request):
    messages = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).order_by('-created_at')
    
    # Mark messages as read
    Message.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'messages/inbox.html', {'messages': messages})

@login_required
def send_message(request, username):
    recipient = get_object_or_404(User, username=username)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                sender=request.user,
                recipient=recipient,
                content=content
            )
            return redirect('messages:inbox')
    
    return render(request, 'messages/send_message.html', {'recipient': recipient})

@login_required
def conversation(request, username):
    other_user = get_object_or_404(User, username=username)
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(recipient=other_user)) |
        (Q(sender=other_user) & Q(recipient=request.user))
    ).order_by('created_at')
    
    # Mark messages as read
    Message.objects.filter(recipient=request.user, sender=other_user, is_read=False).update(is_read=True)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                sender=request.user,
                recipient=other_user,
                content=content
            )
            return redirect('messages:conversation', username=username)
    
    return render(request, 'messages/conversation.html', {
        'messages': messages,
        'other_user': other_user
    }) 