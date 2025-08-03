from django.core.management.base import BaseCommand
from friends.models import Friendship, FriendRequest
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Check friendships and friend requests in the database'

    def handle(self, *args, **options):
        # Print all friendships
        self.stdout.write("All Friendships:")
        for friendship in Friendship.objects.all():
            self.stdout.write(f"{friendship.user1.username} - {friendship.user2.username} ({friendship.status})")

        # Print all friend requests
        self.stdout.write("\nAll Friend Requests:")
        for request in FriendRequest.objects.all():
            self.stdout.write(f"{request.sender.username} -> {request.receiver.username} ({request.status})") 