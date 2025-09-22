"""
User views for PesaPlan
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from django.utils import timezone
from django.db import transaction
from .models import User, UserProfile, UserSession
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UserProfileSerializer, UserUpdateSerializer, ChangePasswordSerializer,
    SetPinSerializer, VerifyPhoneSerializer, ResendVerificationSerializer,
    UserSessionSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Create new user account"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            user = serializer.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Create user session
            UserSession.objects.create(
                user=user,
                session_key=request.session.session_key or 'api_session',
                device_info=request.META.get('HTTP_USER_AGENT', ''),
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                expires_at=timezone.now() + timezone.timedelta(days=7)
            )
        
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(access_token),
            }
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    """
    User login endpoint
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Authenticate user and return JWT tokens"""
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Reset failed login attempts
        user.reset_failed_login()
        user.last_login_at = timezone.now()
        user.save(update_fields=['last_login_at'])
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Create or update user session
        session_key = request.session.session_key or 'api_session'
        UserSession.objects.update_or_create(
            user=user,
            session_key=session_key,
            defaults={
                'device_info': request.META.get('HTTP_USER_AGENT', ''),
                'ip_address': request.META.get('REMOTE_ADDR', ''),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'is_active': True,
                'expires_at': timezone.now() + timezone.timedelta(days=7)
            }
        )
        
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(access_token),
            }
        }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile view
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    User profile detail view
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class ChangePasswordView(APIView):
    """
    Change password endpoint
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Change user password"""
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)


class SetPinView(APIView):
    """
    Set user PIN endpoint
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Set user PIN"""
        serializer = SetPinSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'PIN set successfully'
        }, status=status.HTTP_200_OK)


class VerifyPhoneView(APIView):
    """
    Verify phone number endpoint
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Verify phone number with code"""
        serializer = VerifyPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # In production, implement actual SMS verification logic
        # For now, accept any 6-digit code
        verification_code = serializer.validated_data['verification_code']
        
        if len(verification_code) == 6 and verification_code.isdigit():
            user = request.user
            user.phone_verified_at = timezone.now()
            user.status = 'active'
            user.save(update_fields=['phone_verified_at', 'status'])
            
            return Response({
                'message': 'Phone number verified successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid verification code'
            }, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationView(APIView):
    """
    Resend verification code endpoint
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Resend verification code"""
        serializer = ResendVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        
        # In production, send actual SMS
        # For now, just return success
        return Response({
            'message': f'Verification code sent to {phone_number}'
        }, status=status.HTTP_200_OK)


class UserSessionsView(generics.ListAPIView):
    """
    List user sessions
    """
    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserSession.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('-last_activity')


class LogoutView(APIView):
    """
    Logout endpoint
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Logout user and invalidate session"""
        try:
            # Invalidate JWT token
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Deactivate current session
            session_key = request.session.session_key or 'api_session'
            UserSession.objects.filter(
                user=request.user,
                session_key=session_key
            ).update(is_active=False)
            
            return Response({
                'message': 'Logged out successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Logout failed'
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def check_pin(request):
    """
    Check user PIN
    """
    pin = request.data.get('pin')
    if not pin:
        return Response({
            'error': 'PIN is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    # In production, compare hashed PIN
    if user.pin_hash == pin:
        return Response({
            'message': 'PIN is correct'
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': 'Invalid PIN'
        }, status=status.HTTP_400_BAD_REQUEST)
