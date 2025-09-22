"""
Pytest configuration and shared fixtures
"""
import pytest
from django.test import Client


@pytest.fixture
def api_client():
    """API client for testing"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def django_client():
    """Django test client"""
    return Client()


@pytest.fixture
def user():
    """Create a test user"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create_user(
        phone_number='+254712345678',
        email='test@example.com',
        first_name='Test',
        last_name='User',
        password='testpass123'
    )
    return user


@pytest.fixture
def admin_user():
    """Create a test admin user"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    admin = User.objects.create_superuser(
        phone_number='+254700000000',
        email='admin@example.com',
        first_name='Admin',
        last_name='User',
        password='adminpass123'
    )
    return admin


@pytest.fixture
def authenticated_client(api_client, user):
    """API client with authenticated user"""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """API client with authenticated admin user"""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def wallet(user):
    """Create a wallet for the user"""
    from pesaplan.apps.wallets.models import Wallet
    wallet, created = Wallet.objects.get_or_create(user=user)
    return wallet


@pytest.fixture
def user_profile(user):
    """Create a user profile"""
    from pesaplan.apps.users.models import UserProfile
    profile, created = UserProfile.objects.get_or_create(user=user)
    return profile


@pytest.fixture
def sample_users():
    """Create multiple test users"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = []
    for i in range(3):
        user = User.objects.create_user(
            phone_number=f'+25471234567{i}',
            email=f'user{i}@example.com',
            first_name=f'User{i}',
            last_name='Test',
            password='testpass123'
        )
        users.append(user)
    return users


@pytest.fixture
def sample_wallets(sample_users):
    """Create wallets for sample users"""
    from pesaplan.apps.wallets.models import Wallet
    wallets = []
    for user in sample_users:
        wallet, created = Wallet.objects.get_or_create(user=user)
        wallets.append(wallet)
    return wallets


# Pytest markers
pytest_plugins = ['pytest_django']
