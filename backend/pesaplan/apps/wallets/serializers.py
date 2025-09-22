"""
Wallet serializers for PesaPlan
"""
from rest_framework import serializers
from decimal import Decimal
from .models import Wallet, WalletTransaction, WalletLimit


class WalletSerializer(serializers.ModelSerializer):
    """
    Wallet serializer
    """
    user = serializers.StringRelatedField(read_only=True)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_deposited = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_withdrawn = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = Wallet
        fields = [
            'id', 'user', 'balance', 'phone_number', 'status',
            'daily_limit', 'monthly_limit', 'total_deposited',
            'total_withdrawn', 'created_at', 'last_transaction_at'
        ]
        read_only_fields = [
            'id', 'user', 'balance', 'total_deposited', 'total_withdrawn',
            'created_at', 'last_transaction_at'
        ]


class WalletTransactionSerializer(serializers.ModelSerializer):
    """
    Wallet transaction serializer
    """
    wallet = serializers.StringRelatedField(read_only=True)
    balance_before = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    balance_after = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = WalletTransaction
        fields = [
            'id', 'wallet', 'amount', 'transaction_type', 'description',
            'reference', 'status', 'balance_before', 'balance_after',
            'mpesa_receipt', 'mpesa_transaction_id', 'created_at',
            'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'wallet', 'balance_before', 'balance_after',
            'mpesa_receipt', 'mpesa_transaction_id', 'created_at',
            'updated_at', 'completed_at'
        ]


class WalletTopupSerializer(serializers.Serializer):
    """
    Wallet top-up serializer
    """
    amount = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2,
        min_value=Decimal('1.00')
    )
    description = serializers.CharField(max_length=255, required=False, default="Wallet top-up")
    
    def validate_amount(self, value):
        """Validate top-up amount"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        if value > Decimal('100000.00'):
            raise serializers.ValidationError("Amount exceeds maximum limit")
        return value


class WalletWithdrawSerializer(serializers.Serializer):
    """
    Wallet withdrawal serializer
    """
    amount = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2,
        min_value=Decimal('1.00')
    )
    description = serializers.CharField(max_length=255, required=False, default="Wallet withdrawal")
    pin = serializers.CharField(max_length=6, min_length=4)
    
    def validate_amount(self, value):
        """Validate withdrawal amount"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value
    
    def validate(self, attrs):
        """Validate withdrawal request"""
        user = self.context['request'].user
        wallet = user.wallet
        
        # Check PIN
        if user.pin_hash != attrs['pin']:
            raise serializers.ValidationError("Invalid PIN")
        
        # Check wallet balance
        if wallet.balance < attrs['amount']:
            raise serializers.ValidationError("Insufficient balance")
        
        # Check daily limit
        can_transact, message = wallet.can_transact(attrs['amount'])
        if not can_transact:
            raise serializers.ValidationError(message)
        
        return attrs


class WalletTransferSerializer(serializers.Serializer):
    """
    Wallet transfer serializer
    """
    amount = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2,
        min_value=Decimal('1.00')
    )
    recipient_phone = serializers.CharField(max_length=15)
    description = serializers.CharField(max_length=255, required=False, default="Wallet transfer")
    pin = serializers.CharField(max_length=6, min_length=4)
    
    def validate_amount(self, value):
        """Validate transfer amount"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value
    
    def validate(self, attrs):
        """Validate transfer request"""
        user = self.context['request'].user
        wallet = user.wallet
        
        # Check PIN
        if user.pin_hash != attrs['pin']:
            raise serializers.ValidationError("Invalid PIN")
        
        # Check wallet balance
        if wallet.balance < attrs['amount']:
            raise serializers.ValidationError("Insufficient balance")
        
        # Check daily limit
        can_transact, message = wallet.can_transact(attrs['amount'])
        if not can_transact:
            raise serializers.ValidationError(message)
        
        # Check if recipient exists
        from pesaplan.apps.users.models import User
        try:
            recipient = User.objects.get(phone_number=attrs['recipient_phone'])
            if recipient == user:
                raise serializers.ValidationError("Cannot transfer to yourself")
        except User.DoesNotExist:
            raise serializers.ValidationError("Recipient not found")
        
        return attrs


class WalletLimitSerializer(serializers.ModelSerializer):
    """
    Wallet limit serializer
    """
    class Meta:
        model = WalletLimit
        fields = [
            'id', 'limit_type', 'amount', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WalletBalanceSerializer(serializers.Serializer):
    """
    Wallet balance serializer
    """
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField(default='KES')
    last_updated = serializers.DateTimeField()
    
    def to_representation(self, instance):
        """Convert wallet instance to balance representation"""
        return {
            'balance': instance.balance,
            'currency': 'KES',
            'last_updated': instance.updated_at
        }
