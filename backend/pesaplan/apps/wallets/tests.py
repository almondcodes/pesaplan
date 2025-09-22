"""
Tests for Wallet models and functionality
"""
import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from pesaplan.apps.wallets.models import Wallet, WalletTransaction
from pesaplan.apps.users.models import User


@pytest.mark.django_db
class TestWalletModel:
    """Test Wallet model functionality"""
    
    def test_create_wallet(self, user):
        """Test creating a wallet"""
        wallet = Wallet.objects.create(
            user=user,
            currency='KES',
            balance=Decimal('1000.00')
        )
        
        assert wallet.user == user
        assert wallet.currency == 'KES'
        assert wallet.balance == Decimal('1000.00')
        assert wallet.is_active is True
        assert wallet.created_at is not None
    
    def test_wallet_str_representation(self, user):
        """Test string representation of wallet"""
        wallet = Wallet.objects.create(
            user=user,
            currency='KES',
            balance=Decimal('1000.00')
        )
        
        assert str(wallet) == f"{user.full_name}'s Wallet - KES 1000.00"
    
    def test_wallet_one_to_one_relationship(self, user):
        """Test one-to-one relationship with user"""
        wallet = Wallet.objects.create(
            user=user,
            currency='KES',
            balance=Decimal('1000.00')
        )
        
        # Test reverse relationship
        assert user.wallet == wallet
        
        # Test that only one wallet can exist per user
        with pytest.raises(IntegrityError):
            Wallet.objects.create(
                user=user,
                currency='USD',
                balance=Decimal('100.00')
            )
    
    def test_wallet_currency_choices(self, user):
        """Test wallet currency choices"""
        wallet = Wallet.objects.create(
            user=user,
            currency='USD',
            balance=Decimal('100.00')
        )
        
        assert wallet.currency == 'USD'
    
    def test_wallet_balance_validation(self, user):
        """Test wallet balance validation"""
        wallet = Wallet.objects.create(
            user=user,
            currency='KES',
            balance=Decimal('-100.00')  # Negative balance should be allowed for overdraft
        )
        
        assert wallet.balance == Decimal('-100.00')
    
    def test_wallet_status_choices(self, user):
        """Test wallet status choices"""
        wallet = Wallet.objects.create(
            user=user,
            currency='KES',
            balance=Decimal('1000.00'),
            status='suspended'
        )
        
        assert wallet.status == 'suspended'
        assert wallet.is_active is False
    
    def test_wallet_metadata(self, user):
        """Test wallet metadata field"""
        metadata = {'bank_account': '1234567890', 'branch': '001'}
        wallet = Wallet.objects.create(
            user=user,
            currency='KES',
            balance=Decimal('1000.00'),
            metadata=metadata
        )
        
        assert wallet.metadata == metadata
        assert wallet.metadata['bank_account'] == '1234567890'


