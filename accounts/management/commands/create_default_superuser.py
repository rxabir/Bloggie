from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create default superuser from hardcoded values'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'newabir'
        email = 'rxabir208@gmail.com'
        password = 'newabir'

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created'))
        else:
            self.stdout.write(f'Superuser "{username}" already exists')
