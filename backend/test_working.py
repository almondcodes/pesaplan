"""
Working tests to demonstrate the testing framework
"""
import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_user_creation():
    """Test creating a user"""
    User = get_user_model()
    
    user = User.objects.create_user(
        phone_number='+254712345678',
        email='test@example.com',
        first_name='John',
        last_name='Doe',
        password='testpass123'
    )
    
    assert user.phone_number == '+254712345678'
    assert user.email == 'test@example.com'
    assert user.first_name == 'John'
    assert user.last_name == 'Doe'
    assert user.check_password('testpass123')
    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.django_db
def test_user_profile_creation():
    """Test creating a user profile"""
    User = get_user_model()
    from pesaplan.apps.users.models import UserProfile
    
    user = User.objects.create_user(
        phone_number='+254712345678',
        email='test@example.com',
        first_name='John',
        last_name='Doe',
        password='testpass123'
    )
    
    profile = UserProfile.objects.create(
        user=user,
        bio='Test bio',
        address_line_1='123 Test Street',
        city='Nairobi',
        county='Nairobi',
        country='Kenya'
    )
    
    assert profile.user == user
    assert profile.bio == 'Test bio'
    assert profile.city == 'Nairobi'


@pytest.mark.django_db
def test_wallet_creation():
    """Test creating a wallet"""
    User = get_user_model()
    from pesaplan.apps.wallets.models import Wallet
    
    user = User.objects.create_user(
        phone_number='+254712345678',
        email='test@example.com',
        first_name='John',
        last_name='Doe',
        password='testpass123'
    )
    
    wallet = Wallet.objects.create(
        user=user,
        balance=1000.00,
        phone_number='+254712345678'
    )
    
    assert wallet.user == user
    assert wallet.balance == 1000.00
    assert wallet.status == 'active'


@pytest.mark.django_db
def test_wallet_transaction():
    """Test creating a wallet transaction"""
    User = get_user_model()
    from pesaplan.apps.wallets.models import Wallet, WalletTransaction
    
    user = User.objects.create_user(
        phone_number='+254712345678',
        email='test@example.com',
        first_name='John',
        last_name='Doe',
        password='testpass123'
    )
    
    wallet = Wallet.objects.create(
        user=user,
        balance=1000.00,
        phone_number='+254712345678'
    )
    
    transaction = WalletTransaction.objects.create(
        wallet=wallet,
        transaction_type='deposit',
        amount=500.00,
        balance_before=1000.00,
        balance_after=1500.00,
        description='Test deposit'
    )
    
    assert transaction.wallet == wallet
    assert transaction.transaction_type == 'deposit'
    assert transaction.amount == 500.00
    assert transaction.description == 'Test deposit'


@pytest.mark.django_db
def test_standing_order_creation():
    """Test creating a standing order"""
    User = get_user_model()
    from pesaplan.apps.wallets.models import Wallet
    from pesaplan.apps.standing_orders.models import StandingOrder
    from django.utils import timezone
    from datetime import timedelta
    
    user = User.objects.create_user(
        phone_number='+254712345678',
        email='test@example.com',
        first_name='John',
        last_name='Doe',
        password='testpass123'
    )
    
    wallet = Wallet.objects.create(
        user=user,
        balance=1000.00,
        phone_number='+254712345678'
    )
    
    standing_order = StandingOrder.objects.create(
        user=user,
        wallet=wallet,
        title='Monthly Rent',
        amount=50000.00,
        frequency='monthly',
        recipient_name='Landlord',
        recipient_phone='+254712345678',
        recipient_account='1234567890',
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=365),
        next_execution=timezone.now() + timedelta(days=30)
    )
    
    assert standing_order.user == user
    assert standing_order.wallet == wallet
    assert standing_order.title == 'Monthly Rent'
    assert standing_order.amount == 50000.00
    assert standing_order.frequency == 'monthly'
    assert standing_order.status == 'active'
