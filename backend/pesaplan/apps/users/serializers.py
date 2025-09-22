"""
User serializers for PesaPlan
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from phonenumber_field.serializerfields import PhoneNumberField
from .models import User, UserProfile, UserSession


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    phone_number = PhoneNumberField()
    
    class Meta:
        model = User
        fields = [
            'id', 'phone_number', 'email', 'first_name', 'last_name',
            'user_type', 'password', 'password_confirm'
        ]
        extra_kwargs = {
            'email': {'required': False},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        """Validate registration data"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def validate_phone_number(self, value):
        """Validate phone number"""
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("User with this phone number already exists")
        return value
    
    def validate_email(self, value):
        """Validate email"""
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value
    
    def create(self, validated_data):
        """Create new user"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        # Create wallet for the user
        from pesaplan.apps.wallets.models import Wallet
        Wallet.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    phone_number = PhoneNumberField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate login credentials"""
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        
        if phone_number and password:
            user = authenticate(
                request=self.context.get('request'),
                phone_number=phone_number,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError('Invalid phone number or password')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            
            if user.is_locked:
                raise serializers.ValidationError('User account is locked')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include phone number and password')


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile
    """
    phone_number = PhoneNumberField(read_only=True)
    full_name = serializers.ReadOnlyField()
    is_verified = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'phone_number', 'email', 'first_name', 'last_name',
            'full_name', 'user_type', 'status', 'is_verified',
            'language', 'timezone', 'created_at', 'last_login_at'
        ]
        read_only_fields = ['id', 'phone_number', 'status', 'created_at', 'last_login_at']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile details
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'bio', 'profile_picture', 'address_line_1',
            'address_line_2', 'city', 'county', 'postal_code', 'country',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information
    """
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'language', 'timezone'
        ]
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if value and User.objects.filter(email=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate password change"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
    
    def save(self):
        """Save new password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class SetPinSerializer(serializers.Serializer):
    """
    Serializer for setting user PIN
    """
    pin = serializers.CharField(write_only=True, min_length=4, max_length=6)
    pin_confirm = serializers.CharField(write_only=True, min_length=4, max_length=6)
    
    def validate(self, attrs):
        """Validate PIN"""
        if attrs['pin'] != attrs['pin_confirm']:
            raise serializers.ValidationError("PINs don't match")
        
        if not attrs['pin'].isdigit():
            raise serializers.ValidationError("PIN must contain only digits")
        
        return attrs
    
    def save(self):
        """Save PIN"""
        user = self.context['request'].user
        # In production, hash the PIN before storing
        user.pin_hash = self.validated_data['pin']  # This should be hashed
        user.is_pin_set = True
        user.save()
        return user


class UserSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for user sessions
    """
    class Meta:
        model = UserSession
        fields = [
            'id', 'device_info', 'ip_address', 'user_agent',
            'is_active', 'created_at', 'last_activity', 'expires_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_activity']


class VerifyPhoneSerializer(serializers.Serializer):
    """
    Serializer for phone verification
    """
    verification_code = serializers.CharField(max_length=6, min_length=6)
    
    def validate_verification_code(self, value):
        """Validate verification code"""
        if not value.isdigit():
            raise serializers.ValidationError("Verification code must contain only digits")
        return value


class ResendVerificationSerializer(serializers.Serializer):
    """
    Serializer for resending verification code
    """
    phone_number = PhoneNumberField()
    
    def validate_phone_number(self, value):
        """Validate phone number"""
        try:
            user = User.objects.get(phone_number=value)
            if user.phone_verified_at:
                raise serializers.ValidationError("Phone number is already verified")
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this phone number does not exist")
        return value
