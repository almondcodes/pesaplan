"""
Tests for User models and functionality
"""
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from phonenumber_field.phonenumber import PhoneNumber


@pytest.mark.django_db
class TestUserModel:
    """Test User model functionality"""
    
    def test_create_user(self):
        """Test creating a regular user"""
        User = get_user_model()
        user = User.objects.create_user(
            phone_number='+254712345678',
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            password='testpass123'
        )
        
        assert user.phone_number == '+254712345678'
        assert user.email == 'test@example.com'
        assert user.first_name == 'John'
        assert user.last_name == 'Doe'
        assert user.full_name == 'John Doe'
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.status == 'pending_verification'
        assert user.user_type == 'individual'
        assert user.language == 'en'
        assert user.timezone == 'Africa/Nairobi'
        assert user.check_password('testpass123')
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        User = get_user_model()
        admin = User.objects.create_superuser(
            phone_number='+254700000000',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='adminpass123'
        )
        
        assert admin.is_staff is True
        assert admin.is_superuser is True
        assert admin.status == 'active'
    
    def test_phone_number_required(self):
        """Test that phone number is required"""
        with pytest.raises(ValueError, match='The Phone Number field must be set'):
            User.objects.create_user(
                phone_number=None,
                email='test@example.com',
                first_name='John',
                last_name='Doe',
                password='testpass123'
            )
    
    def test_phone_number_unique(self):
        """Test that phone numbers must be unique"""
        User.objects.create_user(
            phone_number='+254712345678',
            email='test1@example.com',
            first_name='John',
            last_name='Doe',
            password='testpass123'
        )
        
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                phone_number='+254712345678',
                email='test2@example.com',
                first_name='Jane',
                last_name='Smith',
                password='testpass123'
            )
    
    def test_email_unique(self):
        """Test that emails must be unique"""
        User.objects.create_user(
            phone_number='+254712345678',
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            password='testpass123'
        )
        
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                phone_number='+254712345679',
                email='test@example.com',
                first_name='Jane',
                last_name='Smith',
                password='testpass123'
            )
    
    def test_full_name_property(self):
        """Test the full_name property"""
        user = User.objects.create_user(
            phone_number='+254712345678',
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            password='testpass123'
        )
        
        assert user.full_name == 'John Doe'
    
    def test_is_verified_property(self):
        """Test the is_verified property"""
        user = User.objects.create_user(
            phone_number='+254712345678',
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            password='testpass123'
        )
        
        assert user.is_verified is False
        
        user.phone_verified_at = timezone.now()
        user.save()
        
        assert user.is_verified is True
    
    def test_user_str_representation(self):
        """Test string representation of user"""
        user = User.objects.create_user(
            phone_number='+254712345678',
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            password='testpass123'
        )
        
        assert str(user) == 'John Doe (+254712345678)'
    
    def test_user_type_choices(self):
        """Test user type choices"""
        user = User.objects.create_user(
            phone_number='+254712345678',
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            password='testpass123',
            user_type='business'
        )
        
        assert user.user_type == 'business'
    
    def test_status_choices(self):
        """Test status choices"""
        user = User.objects.create_user(
            phone_number='+254712345678',
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            password='testpass123',
            status='active'
        )
        
        assert user.status == 'active'


@pytest.mark.django_db
class TestUserProfileModel:
    """Test UserProfile model functionality"""
    
    def test_create_user_profile(self, user):
        """Test creating a user profile"""
        profile = UserProfile.objects.create(
            user=user,
            bio='Test bio',
            address_line_1='123 Test Street',
            city='Nairobi',
            county='Nairobi',
            country='Kenya'
        )
        
        assert profile.user == user
        assert profile.bio == 'Test bio'
        assert profile.address_line_1 == '123 Test Street'
        assert profile.city == 'Nairobi'
        assert profile.county == 'Nairobi'
        assert profile.country == 'Kenya'
    
    def test_user_profile_str_representation(self, user):
        """Test string representation of user profile"""
        profile = UserProfile.objects.create(user=user)
        assert str(profile) == f'{user.full_name} Profile'
    
    def test_user_profile_one_to_one_relationship(self, user):
        """Test one-to-one relationship with user"""
        profile = UserProfile.objects.create(user=user)
        
        # Test reverse relationship
        assert user.userprofile == profile
        
        # Test that only one profile can exist per user
        with pytest.raises(IntegrityError):
            UserProfile.objects.create(user=user)


@pytest.mark.django_db
class TestUserSessionModel:
    """Test UserSession model functionality"""
    
    def test_create_user_session(self, user):
        """Test creating a user session"""
        session = UserSession.objects.create(
            user=user,
            session_key='test_session_key',
            device_info='Test Device',
            ip_address='192.168.1.1',
            user_agent='Test User Agent'
        )
        
        assert session.user == user
        assert session.session_key == 'test_session_key'
        assert session.device_info == 'Test Device'
        assert session.ip_address == '192.168.1.1'
        assert session.user_agent == 'Test User Agent'
        assert session.is_active is True
    
    def test_user_session_str_representation(self, user):
        """Test string representation of user session"""
        session = UserSession.objects.create(
            user=user,
            session_key='test_session_key',
            device_info='Test Device',
            ip_address='192.168.1.1',
            user_agent='Test User Agent'
        )
        
        assert str(session) == f'{user.full_name} - test_session_key'
    
    def test_session_expiration(self, user):
        """Test session expiration logic"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Create session that expires in 1 hour
        expires_at = timezone.now() + timedelta(hours=1)
        session = UserSession.objects.create(
            user=user,
            session_key='test_session_key',
            device_info='Test Device',
            ip_address='192.168.1.1',
            user_agent='Test User Agent',
            expires_at=expires_at
        )
        
        assert session.is_expired() is False
        
        # Create session that already expired
        expired_at = timezone.now() - timedelta(hours=1)
        expired_session = UserSession.objects.create(
            user=user,
            session_key='expired_session_key',
            device_info='Test Device',
            ip_address='192.168.1.1',
            user_agent='Test User Agent',
            expires_at=expired_at
        )
        
        assert expired_session.is_expired() is True


@pytest.mark.django_db
class TestUserManager:
    """Test UserManager functionality"""
    
    def test_create_user_with_manager(self):
        """Test creating user with custom manager"""
        user = User.objects.create_user(
            phone_number='+254712345678',
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            password='testpass123'
        )
        
        assert user.phone_number == '+254712345678'
        assert user.check_password('testpass123')
    
    def test_create_superuser_with_manager(self):
        """Test creating superuser with custom manager"""
        admin = User.objects.create_superuser(
            phone_number='+254700000000',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='adminpass123'
        )
        
        assert admin.is_staff is True
        assert admin.is_superuser is True
        assert admin.status == 'active'
