"""
Transaction models for PesaPlan
"""
import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from pesaplan.apps.users.models import User
from pesaplan.apps.wallets.models import Wallet
from pesaplan.apps.standing_orders.models import StandingOrder


class Transaction(models.Model):
    """
    Main transaction model for all payment activities
    """
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
        ('payment', 'Payment'),
        ('standing_order', 'Standing Order'),
        ('refund', 'Refund'),
        ('fee', 'Fee'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('reversed', 'Reversed'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('wallet', 'Wallet Balance'),
        ('mpesa_stk', 'M-Pesa STK Push'),
        ('mpesa_c2b', 'M-Pesa C2B'),
        ('mpesa_b2c', 'M-Pesa B2C'),
        ('bank_transfer', 'Bank Transfer'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='transactions'
    )
    wallet = models.ForeignKey(
        Wallet, 
        on_delete=models.CASCADE, 
        related_name='main_transactions'
    )
    standing_order = models.ForeignKey(
        StandingOrder, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='transactions'
    )
    
    # Transaction details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    fee = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    total_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="Amount + Fee"
    )
    
    # Payment method and status
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # References and descriptions
    reference = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255)
    external_reference = models.CharField(max_length=100, null=True, blank=True)
    
    # M-Pesa integration
    mpesa_receipt = models.CharField(max_length=50, null=True, blank=True)
    mpesa_transaction_id = models.CharField(max_length=50, null=True, blank=True)
    mpesa_checkout_request_id = models.CharField(max_length=50, null=True, blank=True)
    
    # Recipient information (for transfers/payments)
    recipient_name = models.CharField(max_length=255, null=True, blank=True)
    recipient_phone = PhoneNumberField(null=True, blank=True)
    recipient_account = models.CharField(max_length=100, null=True, blank=True)
    
    # Error handling
    error_code = models.CharField(max_length=50, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['wallet', 'created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['reference']),
            models.Index(fields=['mpesa_receipt']),
            models.Index(fields=['mpesa_transaction_id']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.full_name} - {self.transaction_type.title()} {self.amount} ({self.status})"

    def save(self, *args, **kwargs):
        """Override save to calculate total_amount"""
        self.total_amount = self.amount + self.fee
        super().save(*args, **kwargs)

    def mark_processing(self):
        """Mark transaction as processing"""
        self.status = 'processing'
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_at'])

    def mark_completed(self, mpesa_receipt=None, mpesa_transaction_id=None):
        """Mark transaction as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if mpesa_receipt:
            self.mpesa_receipt = mpesa_receipt
        if mpesa_transaction_id:
            self.mpesa_transaction_id = mpesa_transaction_id
        self.save(update_fields=['status', 'completed_at', 'mpesa_receipt', 'mpesa_transaction_id'])

    def mark_failed(self, error_code=None, error_message=None):
        """Mark transaction as failed"""
        self.status = 'failed'
        if error_code:
            self.error_code = error_code
        if error_message:
            self.error_message = error_message
        self.save(update_fields=['status', 'error_code', 'error_message'])

    def can_retry(self):
        """Check if transaction can be retried"""
        return (
            self.status in ['failed', 'cancelled'] and 
            self.retry_count < 3
        )

    def increment_retry(self):
        """Increment retry count"""
        self.retry_count += 1
        self.save(update_fields=['retry_count'])


class TransactionFee(models.Model):
    """
    Transaction fee configuration
    """
    FEE_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('tiered', 'Tiered'),
    ]

    transaction_type = models.CharField(max_length=20, choices=Transaction.TRANSACTION_TYPE_CHOICES)
    payment_method = models.CharField(max_length=20, choices=Transaction.PAYMENT_METHOD_CHOICES)
    fee_type = models.CharField(max_length=10, choices=FEE_TYPE_CHOICES)
    fee_value = models.DecimalField(max_digits=8, decimal_places=4)
    min_fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    max_fee = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transaction_fees'
        verbose_name = 'Transaction Fee'
        verbose_name_plural = 'Transaction Fees'
        unique_together = ['transaction_type', 'payment_method']
        indexes = [
            models.Index(fields=['transaction_type', 'payment_method']),
        ]

    def __str__(self):
        return f"{self.transaction_type} - {self.payment_method}: {self.fee_value}"

    def calculate_fee(self, amount):
        """Calculate fee for given amount"""
        if self.fee_type == 'percentage':
            fee = amount * (self.fee_value / 100)
        elif self.fee_type == 'fixed':
            fee = self.fee_value
        else:  # tiered
            # Implement tiered fee calculation based on amount ranges
            fee = self.fee_value
        
        # Apply min/max limits
        if fee < self.min_fee:
            fee = self.min_fee
        if self.max_fee and fee > self.max_fee:
            fee = self.max_fee
        
        return fee


class TransactionAuditLog(models.Model):
    """
    Audit log for transaction changes
    """
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('status_changed', 'Status Changed'),
        ('failed', 'Failed'),
        ('retried', 'Retried'),
        ('reversed', 'Reversed'),
    ]

    transaction = models.ForeignKey(
        Transaction, 
        on_delete=models.CASCADE, 
        related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    old_status = models.CharField(max_length=20, null=True, blank=True)
    new_status = models.CharField(max_length=20, null=True, blank=True)
    changed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transaction_audit_logs'
        verbose_name = 'Transaction Audit Log'
        verbose_name_plural = 'Transaction Audit Logs'
        indexes = [
            models.Index(fields=['transaction', 'created_at']),
            models.Index(fields=['action']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction.reference} - {self.action} at {self.created_at}"
