"""
Tests for User API views
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from pesaplan.apps.users.models import User, UserProfile


@pytest.mark.django_db
class TestUserRegistrationView:
    """Test user registration API"""
    
    def test_user_registration_success(self, api_client):
        """Test successful user registration"""
        url = reverse('user-register')
        data = {
            'phone_number': '+254712345678',
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
        
        # Check user was created
        user = User.objects.get(phone_number='+254712345678')
        assert user.email == 'test@example.com'
        assert user.first_name == 'John'
        assert user.last_name == 'Doe'
        assert user.check_password('testpass123')
        
        # Check user profile was created
        assert hasattr(user, 'userprofile')
        
        # Check wallet was created
        assert hasattr(user, 'wallet')
    
    def test_user_registration_duplicate_phone(self, api_client, user):
        """Test registration with duplicate phone number"""
        url = reverse('user-register')
        data = {
            'phone_number': user.phone_number,
            'email': 'different@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'phone_number' in response.data
    
    def test_user_registration_duplicate_email(self, api_client, user):
        """Test registration with duplicate email"""
        url = reverse('user-register')
        data = {
            'phone_number': '+254712345679',
            'email': user.email,
            'first_name': 'Jane',
            'last_name': 'Smith',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
    
    def test_user_registration_password_mismatch(self, api_client):
        """Test registration with password mismatch"""
        url = reverse('user-register')
        data = {
            'phone_number': '+254712345678',
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'testpass123',
            'password_confirm': 'differentpass123'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_confirm' in response.data
    
    def test_user_registration_missing_fields(self, api_client):
        """Test registration with missing required fields"""
        url = reverse('user-register')
        data = {
            'phone_number': '+254712345678',
            'email': 'test@example.com',
            # Missing first_name, last_name, password, password_confirm
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'first_name' in response.data
        assert 'last_name' in response.data
        assert 'password' in response.data


@pytest.mark.django_db
class TestUserLoginView:
    """Test user login API"""
    
    def test_user_login_success(self, api_client, user):
        """Test successful user login"""
        url = reverse('user-login')
        data = {
            'phone_number': user.phone_number,
            'password': 'testpass123'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
    
    def test_user_login_invalid_phone(self, api_client, user):
        """Test login with invalid phone number"""
        url = reverse('user-login')
        data = {
            'phone_number': '+254712345679',  # Non-existent phone
            'password': 'testpass123'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_user_login_invalid_password(self, api_client, user):
        """Test login with invalid password"""
        url = reverse('user-login')
        data = {
            'phone_number': user.phone_number,
            'password': 'wrongpassword'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_user_login_missing_fields(self, api_client):
        """Test login with missing fields"""
        url = reverse('user-login')
        data = {
            'phone_number': '+254712345678',
            # Missing password
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data


@pytest.mark.django_db
class TestUserProfileView:
    """Test user profile API"""
    
    def test_get_user_profile_success(self, authenticated_client, user):
        """Test successful profile retrieval"""
        url = reverse('user-profile')
        
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['phone_number'] == user.phone_number
        assert response.data['email'] == user.email
        assert response.data['first_name'] == user.first_name
        assert response.data['last_name'] == user.last_name
    
    def test_get_user_profile_unauthorized(self, api_client):
        """Test profile retrieval without authentication"""
        url = reverse('user-profile')
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_user_profile_success(self, authenticated_client, user):
        """Test successful profile update"""
        url = reverse('user-profile')
        data = {
            'first_name': 'Updated John',
            'last_name': 'Updated Doe',
            'email': 'updated@example.com'
        }
        
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated John'
        assert response.data['last_name'] == 'Updated Doe'
        assert response.data['email'] == 'updated@example.com'
        
        # Check database was updated
        user.refresh_from_db()
        assert user.first_name == 'Updated John'
        assert user.last_name == 'Updated Doe'
        assert user.email == 'updated@example.com'
    
    def test_update_user_profile_unauthorized(self, api_client):
        """Test profile update without authentication"""
        url = reverse('user-profile')
        data = {
            'first_name': 'Updated John'
        }
        
        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserLogoutView:
    """Test user logout API"""
    
    def test_user_logout_success(self, authenticated_client):
        """Test successful user logout"""
        url = reverse('user-logout')
        
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Successfully logged out'
    
    def test_user_logout_unauthorized(self, api_client):
        """Test logout without authentication"""
        url = reverse('user-logout')
        
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserChangePasswordView:
    """Test user change password API"""
    
    def test_change_password_success(self, authenticated_client, user):
        """Test successful password change"""
        url = reverse('user-change-password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Password changed successfully'
        
        # Check password was actually changed
        user.refresh_from_db()
        assert user.check_password('newpass123')
        assert not user.check_password('testpass123')
    
    def test_change_password_wrong_old_password(self, authenticated_client):
        """Test password change with wrong old password"""
        url = reverse('user-change-password')
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'old_password' in response.data
    
    def test_change_password_mismatch(self, authenticated_client):
        """Test password change with password mismatch"""
        url = reverse('user-change-password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'differentpass123'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'new_password_confirm' in response.data
    
    def test_change_password_unauthorized(self, api_client):
        """Test password change without authentication"""
        url = reverse('user-change-password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserSessionsView:
    """Test user sessions API"""
    
    def test_get_user_sessions_success(self, authenticated_client, user):
        """Test successful sessions retrieval"""
        url = reverse('user-sessions')
        
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
    
    def test_get_user_sessions_unauthorized(self, api_client):
        """Test sessions retrieval without authentication"""
        url = reverse('user-sessions')
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_terminate_user_session_success(self, authenticated_client, user):
        """Test successful session termination"""
        # Create a session first
        from pesaplan.apps.users.models import UserSession
        session = UserSession.objects.create(
            user=user,
            session_key='test_session_key',
            device_info='Test Device',
            ip_address='192.168.1.1',
            user_agent='Test User Agent'
        )
        
        url = reverse('user-session-terminate', kwargs={'session_id': session.id})
        
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Session terminated successfully'
        
        # Check session was terminated
        session.refresh_from_db()
        assert session.is_active is False
    
    def test_terminate_user_session_unauthorized(self, api_client, user):
        """Test session termination without authentication"""
        from pesaplan.apps.users.models import UserSession
        session = UserSession.objects.create(
            user=user,
            session_key='test_session_key',
            device_info='Test Device',
            ip_address='192.168.1.1',
            user_agent='Test User Agent'
        )
        
        url = reverse('user-session-terminate', kwargs={'session_id': session.id})
        
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