@pytest.mark.django_db
class TestWalletTransactionModel:
    """Test WalletTransaction model functionality"""
    
    def test_create_wallet_transaction(self, wallet):
        """Test creating a wallet transaction"""
        transaction = WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='deposit',
            amount=Decimal('500.00'),
            balance_before=Decimal('1000.00'),
            balance_after=Decimal('1500.00'),
            description='Test deposit'
        )
        
        assert transaction.wallet == wallet
        assert transaction.transaction_type == 'deposit'
        assert transaction.amount == Decimal('500.00')
        assert transaction.balance_before == Decimal('1000.00')
        assert transaction.balance_after == Decimal('1500.00')
        assert transaction.description == 'Test deposit'
        assert transaction.status == 'completed'
    
    def test_wallet_transaction_str_representation(self, wallet):
        """Test string representation of wallet transaction"""
        transaction = WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='deposit',
            amount=Decimal('500.00'),
            balance_before=Decimal('1000.00'),
            balance_after=Decimal('1500.00'),
            description='Test deposit'
        )
        
        expected = f"Deposit of KES 500.00 - {wallet.user.full_name}"
        assert str(transaction) == expected
    
    def test_wallet_transaction_type_choices(self, wallet):
        """Test wallet transaction type choices"""
        transaction = WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='withdrawal',
            amount=Decimal('200.00'),
            balance_before=Decimal('1000.00'),
            balance_after=Decimal('800.00'),
            description='Test withdrawal'
        )
        
        assert transaction.transaction_type == 'withdrawal'
    
    def test_wallet_transaction_status_choices(self, wallet):
        """Test wallet transaction status choices"""
        transaction = WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='deposit',
            amount=Decimal('500.00'),
            balance_before=Decimal('1000.00'),
            balance_after=Decimal('1500.00'),
            description='Test deposit',
            status='pending'
        )
        
        assert transaction.status == 'pending'
    
    def test_wallet_transaction_reference_generation(self, wallet):
        """Test automatic reference generation"""
        transaction = WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='deposit',
            amount=Decimal('500.00'),
            balance_before=Decimal('1000.00'),
            balance_after=Decimal('1500.00'),
            description='Test deposit'
        )
        
        assert transaction.reference is not None
        assert len(transaction.reference) > 0
    
    def test_wallet_transaction_metadata(self, wallet):
        """Test wallet transaction metadata field"""
        metadata = {'external_id': 'ext_123', 'gateway': 'mpesa'}
        transaction = WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='deposit',
            amount=Decimal('500.00'),
            balance_before=Decimal('1000.00'),
            balance_after=Decimal('1500.00'),
            description='Test deposit',
            metadata=metadata
        )
        
        assert transaction.metadata == metadata
        assert transaction.metadata['external_id'] == 'ext_123'
    
    def test_wallet_transaction_ordering(self, wallet):
        """Test wallet transaction ordering"""
        # Create transactions with different timestamps
        transaction1 = WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='deposit',
            amount=Decimal('100.00'),
            balance_before=Decimal('1000.00'),
            balance_after=Decimal('1100.00'),
            description='First deposit'
        )
        
        transaction2 = WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='deposit',
            amount=Decimal('200.00'),
            balance_before=Decimal('1100.00'),
            balance_after=Decimal('1300.00'),
            description='Second deposit'
        )
        
        # Get transactions ordered by created_at (most recent first)
        transactions = WalletTransaction.objects.filter(wallet=wallet)
        
        assert transactions[0] == transaction2  # Most recent first
        assert transactions[1] == transaction1


@pytest.mark.django_db
class TestWalletBusinessLogic:
    """Test wallet business logic"""
    
    def test_wallet_balance_calculation(self, wallet):
        """Test wallet balance calculation through transactions"""
        # Initial balance
        assert wallet.balance == Decimal('0.00')
        
        # Add deposit transaction
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='deposit',
            amount=Decimal('1000.00'),
            balance_before=Decimal('0.00'),
            balance_after=Decimal('1000.00'),
            description='Initial deposit'
        )
        
        # Update wallet balance
        wallet.balance = Decimal('1000.00')
        wallet.save()
        
        assert wallet.balance == Decimal('1000.00')
        
        # Add withdrawal transaction
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='withdrawal',
            amount=Decimal('200.00'),
            balance_before=Decimal('1000.00'),
            balance_after=Decimal('800.00'),
            description='Withdrawal'
        )
        
        # Update wallet balance
        wallet.balance = Decimal('800.00')
        wallet.save()
        
        assert wallet.balance == Decimal('800.00')
    
    def test_wallet_transaction_history(self, wallet):
        """Test getting wallet transaction history"""
        # Create multiple transactions
        for i in range(3):
            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type='deposit',
                amount=Decimal(f'{100 * (i + 1)}.00'),
                balance_before=Decimal(f'{100 * i}.00'),
                balance_after=Decimal(f'{100 * (i + 1)}.00'),
                description=f'Deposit {i + 1}'
            )
        
        # Get transaction history
        transactions = wallet.wallet_transactions.all()
        
        assert transactions.count() == 3
        assert transactions[0].amount == Decimal('300.00')  # Most recent first
        assert transactions[2].amount == Decimal('100.00')  # Oldest last
    
    def test_wallet_suspension(self, wallet):
        """Test wallet suspension functionality"""
        assert wallet.is_active is True
        
        # Suspend wallet
        wallet.status = 'suspended'
        wallet.save()
        
        assert wallet.is_active is False
        assert wallet.status == 'suspended'
    
    def test_wallet_reactivation(self, wallet):
        """Test wallet reactivation functionality"""
        # Suspend wallet first
        wallet.status = 'suspended'
        wallet.save()
        assert wallet.is_active is False
        
        # Reactivate wallet
        wallet.status = 'active'
        wallet.save()
        
        assert wallet.is_active is True
        assert wallet.status == 'active'
