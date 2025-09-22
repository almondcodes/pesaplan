"""
Wallet models for PesaPlan
"""
import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from pesaplan.apps.users.models import User


class Wallet(models.Model):
    """
    User wallet for storing balance and managing transactions
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('closed', 'Closed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='wallet'
    )
    balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    phone_number = PhoneNumberField(help_text="M-Pesa linked phone number")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active'
    )
    
    # Wallet limits
    daily_limit = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('100000.00'),
        help_text="Daily transaction limit"
    )
    monthly_limit = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('1000000.00'),
        help_text="Monthly transaction limit"
    )
    
    # Tracking
    total_deposited = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    total_withdrawn = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_transaction_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'wallets'
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.full_name}'s Wallet - KES {self.balance}"

    def can_transact(self, amount):
        """Check if wallet can handle the transaction amount"""
        if self.status != 'active':
            return False, "Wallet is not active"
        
        if amount <= 0:
            return False, "Amount must be positive"
        
        if self.balance < amount:
            return False, "Insufficient balance"
        
        # Check daily limit
        today = timezone.now().date()
        daily_spent = self.transactions.filter(
            transaction_type='debit',
            created_at__date=today
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        
        if daily_spent + amount > self.daily_limit:
            return False, "Daily limit exceeded"
        
        # Check monthly limit
        month_start = today.replace(day=1)
        monthly_spent = self.transactions.filter(
            transaction_type='debit',
            created_at__date__gte=month_start
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        
        if monthly_spent + amount > self.monthly_limit:
            return False, "Monthly limit exceeded"
        
        return True, "Transaction allowed"

    def debit(self, amount, description="", reference=None):
        """Debit amount from wallet"""
        can_transact, message = self.can_transact(amount)
        if not can_transact:
            raise ValueError(message)
        
        self.balance -= amount
        self.total_withdrawn += amount
        self.last_transaction_at = timezone.now()
        self.save(update_fields=['balance', 'total_withdrawn', 'last_transaction_at'])
        
        # Create transaction record
        return WalletTransaction.objects.create(
            wallet=self,
            amount=amount,
            transaction_type='debit',
            description=description,
            reference=reference,
            balance_after=self.balance
        )

    def credit(self, amount, description="", reference=None):
        """Credit amount to wallet"""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        self.balance += amount
        self.total_deposited += amount
        self.last_transaction_at = timezone.now()
        self.save(update_fields=['balance', 'total_deposited', 'last_transaction_at'])
        
        # Create transaction record
        return WalletTransaction.objects.create(
            wallet=self,
            amount=amount,
            transaction_type='credit',
            description=description,
            reference=reference,
            balance_after=self.balance
        )


class WalletTransaction(models.Model):
    """
    Wallet transaction history
    """
    TRANSACTION_TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(
        Wallet, 
        on_delete=models.CASCADE, 
        related_name='wallet_transactions'
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    transaction_type = models.CharField(
        max_length=10, 
        choices=TRANSACTION_TYPE_CHOICES
    )
    description = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    balance_before = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    
    # M-Pesa integration
    mpesa_receipt = models.CharField(max_length=50, null=True, blank=True)
    mpesa_transaction_id = models.CharField(max_length=50, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'wallet_transactions'
        verbose_name = 'Wallet Transaction'
        verbose_name_plural = 'Wallet Transactions'
        indexes = [
            models.Index(fields=['wallet', 'created_at']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['status']),
            models.Index(fields=['reference']),
            models.Index(fields=['mpesa_receipt']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.wallet.user.full_name} - {self.transaction_type.title()} {self.amount}"

    def mark_completed(self):
        """Mark transaction as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])

    def mark_failed(self):
        """Mark transaction as failed"""
        self.status = 'failed'
        self.save(update_fields=['status'])


class WalletLimit(models.Model):
    """
    Wallet transaction limits configuration
    """
    LIMIT_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    wallet = models.ForeignKey(
        Wallet, 
        on_delete=models.CASCADE, 
        related_name='limits'
    )
    limit_type = models.CharField(max_length=10, choices=LIMIT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wallet_limits'
        verbose_name = 'Wallet Limit'
        verbose_name_plural = 'Wallet Limits'
        unique_together = ['wallet', 'limit_type']
        indexes = [
            models.Index(fields=['wallet', 'limit_type']),
        ]

    def __str__(self):
        return f"{self.wallet.user.full_name} - {self.limit_type.title()} Limit: {self.amount}"
