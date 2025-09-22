"""
Standing Orders serializers for PesaPlan
"""
from rest_framework import serializers
from decimal import Decimal
from .models import StandingOrder, StandingOrderExecution


class StandingOrderSerializer(serializers.ModelSerializer):
    """
    Standing order serializer
    """
    user = serializers.StringRelatedField(read_only=True)
    wallet = serializers.StringRelatedField(read_only=True)
    total_executions = serializers.ReadOnlyField()
    successful_executions = serializers.ReadOnlyField()
    failed_executions = serializers.ReadOnlyField()
    is_due = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    
    class Meta:
        model = StandingOrder
        fields = [
            'id', 'user', 'wallet', 'title', 'amount', 'frequency',
            'payment_method', 'recipient_name', 'recipient_phone',
            'recipient_account', 'start_date', 'end_date', 'next_execution',
            'last_execution', 'status', 'total_executions', 'successful_executions',
            'failed_executions', 'max_executions', 'max_amount', 'retry_attempts',
            'retry_interval_hours', 'is_due', 'is_completed', 'created_at',
            'updated_at', 'cancelled_at'
        ]
        read_only_fields = [
            'id', 'user', 'wallet', 'total_executions', 'successful_executions',
            'failed_executions', 'last_execution', 'is_due', 'is_completed',
            'created_at', 'updated_at', 'cancelled_at'
        ]
    
    def validate_amount(self, value):
        """Validate standing order amount"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        if value > Decimal('100000.00'):
            raise serializers.ValidationError("Amount exceeds maximum limit")
        return value
    
    def validate(self, attrs):
        """Validate standing order data"""
        # Check if end_date is after start_date
        if attrs.get('end_date') and attrs.get('start_date'):
            if attrs['end_date'] <= attrs['start_date']:
                raise serializers.ValidationError("End date must be after start date")
        
        # Check if max_amount is reasonable
        if attrs.get('max_amount') and attrs.get('amount'):
            if attrs['max_amount'] < attrs['amount']:
                raise serializers.ValidationError("Max amount must be at least the order amount")
        
        return attrs


class CreateStandingOrderSerializer(serializers.ModelSerializer):
    """
    Serializer for creating standing orders
    """
    class Meta:
        model = StandingOrder
        fields = [
            'title', 'amount', 'frequency', 'payment_method',
            'recipient_name', 'recipient_phone', 'recipient_account',
            'start_date', 'end_date', 'max_executions', 'max_amount',
            'retry_attempts', 'retry_interval_hours'
        ]
    
    def validate_amount(self, value):
        """Validate standing order amount"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        if value > Decimal('100000.00'):
            raise serializers.ValidationError("Amount exceeds maximum limit")
        return value
    
    def validate(self, attrs):
        """Validate standing order data"""
        # Check if end_date is after start_date
        if attrs.get('end_date') and attrs.get('start_date'):
            if attrs['end_date'] <= attrs['start_date']:
                raise serializers.ValidationError("End date must be after start date")
        
        # Check if max_amount is reasonable
        if attrs.get('max_amount') and attrs.get('amount'):
            if attrs['max_amount'] < attrs['amount']:
                raise serializers.ValidationError("Max amount must be at least the order amount")
        
        return attrs


class StandingOrderExecutionSerializer(serializers.ModelSerializer):
    """
    Standing order execution serializer
    """
    standing_order = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = StandingOrderExecution
        fields = [
            'id', 'standing_order', 'amount', 'status', 'payment_method_used',
            'transaction_reference', 'mpesa_receipt', 'error_message',
            'retry_count', 'next_retry_at', 'created_at', 'updated_at',
            'executed_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'standing_order', 'amount', 'status', 'payment_method_used',
            'transaction_reference', 'mpesa_receipt', 'error_message',
            'retry_count', 'next_retry_at', 'created_at', 'updated_at',
            'executed_at', 'completed_at'
        ]


class StandingOrderStatsSerializer(serializers.Serializer):
    """
    Standing order statistics serializer
    """
    total_orders = serializers.IntegerField()
    active_orders = serializers.IntegerField()
    paused_orders = serializers.IntegerField()
    completed_orders = serializers.IntegerField()
    cancelled_orders = serializers.IntegerField()
    total_amount_paid = serializers.DecimalField(max_digits=12, decimal_places=2)
    successful_executions = serializers.IntegerField()
    failed_executions = serializers.IntegerField()
    next_due_order = serializers.DateTimeField(allow_null=True)


class ExecuteStandingOrderSerializer(serializers.Serializer):
    """
    Serializer for manually executing standing orders
    """
    pin = serializers.CharField(max_length=6, min_length=4)
    
    def validate_pin(self, value):
        """Validate PIN"""
        if not value.isdigit():
            raise serializers.ValidationError("PIN must contain only digits")
        return value
    
    def validate(self, attrs):
        """Validate execution request"""
        user = self.context['request'].user
        standing_order = self.context['standing_order']
        
        # Check PIN
        if user.pin_hash != attrs['pin']:
            raise serializers.ValidationError("Invalid PIN")
        
        # Check if order can be executed
        if not standing_order.is_due:
            raise serializers.ValidationError("Standing order is not due for execution")
        
        if standing_order.status != 'active':
            raise serializers.ValidationError("Standing order is not active")
        
        return attrs


class PauseResumeStandingOrderSerializer(serializers.Serializer):
    """
    Serializer for pausing/resuming standing orders
    """
    pin = serializers.CharField(max_length=6, min_length=4)
    
    def validate_pin(self, value):
        """Validate PIN"""
        if not value.isdigit():
            raise serializers.ValidationError("PIN must contain only digits")
        return value
    
    def validate(self, attrs):
        """Validate pause/resume request"""
        user = self.context['request'].user
        
        # Check PIN
        if user.pin_hash != attrs['pin']:
            raise serializers.ValidationError("Invalid PIN")
        
        return attrs


class CancelStandingOrderSerializer(serializers.Serializer):
    """
    Serializer for cancelling standing orders
    """
    pin = serializers.CharField(max_length=6, min_length=4)
    reason = serializers.CharField(max_length=255, required=False)
    
    def validate_pin(self, value):
        """Validate PIN"""
        if not value.isdigit():
            raise serializers.ValidationError("PIN must contain only digits")
        return value
    
    def validate(self, attrs):
        """Validate cancellation request"""
        user = self.context['request'].user
        
        # Check PIN
        if user.pin_hash != attrs['pin']:
            raise serializers.ValidationError("Invalid PIN")
        
        return attrs
