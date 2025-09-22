"""
Custom superuser creation command
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from pesaplan.apps.wallets.models import Wallet

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser with wallet'

    def add_arguments(self, parser):
        parser.add_argument('--phone', type=str, help='Phone number')
        parser.add_argument('--email', type=str, help='Email address')
        parser.add_argument('--first-name', type=str, help='First name')
        parser.add_argument('--last-name', type=str, help='Last name')
        parser.add_argument('--password', type=str, help='Password')

    def handle(self, *args, **options):
        phone = options['phone'] or input('Phone number: ')
        email = options['email'] or input('Email address: ')
        first_name = options['first_name'] or input('First name: ')
        last_name = options['last_name'] or input('Last name: ')
        password = options['password'] or input('Password: ')

        try:
            user = User.objects.create_superuser(
                phone_number=phone,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            
            # Create wallet for superuser
            Wallet.objects.create(
                user=user,
                phone_number=phone,
                balance=0.00
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created superuser: {user.full_name}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {str(e)}')
            )
