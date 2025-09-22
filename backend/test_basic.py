"""
Basic test to verify pytest setup
"""
import pytest
from django.test import TestCase


@pytest.mark.django_db
def test_basic_setup():
    """Test that Django is properly configured"""
    from django.conf import settings
    assert settings.DEBUG is False  # Should be False in test settings
    assert settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3'


@pytest.mark.django_db
def test_user_model_exists():
    """Test that User model can be imported"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    assert User is not None
    assert hasattr(User, 'objects')


@pytest.mark.django_db
def test_create_simple_user():
    """Test creating a simple user"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    user = User.objects.create_user(
        phone_number='+254712345678',
        email='test@example.com',
        first_name='Test',
        last_name='User',
        password='testpass123'
    )
    
    assert user.phone_number == '+254712345678'
    assert user.email == 'test@example.com'
    assert user.first_name == 'Test'
    assert user.last_name == 'User'
    assert user.check_password('testpass123')
