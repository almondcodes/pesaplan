"""
Standing Orders models for PesaPlan
"""
import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from pesaplan.apps.users.models import User
from pesaplan.apps.wallets.models import Wallet


class StandingOrder(models.Model):
    """
    Standing order for recurring payments
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('wallet', 'Wallet Balance'),
        ('mpesa', 'M-Pesa Direct'),
        ('both', 'Wallet then M-Pesa'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='standing_orders'
    )
    wallet = models.ForeignKey(
        Wallet, 
        on_delete=models.CASCADE, 
        related_name='standing_orders'
    )
    
    # Order details
    title = models.CharField(max_length=255, help_text="Name/description of the standing order")
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('1.00'))]
    )
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    payment_method = models.CharField(
        max_length=10, 
        choices=PAYMENT_METHOD_CHOICES, 
        default='wallet'
    )
    
    # Recipient information
    recipient_name = models.CharField(max_length=255)
    recipient_phone = PhoneNumberField()
    recipient_account = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        help_text="Account number or reference"
    )
    
    # Scheduling
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    next_execution = models.DateTimeField()
    last_execution = models.DateTimeField(null=True, blank=True)
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    total_executions = models.PositiveIntegerField(default=0)
    successful_executions = models.PositiveIntegerField(default=0)
    failed_executions = models.PositiveIntegerField(default=0)
    
    # Limits and conditions
    max_executions = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Maximum number of executions (null for unlimited)"
    )
    max_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum total amount to be paid"
    )
    
    # Retry configuration
    retry_attempts = models.PositiveIntegerField(default=3)
    retry_interval_hours = models.PositiveIntegerField(default=24)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'standing_orders'
        verbose_name = 'Standing Order'
        verbose_name_plural = 'Standing Orders'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['next_execution']),
            models.Index(fields=['status', 'next_execution']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.full_name} - {self.title} ({self.amount} {self.frequency})"

    @property
    def is_due(self):
        """Check if standing order is due for execution"""
        return (
            self.status == 'active' and 
            self.next_execution <= timezone.now() and
            (self.max_executions is None or self.total_executions < self.max_executions) and
            (self.max_amount is None or self.get_total_paid() < self.max_amount)
        )

    @property
    def is_completed(self):
        """Check if standing order is completed"""
        if self.max_executions and self.total_executions >= self.max_executions:
            return True
        if self.max_amount and self.get_total_paid() >= self.max_amount:
            return True
        if self.end_date and timezone.now() > self.end_date:
            return True
        return False

    def get_total_paid(self):
        """Get total amount paid through this standing order"""
        return self.executions.filter(
            status='completed'
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

    def calculate_next_execution(self):
        """Calculate next execution date based on frequency"""
        if self.last_execution:
            base_date = self.last_execution
        else:
            base_date = self.start_date
        
        if self.frequency == 'daily':
            return base_date + timezone.timedelta(days=1)
        elif self.frequency == 'weekly':
            return base_date + timezone.timedelta(weeks=1)
        elif self.frequency == 'monthly':
            # Add one month, handling month-end edge cases
            if base_date.month == 12:
                return base_date.replace(year=base_date.year + 1, month=1)
            else:
                return base_date.replace(month=base_date.month + 1)
        elif self.frequency == 'quarterly':
            return base_date + timezone.timedelta(days=90)
        elif self.frequency == 'yearly':
            return base_date.replace(year=base_date.year + 1)
        
        return base_date

    def execute(self):
        """Execute the standing order"""
        if not self.is_due:
            return False, "Standing order is not due for execution"
        
        # Create execution record
        execution = StandingOrderExecution.objects.create(
            standing_order=self,
            amount=self.amount,
            status='pending'
        )
        
        # Update counters
        self.total_executions += 1
        self.last_execution = timezone.now()
        self.next_execution = self.calculate_next_execution()
        
        # Check if completed
        if self.is_completed:
            self.status = 'completed'
        
        self.save(update_fields=[
            'total_executions', 
            'last_execution', 
            'next_execution', 
            'status'
        ])
        
        return True, execution

    def pause(self):
        """Pause the standing order"""
        self.status = 'paused'
        self.save(update_fields=['status'])

    def resume(self):
        """Resume the standing order"""
        if self.status == 'paused':
            self.status = 'active'
            # Recalculate next execution if needed
            if self.next_execution <= timezone.now():
                self.next_execution = timezone.now()
            self.save(update_fields=['status', 'next_execution'])

    def cancel(self):
        """Cancel the standing order"""
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.save(update_fields=['status', 'cancelled_at'])


class StandingOrderExecution(models.Model):
    """
    Individual execution of a standing order
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    standing_order = models.ForeignKey(
        StandingOrder, 
        on_delete=models.CASCADE, 
        related_name='executions'
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment details
    payment_method_used = models.CharField(max_length=10, null=True, blank=True)
    transaction_reference = models.CharField(max_length=100, null=True, blank=True)
    mpesa_receipt = models.CharField(max_length=50, null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(null=True, blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'standing_order_executions'
        verbose_name = 'Standing Order Execution'
        verbose_name_plural = 'Standing Order Executions'
        indexes = [
            models.Index(fields=['standing_order', 'created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['next_retry_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.standing_order.title} - {self.amount} ({self.status})"

    def mark_processing(self):
        """Mark execution as processing"""
        self.status = 'processing'
        self.executed_at = timezone.now()
        self.save(update_fields=['status', 'executed_at'])

    def mark_completed(self, transaction_reference=None, mpesa_receipt=None):
        """Mark execution as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if transaction_reference:
            self.transaction_reference = transaction_reference
        if mpesa_receipt:
            self.mpesa_receipt = mpesa_receipt
        self.save(update_fields=['status', 'completed_at', 'transaction_reference', 'mpesa_receipt'])

    def mark_failed(self, error_message=None):
        """Mark execution as failed"""
        self.status = 'failed'
        if error_message:
            self.error_message = error_message
        self.retry_count += 1
        
        # Schedule retry if within retry limit
        if self.retry_count < self.standing_order.retry_attempts:
            self.next_retry_at = timezone.now() + timezone.timedelta(
                hours=self.standing_order.retry_interval_hours
            )
        
        self.save(update_fields=['status', 'error_message', 'retry_count', 'next_retry_at'])

    def can_retry(self):
        """Check if execution can be retried"""
        return (
            self.status == 'failed' and 
            self.retry_count < self.standing_order.retry_attempts and
            self.next_retry_at and 
            timezone.now() >= self.next_retry_at
        )
