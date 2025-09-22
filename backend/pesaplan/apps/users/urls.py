"""
User URLs for PesaPlan
"""
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('logout/', views.LogoutView.as_view(), name='user-logout'),
    
    # Profile
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/detail/', views.UserProfileDetailView.as_view(), name='user-profile-detail'),
    
    # Security
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('set-pin/', views.SetPinView.as_view(), name='set-pin'),
    path('check-pin/', views.check_pin, name='check-pin'),
    
    # Verification
    path('verify-phone/', views.VerifyPhoneView.as_view(), name='verify-phone'),
    path('resend-verification/', views.ResendVerificationView.as_view(), name='resend-verification'),
    
    # Sessions
    path('sessions/', views.UserSessionsView.as_view(), name='user-sessions'),
]
