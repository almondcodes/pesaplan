"""
User models for PesaPlan
"""
import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    """
    Custom user manager for phone-based authentication
    """
    def create_user(self, phone_number, password=None, **extra_fields):
        """Create and return a regular user with the given phone number and password."""
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        """Create and return a superuser with the given phone number and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('status', 'active')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model for PesaPlan
    Supports phone-based authentication and user types
    """
    USER_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('group', 'Group'),
        ('organization', 'Organization'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('pending_verification', 'Pending Verification'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = PhoneNumberField(unique=True, help_text="Primary phone number for M-Pesa")
    email = models.EmailField(unique=True, null=True, blank=True)
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPE_CHOICES, 
        default='individual',
        help_text="Type of user account"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending_verification'
    )
    
    # Profile information
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    date_of_birth = models.DateField(null=True, blank=True)
    national_id = models.CharField(
        max_length=20, 
        null=True, 
        blank=True,
        validators=[RegexValidator(
            regex=r'^\d{7,8}$',
            message='National ID must be 7-8 digits'
        )]
    )
    
    # Security
    pin_hash = models.CharField(max_length=255, null=True, blank=True)
    is_pin_set = models.BooleanField(default=False)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    phone_verified_at = models.DateTimeField(null=True, blank=True)
    
    # Preferences
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='Africa/Nairobi')
    
    # Remove username field since we're using phone_number
    username = None
    
    # Custom manager
    objects = UserManager()
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_verified(self):
        return self.phone_verified_at is not None

    @property
    def is_locked(self):
        if self.locked_until:
            return timezone.now() < self.locked_until
        return False

    def lock_account(self, duration_minutes=30):
        """Lock account for specified duration"""
        self.locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        self.save(update_fields=['locked_until'])

    def unlock_account(self):
        """Unlock account"""
        self.locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=['locked_until', 'failed_login_attempts'])

    def increment_failed_login(self):
        """Increment failed login attempts"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.lock_account()
        self.save(update_fields=['failed_login_attempts', 'locked_until'])

    def reset_failed_login(self):
        """Reset failed login attempts"""
        self.failed_login_attempts = 0
        self.save(update_fields=['failed_login_attempts'])


class UserProfile(models.Model):
    """
    Extended user profile information
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    
    # Additional profile information
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(
        upload_to='profiles/', 
        null=True, 
        blank=True
    )
    
    # Address information
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='Kenya')
    
    # Emergency contact
    emergency_contact_name = models.CharField(max_length=255, blank=True)
    emergency_contact_phone = PhoneNumberField(blank=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.full_name}'s Profile"


class UserSession(models.Model):
    """
    Track user sessions for security
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sessions'
    )
    session_key = models.CharField(max_length=40, unique=True)
    device_info = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'user_sessions'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.user.full_name} - {self.session_key[:8]}..."

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
