from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import FriendRequest, Friendship, Message
from notifications.models import Notification

User = get_user_model()

@login_required
def friend_list(request):
    """View to display friend requests and friends list."""
    # Get pending friend requests (received)
    pending_requests = FriendRequest.objects.filter(
        receiver=request.user,
        status='pending'
    ).select_related('sender')

    # Get sent friend requests
    sent_requests = FriendRequest.objects.filter(
        sender=request.user,
        status='pending'
    ).select_related('receiver')

    try:
        # Get accepted friends (both directions)
        friends_as_user1 = Friendship.objects.filter(
            user1=request.user,
            status='accepted'
        ).select_related('user2')

        friends_as_user2 = Friendship.objects.filter(
            user2=request.user,
            status='accepted'
        ).select_related('user1')
    except Exception as e:
        # If status field doesn't exist yet, get all friendships
        friends_as_user1 = Friendship.objects.filter(
            user1=request.user
        ).select_related('user2')

        friends_as_user2 = Friendship.objects.filter(
            user2=request.user
        ).select_related('user1')

    # Debug information
    print("Friends as user1:", [f.user2.username for f in friends_as_user1])
    print("Friends as user2:", [f.user1.username for f in friends_as_user2])

    context = {
        'pending_requests': pending_requests,
        'sent_requests': sent_requests,
        'friends_as_user1': friends_as_user1,
        'friends_as_user2': friends_as_user2,
    }
    return render(request, 'friends/friend_list.html', context)

@login_required
def send_friend_request(request, username):
    """Send a friend request to another user."""
    receiver = get_object_or_404(User, username=username)
    
    # Check if a friend request already exists
    if FriendRequest.objects.filter(
        Q(sender=request.user, receiver=receiver) |
        Q(sender=receiver, receiver=request.user)
    ).exists():
        messages.error(request, 'A friend request already exists.')
        return redirect('friends:friend_list')
    
    # Create new friend request
    friend_request = FriendRequest.objects.create(
        sender=request.user,
        receiver=receiver
    )
    
    # Create notification for the receiver
    Notification.objects.create(
        recipient=receiver,
        sender=request.user,
        notification_type='friend_request',
        message=f'{request.user.username} sent you a friend request!'
    )
    
    messages.success(request, f'Friend request sent to {receiver.username}!')
    return redirect('friends:friend_list')

@login_required
def accept_request(request, request_id):
    """Accept a friend request."""
    friend_request = get_object_or_404(
        FriendRequest,
        id=request_id,
        receiver=request.user,
        status='pending'
    )
    
    # Create friendship
    friendship = Friendship.objects.create(
        user1=friend_request.sender,
        user2=friend_request.receiver,
        status='accepted'
    )
    
    # Update friend request status
    friend_request.status = 'accepted'
    friend_request.save()
    
    # Create notification for the sender
    Notification.objects.create(
        recipient=friend_request.sender,
        sender=request.user,
        notification_type='friend_request_accepted',
        message=f'{request.user.username} accepted your friend request!'
    )
    
    messages.success(request, f'You are now friends with {friend_request.sender.username}!')
    return redirect('friends:friend_list')

@login_required
def reject_request(request, request_id):
    """Reject a friend request."""
    friend_request = get_object_or_404(
        FriendRequest,
        id=request_id,
        receiver=request.user,
        status='pending'
    )
    
    friend_request.status = 'rejected'
    friend_request.save()
    
    messages.success(request, 'Friend request rejected.')
    return redirect('friends:friend_list')

@login_required
def cancel_request(request, request_id):
    """Cancel a sent friend request."""
    friend_request = get_object_or_404(
        FriendRequest,
        id=request_id,
        sender=request.user,
        status='pending'
    )
    
    friend_request.delete()
    messages.success(request, 'Friend request cancelled.')
    return redirect('friends:friend_list')

@login_required
def remove_friend(request, friendship_id):
    """Remove a friend."""
    friendship = get_object_or_404(
        Friendship,
        id=friendship_id
    )
    
    if friendship.user1 != request.user and friendship.user2 != request.user:
        messages.error(request, 'You can only remove your own friends.')
        return redirect('friends:friend_list')
    
    friendship.delete()
    messages.success(request, 'Friend removed.')
    return redirect('friends:friend_list')

@login_required
def send_message(request, username):
    """Send a message to a friend."""
    if request.method == 'POST':
        receiver = get_object_or_404(User, username=username)
        content = request.POST.get('content', '').strip()
        
        if not content:
            messages.error(request, 'Message cannot be empty.')
            return redirect('friends:friend_list')
        
        # Check if users are friends
        is_friend = Friendship.objects.filter(
            (Q(user1=request.user, user2=receiver) | Q(user1=receiver, user2=request.user)),
            status='accepted'
        ).exists()
        
        if not is_friend:
            messages.error(request, 'You can only message your friends.')
            return redirect('friends:friend_list')
        
        # Create message
        Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content
        )
        
        # Create notification
        Notification.objects.create(
            recipient=receiver,
            sender=request.user,
            notification_type='message',
            message=f'New message from {request.user.username}'
        )
        
        messages.success(request, 'Message sent successfully!')
        return redirect('friends:messages', username=username)
    
    return redirect('friends:friend_list')

@login_required
def view_messages(request, username):
    """View conversation with a friend."""
    friend = get_object_or_404(User, username=username)
    
    # Check if users are friends
    is_friend = Friendship.objects.filter(
        (Q(user1=request.user, user2=friend) | Q(user1=friend, user2=request.user)),
        status='accepted'
    ).exists()
    
    if not is_friend:
        messages.error(request, 'You can only view messages from your friends.')
        return redirect('friends:friend_list')
    
    # Get messages between users
    messages = Message.objects.filter(
        (Q(sender=request.user, receiver=friend) | Q(sender=friend, receiver=request.user))
    ).order_by('created_at')
    
    # Mark messages as read
    Message.objects.filter(receiver=request.user, sender=friend, is_read=False).update(is_read=True)
    
    context = {
        'friend': friend,
        'messages': messages,
    }
    return render(request, 'friends/messages.html', context) 