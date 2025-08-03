from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q, Max, Count
from .models import Message

User = get_user_model()

@login_required
def messages(request, username=None):
    # Get all conversations for the current user
    conversations = []
    sent_messages = Message.objects.filter(sender=request.user).values('recipient').annotate(
        last_message=Max('created_at')
    )
    received_messages = Message.objects.filter(recipient=request.user).values('sender').annotate(
        last_message=Max('created_at')
    )
    
    # Combine and process conversations
    for msg in sent_messages:
        other_user = User.objects.get(id=msg['recipient'])
        last_message = Message.objects.filter(
            Q(sender=request.user, recipient=other_user) |
            Q(sender=other_user, recipient=request.user)
        ).latest('created_at')
        
        unread_count = Message.objects.filter(
            sender=other_user,
            recipient=request.user,
            is_read=False
        ).count()
        
        conversations.append({
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count
        })
    
    for msg in received_messages:
        other_user = User.objects.get(id=msg['sender'])
        if not any(c['other_user'].id == other_user.id for c in conversations):
            last_message = Message.objects.filter(
                Q(sender=request.user, recipient=other_user) |
                Q(sender=other_user, recipient=request.user)
            ).latest('created_at')
            
            unread_count = Message.objects.filter(
                sender=other_user,
                recipient=request.user,
                is_read=False
            ).count()
            
            conversations.append({
                'other_user': other_user,
                'last_message': last_message,
                'unread_count': unread_count
            })
    
    # Sort conversations by last message time
    conversations.sort(key=lambda x: x['last_message'].created_at, reverse=True)
    
    # Get active conversation if username is provided
    active_conversation = None
    if username:
        other_user = get_object_or_404(User, username=username)
        messages = Message.objects.filter(
            (Q(sender=request.user) & Q(recipient=other_user)) |
            (Q(sender=other_user) & Q(recipient=request.user))
        ).order_by('created_at')
        
        # Mark messages as read
        Message.objects.filter(
            recipient=request.user,
            sender=other_user,
            is_read=False
        ).update(is_read=True)
        
        active_conversation = {
            'other_user': other_user,
            'messages': messages
        }
        
        if request.method == 'POST':
            content = request.POST.get('content')
            if content:
                Message.objects.create(
                    sender=request.user,
                    recipient=other_user,
                    content=content
                )
                return redirect('private_messages:messages', username=username)
    
    return render(request, 'private_messages/messages.html', {
        'conversations': conversations,
        'active_conversation': active_conversation
    }) 